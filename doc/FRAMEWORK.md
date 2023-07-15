# Framework for JupyterHub Deployments and Testing

## Configuring your environment

Copy `setup-env.template` to setup-env and set the environment variables at
the top of the file to describe your deployment and images.

## Building Images

To factor out common features, the image has been partitioned into two separate
Docker builds: (1) a common base image shared by all missions providing a more
consistent environment across missions and (2) a mission specific image which
adds the specific software and dependencies required by that mission.

### Convenience scripts

- image-build   -  Build both common and mission images

- image-test    -  Run mission image tests in container using /opt/environments/test

### Build Requirements

#### General Strategy

Requirements for each environment type come in several formats which are
nominally *always* broken down into `conda` and `pip` files, but which tend to
have more than one instance of each type due to:

1. Verbatim requirements delivered to JH as part of the base image or a CAL
release version.

2. Additional package lists which are divided either to orchestrate install
ordering or to separate lists by shareable topics, e.g. basic analysis or ML.
Addional lists might be shared verbatim within JH either to add the same
packages to multiple missions or to add them to multiple environments.

Types of package lists are identified by extension rather than overall name:

1. `.yml` specs nominally define an initial conda environment
2. `.explicit` specs are like `.yml` (and mutually exclusive) but are in conda's `@explicit` format
2. `.conda` specs define conda packages which must be added after the initial environment is created and before `.pip` files.
3. `.pip`  specs define packages to be installed by pip-tools and/or raw pip.
4. GitHub or PyPi source URI's are sometimes required and should nominally occur last using env-src-install if it is not possible to install them with pip-tools

To keep verbatim requirements pristine or enforce ordering, the additional package lists are kept separate.

Typically the fundamental environment will be described by an `<env>.yml` or `<env>.explicit` file,  and any fundamental applications will be defined in an `<env>.pip` file.   These are the recommended names for package lists downloaded as part of releases but can just as easily describe homebrew floating environments.

As a rule packages in the initial conda environment should be limited to packages not installable via pip.   These include things like Python, C and Fortan compilers, pip, cython, etc... or simply whatever a verbatim environment file defines.  Note that even packages available on PyPi are sometimes installed via conda to achieve ordering not obtainable with pip-tools simultaneous unordered install of all packages,  e.g. cython is a prerequisite to installing compiled extensions in a pip package.

### Common base contents

The common base image defines software and setup which is shared for all missions.  The common base image includes these parts:

1. A *Dockerfile* which defines the core Linux package set and base Jupyter environment,
extending the jupyter/scipy-notebook image.

2. A *common/common-scripts* directory which includes scripts used to standardize
installation and testing.   These generally run inside the container and/or installed
environments.

3. A *common/common-env* directory which defines packages which are nominally
installed in all conda environments.

4. A *Dockerfile.trailer* file which represents the final steps required to prepare
a mission image.  As implemented this is just concatenated to a mission's Dockerfile.custom
to produce the mission image Dockerfile.

It's noteworthy that at present the base image Ubuntu packages, npm installs, and `base` conda environment and `common-env` additions,  which (probably) define the notebook UI behind the scenes,  all float,  even for `frozen` or `chilly` builds. Whether it is better to track community work constantly or better to be able to pin,  the derivation of our base image from `jupyter/docker-stacks` places it largely outside our control,  unless we either accept image-bloat for retroactive version changes or Docker layer squashing becomes a standard capability.

### Deployment/Mission Image

The mission image for each deployment is based on the common image and adds extra software and setup unique to the mission:

1. `Dockerfile.custom` defines the core mission specific software setup.  This primarily consists of conda environment setups which are layered in multiple pieces to support incremental development and Docker caching.  See `roman/Dockerfile.custom` for an example of the `COPY` and `RUN` commands which first transfer and then install packages for environment specs.   The copies of requirements specs and corresponding env-xxx commands which install them are carefully ordered to minimize Docker cache busting to e.g. avoid rebuilding the base conda environment every time a different .pip install is tried.

2. The `environments` subdirectory defines conda environments and related pip installs.  Each environment is given a subdirectory where lists of conda and pip packages are defined.  This structure separates the "what" from the "how" and ensures package lists of the same kind are installed the same way,  within and across missions.  It also makes it easier to see, update, and share what is installed.  Each environment automatically becomes a JH kernel and defines a `kernel.name` file defining the kernel's notebook display name.  In contrast,  the environment directory name defines the Python environment name.   To resolve dependency conflicts which may arise from requirements which are too vague,  each environment defines a build-hints.pip file which should defined all pip constraints required to define and ensure a successful build;  see Resolving Dependency Conflicts below.

3. Within each environment, a `tests` subdirectory defines tests for that environment.   An top-level `environments/test` script defines arbitrary tests for the mission and is ultimately installed at `/opt/test` and run by `image-test` in CI.  While the top-level `test` is arbitrary,  it typically calls standard subscripts which create common behavior across missions and environments:  support for import tests,  notebook smoke tests, and an environment-specific `test` script that is executed.   If any of these are omitted,  that kind of test is just skipped.
#### Environment Build Scripts

The Dockerfile workflow used to create a conda environment using pip-tools is typically something like:

```
/opt/common-scripts/env-conda   <env>    # Create minimal conda environment.
/opt/common-scripts/env-compile <env>    # Resolve loose pip constraints to requirements.txt
/opt/common-scripts/env-sync    <env>    # Download and install requirements.txt
/opt/common-scripts/env-src-install  ... # Build packages with missing or incompatible binaries from source.
/opt/common-scripts/env-update <env>     # Add .conda or .pip lists after other install steps, particulary for `base`
...
```
These commands generally produce improved diagnostics relative to pip defaults and also do a better job with frozen builds.  They compile loosely constrained conda or pip requirements into fully pinned requirements.yml and requirements.txt. Ultimately a frozen or chilly environment is built with respect to requirements.* rather than on-the-fly dependency resolution.

`env-update` predates and does not use pip-tools so it may degrade or break earlier dependency solutions.  With the exception of retroactively updating the `base` environment `env-update` should be avoided unless called implicitly by other scripts.

#### Resolving Dependency Conflicts

Fundamentally, resolving dependency conflicts entails changing loose requirements definitions as needed and recompiling the package version solutions.   It's both a mathematically precise specification process, and at the same time more of an art than a science.

*IMPORTANT* historically we have solved pip dependency conflicts by directly changing the requirement spec where a bad requirement is first requested.    This left pins scattered throughout the codebase in ways which are difficult to keep tabs on and/or increased the likelihood of inter-mission conflicts.  Moreover,  with the advent of chilly builds,  build failures associated with not carrying over *required* version hints became an issue.   As a result,  to the degree possible,  .pip requirements needed to make builds work should be defined for each environment in a file named `build-hints.pip`.  `build-hints.pip` is the one .pip file carried over,  verbatim, to frozen or chilly builds.   All other .pip files should be versionless package lists.  It is OK to specify the same package with different constraints so packages added to `build-hints.pip` should not be removed from the spec which originally requests them.

##### Wrong Version of Python Supported

One particularly confusing dependency resolution problem occurs when a
particular x.y.z version of some package does exist, but not for the desired
Python version.  In this case pip can make it sound like version x.y.z doesn't
exist at all, but a quick visit to PyPi immediately contradicts pip: look,
x.y.z is right there!  Digging deeper by looking at file downloads on PyPi, one
may find that no distribution exists for the exact version of Python in the
target environment.  This problem can be resolved using `env-src-install` and
compiling a version for the target environment from source.

##### Incompatible Numpy ABI Used

A pernicious conflict occurs when an environment has pinned numpy for some
reason while numpy is in the process of undergoing an ABI change (Application
Binary Interface).  In this case, a package compiled for one version of numpy
won't work for versions of numpy with a different ABI.  Worse, this is only
detected on package import because PyPi has no mechanism to communicate which
ABI is being supported and can only distribute a package compiled for a single
ABI version.  Generally newly compiled pacakges on PyPi will track the new
numpy ABI version, while a back-pinned numpy uses the old ABI version by
definition.  Here again the solution is to re-compile new package sources
against the older installed numpy using `env-src-install`.

##### Dependency Maze

A network of dependency constraints on 5-6 interrelated packages can be
difficult to follow.  Fortunately, this is a common problem so scripts have been
developed that can help out, particularly `pipdeptree`.  In cooperation with
`Graphviz`, `pipdeptree` can produce graphs of dependency relationships as .png
files which are annotated with version constraints.  This makes it easier to
see which constraints must be mutually satisfied.

The script `image-graph-env` is used to run `pipdeptree` as a container job
conveniently.  This is only useful for environments which build successfully
but fail to run correctly, and it further helps if packages in conflict can be
named precisely.  For environments which fail to build, output from
`env-compile` can often show the dependency conflicts causing the failure
instead but can be more difficult to understand.

#### Test Definitions

Standard test setup for each `environment/<kernel>/tests` can include:

1. An `imports` file which lists packages for which Python-importability should be
verified one per line.

2. A `notebooks` file which lists paths to test notebooks which should execute without
errors when run headless.

3. Individual `.ipynb` notebook files which should execute without errors when
run headless.

4. A `test` script which is executed if defined.

Additional files or subdirectories which will be installed along with the rest of the
environment/`kernel` files under `/opt/environments/<kernel>`.

By convention `imports` tests are defined statically as part of defining
required packages for each environment.  Failing imports imply the environment
is broken.

In contrast, the `notebooks` file is currently defined on the fly by the
`post-start-hook` script where the appropriate notebook kernel for each
notebook is also defined by running `set-notebook-kernels`.  Partly this is
because notebooks are defined independently of JupyterHub and are not intrinsic
to the kernel definitions,  partly it is because actual notebooks are not
available until `git-sync` is run to clone them by the `post-start-hook`.

Where defined, `notebooks-failing`, `long-notebooks`, and
`long-notebooks-failing` define notebook lists which are not executed by
default by CI (`image-test`).  These define notebooks with excessive runtime
and notebooks or persistent failures which haven't been addressed.  Like
`notebooks` all are created by the `post-start-hook` script.

### Running Tests

You can run tests locally using the script `image-test`.  The `image-test`
script launches a container from the local Docker build and then executes the
`/opt/environments/test` entry point.

There are additional common entry points which can be executed independently
for focusing on specific problems:

- `/opt/common-scripts/test-environments`

- `/opt/common-scripts/env-test <kernel>`

- `/opt/common-scripts/test-notebooks   <kernel>   <notebook .ipynb files...>`

- `/opt/common-scripts/test-imports  <kernel>  <pkgs to test imports for...>`

### Using image-dev to Debug

If you find yourself hating life because you're waiting an hour for a Docker
build after changing two lines of source, over-and-over, give image-dev a try.

The image-dev script runs an interactive bash shell inside a JH container to
let you debug environments, scripts, and tests.  The key behavior is that
image-dev mounts:

   common/common-scripts -->  /opt/common-scripts

   common/common-env     -->  /opt/common-env

   <mission>/environments --> /opt/environments

all as r/w inside the container.  This lets you edit files inside or outside
the container and immediately see the results in both contexts.  It enables you
make source changes and evaluate the effects in a high fidelity environment
without doing full Docker builds.

Because the sources are mounted r/w, when you are done editing and testing and
exit the container, changes are waiting for you ready to add and commit.

Note that if you modify test definitions by editing
/opt/environments/post-start-hook, you need to re-run it to regenerated
`notebooks` files.  Similarly, changing package definitions you need to
re-install those package lists prior to seeing the effects.

### Updating Frozen and Chilly Images

Reproducing Docker images in a repeatable way requires freezing the versions of important packages.  To do this our build scripts output summation requirements.yml and requirements.txt files which govern consolidated environment installs for frozen and chilly builds.   A frozen build pins every package with package==version where version is typically `x.y.z`.  A chilly build pins x.y.z requirements with ~= when requirements are of the form `x.y.z` whiuch lets the .z float to the highest patch version.   Chilly generally lets oddball formats float because ~= won't work.

#### USE_FROZEN

This framework introduces an approach for updating conda environments primarily
driven by the `USE_FROZEN` env var in setup-env.  `USE_FROZEN` defines which of
3 different sets of requirements are used for a particiular build:

1. Defining environment varaiable `USE_FROZEN=0` tells the environment install
scripts to use floating dependency specs defined in `common-env/` and each
mission's `environments/` directory.  Frozen and chilly specs are ignored.

2. Defining environment variable `USE_FROZEN=1` tells environment install scripts
to use fully pinned requirements specs defined for each mission and kernel under `env-frozen/`.
Floating dependency specs are ignored in this mode.

3. Defining environment variable `USE_FROZEN=2` tells the environment install scripts
to use ~= pinned requirements defined under `env-chilly`.

#### FREEZE_CHILL

The `FREEZE_CHILL` env vars has values of `0` and `1` and defines whether or not the `image-build`
script should invoke the scripts that update the frozen and chilly requirements automatically afer a successul floating build.  `0` does not update and should typically be the developer setting.  `1` does update requirements but has the drawback of leading to git conflicts if multiple developers are working on the same mission at the same time.

As image CI/CD matures it seems likely we will be able to automatically update and commit frozen and chilly requirements as a result of a merge and successful post-merge floating build.

### Automatically updating and selecting release requirements

As roman matures and jwst is added,  it will be increasingly common to build highly pinned environments based on requirements downloaded for specific software versions.

Consequently:

#### CAL_VERSION

The `CAL_VERSION` env variable has been added to `setup-env` and `setup-env.template` as well as the GitHub workflows as a build parameter.  It defines a specific version of CAL s/w requirements,  nominally to download from external sites like GitHub or artifactory.   It takes the values `none`, `latest`, and `x.y.z`.

To update requirements automatically as part of GitHub actions,  `CAL_VERSION`  needs to be defined in the configuration matrix for the build-test.yaml workflow for each specific version that should be built.

#### image-update

The `tools-update` script iterates over each environment defined for a mission.  If `CAL_VERSION` is `none` the environment is skipped.   If `CAL_VERSION` is `latest` or `x.y.z`,  and an environment defines an `update-requirements` script,  the `update-requirements` script is called to define/update the floating requirements.  `image-update` is called by `image-build` automatically for this and other purposes.   `update-requirements` is one of a few exceptions where a script defined under `deployments` vs. `scripts` executes outside Docker or a running notebook container.

#### update-requirements

This is a mission and/or kernel-specific script and which,  if optionally defined,  is designed to update "floating" requirements with either a precise `x.y.z` release or a more lightly pinned `latest` version.  One might also consider using a CAL release as frozen env requirements because they are,  but OTOH they generally will only define part of the environment with extra packages added by Octarine,  and with this approach the remainder of the freezing and chilling machinery works normally.
