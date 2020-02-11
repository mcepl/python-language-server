# Copyright 2017 Palantir Technologies, Inc.
# pylint: disable=redefined-builtin, unused-argument
from rols import hookspec


@hookspec
def rols_code_actions(config, workspace, document, range, context):
    pass


@hookspec
def rols_code_lens(config, workspace, document):
    pass


@hookspec
def rols_commands(config, workspace):
    """The list of command strings supported by the server.

    Returns:
        List[str]: The supported commands.
    """


@hookspec
def rols_completions(config, workspace, document, position):
    pass


@hookspec
def rols_definitions(config, workspace, document, position):
    pass


@hookspec
def rols_dispatchers(config, workspace):
    pass


@hookspec
def rols_document_did_open(config, workspace, document):
    pass


@hookspec
def rols_document_did_save(config, workspace, document):
    pass


@hookspec
def rols_document_highlight(config, workspace, document, position):
    pass


@hookspec
def rols_document_symbols(config, workspace, document):
    pass


@hookspec(firstresult=True)
def rols_execute_command(config, workspace, command, arguments):
    pass


@hookspec
def rols_experimental_capabilities(config, workspace):
    pass


@hookspec(firstresult=True)
def rols_folding_range(config, workspace, document):
    pass


@hookspec(firstresult=True)
def rols_format_document(config, workspace, document):
    pass


@hookspec(firstresult=True)
def rols_format_range(config, workspace, document, range):
    pass


@hookspec(firstresult=True)
def rols_hover(config, workspace, document, position):
    pass


@hookspec
def rols_initialize(config, workspace):
    pass


@hookspec
def rols_initialized():
    pass


@hookspec
def rols_lint(config, workspace, document, is_saved):
    pass


@hookspec
def rols_references(config, workspace, document, position, exclude_declaration):
    pass


@hookspec(firstresult=True)
def rols_rename(config, workspace, document, position, new_name):
    pass


@hookspec
def rols_settings(config):
    pass


@hookspec(firstresult=True)
def rols_signature_help(config, workspace, document, position):
    pass
