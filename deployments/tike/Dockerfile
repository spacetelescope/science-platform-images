# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE
FROM $BASE_IMAGE AS build

# ---------------------------------------------------------------
# VARTOOLS Light Curve Analysis Program
USER root
RUN curl --silent --show-error https://www.astro.princeton.edu/~jhartman/vartools/vartools-1.38.tar.gz -o vartools-1.38.tar.gz && \
   tar zxf vartools-1.38.tar.gz &&\
   cd vartools-1.38 &&\
   mkdir -p /usr/local &&\
   ./configure --prefix=/use/local &&\
   make &&\
   make install &&\
   cd .. &&\
   rm -rf vartools-1.38 vartools-1.38.tar.gz

# ----------------------------------------------------------------------
# Install environments

USER ${NB_UID}

# ----------------------------------------------------------------------
# Add jupyter-lab-extensions to base environment as well as standard packages.
# Performing common update here enables mission specific frozen spec.

COPY --chown=${NB_UID}:${NB_GID} env-frozen/base/  /opt/env-frozen/base/
RUN   /opt/common-scripts/install-common  base

# --------------------------- TESS -------------------------------------

COPY --chown=${NB_UID}:${NB_GID} env-frozen/tess/  /opt/env-frozen/tess/
COPY --chown=${NB_UID}:${NB_GID} env-chilly/tess/  /opt/env-chilly/tess/
COPY --chown=${NB_UID}:${NB_GID} environments/tess/*.yml /opt/environments/tess/
RUN /opt/common-scripts/env-conda tess

COPY --chown=${NB_UID}:${NB_GID} environments/tess/*.pip /opt/environments/tess/
RUN /opt/common-scripts/env-compile tess

RUN /opt/common-scripts/env-sync  tess

COPY --chown=${NB_UID}:${NB_GID} environments/tess/ /opt/environments/tess/

# ----------
# Due to numpy binary API incompatibilities and available compiled pip package versions
# Re-building from source ensures compatability with the installed numpy
# Install these BEFORE the packages which depend on them or you may get incompatible versions from PyPi

RUN /opt/common-scripts/env-src-install  tess  batman-package

RUN /opt/common-scripts/env-src-install  tess  radvel

RUN /opt/common-scripts/env-src-install  tess  juliet

RUN /opt/common-scripts/env-src-install  tess  tvguide

# ellc is a dependency of allesfitter
RUN /opt/common-scripts/env-src-install  tess  ellc
RUN /opt/common-scripts/env-src-install  tess  allesfitter

# ----------------------------------------------------------------------
# YYYY SEC

USER $NB_USER
RUN  /opt/common-scripts/npm-audit  /opt/conda/envs/tess/lib/python3.8/site-packages/panel  fix  && \
     /opt/common-scripts/env-clean

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
