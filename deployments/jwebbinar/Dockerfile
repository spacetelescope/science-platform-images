# ========================= vvvvv Custom  vvvvv =========================

ARG BASE_IMAGE
FROM $BASE_IMAGE AS build

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
# Install environments

USER ${NB_UID}

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
# ========================= vvvvv Generic vvvvv  =========================

USER $NB_UID

# ----------------------------------------------------------------------

RUN /opt/common-scripts/kernel-setup   # set up Ipython / JupyterLab kernels

# ----------------------------------------------------------------------
# As part of Dockerfile.trailer,  these statements are executed from the
# perspective of the deployment image directory,  not common.

USER root

RUN find /home/${NB_USER} ! -uid ${NB_UID} | xargs chown ${NB_UID}:${NB_GID} || true

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

# ----------------------------------------------------------------------
# YYYY SEC

USER root
#RUN  /opt/common-scripts/npm-audit  /usr/share/npm/node_modules/socks-proxy-agent  fix  && \
#RUN   /opt/common-scripts/env-clean

#RUN  find /opt/conda -name yarn.lock | grep jupyterlab/staging | xargs rm -f || true

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

# For testing mutability of pre-installed environments once uidgid's are real, membership in users controls
# mutability but fix-permissions must be called on files which need to be mutable, particularly those we install.
#
## USER root
## RUN echo "jmiller:x:1001:1001::/home/jovyan:/bin/bash" >>/etc/passwd
## RUN grep -v users /etc/group >tmp
## RUN mv tmp /etc/group
## RUN echo "users:x:100:jmiller" >>/etc/group
## RUN echo "jmiller:x:1001:jmiller" >>/etc/group
## USER $NB_USER

USER $NB_USER
WORKDIR /home/$NB_USER
RUN /opt/environments/post-start-hook  docker   # docker == do not run hub-specific functions of hook
CMD [ "start-notebook.py" ]
