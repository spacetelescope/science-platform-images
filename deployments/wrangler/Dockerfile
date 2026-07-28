# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE=notebook-common
FROM ${BASE_IMAGE} AS build

ARG NBW_ROOT="/opt/nbw-live"
ENV NBW_ROOT="${NBW_ROOT}"

ARG NBW_PANTRY="/teams/admin/nbw-pantry"
ENV NBW_PANTRY="${NBW_PANTRY}"

SHELL ["/bin/bash", "--login", "-c"]

# ----------------------------------------------------------------------
# Install environments

ENV PYTHONPATH="/srv/jupyter"

USER root
RUN chown ${NB_UID}:${NB_GID} /opt/conda/conda-meta  && \
    rm -f /opt/conda/conda-meta/conda-meta.lock

RUN mkdir -p ${NBW_ROOT} && chown -R ${NB_UID}:${NB_GID} ${NBW_ROOT} && \
    mkdir -p ${NBW_PANTRY} && chown -R ${NB_UID}:${NB_GID} ${NBW_PANTRY}

# ----------------------------------------------------------------------
# Add jupyter-lab-extensions to base environment as well as standard packages.
# Performing common update here enables mission specific frozen spec.

COPY --chown=${NB_UID}:${NB_GID} environments/  /opt/environments/
COPY --chown=${NB_UID}:${NB_GID} env-frozen/base/  /opt/env-frozen/base/

# ----------------------------------------------------------------------

# (a) Wrangler/System bash script to copy assets to destinations
USER ${NB_UID}:${NB_GID}
RUN [ ! -f /opt/environments/install-assets.sh ] || \
    bash /opt/environments/install-assets.sh

# (b) Optional Ubuntu packages if api-packages.txt is defined
USER root
RUN [ ! -f /opt/environments/apt-packages.txt ] || \
    /opt/common-scripts/apt-install $(cat /opt/environments/apt-packages.txt)

# (c) Curator bash script for arbitrary commands
USER root
RUN [ ! -f /opt/environments/dockerfile-aux.sh ] || \
    bash /opt/environments/dockerfile-aux.sh

# ------------------------------------------------------------------------------
# Install environments

# All specs for frozen builds need to be available before their normal installs
USER ${NB_UID}:${NB_GID}

WORKDIR ${NBW_ROOT}

RUN   /opt/common-scripts/install-common  base

# Run wrangler from base environment creating/installing spec'ed environment
# If the spec says python3 ("base") it will add to the base environment instead of creating a second
RUN source /opt/common-scripts/env-activate base && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --reinstall ) && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --data-print --data-env-vars-mode pantry --data-no-symlinks  >/opt/environments/nbw-exports.sh ) && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --env-compact --delete-repos ) && \
    /opt/common-scripts/env-clean

# Suppress tensorflow warnings by default, ERROR and up only
ENV TF_CPP_MIN_LOG_LEVEL=2

USER ${NB_UID}:${NB_GID}

# ========================= ^^^^^ Custom  ^^^^^ =========================
# ========================= vvvvv Generic vvvvv  =========================

# As part of Dockerfile.trailer,  these statements are executed from the
# perspective of the deployment directory,  not common.

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
