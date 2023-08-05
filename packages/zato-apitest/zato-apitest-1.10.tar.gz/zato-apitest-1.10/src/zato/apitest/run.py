# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Originally part of Zato - open-source ESB, SOA, REST, APIs and cloud integrations in Python
# https://zato.io

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Behave
from behave.configuration import Configuration
from behave.runner import Runner

# ConfigObj
from configobj import ConfigObj

def handle(path, args=None):
    file_conf = ConfigObj(os.path.join(path, 'features', 'config.ini'))
    try:
        behave_options = file_conf['behave']['options']
    except KeyError:
        raise ValueError("Behave config not found."
            " Are you running with the right path?")
    if args:
        behave_options += ' ' + ' '.join(args)

    conf = Configuration(behave_options)
    conf.paths = [os.path.join(path, 'features')]
    runner = Runner(conf)
    runner.run()
