# Copyright 2017 Palantir Technologies, Inc.
from rols import lsp, uris
from rols.plugins.highlight import rols_document_highlight
from rols.workspace import Document

DOC_URI = uris.from_fs_path(__file__)
DOC = """a = "hello"
a.startswith("b")
"""


def test_highlight(workspace):
    # Over 'a' in a.startswith
    cursor_pos = {"line": 1, "character": 0}

    doc = Document(DOC_URI, workspace, DOC)
    assert rols_document_highlight(doc, cursor_pos) == [{
        'range': {
            'start': {'line': 0, 'character': 0},
            'end': {'line': 0, 'character': 1},
        },
        {
            "range": {
                "start": {"line": 1, "character": 0},
                "end": {"line": 1, "character": 1},
            },
            # The second usage is Read
            "kind": lsp.DocumentHighlightKind.Read,
        },
    ]


SYS_DOC = """import sys
print sys.path
"""


def test_sys_highlight(workspace):
    cursor_pos = {'line': 0, 'character': 8}

    doc = Document(DOC_URI, workspace, SYS_DOC)
    assert rols_document_highlight(doc, cursor_pos) == [{
        'range': {
            'start': {'line': 0, 'character': 7},
            'end': {'line': 0, 'character': 10}
        },
        {
            "range": {
                "start": {"line": 1, "character": 6},
                "end": {"line": 1, "character": 9},
            },
            "kind": lsp.DocumentHighlightKind.Read,
        },
    ]
