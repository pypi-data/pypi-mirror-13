from __future__ import unicode_literals

from pygments.token import Token, Keyword, Name, Comment, String, Operator, Number
from pygments.style import Style
from pygments.styles import get_style_by_name, get_all_styles
from prompt_toolkit.styles import default_style_extensions

import sys

__all__ = (
    'get_all_code_styles',
    'get_all_ui_styles',
    'generate_style',
)


def get_all_code_styles():
    """
    Return a mapping from style names to their classes.
    """
    result = dict((name, get_style_by_name(name).styles) for name in get_all_styles())
    result['win32'] = win32_code_style
    return result


def get_all_ui_styles():
    """
    Return a dict mapping {ui_style_name -> style_dict}.
    """
    return {
        'default': default_ui_style,
        'blue': blue_ui_style,
    }


def generate_style(python_style, ui_style):
    """
    Generate Pygments Style class from two dictionaries
    containing style rules.
    """
    assert isinstance(python_style, dict)
    assert isinstance(ui_style, dict)

    class PythonStyle(Style):
        styles = {}
        styles.update(default_style_extensions)
        styles.update(python_style)
        styles.update(ui_style)

    return PythonStyle


# Code style for Windows consoles. They support only 16 colors,
# so we choose a combination that displays nicely.
win32_code_style = {
    Comment:                   "#00ff00",
    Keyword:                   '#44ff44',
    Number:                    '',
    Operator:                  '',
    String:                    '#ff44ff',

    Name:                      '',
    Name.Decorator:            '#ff4444',
    Name.Class:                '#ff4444',
    Name.Function:             '#ff4444',
    Name.Builtin:              '#ff4444',

    Name.Attribute:            '',
    Name.Constant:             '',
    Name.Entity:               '',
    Name.Exception:            '',
    Name.Label:                '',
    Name.Namespace:            '',
    Name.Tag:                  '',
    Name.Variable:             '',
}


default_ui_style = {
        # (Python) Prompt: "In [1]:"
        Token.In:                                     'bold #008800',
        Token.In.Number:                              '',

        # Return value.
        Token.Out:                                    '#ff0000',
        Token.Out.Number:                             '#ff0000',

        # Separator between windows. (Used above docstring.)
        Token.Separator:                              '#bbbbbb',

        # Search toolbar.
        Token.Toolbar.Search:                         '#22aaaa noinherit',
        Token.Toolbar.Search.Text:                    'noinherit',
        Token.Toolbar.Search.Text.NoMatch:            'bg:#aa4444 #ffffff',

        # System toolbar
        Token.Toolbar.System.Prefix:                  '#22aaaa noinherit',

        # "arg" toolbar.
        Token.Toolbar.Arg:                            '#22aaaa noinherit',
        Token.Toolbar.Arg.Text:                       'noinherit',

        # Signature toolbar.
        Token.Toolbar.Signature:                      'bg:#44bbbb #000000',
        Token.Toolbar.Signature.CurrentName:          'bg:#008888 #ffffff bold',
        Token.Toolbar.Signature.Operator:             '#000000 bold',

        Token.Docstring:                              '#888888',

        # Validation toolbar.
        Token.Toolbar.Validation:                     'bg:#440000 #aaaaaa',

        # Status toolbar.
        Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',
        Token.Toolbar.Status.InputMode:               'bg:#222222 #ffffaa',
        Token.Toolbar.Status.Off:                     'bg:#222222 #888888',
        Token.Toolbar.Status.On:                      'bg:#222222 #ffffff',
        Token.Toolbar.Status.PythonVersion:           'bg:#222222 #ffffff bold',

        # When Control-C has been pressed. Grayed.
        Token.Aborted:                                '#888888',

        # The options sidebar.
        Token.Sidebar:                                'bg:#bbbbbb #000000',
        Token.Sidebar.Title:                          'bg:#668866 #ffffff underline',
        Token.Sidebar.Label:                          'bg:#bbbbbb #222222',
        Token.Sidebar.Status:                         'bg:#dddddd #000011',
        Token.Sidebar.Selected.Label:                 'bg:#222222 #eeeeee',
        Token.Sidebar.Selected.Status:                'bg:#444444 #ffffff bold',

        Token.Sidebar.Separator:                      'bg:#bbbbbb #ffffff underline',
        Token.Sidebar.Key:                            'bg:#bbddbb #000000 bold',
        Token.Sidebar.Key.Description:                'bg:#bbbbbb #000000',
        Token.Sidebar.HelpText:                       'bg:#bbeebb #000000',

        # Exit confirmation.
        Token.ExitConfirmation:                       'bg:#884444 #ffffff',
}


# Some changes to get a bit more contrast on Windows consoles.
# (They only support 16 colors.)
if sys.platform == 'win32':
    default_ui_style.update({
        Token.Sidebar.Title:                          'bg:#00ff00 #ffffff',
        Token.ExitConfirmation:                       'bg:#ff4444 #ffffff',
        Token.Toolbar.Validation:                     'bg:#ff4444 #ffffff',
    })


blue_ui_style = {}
blue_ui_style.update(default_ui_style)
blue_ui_style.update({
        # Line numbers.
        Token.LineNumber:                             '#aa6666',

        # Highlighting of search matches in document.
        Token.SearchMatch:                            '#ffffff bg:#4444aa',
        Token.SearchMatch.Current:                    '#ffffff bg:#44aa44',

        # Highlighting of select text in document.
        Token.SelectedText:                           '#ffffff bg:#6666aa',

        # Completer toolbar.
        Token.Toolbar.Completions:                    'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Arrow:              'bg:#44bbbb #000000 bold',
        Token.Toolbar.Completions.Completion:         'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Completion.Current: 'bg:#008888 #ffffff',

        # Completer menu.
        Token.Menu.Completions.Completion:            'bg:#44bbbb #000000',
        Token.Menu.Completions.Completion.Current:    'bg:#008888 #ffffff',
        Token.Menu.Completions.Meta:                  'bg:#449999 #000000',
        Token.Menu.Completions.Meta.Current:          'bg:#00aaaa #000000',
        Token.Menu.Completions.ProgressBar:           'bg:#aaaaaa',
        Token.Menu.Completions.ProgressButton:        'bg:#000000',
})
