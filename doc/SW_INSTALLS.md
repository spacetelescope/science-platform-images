# User S/W Installation Methods

## Overview

The STScI Science Platforms all come pre-installed with both doman specific
astronomical and generic analysis software.  It's our intent to make these
environments full featured, current, and useful but inevitably they will not
meet every need.  Hence to give users full control over their environments, the
science platforms also provide the capability to install persistent custom
Python environments and corresponding JupyterLab kernels needed to use them
in notebooks.

## Environments and Kernels

*Environments* are a basic feature of Python and conda and are used to install
sets of independent packages.  By switching environments, different collections
of installed packages and/or package versions are made available.  *Kernels* in
contrast are the way in which Python environments are made available to
JupyterLab.  There is a one-to-one relationship between environments and
kernels.  One consequence of this arrangement is that to create a useful user
s/w installation one needs to first create an environment, then create a kernel
from it so that it can be selected inside JupyterLab to run notebooks.

## Persistence

The science platforms include the ability to modify the pre-installed s/w for
the duration of the current session and current user only.   To do this just
use conda and pip normally while a pre-installed environment is active.   Note
however that such changes will be discarded at the end of the user session.
In order to perform s/w installations which will persist for longer than one
session,  it is necessary to create a custom environment which is installed
under $HOME.

## Temorary Package installs from a Notebook

Installing additional packages into the pre-existing environments is fairly
straight forward even within the notebook environment.   The only real trick
is that you must first activate the desired installation environment and then
conda or pip install the additional packages:

From a notebook cell:

```
[1]: !conda run -n <pre-installed environment> pip install <pkg1> <pkg2> ...
```

Or from a terminal window:

```
$ conda activate <pre-installed environment>
pip install <pkg1> <pkg2> ...
```

Note that in addition to being temporary, these techniques may result in
package version conflicts due to the large numbers of pre-installed packages.
In the case of conflicts,  switching to a smaller personal persistent
environment as documented below may help.


## Science Platform Persistent User Environments

To assist setting up persistent custom environments and JupyterLab kernels, the
science plaforms provide a set of scripts which manage the details.  **Its
highly recommended** the below commands be run from the terminal window as
needed.  The `kernel-create` and `kernel-create-venv` commands should ideally
be run starting with an active environment other than `base`; typically the
terminal window will open with such an environment active.  While the commands
are numbered and arranged below in the order you are likely to use them over
time, there is no expectation that you would run them all at once.  Rather, the
expectation is that you will create a kernel(s), activate the environment if
you want to use it from the command line, install s/w using pip or conda when
applicable, and delete the kernel when you no longer need it, possibly many
weeks and JupyterLab sessions later.

### 1. `kernel-create  <environment-name> [<python-version>]  [<lab-display-name>]`

`kernel-create` creates a minimal persistent conda environment stored in the
`$HOME/envs/conda/<environment-name>` subdirectory.  It also creates a
jupyterlab kernel so the environment may be used in notebooks.  conda
environments made this way consume more space than virtual environments but
should be largely independent of the pre-installed s/w and other persistent
environments.

```
$ kernel-create  a-conda-env-name  3.10  "Lab Kernel Menu Item"
```

The above command creates the conda environment `a-conda-env-name` with a
basic `Python-3.10.x` installation and an item in the JupyterLab kernel
selection menu displayed as `Lab Kernel Menu Item`.

Once you have created your new kernel, you should be able to activate it with
`kernel-activate` and install packages using conda or pip.  Additional support
is documented below for setting up Python virtual environments but it's worth
noting that you can stop right here and work in conda alone.

### 2. `kernel-create-venv  <environment-name>  [<lab-display-name>]`

*kernel-create-venv* creates a persistent python virtualenv stored in the
*$HOME/envs/venv/<environment-name>* subdirectory.  It also creates a
jupyterlab kernel so the environment may be used in notebooks.  The vitrualenv
will be based on the Python of the active environment, so for the most stable
results a persistent conda environment should be active when you run it.
Virtual envirionments consume less space than typical conda environments by
linking to s/w which is already installed in the active environment.  They
also tend to be quicker to install due to avoided downloads and installations.

```
$ source kernel-activate a-conda-env-name
$ kernel-create-venv  some-notebook-venv  "Lab Notebook Kernel Menu Item"
$ source kernel-activate some-notebook-venv
```

Because `some-notebook-venv` is created while `a-conda-env-name` is active
it should inherit the persistence and stability of `some-notebook-env`.  In
contrast,  if it is based on a pre-installed environment,  it may degrade
or become unusable when the pre-installed environment is replaced with a
newer version.

### 3. `source kernel-activate <environment-name>`

When sourced in a terminal window, the *kernel-activate* script will activate the
specified *environment-name* for use on the command line.  The environment may be
either conda or virtual environment but must be installed as described above.
Note that the active kernel for a notebook is not conveyed to shell commands run
using `!`.  By choosing the appropriate item from the kernel menu,  it is possible
to set the kernel used for all cells in a notebook;  this is the analog for using
*kernel-activate* in the terminal.

```
$ source kernel-activate an-env-name
```

### 4. `source kernel-deactivate <environment-name>`

This script deactivates the specified persistent environment.  Note that unlike conda
and ordinary virtual environments,  the *kernel-deactivate* command needs to know the
name of the environment being deactivated.   *Kernel-deactivate* must also be sourced
into the terminal's current shell.   Note that there is no direct analog in notebook
windows for kernel-deactivate;  the two choices which come close are to select an alternate
kernel or to shut down the current kernel.

```
$ source kernel-deactivate an-env-name
```

### 5. `kernel-delete <environment-name>`

This script deletes the specified environment and corresponding jupyterlab
kernel.  It can delete both persistent conda and virtual environments. As
you might expect,  deleting a kernel/environment of either kind frees disk
space formerly occupied by the kernel's packages.

```
$ kernel-delete  an-env-name
```

## Supporting Specific Notebook Requirements

Where possible, using general purpose environments is probably best and will
save you storage space and install time.  Nevertheless, at some point you may
find yourself wanting or needing the certainty of installing exactly an
application's requested environment.  Here an "application" might be as small
as a single notebook.  Regardless of your application, this workflow may help:

  - Create a generic persistent base environment using `kernel-create <your-conda-env>`.

  - Activate your new persistent conda environment using `source kernel-activate <your-conda-env>`.

  - Create a notebook specific virtualenv based on (a) above using `kernel-create-venv <your-virtualenv>.

  - Activate your new virtual environment using `source kernel-activate <your-virtualenv>`.

  - Use `pip install -r requirements.txt` to install the notebook's specific requirements into the virtualenv.

This approach should leverage the storage and install-time efficiency of
virtualenv's while keeping close fidelity to the specified requirements of a
particular notebook.

Note: it is possible to simplify the above by eliminating the virtual
environment and installing directly to your persistent conda env.  However, if
you desire to support multiple notebooks or other use cases, adding all their
individual `requirements.txt` files to the same environment will inevitably
lead to conflicts.  Hence exploiting multiple lighter weight virtual
environments, one for each dedicated notebook kernel, may be easier and more
exacting in the long run.
