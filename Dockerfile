FROM nvidia/cuda:9.2-base-ubuntu16.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

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
 && rm ~/miniconda.sh \
 && conda install -y python==3.6.9 \
 && conda clean -ya

# CUDA 9.2-specific steps
RUN conda install -y -c pytorch \
    cudatoolkit=9.2 \
    "pytorch=1.4.0=py3.6_cuda9.2.148_cudnn7.6.3_0" \
    "torchvision=0.5.0=py36_cu92" \
 && conda clean -ya

# Set the default command to python3
CMD ["python3"]

COPY requirements.txt /app/.

RUN pip install -r requirements.txt --ignore-installed certifi==2018.10.15

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${HOME}/${PROGRAM_PATH}

# Add program
ADD ./ ${HOME}/${PROGRAM_PATH}

WORKDIR ${HOME}/${PROGRAM_PATH}