"""
Open-Webui Pipeline Filter for Langfuse monitoring.
Based on:

https://github.com/open-webui/pipelines/blob/98604da8ec79323d02086fd5c5a906f1c190bf6e/examples/filters/langfuse_filter_pipeline.py
title: Langfuse Filter Pipeline
author: open-webui
date: 2024-05-30
version: 1.1
license: MIT
description: A filter pipeline that uses Langfuse.
requirements: langfuse
"""

from typing import List, Optional
from schemas import OpenAIChatMessage
import os
from copy import deepcopy

from utils.pipelines.main import get_last_user_message, get_last_assistant_message
from pydantic import BaseModel
from langfuse import Langfuse


def obscure_message(input:str)->str:
    return "A"*len(input)


def obscure_messages(body:dict)->dict:
    obscure_body = deepcopy(body)
    for i,m in enumerate(body["messages"]):
        obscure_body["messages"][i]["content"] = obscure_message(m["content"])
    return obscure_body


class Pipeline:
    class Valves(BaseModel):
        pipelines: List[str] = []
        priority: int = 0

        # Valves
        secret_key: str
        public_key: str
        host: str

    def __init__(self):
        self.type = "filter"
        self.name = "Langfuse Filter"

        # Initialize
        self.valves = self.Valves(
            **{
                "pipelines": ["*"],  # Connect to all pipelines
                "secret_key": os.getenv("LANGFUSE_SECRET_KEY", "your-secret-key-here"),
                "public_key": os.getenv("LANGFUSE_PUBLIC_KEY", "your-public-key-here"),
                "host": os.getenv("LANGFUSE_HOST", "http://langfuse-server:3000"),
            }
        )

        self.langfuse = None
        self.chat_generations = {}
        pass

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        self.set_langfuse()
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        self.langfuse.flush()
        pass

    async def on_valves_updated(self):

        self.set_langfuse()
        pass

    def set_langfuse(self):
        self.langfuse = Langfuse(
            secret_key=self.valves.secret_key,
            public_key=self.valves.public_key,
            host=self.valves.host,
            debug=False,
        )
        self.langfuse.auth_check()

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")

        # if user is not admin, obscure message for privacy
        obscure_body = deepcopy(body) if user.get("role", "user")=="admin" else obscure_messages(body)
        trace = self.langfuse.trace(
            name=f"filter:{__name__}",
            input=obscure_body,
            user_id=user["id"],
            metadata={"rag": ("citations" in body.keys()), "options":body.get("options",None), "user_role":user.get("role",None)},
            session_id=body["chat_id"],
        )

        # keep track of total document(s) length for cost calc in outlet
        self.rag_meta = {"nfiles":0, "totalCharacters":0}
        if "files" in body.keys():
            self.rag_meta["nfiles"]=len(body["files"])
            self.rag_meta["totalCharacters"] = sum([file_["file"]["meta"]["size"] for file_ in body["files"]])

        generation = trace.generation(
            name=body["chat_id"],
            model=body["model"],
            input=obscure_body["messages"],
            metadata={"interface": "open-webui"},
        )

        self.chat_generations[body["chat_id"]] = generation
        print(trace.get_trace_url())

        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"outlet:{__name__}")
        if body["chat_id"] not in self.chat_generations:
            return body
        generation = self.chat_generations[body["chat_id"]]
        print(dir(self))

        user_message = get_last_user_message(body["messages"])
        generated_message = get_last_assistant_message(body["messages"])

        generation.end(
            output=generated_message if user.get("role", "user")=="admin" else obscure_message(generated_message),
            usage={
                "input": len(user_message)+self.rag_meta["totalCharacters"], 
                "output": len(generated_message),
                "unit": "CHARACTERS",
                "totalCost":(len(user_message)+self.rag_meta["totalCharacters"]+len(generated_message))/1000,
            },
            metadata={"interface": "open-webui"},
        )

        return body
