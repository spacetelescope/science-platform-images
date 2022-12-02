# ================ vvvvv Generic Image vvvvv ==================

# If the image (jupyter/scipy-notebook) exists locally it will be used,
# otherwise the latest from https://hub.docker.com/_/buildpack-deps will be used

ARG BASE_IMAGE=stsci-jh/scipy-notebook
FROM $BASE_IMAGE

# ------------------------------------------------------------------------

LABEL maintainer="Science Platforms <dmd_octarine@stsci.edu>"

# Environment variables
ENV MKL_THREADING_LAYER="GNU"

# conda related env vars
ENV CONDA_DIR=/opt/conda
ENV SHELL=/bin/bash
ENV PATH=${CONDA_DIR}/bin:${PATH}
ENV CFLAGS="-fcommon"

# ------------------------------------------------------------------------
USER root

# Breaking into separate runs will build slower but also defines storage
# consumption in docker history.
#
# COPY common-scripts/apt-install  /opt/common-scripts/apt-install

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
# This must be run after conda installs
RUN /opt/common-scripts/fix-certs

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
RUN cat /opt/common-scripts/global_bashrc >> /etc/bash.bashrc

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

RUN npm set config set cafile /etc/ssl/certs/stsci-tls-ca-bundle.pem

RUN npm install -g --prod yarn             && \
    npm install -g --prod yarn-audit-fix   && \
    npm install -g minimist                && \
    yarn config set cafile /etc/ssl/certs/stsci-tls-ca-bundle.pem && \
    npm cache clean --force && \
    yarn cache clean --force
