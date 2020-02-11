# Copyright 2017 Palantir Technologies, Inc.
import os
import pathlib
import sys

import pytest

from rols import uris

PY2 = sys.version_info.major == 2



DOC_URI = uris.from_fs_path(__file__)


def path_as_uri(path):
    return pathlib.Path(os.path.abspath(path)).as_uri()


def test_local(rols):
    """ Since the workspace points to the test directory """
    assert rols.workspace.is_local()


def test_put_document(rols):
    rols.workspace.put_document(DOC_URI, "content")
    assert DOC_URI in rols.workspace._docs


def test_get_document(rols):
    rols.workspace.put_document(DOC_URI, "TEXT")
    assert rols.workspace.get_document(DOC_URI).source == "TEXT"


def test_get_missing_document(tmpdir, rols):
    source = "TEXT"
    doc_path = tmpdir.join("test_document.py")
    doc_path.write(source)
    doc_uri = uris.from_fs_path(str(doc_path))
    assert rols.workspace.get_document(doc_uri).source == "TEXT"


def test_rm_document(rols):
    rols.workspace.put_document(DOC_URI, "TEXT")
    assert rols.workspace.get_document(DOC_URI).source == "TEXT"
    rols.workspace.rm_document(DOC_URI)
    assert rols.workspace.get_document(DOC_URI)._source is None


@pytest.mark.parametrize(
    "metafiles", [("setup.py",), ("pyproject.toml",), ("setup.py", "pyproject.toml")]
)
def test_non_root_project(rols, metafiles):
    repo_root = os.path.join(rols.workspace.root_path, "repo-root")
    os.mkdir(repo_root)
    project_root = os.path.join(repo_root, "project-root")
    os.mkdir(project_root)

    for metafile in metafiles:
        with open(os.path.join(project_root, metafile), "w+") as f:
            f.write("# " + metafile)

    test_uri = uris.from_fs_path(os.path.join(project_root, "hello/test.py"))
    rols.workspace.put_document(test_uri, "assert True")
    test_doc = rols.workspace.get_document(test_uri)
    assert project_root in test_doc.sys_path()


def test_root_project_with_no_setup_py(rols):
    """Default to workspace root."""
    workspace_root = rols.workspace.root_path
    test_uri = uris.from_fs_path(os.path.join(workspace_root, "hello/test.py"))
    rols.workspace.put_document(test_uri, "assert True")
    test_doc = rols.workspace.get_document(test_uri)
    assert workspace_root in test_doc.sys_path()


def test_multiple_workspaces(tmpdir, rols):
    workspace1_dir = tmpdir.mkdir("workspace1")
    workspace2_dir = tmpdir.mkdir("workspace2")
    file1 = workspace1_dir.join("file1.py")
    file2 = workspace2_dir.join("file1.py")
    file1.write("import os")
    file2.write("import sys")

    msg = {"uri": path_as_uri(str(file1)), "version": 1, "text": "import os"}

    rols.m_text_document__did_open(textDocument=msg)
    assert msg["uri"] in rols.workspace._docs

    added_workspaces = [{'uri': path_as_uri(str(x))}
                        for x in (workspace1_dir, workspace2_dir)]
    event = {'added': added_workspaces, 'removed': []}
    rols.m_workspace__did_change_workspace_folders(event)

    for workspace in added_workspaces:
        assert workspace["uri"] in rols.workspaces

    workspace1_uri = added_workspaces[0]["uri"]
    assert msg["uri"] not in rols.workspace._docs
    assert msg["uri"] in rols.workspaces[workspace1_uri]._docs

    msg = {"uri": path_as_uri(str(file2)), "version": 1, "text": "import sys"}
    rols.m_text_document__did_open(textDocument=msg)

    workspace2_uri = added_workspaces[1]["uri"]
    assert msg["uri"] in rols.workspaces[workspace2_uri]._docs

    event = {'added': [], 'removed': [added_workspaces[0]]}
    rols.m_workspace__did_change_workspace_folders(event)
    assert workspace1_uri not in rols.workspaces


def test_multiple_workspaces_wrong_removed_uri(rols, tmpdir):
    workspace = {'uri': str(tmpdir.mkdir('Test123'))}
    event = {'added': [], 'removed': [workspace]}
    rols.m_workspace__did_change_workspace_folders(event)
    assert workspace['uri'] not in rols.workspaces


def test_root_workspace_changed(rols, tmpdir):
    test_uri = str(tmpdir.mkdir('Test123'))
    rols.root_uri = test_uri
    rols.workspace._root_uri = test_uri

    workspace1 = {'uri': test_uri}
    workspace2 = {'uri': str(tmpdir.mkdir('NewTest456'))}

    event = {'added': [workspace2], 'removed': [workspace1]}
    rols.m_workspace__did_change_workspace_folders(event)

    assert workspace2['uri'] == rols.workspace._root_uri
    assert workspace2['uri'] == rols.root_uri


def test_root_workspace_not_changed(rols, tmpdir):
    # removed uri != root_uri
    test_uri_1 = str(tmpdir.mkdir('Test12'))
    rols.root_uri = test_uri_1
    rols.workspace._root_uri = test_uri_1
    workspace1 = {'uri': str(tmpdir.mkdir('Test1234'))}
    workspace2 = {'uri': str(tmpdir.mkdir('NewTest456'))}
    event = {'added': [workspace2], 'removed': [workspace1]}
    rols.m_workspace__did_change_workspace_folders(event)
    assert test_uri_1 == rols.workspace._root_uri
    assert test_uri_1 == rols.root_uri
    # empty 'added' list
    test_uri_2 = str(tmpdir.mkdir('Test123'))
    new_root_uri = workspace2['uri']
    rols.root_uri = test_uri_2
    rols.workspace._root_uri = test_uri_2
    workspace1 = {'uri': test_uri_2}
    event = {'added': [], 'removed': [workspace1]}
    rols.m_workspace__did_change_workspace_folders(event)
    assert new_root_uri == rols.workspace._root_uri
    assert new_root_uri == rols.root_uri
    # empty 'removed' list
    event = {'added': [workspace1], 'removed': []}
    rols.m_workspace__did_change_workspace_folders(event)
    assert new_root_uri == rols.workspace._root_uri
    assert new_root_uri == rols.root_uri
    # 'added' list has no 'uri'
    workspace2 = {'TESTuri': 'Test1234'}
    event = {'added': [workspace2], 'removed': [workspace1]}
    rols.m_workspace__did_change_workspace_folders(event)
    assert new_root_uri == rols.workspace._root_uri
    assert new_root_uri == rols.root_uri


def test_root_workspace_removed(tmpdir, rols):
    workspace1_dir = tmpdir.mkdir('workspace1')
    workspace2_dir = tmpdir.mkdir('workspace2')
    root_uri = rols.root_uri

    # Add workspaces to the pyls
    added_workspaces = [{'uri': path_as_uri(str(x))}
                        for x in (workspace1_dir, workspace2_dir)]
    event = {'added': added_workspaces, 'removed': []}
    rols.m_workspace__did_change_workspace_folders(event)

    # Remove the root workspace
    removed_workspaces = [{'uri': root_uri}]
    event = {'added': [], 'removed': removed_workspaces}
    rols.m_workspace__did_change_workspace_folders(event)

    # Assert that the first of the workspaces (in alphabetical order) is now
    # the root workspace
    assert rols.root_uri == path_as_uri(str(workspace1_dir))
    assert rols.workspace._root_uri == path_as_uri(str(workspace1_dir))


@pytest.mark.skipif(os.name == 'nt', reason="Fails on Windows")
def test_workspace_loads_pycodestyle_config(rols, tmpdir):
    workspace1_dir = tmpdir.mkdir('Test123')
    rols.root_uri = str(workspace1_dir)
    rols.workspace._root_uri = str(workspace1_dir)

    # Test that project settings are loaded
    workspace2_dir = tmpdir.mkdir('NewTest456')
    cfg = workspace2_dir.join("pycodestyle.cfg")
    cfg.write(
        "[pycodestyle]\n"
        "max-line-length = 1000"
    )

    workspace1 = {'uri': str(workspace1_dir)}
    workspace2 = {'uri': str(workspace2_dir)}

    event = {'added': [workspace2], 'removed': [workspace1]}
    rols.m_workspace__did_change_workspace_folders(event)

    seetings = rols.workspaces[str(workspace2_dir)]._config.settings()
    assert seetings['plugins']['pycodestyle']['maxLineLength'] == 1000

    # Test that project settings prevail over server ones.
    server_settings = {'rols': {'plugins': {'pycodestyle': {'maxLineLength': 10}}}}
    rols.m_workspace__did_change_configuration(server_settings)
    assert seetings['plugins']['pycodestyle']['maxLineLength'] == 1000

    # Test switching to another workspace with different settings
    workspace3_dir = tmpdir.mkdir('NewTest789')
    cfg1 = workspace3_dir.join("pycodestyle.cfg")
    cfg1.write(
        "[pycodestyle]\n"
        "max-line-length = 20"
    )

    workspace3 = {'uri': str(workspace3_dir)}

    event = {'added': [workspace3], 'removed': [workspace2]}
    rols.m_workspace__did_change_workspace_folders(event)

    seetings = rols.workspaces[str(workspace3_dir)]._config.settings()
    assert seetings['plugins']['pycodestyle']['maxLineLength'] == 20


def test_settings_of_added_workspace(rols, tmpdir):
    test_uri = str(tmpdir.mkdir('Test123'))
    rols.root_uri = test_uri
    rols.workspace._root_uri = test_uri

    # Set some settings for the server.
    server_settings = {'rols': {'plugins': {'jedi': {'environment': '/usr/bin/python3'}}}}
    rols.m_workspace__did_change_configuration(server_settings)

    # Create a new workspace.
    workspace1 = {'uri': str(tmpdir.mkdir('NewTest456'))}
    event = {'added': [workspace1]}
    rols.m_workspace__did_change_workspace_folders(event)

    # Assert settings are inherited from the server config.
    workspace1_object = rols.workspaces[workspace1['uri']]
    workspace1_jedi_settings = workspace1_object._config.plugin_settings('jedi')
    assert workspace1_jedi_settings == server_settings['rols']['plugins']['jedi']
