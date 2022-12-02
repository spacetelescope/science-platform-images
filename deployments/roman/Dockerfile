
# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE
FROM $BASE_IMAGE AS build

# ----------------------------------------------------------------------
# Duplicated in config,  these are for standalone non-hub lab use.

ENV CRDS_PATH=/home/jovyan/crds_cache
ENV CRDS_SERVER_URL=https://roman-crds-test.stsci.edu
# ENV CRDS_VERBOSITY=20

# ----------------------------------------------------------------------
USER root

# ------------------------------------------------------------------------------
# Install environments

# All specs for frozen builds need to be available before their normal installs
USER ${NB_UID}

# ----------------------------------------------------------------------
# Add jupyter-lab-extensions to base environment as well as standard packages.
# Performing common update here enables mission specific frozen spec.

COPY --chown=${NB_UID}:${NB_GID} env-frozen/base/  /opt/env-frozen/base/
RUN   /opt/common-scripts/install-common  base

# ----------------------------------------------------------------------
# Roman CAL
#
# Copy romcan-cal conda environment requirements: floating, frozen, chilly
# All copies below are factored to enable Docker idempotence / build caching
# e.g. changing tests should not result in re-installing conda

#COPY --chown=${NB_UID}:${NB_GID} environments/roman-cal/*.yml  /opt/environments/roman-cal/
COPY --chown=${NB_UID}:${NB_GID} environments/roman-cal/*.explicit  /opt/environments/roman-cal/

# roman-cal currently needs to pin pip<21.3 due to issue with git clone --filter=blob:none
# and pip-compile when installing git+https://github.com style requirements.  This potentially
# should be a generic hint.
COPY --chown=${NB_UID}:${NB_GID} environments/roman-cal/*.conda  /opt/environments/roman-cal/

COPY --chown=${NB_UID}:${NB_GID} env-frozen/roman-cal/  /opt/env-frozen/roman-cal/

COPY --chown=${NB_UID}:${NB_GID} env-chilly/roman-cal/  /opt/env-chilly/roman-cal/

# ----- Install romcan-cal conda environment
RUN /opt/common-scripts/env-conda roman-cal

# ----- Copy romcan-cal pip requirements
# ----- This will include both romancal release requirements and anything JH adds.
COPY --chown=${NB_UID}:${NB_GID} environments/roman-cal/*.pip  /opt/environments/roman-cal/

# ----  Compile romcan-cal pip requirements to dependency solution
RUN /opt/common-scripts/env-compile roman-cal

# ----- Install compiled roman-cal pip dependency solution
RUN /opt/common-scripts/env-sync roman-cal

# ----- Copy remaining roman environments files, including tests and post-start-hook scripts
# NOTE: this is a Docker cache buster and why builds back up to env installation when you're
# iterating on the post-start-hook or tests.  The problem is that the broad copy makes it look
# like potentially all roman-cal-specific requirements have changed.
COPY --chown=${NB_UID}:${NB_GID} environments/roman-cal/ /opt/environments/roman-cal/

# ----- COPY --chown=${NB_UID}:${NB_GID} nersc-refresh-announcements/ nersc-refresh-announcements/
# ----- RUN cd nersc-refresh-announcements && \
# -----     pip install . && \
# -----     cd .. && \
# -----     rm -rf nersc-refresh-announcements

# ========================= ^^^^^ Custom  ^^^^^ =========================
# ========================= vvvvv Generic vvvvv  =========================

# Fix JS encoding issue that prevents widgets from displaying properly in notebook mode
# See https://github.com/jupyter/notebook/issues/6033 for details
RUN sed -i 's/data-base-url="{{base_url | urlencode}}"/data-base-url="{{base_url}}"/g' `ls -1 ${CONDA_DIR}/lib/python*/site-packages/notebook/templates/notebook.html`

# ----------------------------------------------------------------------

USER $NB_UID
RUN /opt/common-scripts/kernel-setup   # set up Ipython / JupyterLab kernels

# ----------------------------------------------------------------------
# As part of Dockerfile.trailer,  these statements are executed from the
# perspective of the deployment image directory,  not common.

USER root

RUN find /home/${NB_USER} ! -uid ${NB_UID} | xargs chown ${NB_UID}:${NB_GID}

# remove this step once nbgitpuller enabled; these contents will be in the
#  jupyterhub-user-content repo.   Install deployment-specific $HOME files.
COPY default-home-contents/ /etc/default-home-contents
RUN  cp -r /home/jovyan/.local /etc/default-home-contents && \
     cp -r /home/jovyan/.jupyter /etc/default-home-contents
COPY global_bashrc /home/jovyan
RUN  cat /home/jovyan/global_bashrc >> /etc/bash.bashrc  && \
     rm /home/jovyan/global_bashrc

# Fix certs in conda for application level SSL, e.g. pass image-test running on CI-node
RUN /opt/common-scripts/fix-certs

# Copy any remaining environments files not caught by more precise as-needed build copies
COPY --chown=${NB_UID}:${NB_GID} environments/    /opt/environments/

# ----------------------------------------------------------------------
# YYYY SEC

USER root
#RUN  /opt/common-scripts/npm-audit  /usr/share/npm/node_modules/socks-proxy-agent  fix  && \
RUN   /opt/common-scripts/env-clean

#RUN  find /opt/conda -name yarn.lock | grep jupyterlab/staging | xargs rm -f || true

# ----------------------------------------------------------------------
# For standalone operation outside JupyterHub,  note that  /etc also includes
# common home directory files.   post-start-hook may not include everything required
# for running on AWS,  just common functions needed for both AWS and standalone/CI.

USER $NB_USER
WORKDIR /home/$NB_USER
RUN /opt/environments/post-start-hook  docker   # docker == do not run hub-specific functions of hook
CMD [ "start-notebook.sh" ]
