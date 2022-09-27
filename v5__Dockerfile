FROM nvidia/cuda:10.2-base-ubuntu18.04

# Refer to https://hub.docker.com/r/anibali/pytorch/dockerfile

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    sudo \
    git \
    gfortran \
    bzip2 \
    libgl1 \
    libevent-dev \
    libfreetype6-dev \
    libxft-dev \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libgeos-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    xclip \
    python3-dev \
    libffi6 libffi-dev \
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

# Install Miniconda and Python 3.8
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH=/home/user/miniconda/bin:$PATH
RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh \
 && conda install -y python==3.8.1 \
 && conda clean -ya

# Create a Python 3.7 environment
# RUN /home/user/miniconda/bin/conda create -y --name py37 python=3.6.9 \
#  && /home/user/miniconda/bin/conda clean -ya
# ENV CONDA_DEFAULT_ENV=py36
# ENV CONDA_PREFIX=/home/user/miniconda/envs/$CONDA_DEFAULT_ENV
# ENV PATH=$CONDA_PREFIX/bin:$PATH
# RUN /home/user/miniconda/bin/conda install conda-build=3.18.9=py36_3 \
#  && /home/user/miniconda/bin/conda clean -ya

RUN conda config --set unsatisfiable_hints True
RUN conda config --add channels conda-forge
# RUN conda config --set channel_priority strict

# CUDA 10.2-specific steps
RUN conda install -y -c pytorch \
    cudatoolkit=10.2 \
    "pytorch=1.5.0=py3.8_cuda10.2.89_cudnn7.6.5_0" \
    "torchvision=0.6.0=py38_cu102" \
 && conda clean -ya

# Install HDF5 Python bindings
RUN conda install -y h5py=3.5.0 \
 && conda clean -ya
RUN pip install h5py-cache==1.0

# Install Torchnet, a high-level framework for PyTorch
RUN pip install torchnet==0.0.4

# Install Requests, a Python library for making HTTP requests
RUN conda install -y requests=2.27.1 \
 && conda clean -ya

# Install Graphviz
RUN conda install -y graphviz=2.40.1 python-graphviz=0.8.4 \
 && conda clean -ya

# Install OpenCV3 Python bindings
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    libgtk2.0-0 \
    libcanberra-gtk-module \
 && sudo rm -rf /var/lib/apt/lists/*
RUN conda install libgcc-ng=11.2.0
RUN conda install -y -c conda-forge opencv \
 && conda clean -ya

# Set the default command to python3
CMD ["python3"]

COPY requirements.txt /app/.

RUN python -m pip install -r requirements.txt --ignore-installed certifi==2018.10.15 --default-timeout=900

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${HOME}/${PROGRAM_PATH}

# Add program
ADD ./ ${HOME}/${PROGRAM_PATH}

WORKDIR ${HOME}/${PROGRAM_PATH}