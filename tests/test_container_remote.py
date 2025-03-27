import pytest

from pytest_container.container import ContainerData

from .images import BUSYBOX


@pytest.mark.parametrize("container", [BUSYBOX], indirect=True)
def test_container_connection_check_output(container: ContainerData) -> None:
    """
    Test that `check_output` works as expected.
    """
    assert container.connection.check_output("uname") == "Linux"


@pytest.mark.parametrize("container", [BUSYBOX], indirect=True)
def test_container_connection_run(container: ContainerData) -> None:
    """
    Test that `run` works as expected.
    """
    rc, stdout, stderr = container.connection.run("uname")
    assert rc == 0
    assert stdout.strip() == "Linux"
    assert stderr == ""


@pytest.mark.parametrize("container", [BUSYBOX], indirect=True)
def test_container_connection_check_exists(container: ContainerData) -> None:
    """
    Test that `check_output` works as expected.
    """
    assert container.connection.exists("ls")
    assert not container.connection.exists("buildah")


@pytest.mark.parametrize("container", [BUSYBOX], indirect=True)
def test_container_connection_file(container: ContainerData) -> None:
    """
    Test that `file` works as expected.
    """

    # Directory
    d = container.connection.file("/usr/share/licenses/busybox")
    assert d.exists
    assert d.is_directory
    assert not d.is_file
    assert d.listdir() == ["LICENSE"]
    with pytest.raises(
        ValueError, match="/usr/share/licenses/busybox is a directory"
    ):
        d.content_string

    # File
    f = container.connection.file("/usr/share/licenses/busybox/LICENSE")
    assert f.exists
    assert f.is_file
    assert not f.is_directory
    assert f.content_string.startswith(
        """\
--- A note on GPL versions

BusyBox is distributed under version 2 of the General Public License (included
in its entirety, below).  Version 2 is the only version of this license which
this version of BusyBox (or modified versions derived from this one) may be
distributed under.
"""
    )
    # Missing file
    assert not container.connection.file(
        "/usr/share/licenses/busybox/MISSING"
    ).exists


@pytest.mark.parametrize("container", [BUSYBOX], indirect=True)
def test_container_remote_copy(container: ContainerData) -> None:
    """
    Test that `copy` works as expected.
    """
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        expected_content = f.read()

    f = container.connection.copy("pyproject.toml", "/tmp/pyproject.toml")
    assert f.path == "/tmp/pyproject.toml"
    assert f.exists
    assert f.is_file
    assert f.content_string == expected_content
