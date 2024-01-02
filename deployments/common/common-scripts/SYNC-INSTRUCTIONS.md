# About this directory and default file installations

This directory is a pre-installed git clone of URL from branch BRANCH.

It is intended to be used as a read-only copy of the repository which is updated
each time you log in with the latest changes from class instructors and other
notebook authors.  To that end each of the files is set to read-only to prevent
you from accidentally changing it, but the directories themselves are read/write.
By avoiding changes to the files,  automatic updates work smoothly and without
conflict.

## ENCOURAGED

DO: Open notebooks and step along (often during a class) without copying the notebook
    to another directory first.  Since JupyterLab automatically saves checkpoints in
    a notebook's directory, directories are kept writable to enable this.

DO: If you modify a notebook,  to save your changes there are two easy options:

    1. Use save-as to save it in a different directory either outside
    this clone,  or in a directory within this clone named something like 'my-changes'.

    2. Use save-as to save to a new filename such as 'my-<original-notebook>.ipynb.

DO: If automatic updates are not to your liking,  that's fine, read up
    on opting out farther below.

## DISCOURAGED

If you choose to keep git-sync enabled,  then don't:

DO NOT: make a file read/write,  then save it in its original location.
    the next time you log in,  at best,  the file will be moved aside to
    a dated copy and the  original filename will be replaced by an updated
    readonly copy.  at worst your changes may be lost.

DO NOT: change mode on a directory to remove all execute/search permissions,
    there's a strong possibility it will be deleted with no warning, but
    at a minimum your changes will be lost at your next login.

## OTHER INFO

### Where'd my old files go?

When the repo update script runs,  if you already have a clone of the repository
and it has not already be archived, the current copy will be moved to the
hidden directory:

   ${HOME}/.git-sync-archive-3

Afterwards a fresh copy of the repository will be made which by default will be
updated and should be used in accordance with these instructions,  files will
be readonly but directories and files under .git will be read/write.

### Opting out of automatic repo updates

If you wish to opt out of repo updates completely once the initial clones are
made,  you can do so as follows from a JupyterLab terminal window:

   echo "AUTO_UPDATE=off" >> $HOME/.git-sync-config

With this setting,  the repo becomes yours completely unless the AUTO_UPDATE
option is changed.   Once yours,  you are free to change modes of the files
and directories and use it as you would any git clone. Typing these commands
in a terminal window should revert the clone to its original git behavior:

    cd $HOME/<clone-directory-name>
    find . -type d -exec chmod 755 {} + \;   # directories are read/write/execute for you
    find . -type f -exec chmod 644 {} + \;   # files are read/write for you
    git reset HEAD
    git checkout -- .

Note that using a terminal window is strongly recommended since JupyterLab's
!-command does not retain shell environment state across commands.

Obviously if there's any trouble with the above you can just delete the clone
and make a new one the normal git way.

If you wish to resume the original automatic syncing behavior you can simply
remove 'AUTO_SYNC=off' from $HOME/.git-sync-config.

If you wish to automatically sync without having to re-login,  you can run
the following command in a terminal:

    /opt/environments/post-start-hook
