# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE=notebook-common
FROM ${BASE_IMAGE}

# ----------------------------------------------------------------------

# All data is arranged on /data opening up options for sharing a file system
ENV MIRAGE_DATA=/data/mirage \
    PYSYN_CDBS=/data/pysynphot \
    WEBBPSF_PATH=/data/webbpsf-data \
    pandeia_refdata=/data/pandeia

# ----------------------------------------------------------------------

ENV CRDS_PATH=$HOME/crds_cache
ENV CRDS_SERVER_URL=https://jwst-crds.stsci.edu
# ENV CRDS_VERBOSITY=20    # 0 or missing for normal output,  -1 for no INFO,  50 for default DEBUG

# ----------------------------------------------------------------------
# Install non-environment packages early to avoid constant trailing rebuilds
# while working conda/pip dependency issues.
# BUG: we have no standard process for adding tests for these.

USER root

# Get webbpsf-data-0.9.0.tar.gz
RUN mkdir /data && cd /data && \
    wget --quiet https://stsci.box.com/shared/static/qcptcokkbx7fgi3c00w2732yezkxzb99.gz && \
    tar zxf qcptcokkbx7fgi3c00w2732yezkxzb99.gz && \
    rm qcptcokkbx7fgi3c00w2732yezkxzb99.gz && \
    chmod -R a+r /data/webbpsf-data && \
    fix-permissions $CONDA_DIR $HOME

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
# Wrangler extensions for (a) extra apt packages and (b) custom script

# (a) Optional Ubuntu packages if api-packages.txt is defined
RUN [ ! -f /opt/environments/apt-packages.txt ] || \
    /opt/common-scripts/apt-install $(cat /opt/environments/apt-packages.txt)

# (b) Bash script for arbitrary commands
RUN [ ! -f /opt/environments/apt-packages.txt ] || \
    bash /opt/environments/dockerfile-aux.sh

# ----------------------------------------------------------------------
# Install environments

USER ${NB_UID}:${NB_GID}

# ----------------------------------------------------------------------
# Add jupyter-lab-extensions to base environment as well as standard packages.
# Performing common update here enables mission specific frozen spec.

COPY --chown=${NB_UID}:${NB_GID} env-frozen/base/  /opt/env-frozen/base/
COPY --chown=${NB_UID}:${NB_GID} environments /opt/environments

RUN   /opt/common-scripts/install-common  base

# --------------------------- Jwebbinar -------------------------------------

# ----------------------------------------------------------------------
# Mission environment reinstalled from curated wrangler spec
# Run wrangler from base environment creating/installing spec'ed environment
# If the spec says python3 ("base") it will add to the base environment instead of creating a second

RUN source /opt/common-scripts/env-activate base && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --reinstall ) && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --data-print >/opt/environments/nbw-exports.sh ) && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --env-compact --delete-repos ) && \
    fix-permissions ${NBW_ROOT} ${NBW_PANTRY} /opt/conda && \
    /opt/common-scripts/env-clean

RUN /opt/common-scripts/env-run jwebbinar  pip install  --no-deps  'eureka@git+https://github.com/kevin218/Eureka.git@jwebbinar41'
# ========================= vvvvv Generic vvvvv  =========================

USER ${NB_UID}:${NB_GID}

# ----------------------------------------------------------------------

#
# RUN /opt/common-scripts/kernel-setup   # set up Ipython / JupyterLab kernels
# RUN /opt/common-scripts/wrangler-register-kernel  (post start hook)

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

# Copy any remaining environments files not caught by more precise as-needed build copies
COPY --chown=${NB_UID}:${NB_GID} environments/    /opt/environments/

RUN  cat $HOME/global_bashrc /opt/environments/nbw-exports.sh >> /etc/bash.bashrc  && \
     cat $HOME/global_bashrc /opt/environments/nbw-exports.sh >> /etc/bash.env  && \
     printf '\nDefaults    lecture = never\n' >> /etc/sudoers && \
     rm -f $HOME/global_bashrc $HOME/.bashrc

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


ENV NBW_PANTRY=/teams/admin/nbw-pantry
RUN mkdir -p ${NBW_PANTRY} && chown -R ${NB_UID}:${NB_GID} ${NBW_PANTRY}

USER ${NB_UID}:${NB_GID}
RUN /opt/environments/post-start-hook  docker   # docker == do not run hub-specific functions of hook

USER root
RUN fix-permissions $CONDA_DIR $HOME

USER ${NB_UID}:${NB_GID}
WORKDIR $HOME
CMD [ "start-notebook.py" ]
