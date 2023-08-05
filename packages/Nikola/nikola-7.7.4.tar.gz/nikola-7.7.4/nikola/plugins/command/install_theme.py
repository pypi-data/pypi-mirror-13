# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Install a theme."""

from __future__ import print_function
import os
import io
import time
import requests

import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

from nikola.plugin_categories import Command
from nikola import utils

LOGGER = utils.get_logger('install_theme', utils.STDERR_HANDLER)


class CommandInstallTheme(Command):
    """Install a theme."""

    name = "install_theme"
    doc_usage = "[[-u] theme_name] | [[-u] -l]"
    doc_purpose = "install theme into current site"
    output_dir = 'themes'
    cmd_options = [
        {
            'name': 'list',
            'short': 'l',
            'long': 'list',
            'type': bool,
            'default': False,
            'help': 'Show list of available themes.'
        },
        {
            'name': 'url',
            'short': 'u',
            'long': 'url',
            'type': str,
            'help': "URL for the theme repository (default: "
                    "https://themes.getnikola.com/v7/themes.json)",
            'default': 'https://themes.getnikola.com/v7/themes.json'
        },
        {
            'name': 'getpath',
            'short': 'g',
            'long': 'get-path',
            'type': bool,
            'default': False,
            'help': "Print the path for installed theme",
        },
    ]

    def _execute(self, options, args):
        """Install theme into current site."""
        listing = options['list']
        url = options['url']
        if args:
            name = args[0]
        else:
            name = None

        if options['getpath'] and name:
            path = utils.get_theme_path(name)
            if path:
                print(path)
            else:
                print('not installed')
            return 0

        if name is None and not listing:
            LOGGER.error("This command needs either a theme name or the -l option.")
            return False
        try:
            data = requests.get(url).json()
        except requests.exceptions.SSLError:
            LOGGER.warning("SSL error, using http instead of https (press ^C to abort)")
            time.sleep(1)
            url = url.replace('https', 'http', 1)
            data = requests.get(url).json()
        if listing:
            print("Themes:")
            print("-------")
            for theme in sorted(data.keys()):
                print(theme)
            return True
        else:
            # `name` may be modified by the while loop.
            origname = name
            installstatus = self.do_install(name, data)
            # See if the theme's parent is available. If not, install it
            while True:
                parent_name = utils.get_parent_theme_name(name)
                if parent_name is None:
                    break
                try:
                    utils.get_theme_path(parent_name)
                    break
                except:  # Not available
                    self.do_install(parent_name, data)
                    name = parent_name
            if installstatus:
                LOGGER.notice('Remember to set THEME="{0}" in conf.py to use this theme.'.format(origname))

    def do_install(self, name, data):
        """Download and install a theme."""
        if name in data:
            utils.makedirs(self.output_dir)
            url = data[name]
            LOGGER.info("Downloading '{0}'".format(url))
            try:
                zip_data = requests.get(url).content
            except requests.exceptions.SSLError:
                LOGGER.warning("SSL error, using http instead of https (press ^C to abort)")
                time.sleep(1)
                url = url.replace('https', 'http', 1)
                zip_data = requests.get(url).content

            zip_file = io.BytesIO()
            zip_file.write(zip_data)
            LOGGER.info("Extracting '{0}' into themes/".format(name))
            utils.extract_all(zip_file)
            dest_path = os.path.join(self.output_dir, name)
        else:
            dest_path = os.path.join(self.output_dir, name)
            try:
                theme_path = utils.get_theme_path(name)
                LOGGER.error("Theme '{0}' is already installed in {1}".format(name, theme_path))
            except Exception:
                LOGGER.error("Can't find theme {0}".format(name))

            return False

        confpypath = os.path.join(dest_path, 'conf.py.sample')
        if os.path.exists(confpypath):
            LOGGER.notice('This theme has a sample config file.  Integrate it with yours in order to make this theme work!')
            print('Contents of the conf.py.sample file:\n')
            with io.open(confpypath, 'r', encoding='utf-8') as fh:
                if self.site.colorful:
                    print(utils.indent(pygments.highlight(
                        fh.read(), PythonLexer(), TerminalFormatter()),
                        4 * ' '))
                else:
                    print(utils.indent(fh.read(), 4 * ' '))
        return True
