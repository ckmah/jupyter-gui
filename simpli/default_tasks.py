"""
Defines default tasks, which are generally useful.
"""

from os import listdir, remove, symlink
from os.path import islink, join, split

from IPython.core.display import display_html

from .support import establish_filepath, get_home_dir

# Make a hidden directory in the user-home directory
HOME_DIR = get_home_dir()
SIMPLI_DIR = join(HOME_DIR, '.simpli')
SIMPLI_JSON_DIR = join(SIMPLI_DIR, 'json/')
establish_filepath(SIMPLI_JSON_DIR)


def just_return(value):
    """
    Just return.
    :param value:
    :return: obj
    """

    return value


# ==============================================================================
# JSON
# ==============================================================================
def link_json(filepath):
    """
    Soft link JSON filepath to $HOME/.simpli/json/ directory.
    :param filepath: str; JSON filepath
    :return: None
    """

    destination = join(SIMPLI_JSON_DIR, split(filepath)[1])
    if islink(destination):
        remove(destination)
    symlink(filepath, destination)


def reset_jsons():
    """
    Delete all files except default_tasks.json in $HOME/.simpli/json/ directory.
    :return: None
    """

    for f in listdir(SIMPLI_JSON_DIR):
        if f != 'default_tasks.json':
            remove(join(SIMPLI_JSON_DIR, f))


# ==============================================================================
# HTML
# ==============================================================================
def set_notebook_theme(filepath):
    """
    Set notebooks theme.
    :param filepath: str; .css
    :return: None
    """

    html = """<style> {} </style>""".format(open(filepath, 'r').read())
    display_raw_html(html)


def display_raw_html(html, hide_input_cell=True):
    """
    Execute raw HTML.
    :param html: str; HTML
    :param hide_input_cell: bool;
    :return: None
    """

    if hide_input_cell:
        html += """<script> $('div .input').hide()"""
    display_html(html, raw=True)
