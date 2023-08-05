#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import os, logging, re, uuid, shutil

from . import exceptions, files, configs, translation

class Template:
    def __init__(self, template_dir, template_name):
        self.log = logging.getLogger('%s-%s' % (__name__, template_name))

        self.template_name = template_name
        self.template_dir = template_dir
        self.root = os.path.join(template_dir, template_name)

        if not os.path.isdir(self.root):
            raise Exception('no such template %s' % self.root)

        self.parent = self.get_parent()

    def get_parent(self):
        config = configs.read_dict_from_config(os.path.join(self.root, '.templect'), ignore_missing=True)
        parent_config = config.get('Parent')

        if parent_config:
            if not 'name' in parent_config:
                raise Exception('no name found in parent config: %s' % parent_config)

            parent_name = parent_config.get('name')

            self.log.info('reading parent template: %s', parent_name)

            return Template(parent_config.get('directory', self.template_dir), parent_name)

    def copy_to(self, path, force, dictionary):
        temporary_path = '/tmp/' + str(uuid.uuid1())

        try:
            if self.parent:
                self.parent.copy_to(temporary_path, force, dictionary)

            files.copy_directory(self.root, temporary_path, force=True, filter_glob = '.templect')

            translation.translate_directory(temporary_path, dictionary)

            files.copy_directory(temporary_path, path, force=force)
        finally:
            shutil.rmtree(temporary_path)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
