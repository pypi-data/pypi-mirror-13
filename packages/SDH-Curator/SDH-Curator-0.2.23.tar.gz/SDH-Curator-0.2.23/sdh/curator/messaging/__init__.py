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
import traceback
from threading import Thread

import pika
from pika.exceptions import ConnectionClosed
from sdh.curator.actions import execute
from sdh.curator.server import app

__author__ = 'Fernando Serena'

log = logging.getLogger('sdh.curator.messaging')
RABBIT_CONFIG = app.config['RABBIT']


def callback(ch, method, properties, body):
    action_args = method.routing_key.split('.')[2:]
    log.info('--> Incoming {} request!'.format(action_args[0]))
    try:
        execute(*action_args, data=body)
    except (EnvironmentError, AttributeError, ValueError) as e:
        # traceback.print_exc()
        log.error(e.message)
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        log.debug('Sent REJECT')
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        log.debug('Sent ACK')


def __setup_queues():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBIT_CONFIG['host']))
    except ConnectionClosed:
        log.error('AMQP broker is not available')
    else:
        channel = connection.channel()
        log.info('Connected to the AMQP broker: {}'.format(RABBIT_CONFIG))

        channel.exchange_declare(exchange='sdh',
                                 type='topic', durable=True)

        # Create the requests queue and binding
        queue_name = 'curator_requests'
        channel.queue_declare(queue_name, durable=True)
        channel.queue_bind(exchange='sdh', queue=queue_name, routing_key='curator.request.*.#')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue=queue_name)

        log.info('Ready to accept requests')
        channel.start_consuming()


th = Thread(target=__setup_queues)
th.daemon = True
th.start()
