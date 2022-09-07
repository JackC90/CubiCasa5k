FROM anibali/pytorch:cuda-9.0

RUN sudo apt-get update
RUN sudo apt-get upgrade -y
RUN sudo apt-get install -y \
        build-essential 

COPY requirements.txt /app/.

RUN pip install -r requirements.txt --ignore-installed certifi==2018.10.15

ENV PROGRAM_PATH floorplan
RUN mkdir -p ${HOME}/${PROGRAM_PATH}

RUN sudo adduser --disabled-password --gecos '' --shell /bin/bash user || echo 'User $user already exists.'
USER user
RUN sudo chown -R user /app && sudo chown -R user ${HOME}/${PROGRAM_PATH}


# Add program
ADD ./ ${HOME}/${PROGRAM_PATH}

WORKDIR ${HOME}/${PROGRAM_PATH}