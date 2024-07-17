FROM ubuntu:22.04


RUN apt update && apt upgrade -y && \
    apt install -y wget net-tools curl iputils-ping git python3 python3-venv libgl1 libglib2.0-0

RUN groupadd --gid 1000 automatic1111 && \
    useradd --uid 1000 --gid 1000 -m automatic1111

USER automatic1111
WORKDIR /home/automatic1111
ENV PYTORCH_TRACING_MODE=TORCHFIX
ENV COMMANDLINE_ARGS="--skip-torch-cuda-test --listen --api --precision full --no-half"

RUN cd && python3 -m venv sd_env && \
    bash sd_env/bin/activate

RUN git clone https://github.com/openvinotoolkit/stable-diffusion-webui.git

RUN cd stable-diffusion-webui && \
    bash webui.sh --exit

WORKDIR /home/automatic1111/stable-diffusion-webui/

RUN rm -rf models && mkdir models

EXPOSE 7860

CMD [ "/bin/bash", "webui.sh" ]