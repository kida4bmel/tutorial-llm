#!/bin/bash

# create models dir structure for automatic1111 container
for dir in Codeformer deepbooru ESRGAN GFPGAN hypernetworks karlo LDSR Lora Stable-diffusion SwinIR VAE VAE-approx
do
    THISDIR=automatic1111/${dir}
    if [[ ! -d $THISDIR ]]
    then
        echo "creating ${THISDIR}"
        mkdir -p $THISDIR
        chmod 777 $THISDIR
    fi
done

for dir in checkpoints clip clip_vision configs controlnet diffusers embeddings gligen hypernetworks loras photomaker style_models unet upscale_models vae vae_approx
do
    THISDIR=comfyui/${dir}
    if [[ ! -d $THISDIR ]]
    then
        echo "creating ${THISDIR}"
        mkdir -p $THISDIR
        chmod 777 $THISDIR
    fi
done
