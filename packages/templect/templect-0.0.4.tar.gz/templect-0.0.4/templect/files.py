#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import os, shutil, re, glob, logging

log = logging.getLogger(__name__)

def remove_directory(path, force=True):
    shutil.rmtree(path, ignore_errors=force)

def target_path(base, path, relative_to):
    return os.path.join(base, path.replace(relative_to, '').lstrip('/'))

def copy_files(source, destination, files, force=False):
    for f in files:
        src_f = os.path.join(source, f)
        dst_f = os.path.join(destination, f)
        if os.path.exists(dst_f):
            if not force:
                raise Exception('%s exists, use -f to force overwriting')
            else:
                log.debug('removing file %s', dst_f)
                os.remove(dst_f)

        log.debug('copying file %s to %s', src_f, dst_f)
        shutil.copy(src_f, dst_f,)

def create_directories(destination, directories):
    for d in directories:
        dst_d = os.path.join(destination, d)

        log.debug('creating directory %s', dst_d)
        os.makedirs(dst_d, exist_ok=True)

def copy_directory(src, dst, recursive=True, force=False, filter_glob=None):
    if src is None:
        return

    log.debug('copying directory %s to %s', src, dst)

    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        dst_root = target_path(dst, root, src)

        if filter_glob is not None:
            files[:] = [ f for f in files if not glob.fnmatch.fnmatch(f, filter_glob) ]
            dirs[:]  = [ d for d in dirs if not glob.fnmatch.fnmatch(d, filter_glob) ]

        copy_files(root, dst_root, files, force)
        create_directories(dst_root, dirs)

def readlines(path):
    with open(path, 'rb') as f:
        content = f.read().decode()
        lines = content.split(os.linesep)

    lines[:] = [ l + os.linesep for l in lines ]
    lines[-1] = lines[-1].rstrip(os.linesep)
    return lines

def rename_file(source, destination_dir, rename_function):
    absolute_path = os.path.join(source)
    translated_filename = translation.translate_string(f, self.dictionary)

    if translated_filename != f:
        new_absolute_path = os.path.join(root, translated_filename)
        shutil.move(absolute_path, new_absolute_path)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
