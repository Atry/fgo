FROM nvidia/cuda:7.5-cudnn4-runtime-ubuntu14.04

RUN apt-get update &&\
    apt-get install -y wget xz-utils

WORKDIR /opt
RUN wget --quiet https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz &&\
    tar xf ffmpeg-git-64bit-static.tar.xz &&\
    rm ffmpeg-git-64bit-static.tar.xz &&\
    mv ffmpeg* ffmpeg
ENV PATH /opt/ffmpeg:$PATH

WORKDIR /root
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh &&\
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda &&\
    rm Miniconda3-latest-Linux-x86_64.sh

# RUN apt-get -y install python3 python3-pip
ENV PATH /opt/conda/bin:$PATH
ADD . /repo
WORKDIR /repo
RUN pip install --ignore-installed https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow-0.9.0-cp35-cp35m-linux_x86_64.whl
RUN conda install -y --file requirements.txt


ENTRYPOINT /bin/bash