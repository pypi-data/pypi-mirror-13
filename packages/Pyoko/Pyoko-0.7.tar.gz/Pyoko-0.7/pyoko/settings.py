# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
"""
Default Settings
"""
import os

DEFAULT_BUCKET_TYPE = os.environ.get('DEFAULT_BUCKET_TYPE', 'pyoko_models')
RIAK_SERVER = os.environ.get('RIAK_SERVER', 'localhost')
RIAK_PROTOCOL = os.environ.get('RIAK_PROTOCOL', 'http')
RIAK_PORT = os.environ.get('RIAK_PORT', 8098)
