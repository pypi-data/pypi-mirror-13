#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import re, logging, os, shutil

from . import files

log = logging.getLogger(__name__)

def translate_string(string, dictionary, prefix = '<', suffix = '>'):
    matcher = re.compile(r'%s([A-Z0-9_]+)%s' % (prefix, suffix))
    for match in matcher.findall(string):
        replacement = dictionary.get(match, '')
        log.debug('replacing %s with %s', match, replacement)
        string = string.replace('%s%s%s' % (prefix, match, suffix), replacement)
    return string

def translate_file(path, dictionary):
    lines = files.readlines(path)

    with open(path, 'wb') as f:
        for line in lines:
            line = translate_string(line, dictionary)
            f.write(line.encode())

def translate_directory(path, dictionary):
    for root, ds, fs in os.walk(path):
        # :(((( TODO: more directories deep than one will fail
        for d in ds:
            absolute_path = os.path.join(root, d)
            translated_filename = translate_string(d, dictionary)
            if translated_filename != d:
                new_absolute_path = os.path.join(root, translated_filename)
                shutil.move(absolute_path, new_absolute_path)
                ds.remove(d)
                ds.append(translated_filename)
                ds[:] = ds

        for f in fs:
            absolute_path = os.path.join(root, f)
            translate_file(absolute_path, dictionary)
            translated_filename = translate_string(f, dictionary)
            if translated_filename != f:
                new_absolute_path = os.path.join(root, translated_filename)
                shutil.move(absolute_path, new_absolute_path)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
