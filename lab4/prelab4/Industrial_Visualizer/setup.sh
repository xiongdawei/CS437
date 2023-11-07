#!/bin/bash

# Define the environment name
ENV_NAME=CS437

conda create --name $ENV_NAME python=3.11

# Activate the new environment
conda init $SHELL
conda activate $ENV_NAME
    
# Install NumPy in the new environment
conda install -n $ENV_NAME numpy
conda install -n $ENV_NAME pyqt
conda install -n $ENV_NAME pyserial
conda install -n $ENV_NAME pyopengl
conda install -n $ENV_NAME pyqtgraph==0.11.0
conda install -n $ENV_NAME scipy
conda install -n $ENV_NAME matplotlib
conda install -n $ENV_NAME pyserial
conda install -n $ENV_NAME jupyter notebook