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

# ------------------------------------------------------------------------
USER root

ARG TZ='America/New_York'
ARG DEBIAN_FRONTEND=noninteractive

ARG USE_FROZEN=1
ENV USE_FROZEN=$USE_FROZEN

ARG PIP_SWITCHES="--no-cache-dir"
ENV PIP_SWITCHES=$PIP_SWITCHES

# Enable easy swap of conda with e.g. mamba
ARG CONDA_VER=conda
ENV CONDA_VER=${CONDA_VER}

# Clearing caches at the end of each RUN saves image space
# but seems to mess up dependency debug tools like pipdeptree.
# NOT setting this is also a requirement of effective Docker
# buildkit cache use.  ATM jupyter/docker-stacks will still wipe
# out caches created prior to the common base image regardless.
ARG CLEAR_PKG_CACHES="1"
ENV CLEAR_PKG_CACHES=${CLEAR_PKG_CACHES}

# These are duplicated in jupyter/docker-stacks so need to be changed
# in both locations.  Better than hard coding in scripts though.
ENV NB_UID=1000
ENV NB_GID=100

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
        rename
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
        fftw3-dev \
        libatlas-base-dev \
        libcurl4-openssl-dev \
        libxml2 \
        libxml2-dev \
        libxslt1.1 \
        libxslt1-dev \
        python3-libxml2 \
        python-dev-is-python3 \
        python-setuptools \
        graphviz \
        libopenblas-dev

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

# ----------------------------------------------------------------------
# YYYY SEC

RUN npm install -g --prod yarn             && \
    npm install -g --prod yarn-audit-fix   && \
    npm install -g minimist                && \
    npm cache clean --force && \
    yarn cache clean --force

COPY --chown=${NB_UID}:${NB_GID}  tools/  /opt/tools/
COPY --chown=${NB_UID}:${NB_GID} VERSION /opt
