FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

RUN apt update && apt upgrade -y  && apt install -y git
RUN mkdir /app && git clone https://github.com/comfyanonymous/ComfyUI/ /app/comfyui
WORKDIR /app/comfyui

RUN pip install -r requirements.txt
RUN rm -rf /app/comfyui/models && mkdir -p /app/comfyui/models

EXPOSE 7860

CMD [ "python", "-u", "main.py", "--listen", "--port", "7860", "--cpu" ]