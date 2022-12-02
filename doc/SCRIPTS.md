# In the `tools` directory, there are a series of convenience scripts.

#### Dependencies

In theory they're automatically installed on all new CI-nodes, but if not you
need to install Python dependencies before executing some of these scripts.

```
pip install --cert /etc/ssl/certs/ca-bundle.crt -r requirements.txt
```

#### Image management scripts

Scripts have been added to the *tools* directory to simplify image development:

- image-build   -- build the Docker image defined by setup-env
- image-base    -- build base images with SSL certs + jupyter docker-stack / scipy-notebook
- image-update  -- as part of building, generate any required Dockerfiles, obtain current SSL certs, etc.

Automated testing:

- image-test    -- run automatic image tests on build image
- image-configure  -- generate setup-env for CI based on simple inputs

Run a JH image in local Docker for inspection, development, debug:

- image-sh          -- start a container running an interactive bash shell for poking around
- image-exec        -- start a container and run an arbitrary command
- image-dev         -- start a container and map in Docker sources r/w for incremental install debug
- run-lab           -- start a JH server in Docker using the current image
- image-graph-env   -- use pipdeptree and graphviz to produce version dependency graphs for an environment
- image-build-all   -- build all missions/deployments to update frozen requirements and test framework, memory intensive (32G?)

Capture conda environment s/w versions (automatic w/ image-build):

- image-freeze     -- dump out frozen environment specs from the current image into deployments tree.
- image-envs       -- run the image to list the names of conda environments
- image-env-export -- run the image to export the specified conda environment s/w versions

Sourcing *setup-env* should add these scripts to your path, they generally require no parameters.

Using the scripts is simple, basically some iterative flow of:

```
# Build the Docker image
image-build

# Run any self-tests defined for this deployment under deployments/<your-deployment>.
# Fix problems and re-build until working
image-test
```

#### CI Source Code Scanning Scripts

As part of CI we run source code scanners which check both our own Python code
and the Python dependencies in the mission images.  These scripts are
independent of the functional CI tests and do note require building an image
prior to running.

```
# One stop dev shopping,  run all source code scans on the current sources
sscan

# Run Python's bandit package on any discoverable Python code
sscan-bandit

# Run Python's flake8 code quality scanner
sscan-flake8
```
