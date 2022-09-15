FROM nvidia/cuda:9.2-base-ubuntu16.04

# Refer to https://hub.docker.com/r/anibali/pytorch/dockerfile

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    mercurial \
    subversion \
    build-essential \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# Create a working directory
RUN mkdir /app
WORKDIR /app

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN mkdir /home/user
RUN chmod 777 /home/user

# Install Miniconda and Python 3.6
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH=/home/user/miniconda/bin:$PATH
RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh

# Create a Python 3.6 environment
# RUN /home/user/miniconda/bin/conda create -y --name py36 python=3.6.9 \
#  && /home/user/miniconda/bin/conda clean -ya
# ENV CONDA_DEFAULT_ENV=py36
# ENV CONDA_PREFIX=/home/user/miniconda/envs/$CONDA_DEFAULT_ENV
# ENV PATH=$CONDA_PREFIX/bin:$PATH
# RUN /home/user/miniconda/bin/conda install conda-build=3.18.9=py36_3 \
#  && /home/user/miniconda/bin/conda clean -ya

# # CUDA 9.2-specific steps
# RUN conda install -y -c pytorch \
#     cudatoolkit=9.2 \
#     "pytorch=1.4.0=py3.6_cuda9.2.148_cudnn7.6.3_0" \
#     "torchvision=0.5.0=py36_cu92" \
#  && conda clean -ya

# Install HDF5 Python bindings
RUN conda install -y h5py=2.8.0 \
 && conda clean -ya
RUN pip install h5py-cache==1.0

# Install Torchnet, a high-level framework for PyTorch
RUN pip install torchnet==0.0.4

# Install Requests, a Python library for making HTTP requests
RUN conda install -y requests=2.19.1 \
 && conda clean -ya

# Install Graphviz
RUN conda install -y graphviz=2.40.1 python-graphviz=0.8.4 \
 && conda clean -ya

# Install OpenCV3 Python bindings
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    libgtk2.0-0 \
    libcanberra-gtk-module \
 && sudo rm -rf /var/lib/apt/lists/*
RUN conda install -y -c menpo opencv \
 && conda clean -ya

# Set the default command to python3
CMD ["python3"]

COPY requirements.txt /app/.

RUN pip install -r requirements.txt --ignore-installed certifi==2018.10.15 --default-timeout=900

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${HOME}/${PROGRAM_PATH}

# Add program
ADD ./ ${HOME}/${PROGRAM_PATH}

WORKDIR ${HOME}/${PROGRAM_PATH}