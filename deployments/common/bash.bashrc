export PS1="${debian_chroot:+($debian_chroot)}\u@notebook:\w\$ "

# Enable conda
. "/opt/conda/etc/profile.d/conda.sh"

# Activate base by default
conda activate base

#export PATH="/opt/TurboVNC/bin:$PATH"

# Utility scripts for users,  mainly python environment management
export PATH="/opt/tools:$PATH"

export LD_LIBRARY_PATH=/usr/local/lib

# make non-login shell (notebook !) use same environment, picking up default kernel
export BASH_ENV=/etc/bash.bashrc

alias ls="ls --color=auto"
