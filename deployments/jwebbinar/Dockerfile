# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE
FROM $BASE_IMAGE AS build

# ----------------------------------------------------------------------

# All data is arranged on /data opening up options for sharing a file system
ENV MIRAGE_DATA=/data/mirage \
    PYSYN_CDBS=/refdata/cdbs \
    # WEBBPSF_PATH=/data/webbpsf-data \
    pandeia_refdata=/data/pandeia \
    STPSF_PATH=/refdata/stpsf-data

# ----------------------------------------------------------------------

ENV CRDS_PATH=$HOME/crds_cache
ENV CRDS_SERVER_URL=https://jwst-crds.stsci.edu
# ENV CRDS_VERBOSITY=20    # 0 or missing for normal output,  -1 for no INFO,  50 for default DEBUG

# ----------------------------------------------------------------------
# Install non-environment packages early to avoid constant trailing rebuilds
# while working conda/pip dependency issues.
# BUG: we have no standard process for adding tests for these.

USER root

# # Get webbpsf-data-0.9.0.tar.gz
# RUN mkdir /data && cd /data && \
#     wget --quiet https://stsci.box.com/shared/static/qcptcokkbx7fgi3c00w2732yezkxzb99.gz && \
#     tar zxf qcptcokkbx7fgi3c00w2732yezkxzb99.gz && \
#     rm qcptcokkbx7fgi3c00w2732yezkxzb99.gz && \
#     chmod -R a+r /data/webbpsf-data && \
#     fix-permissions $CONDA_DIR $HOME

# Install sextractor under /usr/local
# NOTE: using master because this fix is required:
#       https://github.com/astromatic/sextractor/commit/46dd48faff6a7b59939096ba55e83e02e865ddfc
RUN cd /tmp && \
    wget https://github.com/astromatic/sextractor/archive/master.zip && \
    unzip master.zip && \
    cd sextractor-master && \
    sh autogen.sh && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    fix-permissions $CONDA_DIR $HOME


# ----------------------------------------------------------------------
# Install environments

USER root

# ----------------------------------------------------------------------
# Add jupyter-lab-extensions to base environment as well as standard packages.
# Performing common update here enables mission specific frozen spec.

COPY --chown=${NB_UID}:${NB_GID} env-frozen/base/  /opt/env-frozen/base/
COPY --chown=${NB_UID}:${NB_GID} environments/common-hints.pip /opt/environments/common-hints.pip
RUN   /opt/common-scripts/install-common  base

# --------------------------- Masterclass -------------------------------------

ENV JH_DEFAULT_KERNEL=masterclass

# BASE
COPY --chown=${NB_UID}:${NB_GID} env-frozen/masterclass/ /opt/env-frozen/masterclass/
COPY --chown=${NB_UID}:${NB_GID} environments/masterclass/*.yml /opt/environments/masterclass/
RUN /opt/common-scripts/env-conda masterclass

# COMPILE ALL
COPY --chown=${NB_UID}:${NB_GID} environments/masterclass/*.pip /opt/environments/masterclass/
RUN /opt/common-scripts/env-compile masterclass

# SYNC ALL
RUN /opt/common-scripts/env-sync masterclass

# REMAINING ENV
COPY --chown=${NB_UID}:${NB_GID} environments/masterclass/ /opt/environments/masterclass/

# --------------------------- jwebbinar 40 -------------------------------------

USER root

## Skip this step, /refdata/stpsf-data will be set up in post-start-hook with custom data
# Get stpsf-data
# RUN mkdir /refdata && cd /refdata && \
#     wget --quiet https://stsci.box.com/shared/static/kqfolg2bfzqc4mjkgmujo06d3iaymahv.gz && \
#     tar zxf kqfolg2bfzqc4mjkgmujo06d3iaymahv.gz && \
#     rm kqfolg2bfzqc4mjkgmujo06d3iaymahv.gz && \
#     chmod -R a+r /refdata/stpsf-data && \
#     fix-permissions $CONDA_DIR $HOME

# Get synphot data
RUN mkdir /refdata && cd /refdata && \
    wget --quiet https://arizona.box.com/shared/static/cbkxlwvokml7n1gref8nw3neg98kzcwn.gz && \
    tar zxf cbkxlwvokml7n1gref8nw3neg98kzcwn.gz && \
    rm cbkxlwvokml7n1gref8nw3neg98kzcwn.gz && \
    chmod 777 /refdata && \
    chmod -R a+r /refdata/cdbs && \
    fix-permissions $CONDA_DIR $HOME
# ========================= vvvvv Generic vvvvv  =========================

USER ${NB_UID}:${NB_GID}

# ----------------------------------------------------------------------

RUN /opt/common-scripts/kernel-setup   # set up Ipython / JupyterLab kernels

# ----------------------------------------------------------------------
# As part of Dockerfile.trailer,  these statements are executed from the
# perspective of the deployment image directory,  not common.

USER root

# remove this step once nbgitpuller enabled; these contents will be in the
#  jupyterhub-user-content repo.   Install deployment-specific $HOME files.
COPY default-home-contents/ /etc/default-home-contents
RUN  cp -r $HOME/.local /etc/default-home-contents && \
     cp -r $HOME/.jupyter /etc/default-home-contents
COPY global_bashrc $HOME
RUN  cat $HOME/global_bashrc >> /etc/bash.bashrc  && \
     cat $HOME/global_bashrc >> /etc/bash.env  && \
     rm $HOME/global_bashrc

# Copy any remaining environments files not caught by more precise as-needed build copies
COPY --chown=${NB_UID}:${NB_GID} environments/    /opt/environments/

# ----------------------------------------------------------------------

COPY --chown=${NB_UID}:${NB_GID}  MISSION_VERSION /opt
COPY --chown=${NB_UID}:${NB_GID}  MISSION_HASH /opt
RUN  [ $USE_FROZEN -eq "1" ] && echo >/opt/FROZEN || echo >/opt/FLOATING

# ----------------------------------------------------------------------
# For standalone operation outside JupyterHub,  note that  /etc also includes
# common home directory files.   post-start-hook may not include everything required
# for running on AWS,  just common functions needed for both AWS and standalone/CI.

# Enable deletion of non-empty directories from lab GUI
RUN echo "# -------------------------------- STSCI Config Overwrites --------------------------------" \
      >> /etc/jupyter/jupyter_notebook_config.py &&\
    echo "c.FileContentsManager.delete_to_trash = False" >> /etc/jupyter/jupyter_notebook_config.py &&\
    echo "c.FileContentsManager.always_delete_dir = True" >> /etc/jupyter/jupyter_notebook_config.py &&\
    echo "# -------------------------------- STSCI Config Overwrites --------------------------------" \
      >> /etc/jupyter/jupyter_server_config.py &&\
    echo "c.FileContentsManager.delete_to_trash = False" >> /etc/jupyter/jupyter_server_config.py &&\
    echo "c.FileContentsManager.always_delete_dir = True" >> /etc/jupyter/jupyter_server_config.py

USER root
RUN fix-permissions $CONDA_DIR $HOME
USER ${NB_UID}:${NB_GID}

WORKDIR $HOME
RUN /opt/environments/post-start-hook  docker   # docker == do not run hub-specific functions of hook
CMD [ "start-notebook.py" ]
