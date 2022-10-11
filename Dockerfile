FROM nvidia/cuda:11.6.1-base-ubuntu20.04

# Refer to https://hub.docker.com/r/anibali/pytorch/dockerfile

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

ENV TZ=Asia/Singapore \
    DEBIAN_FRONTEND=noninteractive

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    sudo \
    autoremove \
    git \
    gfortran \
    bzip2 \
    dos2unix \
    libgl1 \
    libgl1-mesa-dev \
	libglu1-mesa \
    libevent-dev \
    libfreetype6-dev \
    libxft-dev \
    libglib2.0-0 \
    libxi6 \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libgeos-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    software-properties-common \
    xclip \
    xz-utils \
    python3-dev \
    libffi7 libffi-dev \
    mercurial \
    subversion \
    build-essential \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# Install OpenCV3 Python bindings
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    libgtk2.0-0 \
    libcanberra-gtk-module \
 && sudo rm -rf /var/lib/apt/lists/*

# Create a working directory
RUN mkdir /app
WORKDIR /app

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN mkdir $HOME $HOME/.cache $HOME/.config \
 && chmod -R 777 $HOME

# Set up the Conda environment (using Miniforge)
ENV PATH=$HOME/mambaforge/bin:$PATH
COPY environment.yml /app/environment.yml
RUN curl -sLo ~/mambaforge.sh https://github.com/conda-forge/miniforge/releases/download/4.12.0-2/Mambaforge-4.12.0-2-Linux-x86_64.sh \
 && chmod +x ~/mambaforge.sh \
 && ~/mambaforge.sh -b -p ~/mambaforge \
 && rm ~/mambaforge.sh \
 && mamba env update -n base -f /app/environment.yml \
 && rm /app/environment.yml \
 && mamba clean -ya

RUN conda install \
 'pytorch=1.12.1=py3.9_cuda11.6_cudnn8.3.2_0' \
 'torchvision=0.13.1=py39_cu116' \
 -c pytorch \
 && conda clean -ya

# Install blender
ENV BLENDER_PATH /usr/local/blender/blender
ENV BLENDER_MAJOR 2.93
ENV BLENDER_VERSION 2.93.0
ENV BLENDER_BZ2_URL https://mirror.clarkson.edu/blender/release/Blender$BLENDER_MAJOR/blender-$BLENDER_VERSION-linux-x64.tar.xz

RUN mkdir /usr/local/blender && \
	curl -SL "$BLENDER_BZ2_URL" -o blender.tar.xz && \
	tar -xf blender.tar.xz -C /usr/local/blender --strip-components=1 && \
	rm blender.tar.xz

# Set the default command to python3
CMD ["python3"]

COPY requirements.txt /app/.

RUN python -m pip install -r requirements.txt --default-timeout=900

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${HOME}/${PROGRAM_PATH}

# Add program
ADD ./ ${HOME}/${PROGRAM_PATH}

WORKDIR ${HOME}/${PROGRAM_PATH}