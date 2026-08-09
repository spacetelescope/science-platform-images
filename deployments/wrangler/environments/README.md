For the wrangler,  the following files are "injected" as needed:

common-hints.mamba      -- extra mamba packages added to base environment by install-common script
common-hints.pip        -- extra pip packages added to base environment by install-common script
apt-packages.txt        -- extra Ubuntu apt packages installed by Dockerfile.custom
install-assets.sh       -- standard assets installation script
dockerfile-aux.sh       -- standard ad hoc shell code executed as subscript inside Dockerfile.custom
nbw-exports.sh          -- wrangler env vars for this environment
nbw-wrangler-spec.yaml  -- wrangler spec for this environment, renamed to generic name

To see what is injected,  run  "nbw --inject-spi <spec.yaml>" and look under the output
directory references/science-platform-images/deployments/wrangler/environments, basically a
copy of this directory *after* wrangler requirements injection.
