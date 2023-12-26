import pytest

INIT_SCRIPT = """
set -eux

chmod -R 777 test-clone || true
rm -rf test-clone
git clone  https://github.com/spacetelescope/nersc-refresh-announcements  test-clone
cd test-clone
echo "Made up user file." >made-up-file.ipynb
echo "Add some stuff to modify" >>README.md
chmod 600 CHANGELOG.md
chmod 700 node_modules
mkdir -p new-dir/sub-dir
echo "Made up user file." >new-dir/made-up-2.txt
echo "Made up user file." >new-dir/sub-dir/made-up-3.txt
rm -f LICENSE
echo "Poison!" >poison-file.txt
chmod 000 poison-file.txt
mkdir -p poison-dir poison-dir-2
echo "Poison!" >poison-dir/poison-file-2.txt
chmod 644 poison-dir/poison-file-2.txt
chmod 000 poison-dir poison-dir-2
"""
