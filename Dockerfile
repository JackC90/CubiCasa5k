FROM nvidia/cuda:9.2-base-ubuntu18.04

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
 && rm -rf /var/lib/apt/lists/*

# Create a working directory
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod -R a+rwX /home/user
# sudo chown -R user /home/user 

# Set up the Conda environment
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH=/home/user/miniconda/bin:$PATH
RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh \
 && conda install -y python==3.8.1 \
 && conda clean -ya

# CUDA 9.2-specific steps
RUN conda install -y -c pytorch \
    cudatoolkit=9.2 \
    "pytorch=1.5.0=py3.8_cuda9.2.148_cudnn7.6.3_0" \
    "torchvision=0.6.0=py38_cu92" \
 && conda clean -ya


RUN sudo apt-get update
RUN sudo apt-get upgrade -y
RUN sudo apt-get install -y \
        build-essential 
RUN sudo apt-get install -y \
        libfreetype6-dev libfontconfig1-dev xclip libgeos-dev libffi6 libffi-dev \
        libgl1-mesa-dev libglu1-mesa libxi6 libsm6 xz-utils libxrender1 nano dos2unix software-properties-common

COPY requirements.txt /app/.

RUN pip install -r requirements.txt --ignore-installed certifi==2018.10.15

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${PROGRAM_PATH}

# Add program
ADD ./ ${PROGRAM_PATH}
