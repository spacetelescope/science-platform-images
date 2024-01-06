REPO_URL = "https://github.com/jaytmiller/sync-test"

# doctest is not a good format for entering these shell commands even with multi-line shell()
# adding here cuts down on test file complexity
CLEANUP_SCRIPT = """
set -ux

# this is to handle "poison" directories and files which unfortunately get created fairly often
# and hence we construct test cases for them.  w/o this test cleanup below doesn't work.
chmod -R 777 references
rm -rf references
rm -f ~/.git-sync-off
rm -f gs*.log
"""

INIT_SCRIPT = CLEANUP_SCRIPT + f"""
set -ux
git clone  {REPO_URL}  references/sync-test-ref
cd references/sync-test-ref
git checkout initial-clone

# User adds untracked file to clone dir.
echo "Made up user file." >made-up-file.ipynb

# User modifies tracked file.
echo "Add some stuff to modify" >>README.md

# User changes file mode
chmod 000 change-mode.md
chmod +w change-mode.md

# User adds untracked subdir, subsubdir, and corresponding files.
# Here new-dir will be backed up and restored as a single DirPath object
# so when we restore it, it will be a single directory including nested
# files:
mkdir -p new-dir/sub-dir
echo "Made up user file 1." >new-dir/made-up-1.txt
echo "Made up user file 2." >new-dir/sub-dir/made-up-2.txt

# User deletes file
rm -f LICENSE

# User copies file
cp copy-me.txt copy-me-2.txt

# User adds file to be committed
echo "Added file" >added.txt
git add added.txt

# User renames file
git mv rename-me.txt renamed-me.txt

# User writes untracked file to tracked dir
echo "This is a user owned file" >rw_to_poison.dir/user_file.txt

# User changes tracked dir to poison
chmod 000 rw_to_poison.dir

# User changes tracked file mode
chmod 666 ro_to_rw.txt

# User adds file with toxic permissions;  what happens when we try to sync?
echo "Poison!" >poison-file.txt
chmod 000 poison-file.txt

# User adds nested poison directories, toxic and non-toxic files
mkdir -p poison-dir/poison-dir-2
echo "Poison!" >poison-dir/poison-file.txt
echo "CoolAid!" >poison-dir/poison-dir-2/poison-file-2.txt
chmod 000 poison-dir/poison-dir-2/poison-file-2.txt
chmod 000 poison-dir/poison-file.txt
chmod 000 poison-dir/poison-dir-2
chmod 000 poison-dir

# The update should collide with these blocker file / dirs
echo "This user file didn't exist in the repo when added." > blocker-file
mkdir blocker-dir
echo "Placeholder required for git to care about blocker-dir but does not directly conflict" > blocker-dir/placeholder-2.txt
"""

if __name__ == "__main__":
    from git_sync_v4 import shell
    shell(INIT_SCRIPT)
