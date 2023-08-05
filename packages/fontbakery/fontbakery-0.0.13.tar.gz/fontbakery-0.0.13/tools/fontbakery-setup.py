#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
from __future__ import print_function

import os
import yaml

from fontaine.font import FontFactory
from fontaine.cmap import Library

from bakery_cli.utils import UpstreamDirectory


class Widgets(object):

    def __init__(self, app):
        self.app = app
        self.commit = urwid.Edit(edit_text=app.commit)
        self.ttfautohint = urwid.Edit(edit_text=app.ttfautohint)
        self.newfamily = urwid.Edit(edit_text=app.newfamily)
        self.pyftsubset = urwid.Edit(edit_text=app.pyftsubset)
        self.notes = urwid.Edit(edit_text=app.notes)
        self.afdko_parameters = urwid.Edit(edit_text=app.afdko)

        self.compiler = []
        self.licenses = []
        self.process_files = []
        self.subset = []

    def on_checkbox_state_change(self, widget, state, user_data):
        self.app.config[user_data['name']] = state

    def on_subset_state_change(self, widget, state, user_data):
        if 'subset' not in self.app.config:
            self.app.config['subset'] = []
        try:
            index = self.app.config['subset'].index(user_data['name'])
            if user_data['name'] == 'devanagari':
                self.ttfautohint.edit_text = self.ttfautohint.edit_text.replace('-f deva', '')
                self.ttfautohint.edit_text = self.ttfautohint.edit_text.replace('-D deva', '')
                self.ttfautohint.edit_text = self.ttfautohint.edit_text.strip()
                self.ttfautohint.edit_text = self.ttfautohint.edit_text.replace('  ', ' ')
            del self.app.config['subset'][index]
        except ValueError:
            if user_data['name'] == 'devanagari':
                self.ttfautohint.edit_text += ' -f deva -D deva'
            self.app.config['subset'].append(user_data['name'])

    def create_checkbox(self, title, name, state=False):
        return urwid.CheckBox(title, user_data={'name': name}, state=state,
                              on_state_change=self.on_checkbox_state_change)

    def create_process_file(self, filepath):
        try:
            state = [x.lstrip('./') for x in self.app.process_files].index(filepath) >= 0
        except ValueError:
            state = False

        widget = urwid.CheckBox(filepath, state=state)
        self.process_files.append(widget)
        return widget


class App(object):

    commit = 'HEAD'
    process_files = []
    subset = []
    compiler = 'fontforge'
    ttfautohint = '-l 7 -r 28 -G 50 -x 13 -w "G"'
    afdko = ''
    downstream = True
    optimize = True
    license = ''
    pyftsubset = '--notdef-outline --name-IDs=* --hinting'
    notes = ''
    newfamily = ''
    fontcrunch = False
    config = {}
    configfile = 'bakery.yaml'

    def __init__(self, directory):

        os.chdir(directory)

        if os.path.exists('bakery.yaml'):
            self.configfile = 'bakery.yaml'
            self.config = yaml.load(open('bakery.yaml'))
        elif os.path.exists('bakery.yml'):
            self.config = yaml.load(open('bakery.yml'))
            self.configfile = 'bakery.yml'

        self.commit = self.config.get('commit', 'HEAD')
        self.process_files = self.config.get('process_files', [])
        self.subset = self.config.get('subset', [])
        self.compiler = self.config.get('compiler', 'fontforge')
        self.ttfautohint = self.config.get('ttfautohint', '-l 7 -r 28 -G 50 -x 13 -w "G"')
        self.afdko = self.config.get('afdko', '')

        self.license = self.config.get('license', '')
        self.pyftsubset = self.config.get('pyftsubset',
                                     '--notdef-outline --name-IDs=* --hinting')
        self.notes = self.config.get('notes', '')
        self.newfamily = self.config.get('newfamily', '')

        self.widgets = Widgets(self)

    def save(self, *args, **kwargs):
        if os.path.exists(self.configfile):
            print('{} exists...'.format(self.configfile))

            self.configfile = '{}.new'.format(self.configfile)
            while os.path.exists(self.configfile):
                self.configfile = '{}.new'.format(self.configfile)

        self.config['commit'] = self.widgets.commit.get_edit_text()
        if not self.config['commit']:
            del self.config['commit']

        self.config['ttfautohint'] = self.widgets.ttfautohint.get_edit_text()
        self.config['newfamily'] = self.widgets.newfamily.get_edit_text()
        if not self.config['newfamily']:
            del self.config['newfamily']

        self.config['pyftsubset'] = self.widgets.pyftsubset.get_edit_text()

        self.config['process_files'] = [w.get_label()
                                        for w in self.widgets.process_files
                                        if w.get_state()]

        self.config['compiler'] = ', '.join([w.get_label()
                                             for w in self.widgets.compiler
                                             if w.get_state()])

        self.config['license'] = ', '.join([w.get_label().replace(' (exists)', '')
                                            for w in self.widgets.licenses
                                            if w.get_state()])

        self.config['notes'] = self.widgets.notes.get_edit_text()
        if not self.config['notes']:
            del self.config['notes']

        self.config['afdko'] = self.widgets.afdko_parameters.get_edit_text()
        if not self.config['afdko']:
            del self.config['afdko']

        yaml.safe_dump(self.config, open(self.configfile, 'w'))
        print('Wrote {}'.format(self.configfile))
        raise urwid.ExitMainLoop()


import argparse


parser = argparse.ArgumentParser()
parser.add_argument('directory')


args = parser.parse_args()


directory = UpstreamDirectory(args.directory)
process_files = [x for x in directory.ALL_FONTS if not x.lower().endswith('.sfd')]

import urwid.curses_display
import urwid.raw_display
import urwid.web_display
import urwid


def show_or_exit(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()

header = urwid.Text("Fontbakery Setup. Q exits.")


app = App(args.directory)


widgets = []
if os.path.exists('.git/config'):
    githead = urwid.Text(u"Build a specific git commit, or HEAD? ")
    widgets.append(urwid.AttrMap(githead, 'key'))
    widgets.append(urwid.LineBox(app.widgets.commit))
    widgets.append(urwid.Divider())


widgets.append(urwid.AttrMap(urwid.Text('Which files to process?'), 'key'))
for f in process_files:
    widgets.append(app.widgets.create_process_file(f))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('License filename?'), 'key'))

for f in ['OFL.txt', 'LICENSE.txt', 'LICENSE']:
    if os.path.exists(f):
        widgets.append(urwid.RadioButton(app.widgets.licenses, f + ' (exists)',
                    state=bool(f == app.license)))
    else:
        widgets.append(urwid.RadioButton(app.widgets.licenses, f,
                    state=bool(f == app.license)))


widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('ttfautohint command line parameters?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.ttfautohint))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text(('New font family name (ie, replacing repo'
                ' codename with RFN)?')), 'key'))

widgets.append(urwid.LineBox(app.widgets.newfamily))


widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(app.widgets.create_checkbox('Use FontCrunch?', 'fontcrunch', app.fontcrunch), 'key'))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(app.widgets.create_checkbox('Run tests?', 'downstream', app.downstream), 'key'))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(app.widgets.create_checkbox('Run optimize?', 'optimize', app.optimize), 'key'))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('pyftsubset defaults parameters?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.pyftsubset))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('Which compiler to use?'), 'key'))

widgets.append(urwid.Divider())
quote = ('By default, bakery uses fontforge to build fonts from ufo.'
         ' But some projects use automake, or their own build system'
         ' and perhaps the AFDKO.')
widgets.append(urwid.Padding(urwid.Text(quote), left=4))
widgets.append(urwid.Divider())

choices = ['fontforge', 'afdko', 'make', 'build.py']
for choice in choices:
    widgets.append(urwid.RadioButton(app.widgets.compiler, choice,
        state=bool(choice == app.compiler)))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('afdko default command line parameters?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.afdko_parameters))

widgets.append(urwid.Divider())
widgets.append(urwid.AttrMap(
    urwid.Text('Notes to display on Summary page?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.notes))

widgets.append(urwid.Button(u'Save and Exit', on_press=app.save))

header = urwid.AttrWrap(header, 'header')
lw = urwid.SimpleListWalker(widgets)

listbox = urwid.ListBox(lw)
listbox = urwid.AttrWrap(listbox, 'listbox')
top = urwid.Frame(listbox, header)

palette = [('header', 'black', 'dark cyan', 'standout'),
           ('key', 'white', 'dark blue', 'bold'),
           ('listbox', 'light gray', 'black')]
loop = urwid.MainLoop(top, palette, unhandled_input=show_or_exit)
loop.run()
