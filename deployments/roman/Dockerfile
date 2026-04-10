# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE=notebook-common
FROM ${BASE_IMAGE}

ARG NBW_ROOT="/opt/nbw-live"
ENV NBW_ROOT="${NBW_ROOT}"
ARG NBW_PANTRY="/teams/admin/nbw-pantry"

# ----------------------------------------------------------------------
# Duplicated in config,  these are for standalone non-hub lab use.

ENV CRDS_PATH=$HOME/crds_cache
ENV CRDS_SERVER_URL=https://roman-crds.stsci.edu
# ENV CRDS_VERBOSITY=20
ENV PYTHONPATH="/srv/jupyter"

# ------------------------------------------------------------------------------
# Install environments

# All specs for frozen builds need to be available before their normal installs
USER ${NB_UID}:${NB_GID}
# USER root

# ----------------------------------------------------------------------
# Add jupyter-lab-extensions to base environment as well as standard packages.
# Performing common update here enables mission specific frozen spec.

COPY --chown=${NB_UID}:${NB_GID} env-frozen/base/  /opt/env-frozen/base/
COPY --chown=${NB_UID}:${NB_GID} environments/common-hints.pip /opt/environments/common-hints.pip
COPY --chown=${NB_UID}:${NB_GID} environments/ /opt/environments/

WORKDIR ${NBW_ROOT}
USER root

RUN   /opt/common-scripts/install-common  base

# Run wrangler from base environment creating/installing spec'ed environment
# If the spec says python3 ("base") it will add to the base environment instead of creating a second
RUN source /opt/common-scripts/env-activate base && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --reinstall ) && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --data-print >/opt/environments/nbw-exports.sh ) && \
    ( python -m nb_wrangler /opt/environments/nbw-wrangler-spec.yaml --env-compact --delete-repos ) && \
    fix-permissions ${NBW_ROOT} ${NBW_PANTRY} /opt/conda && \
    /opt/common-scripts/env-clean

# ----- Copy remaining roman environments files, including tests and post-start-hook scripts
# NOTE: this is a Docker cache buster and why builds back up to env installation when you're
# iterating on the post-start-hook or tests.  The problem is that the broad copy makes it look
# like potentially all roman-cal-specific requirements have changed.
# COPY --chown=${NB_UID}:${NB_GID} environments/roman-cal/ /opt/environments/roman-cal/
COPY stop_server_ext.json /etc/jupyter/jupyter_server_config.d/stop_server_ext.json
COPY stop_server_ext.py /srv/jupyter/stop_server_ext.py

# ========================= ^^^^^ Custom  ^^^^^ =========================
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
