# ================ vvvvv Generic Image vvvvv ==================

# If the image (jupyter/scipy-notebook) exists locally it will be used,
# otherwise the latest from https://hub.docker.com/_/buildpack-deps will be used

ARG BASE_IMAGE=spacetelescope/scipy-notebook
FROM $BASE_IMAGE

# ------------------------------------------------------------------------

LABEL maintainer="Science Platforms <dmd_octarine@stsci.edu>"

# Environment variables
ENV MKL_THREADING_LAYER="GNU"

# conda related env vars
ENV CONDA_DIR=/opt/conda
ENV SHELL=/bin/bash
ENV PATH=${CONDA_DIR}/bin:${PATH}
ENV CFLAGS="-fcommon -fpic"

ARG TZ='America/New_York'
ARG DEBIAN_FRONTEND=noninteractive

ARG USE_FROZEN=1
ENV USE_FROZEN=$USE_FROZEN

ARG PIP_SWITCHES=""
ENV PIP_SWITCHES=$PIP_SWITCHES

# Enable easy swap of conda with e.g. mamba
ARG CONDA_VER=conda
ENV CONDA_VER=${CONDA_VER}

ARG USER_CACHE_DIRS=""
ENV USER_CACHE_DIRS=${USER_CACHE_DIRS}

# These are duplicated in jupyter/docker-stacks so need to be changed
# in both locations.  Better than hard coding in scripts though.
ENV NB_UID=1000
ENV NB_GID=100

# ------------------------------------------------------------------------
# Make sure user cache directories exist before RUN caching uses then as mount points

USER root

RUN for DIR in ${USER_CACHE_DIRS};  do mkdir -p ${DIR}; chown -R $NB_UID:$NB_GID ${DIR}; done

# ------------------------------------------------------------------------
# Breaking into separate runs will build slower but also defines storage
# consumption in docker history.
#
COPY common-scripts/apt-install  /opt/common-scripts/apt-install
RUN /opt/common-scripts/apt-install \
    apt-utils \
    tzdata \
    ca-certificates \
    openssl \
    wget \
    vim \
    npm \
    nodejs

# Misc system tools
RUN /opt/common-scripts/apt-install \
        tree \
        curl \
        wget \
        rsync \
        locales \
        less \
        ssh \
        htop \
        sysstat \
        net-tools \
        rename \
        stress-ng
        #        libexpat1

# S/W Development Tools
RUN /opt/common-scripts/apt-install \
        build-essential \
        gfortran \
        automake \
        libtool \
        make \
        cmake \
        vim \
        emacs-nox \
        libfftw3-dev \
        libatlas-base-dev \
        libcurl4-openssl-dev \
        libxml2 \
        libxml2-dev \
        libxslt1.1 \
        libxslt1-dev \
        python3-libxml2 \
        python-dev-is-python3 \
        graphviz \
        libopenblas-dev

# Install Rust language
RUN /opt/common-scripts/apt-install cargo rustc

# Libraries for FITS, DS9, ML
RUN /opt/common-scripts/apt-install \
        file \
        libcfitsio-bin \
        libcfitsio-dev \
        apt-file \
        libxpa-dev \
        libxt-dev \
        libbz2-dev

# YYYY SEC
#       nvidia-cuda-toolkit

# Latex
# RUN /opt/common-scripts/apt-install \
#        texlive-latex-recommended \
#        cm-super

# YYYY SEC
# RUN apt-get update && \
#    apt-get remove --yes libpdfbox-java libfontbox-java && \
#    apt autoremove --yes

# ------------------------------------------------------------------------
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# ==================== Begin pip & conda installs =======================

USER root

# Load conda profile scripts by default, symlink target doesn't exist for a bit
RUN ln -s ${CONDA_DIR}/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# ------------------------------------------------------------------------
USER root

# Keep Xfce directories out of home and set up shortcuts for DS9.
#COPY user-dirs.defaults /etc/xdg/user-dirs.defaults

COPY --chown=${NB_UID}:${NB_GID}  common-scripts/ /opt/common-scripts
COPY --chown=${NB_UID}:${NB_GID}  common-env/ /opt/common-env

COPY bash.bashrc /tmp
RUN cat /tmp/bash.bashrc >> /etc/bash.bashrc

# For ENV_BASH definition for non-login shells
COPY bash.env /etc/bash.env
ENV BASH_ENV=/etc/bash.env

# ----------------------------------------------------------------------
# Common conda environments
#USER ${NB_UID}
#COPY environments/ /opt/environments/

# ----------------------------------------------------------------------
# Set up astroquery and ds9 desktop short-cut, will be further
# augmented by specific deployments
USER ${NB_UID}
COPY default-home-contents/   /etc/default-home-contents

ENV  PIP_TOOLS_CACHE_DIR=$HOME/.cache/pip

# ----------------------------------------------------------------------
# YYYY SEC

RUN npm install -g --prod yarn             && \
    npm install -g --prod yarn-audit-fix   && \
    npm install -g minimist                && \
    npm cache clean --force && \
    yarn cache clean --force

COPY --chown=${NB_UID}:${NB_GID}  tools/  /opt/tools/
COPY --chown=${NB_UID}:${NB_GID} VERSION /opt
COPY --chown=${NB_UID}:${NB_GID} HASH /opt
