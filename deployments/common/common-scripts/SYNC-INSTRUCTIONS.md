# About this reference directory

The reference directory contains a pre-installed copy of a notebook or 
software repository. We use git to track and manage various versions 
of files and directories.

## Intended usage of reference directories

This directory is intended for use in training sessions, and as a general
reference. It is not for general-purpose development.

Nominal uses:

- As training materials, with notebooks that can be run in place.
- As reference materials containing the latest copy of a repository.
- On occasion, as test materials to vet the performance of the platform.

Discouraged uses:

- Performing typical git development tasks such as adding, copying, renaming, deleting, or modifying files.
- Committing changes.
- Switching branches or remotes.
- Changing file or directory permissions.

## Non-standard git behavior

To support and guide these uses the cloned directory has the following properties:

### Readonly Files

Files stored in the reference directory have read-only permissions. This prevents
users from accidentally modifying a notebook and saving changes to its original location. 
To edit an existing notebook, save it in a different directory, or with a different name.

### Read/Write Directories

All directories in the reference repository are set to read/write/execute
permissions. This allows notebooks to be opened and executed in their original
locations. As the notebook executes, JupyterLab saves related information in a 
checkpoint file located within the same directory.

Any changes to reference directory permissions will be lost upon your next login.

### Automatic Updates

The reference directory is synced with its source repository each time you log in,
ensuring you automatically receive the latest materials committed by the authors.  
Any changes you make to existing files or directories within the reference 
repository are saved upon sync. Thus, after each sync the contents of the directory
is an exact copy of the source repository, plus your changes stored as untracked files.

## But I never Read This... / Do No Harm

If you proceed without reading the instructions and change file permissions
to read/write, make changes, and a sync occurs, the original or 
repository-updated file will be restored. Your modified copy will also be
backed up with an incrementing number as a suffix:

<original_file_name>.12345678...

where 12345678... is be a number that increases each time you log
in. Your modified copy is renamed but not altered by any automatic merge with
changes from the repository.

## Turn off auto-sync!

To prevent the automatic sync process from performing unnecessary updates
 or recreating reference copies that you intend to delete, simply create a file:

```
touch $HOME/.git-sync-off
```

The existence of this file will not remove existing reference directories;
however, they will not be updated or restored if you delete them.
