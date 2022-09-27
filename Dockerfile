FROM nvidia/cuda:11.5.1-base-ubuntu20.04

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

# Set the default command to python3
CMD ["python3"]

COPY requirements.txt /app/.

RUN python -m pip install -r requirements.txt --ignore-installed certifi==2018.10.15 --default-timeout=900

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${HOME}/${PROGRAM_PATH}

# Add program
ADD ./ ${HOME}/${PROGRAM_PATH}

WORKDIR ${HOME}/${PROGRAM_PATH}