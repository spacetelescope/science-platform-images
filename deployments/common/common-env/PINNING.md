This directory contains files which are nominally installed in every environment.
Currently this is typically done in two ways:

1. Most environments install the specs from common-env using the pip-tools
based framework.  Typically this means that common-env/*.conda are installed
using conda during env-conda environment creation.  Later common-env/*.pip are
installed as part of env-compile and env-sync.  Between saved frozen specs
requirements.yml and requirements.txt, these environments are tightly spec'ed
for frozen builds.

2. For the base environment, common-env/*.conda and common-env/*.pip are added
using env-update after the base environment is built as part of scipy-notebook.
Additionally,  some jupyterlab extension setup steps are performed as part of
install-common for the base environment only.   While each environment may need
common-env/*.pip,  it should be sufficient to perform labextension and npm setup
only in base because these are not differentiated by conda env.

IMPORTANT: It's recommended to keep these files at a minimum because the
likelihood of dependency conflicts increases as more files are added and may
affect any of the other deployments.  Conflicts can be sidestepped either by
dropping new conflicting files or cherry picking .pip files installed by
env-compile.  The ability to omit selected .pip files is one rationale
for organizing packages into sublists like common.pip or jupyter.pip.

Unfortunate conda packages
==========================

See common.conda which violates the general principal of minimizing conda
installs because of some installation-related or non-pip packages:

 - pip
 - pip-tools
 - setuptools
 - nodejs
 - conda-tree
 - conda-build

Some packages are "unsafe" for pip-tools and if not installed early result in
e.g. wrong python used.   Since these packages must precede pip-tools,  they
cannot follow the normal pip-tools process of compiling all requirements at
one time.

jupyterlab + notebook CVE
=========================

[CVE Blog](https://blog.jupyter.org/cve-2021-32797-and-cve-2021-32798-remote-code-execution-in-jupyterlab-and-jupyter-notebook-a70fae0d3239)

- jupyterlab>=3.1.4
- notebook>=6.4.1

Jupyter Notebook 6.4.1 or above, 5.7.11 or above.
Jupyter Lab 3.1.4 or above, 3.0.17 or above, 2.3.2 or above, 2.2.10 or above , 1.2.21 or above


jupyter-desktop-server
======================

websockify installed in common.conda to avoid:

```
Exception: rebind.so not found, perhaps you need to run make
```

where:

[websockify issue](https://github.com/novnc/websockify/issues/413)

suggests that locating rebind.so is fragile,  presumably conda gets it right.

Works with websocketify==0.10.0 (unpinned pypi)
Works with jupyter-desktop-server on pypi vs. Yuvi's personal git repo

setuptools
==========

- setuptools~=57.0

Pinned due to use_2to3 removal in 58.x setuptools.


jupyter_server_proxy
====================

[jupyter-server-proxy readthedocs](https://jupyter-server-proxy.readthedocs.io/en/latest/install.html)

  `pip install jupyter-server-proxy`

Needed for `pip install -e`:

  `jupyter serverextension enable --sys-prefix jupyter_server_proxy`

notebook extensions
===================

ipywidgets
----------

In most cases, installing the Python ipywidgets package will also automatically
configure classic Jupyter Notebook and JupyterLab 3.0 to display
ipywidgets. With pip, do:

  `pip install ipywidgets`


nbwidgetsextension
------------------

Is related ipywidgets.

[ipywidgets docs](https://ipywidgets.readthedocs.io/en/latest/user_install.html)

Most of the time, installing ipywidgets automatically configures Jupyter
Notebook to use widgets. The ipywidgets package does this by depending on the
widgetsnbextension package, which configures the classic Jupyter Notebook to
display and use widgets. If you have an old version of Jupyter Notebook
installed, you may need to manually enable the ipywidgets notebook extension
with:

  `jupyter nbextension enable --py widgetsnbextension`

When using virtualenv and working in an activated virtual environment, the
--sys-prefix option may be required to enable the extension and keep the
environment isolated:

  `jupyter nbextension enable --py widgetsnbextension --sys-prefix`

ipyevents
---------

[ipyevents github](https://github.com/mwcraig/ipyevents)

```
  pip install ipyevents

  jupyter labextension install @jupyter-widgets/jupyterlab-manager ipyevents
```

ipyvuetify
----------

[ipyvuetify docs](https://github.com/mwcraig/ipyevents)

Always:

```
  pip install ipyvuetify
  jupyter nbextension enable --py --sys-prefix ipyvuetify
```

For lab support:

  `jupyter labextension install jupyter-vuetify`


ipysplitpanes
-------------

[ipysplitpanes github](https://github.com/nmearl/ipysplitpanes)

To install use pip:

```
  pip install ipysplitpanes
  jupyter nbextension enable --py --sys-prefix ipysplitpanes
```

To install for jupyterlab:

```
  jupyter labextension install ipysplitpanes
```

bqplot
------

[bqplot github](https://github.com/bqplot/bqplot)

Using pip:

```
  pip install bqplot
```

If you are using JupyterLab <=2:

```
  jupyter labextension install @jupyter-widgets/jupyterlab-manager bqplot
```

bqplot_image_gl
---------------

An ipywidget image widget for showing images in bqplot using WebGL.

Used for: [glue-viz github](https://github.com/glue-viz/glue-jupyter)

- currently requires latest developer version of bqplot

[bqplot image gl github](https://github.com/glue-viz/bqplot-image-gl)

To install use pip:

```
  pip install bqplot-image-gl
```

jupyter golden layout
---------------------

[ipygoldenlayout github](https://github.com/nmearl/ipygoldenlayout)

To install use pip:

```
  pip install ipygoldenlayout
  jupyter nbextension enable --py --sys-prefix ipygoldenlayout
```

To install for jupyterlab:

```
  jupyter labextension install ipygoldenlayout
```

[jupyter-golden-layout npmjs](https://www.npmjs.com/package/jupyter-golden-layout)

```
  npm install --save jupyter-golden-layout
```

jupyterlab extensions
=====================

jupyterlab/server-proxy
-----------------------

[jupyterlab-server-proxy github](https://github.com/jupyterhub/jupyter-server-proxy)

General install:

```
  pip install jupyter-server-proxy
```

For jupyterlab:

```
  jupyter labextension install @jupyterlab/server-proxy
```

jupyter-widgets/jupyterlab-manager
----------------------------------

From pip:

```
  pip install jupyterlab_widgets
```

No labenable required >= v3

ipyevents
---------

See above under notebook extensions:

jupyter-vuetify
---------------

None required >= v3

d3-seletion-multi
-----------------

No docs on install,  leave as-is with:

```
  jupyter labextension install d3-selection-multi
```

bqplot
------

No labextension install required >= v3

npm packages
============

jupyter-splitpanes
------------------

[jupyter-splitpanes npmjs](https://www.npmjs.com/package/jupyter-splitpanes)

IPyWidget wrapper for the SplitPanes Vue package

jupyter-golden-layout
---------------------

bqplot-image-gl
---------------
   [bqplot-image-gl npmjs](https://www.npmjs.com/package/bqplot-image-gl)

```
   npm install --save jupyter-golden-layout
```
