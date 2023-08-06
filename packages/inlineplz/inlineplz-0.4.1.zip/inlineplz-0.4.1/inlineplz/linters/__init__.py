# -*- coding: utf-8 -*-
# pylint: disable=W0703

"""Linter configurations."""

from __future__ import absolute_import
from __future__ import print_function

import os
import subprocess
import traceback

from inlineplz import parsers
from inlineplz import message

LINTERS = {
    'prospector': {
        'install': ['pip', 'install', 'prospector'],
        'run': ['prospector', '--zero-exit', '-o', 'json'],
        'dotfiles': ['.prospector.yaml'],
        'parser': parsers.ProspectorParser
    },
    'eslint': {
        'install': ['npm', 'install'],
        'run': [os.path.normpath('./node_modules/.bin/eslint'), '.', '-f', 'json'],
        'dotfiles': [
            '.eslintrc.yml',
            '.eslintignore',
            '.eslintrc',
            'eslintrc.yml'
        ],
        'parser': parsers.ESLintParser
    },
    'jshint': {
        'install': ['npm', 'install'],
        'run': [os.path.normpath('./node_modules/.bin/jshint'), '.', '--reporter', 'checkstyle'],
        'dotfiles': ['.jshintrc'],
        'parser': parsers.JSHintParser
    },
    'jscs': {
        'install': ['npm', 'install'],
        'run': [os.path.normpath('./node_modules/.bin/jscs'), '.', '-r', 'json', '-m', '-1', '-v'],
        'dotfiles': ['.jscsrc', '.jscs.json'],
        'parser': parsers.JSCSParser
    }
}


def lint(install=False):
    messages = message.Messages()
    for linter, config in LINTERS.items():
        if any(dotfile in os.listdir(os.getcwd())
               for dotfile in config.get('dotfiles')):
            try:
                if install and config.get('install'):
                    subprocess.check_call(config.get('install'))
                print(config.get('run'))
                output = subprocess.check_output(config.get('run')).decode('utf-8')
            except subprocess.CalledProcessError as err:
                traceback.print_exc()
                output = err.output
            except Exception:
                traceback.print_exc()
                print(output)
            try:
                if output.strip():
                    linter_messages = config.get('parser')().parse(output)
                    # prepend linter name to message content
                    linter_messages = {
                        (msg[0], msg[1], '{0}: {1}'.format(linter, msg[2])) for msg in linter_messages
                    }
                    messages.add_messages(linter_messages)
            except Exception:
                traceback.print_exc()
                print(output)
    return messages.get_messages()
