import importlib.machinery
import importlib.util
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "common-scripts" / "git-sync-v4"
loader = importlib.machinery.SourceFileLoader("git_sync_v4_exact_refs", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
gs = importlib.util.module_from_spec(spec)
loader.exec_module(gs)


def git(cwd, *args):
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def make_remote(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "--initial-branch", "main")
    git(source, "config", "user.name", "Git Sync Test")
    git(source, "config", "user.email", "git-sync@example.invalid")

    tracked = source / "tracked.txt"
    tracked.write_text("first\n")
    git(source, "add", "tracked.txt")
    git(source, "commit", "-m", "First")
    first = git(source, "rev-parse", "HEAD")
    git(source, "tag", "release-1")

    tracked.write_text("second\n")
    git(source, "commit", "-am", "Second")
    second = git(source, "rev-parse", "HEAD")

    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "clone", "--bare", str(source), str(remote)],
        check=True,
        capture_output=True,
        text=True,
    )
    return remote, first, second


def sync(remote, checkout, ref, tmp_path):
    gs.log = gs.Log(str(tmp_path / f"{ref}.log"))
    gs.Syncer(str(remote), str(checkout), ref, str(SCRIPT)).sync()
    return git(checkout, "rev-parse", "HEAD")


def test_branch_tag_and_sha_resolve_to_exact_commits(tmp_path):
    remote, first, second = make_remote(tmp_path)

    checkout = tmp_path / "checkout"
    assert sync(remote, checkout, "main", tmp_path) == second
    assert sync(remote, checkout, "release-1", tmp_path) == first

    sha_checkout = tmp_path / "sha-checkout"
    assert sync(remote, sha_checkout, first, tmp_path) == first
