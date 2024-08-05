# Release process for Roman DMS or similar builds

## Setting up

If for example we are setting up an image release where:

   1. The new CAL s/w version is 0.13.0
   2. The DMS build is B12
   3. Our overall JupyterHub infrastructure version is 1.3.0

do the following:

```bash
scripts/image-configure roman --use-frozen=floating --freeze=1 --cal-version=0.13.0
source setup-env
```

This will prepare your environment for the "requirements capture" phase of the
build which is driven by (a) specifying an explicit --cal-version and (b) doing
a floating build (--use-frozen=floating) and saving the resulting frozen requirements
(--freeze=1).

NOTE: the CAL s/w version amd DMS build number are only coincidentally similar as
seen here,  generally they increase in lockstep but are otherwise unrelated.


## Update version files

Edit deployments/roman/MISSION_VERSION  and set it to roman-12.0.0  (for Roman B12)
Edit deployments/common/VERSION  and set it to 1.3.0  (for JupyterHub generic 1.3.0)

## Update floating kernel requirements (optional)

Despite being called "floating" the requirments for formal Roman builds are currently very
strict,  exact conda and pip requirements are downloaded from Artifactory and placed in the
roman-cal environment directory where they pretend they're vague.

To see this you can type:

```bash
image-update
git status
```

and if all goes well image-update will do whatever is needed to update the Roman environment(s) requirements.

Note that you must be on VPN for this to work since formal requirements files
are fetched from an internal Artifactory.  This process of fetching
requirements from Artifactory is piggy-backing on how the CAL s/w group and DMS
pipelines formally deliver requirements to the pipelines; if the process fails
then contact SCSB or the DMS pipeline groups to see if everything is ready,
something has changed, etc.

This step is only optional in the sense that the image-build script called below will
automatically run image-update.  W/o this step,  the official kernel requirements for
the release are not available to build.

## Build and freeze the floating kernel requirements

To build the image,  type:

```bash
image-build
```

At present this will also automatically run image-update to update the kernel requirements
as described previously.  Because we set --freeze=1 when we configured,  af the
build completes the requirements for the conda environments will be dumped out into the
deployments/roman/env-frozen directory tree.

## Test the floating image

Run the built-in tests to verify the build is working.  Iterate building and testing
as needed:

```bash
image-test
```

Actual test definitions are stored in the deployments/roman/environments/roman-cal/tests directories,  typically as a file `imports` which lists Python modules and packages to attempt to import as a check they were compiled correctly.  See the framework documentation for more information about how tests are defined and run.

## Save all the updated files

Use git to save the `MISSION_VERSION`, `VERSION`, and `deployments/roman` files for archiving
and later use in the final "frozen" build.

If changes were needed to get a working build,  also save those,  e.g.  changes to
common package lists and/or framework scripts and/or tests.

## Rebuild the image from frozen requirements

Now that frozen requirements have been saved the way our framework understands them (and
potentially adding packages which don't conflict with the CAL release),  we reconfigure
to do a frozen build using the requirements we just saved:

```bash
scripts/image-configure roman --use-frozen=frozen --freeze=1 --cal-version=none
source setup-env
image-build
image-test
```

Running in this mode,  the build will be repeated using requirements frozen by the
framework.   Specifying `--cal-version=none` means that the `image-update` will not access Artifactory or touch the "floating" requirements which were already downloaded and saved.

Specifying `--cal-version=latest` instead would switch back to development versions of
roman-cal as the "floating" requirements.  Continuing to specify `--freeze=1` will cause the framework to dump the as-built versions of the frozen build,  and while not intended to update the frozen requirements,  it can potentially show any drift between what was frozen and what was built.

## PR, merge, and tag on GitHub

If the frozen build looks good,  push the changes to GitHub and create a PR.  Verify that the image builds and tests on GitHub using the output of the configured Actions.
If tests are reporting problems,  try to fix them and/or update the PR as needed.

Once the PR has been reviewed and merge tag the repo something like:

```bash
roman-12.0.0
```

and

```bash
1.3.0
```

The first tag documents the *DMS build number* while the second tag documents the
*multi-repo state of infrastructure and common scripts* at the time of the release.
The calibration s/w version is saved in the file `CAL_VERSION` in the `deployments/roman/environments/roman-cal` directory.

## Delivering to AWS ECR

Once the source code tags have been pushed to GitHub, we can switch over to the
`aws-mult-science-platform/jupyterhub-deploy` repo and deploy it there for testing
on the platform and tagging for ECR.

Further instructions for AWS science platform image delivery are documented
under jupyterhub-deploy/doc. That process will basically involve getting a build of the image into ECR, either by pushing this locally built image or by rebuilding it
altogether using a pipeline,  then formally tagging it in ECR roman-12.0.0.
