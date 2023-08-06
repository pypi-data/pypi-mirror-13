"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

import logging

import os

__author__ = 'Fernando Serena'


def _api_port():
    return int(os.environ.get('API_PORT', 5007))


def _redis_conf(def_host, def_db, def_port):
    return {'host': os.environ.get('DB_HOST', def_host),
            'db': int(os.environ.get('DB_DB', def_db)),
            'port': int(os.environ.get('DB_PORT', def_port))}


def _agora_conf(def_host, def_port):
    return {'host': os.environ.get('AGORA_HOST', def_host),
            'port': int(os.environ.get('AGORA_PORT', def_port))}


def _rabbit_conf(def_host, def_port):
    return {'host': os.environ.get('AMQP_HOST', def_host),
            'port': int(os.environ.get('AMQP_PORT', def_port))}


def _params_conf(def_on_demand_th, def_sync_time, def_frag_collectors, def_max_conc_fragments, def_max_conc_deliveries,
                 def_collect_throttling):
    return {'on_demand_threshold': float(os.environ.get('CURATOR_DEMAND_TH', def_on_demand_th)),
            'min_sync_time': int(os.environ.get('CURATOR_MIN_SYNC_TIME', def_sync_time)),
            'fragment_collectors': int(os.environ.get('N_FRAGMENT_COLLECTORS', def_frag_collectors)),
            'max_concurrent_fragments': int(os.environ.get('MAX_CONCURRENT_FRAGMENTS', def_max_conc_fragments)),
            'max_concurrent_deliveries': int(os.environ.get('MAX_CONCURRENT_DELIVERIES', def_max_conc_deliveries)),
            'collect_throttling': int(os.environ.get('COLLECT_THROTTLING', def_collect_throttling))}


def _logging_conf(def_level):
    return int(os.environ.get('LOG_LEVEL', def_level))


class Config(object):
    PORT = _api_port()
    PARAMS = _params_conf(2.0, 10, 8, 8, 4, 10)


class DevelopmentConfig(Config):
    DEBUG = True
    LOG = logging.DEBUG
    STORE = 'persist'
    REDIS = _redis_conf('localhost', 4, 6379)
    AGORA = _agora_conf('localhost', 9002)
    RABBIT = _rabbit_conf('localhost', 5672)


class TestingConfig(Config):
    DEBUG = False
    LOG = logging.DEBUG
    TESTING = True
    STORE = 'memory'
    REDIS = _redis_conf('localhost', 5, 6379)
    RABBIT = _rabbit_conf('localhost', 5672)
    AGORA = _agora_conf('localhost', 9002)


class ProductionConfig(Config):
    DEBUG = False
    LOG = _logging_conf(logging.INFO)
    STORE = 'persist'
    REDIS = _redis_conf('redis', 4, 6379)
    AGORA = _agora_conf('localhost', 9009)
    RABBIT = _rabbit_conf('rabbit', 5672)
