#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import configparser, logging

from . import exceptions

log = logging.getLogger(__name__)

def config2dict(config):
    dictionary = dict(config)
    for k,v in dictionary.items():
        dictionary.update({k: dict(v)})
    return dictionary

def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    return config

def read_dict_from_config(path, ignore_missing=False):
    try:
        config = read_config(path)

        return config2dict(config)
    except Exception as e:
        log.exception(e)
        if ignore_missing:
            return {}
        else:
            raise

def read_category_from_config(path, category, base = 'general'):
    config = read_dict_from_config(path)

    if category not in config:
        raise InvalidConfigCategoryException(category)

    general_section = config[base] if base in config else {}
    category_section = config[category]

    general_section.update(category_section)

    return { k.upper(): v for k,v in general_section.items() }

def prepare_dictionary_for_translation(config):
    for k,v in config.items():
        if not k.startswith('<'):
            config.pop(k)
            config['<%s>' % k] = v

    return config

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
