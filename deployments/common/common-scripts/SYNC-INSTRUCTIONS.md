# About this reference directory

This directory contains a pre-installed reference copy of a notebook or
software git repository.  git is a system which is used to track and manage
different versions of a set of files and directories.

## Intended usage

The directory is intended to be used for classes, platform testing of
pre-installed s/w, and to act as reference code and not for general purpose
development.

Nominal uses:

- As class materials with notebooks which can be executed directly, in place.
- As test materials for the pre-installed s/w of the platform itself.
- As refence materials containing the latest copy of a repo.
- Untracked files or directories will be ignored unless added by the repo itself.

Discouraged uses, all bets are off:

- Normal git development adding, copying, renaming, deleting, or modifying files
- Commiting changes
- Switching branches or remotes
- Changing file or directory permissions

# Non-standard git behavior

To support and guide these uses the directory (git clone) has the following
non-standard behavior:

## '-ref' directory name suffix and/or 'references' parent directory

The name of the directory ends with a '-ref' suffix designating its intended
limited purpose.  Likewise, if it is located under a 'references' parent
directory it is being declared as "for reference use only".

If you really do wish to do development for the associated repo and utilize git
fully, this naming convention makes it possible to do normal git clones with
standard directory names, owned by you, which will be ignored by the sync process.

## Readonly Files

Files stored in the clone are set to readonly file permissions.  This prevents
you from accidentally changing a notebook and saving it back to its original
location.  Instead, save it in a different directory, or with a different name.
Unless a similar file or directory is added by the source repository, your copy
of a file using a different name or location will not be touched.

## Read/Write Directories

All of the directories in the clone are set to read/write/execute for you.
This enables notebooks to be opened simply and executed in their original
locations.  As the notebook executes, JupyterLab saves related information in a
checkpoint file located in the same directory.  If you do change permissions of
a clone directory to something else, your changes will be lost during the next
sync.

## Automatic Updates

This reference directory is sync'ed with its source repository each time you
log in so that you automatically receive the latest materials the authors have
committed to the source repository. If however you modify any files or
directories in place, upon sync your changes will be backed up and the original
file locations reverted and updated normally.  Likewise, if you save a file to
a new name, and the source repository coincidentally adds the same file name
later with different contents, during the sync your version of the file will be
backed up to a different name.  To the extent possible, after every sync the
file contents of this directory will be an exact copy of files in the source
repository and your changes and additions will be stored in backups and/or
other untracked file names.

## But I never Read This... / Do No Harm

If you forged ahead without reading and changed file permissions to read/write
and made changes and a sync happened, while the original or repo-updated file
will be restored, your modified copy will also be backed up with an
increasing number as a suffix:

<original_name>.12345678...

where 12345678... will be a number which monotonically increases each time you log
in.  Your modified copy is renamed but not altered by any automatic merge with
changes to the repo.

## Opting out / I got this,  nix all these updates,  it's not for me

To stop the automtic sync process from performing wasted updates and/or
recreating reference copies you want deleted, just create a file:

```
touch $HOME/.git-sync-off
```

The existence of the file will not remove existing reference directories, but
neither will they be updated or restored if you delete them yourself.
