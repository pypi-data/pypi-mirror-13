#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import configparser

from . import exceptions

def make_dict_from_config(path, category):
    """TODO: Docstring for make_dict_from_config.

    :path: TODO
    :returns: TODO

    """
    config = configparser.ConfigParser()
    config.read(path)

    if 'general' not in config:
        raise exceptions.InvalidConfigCategoryException('general')

    dictionary = dict(config['general'])

    if category != 'general':
        if category not in config:
            raise exceptions.InvalidConfigCategoryException(category)

        dictionary.update(dict(config[category]))

    return { k.upper(): v for k,v in dictionary.items() }

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
