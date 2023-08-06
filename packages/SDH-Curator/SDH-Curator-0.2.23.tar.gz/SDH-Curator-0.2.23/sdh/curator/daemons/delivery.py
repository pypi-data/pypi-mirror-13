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

from concurrent.futures.thread import ThreadPoolExecutor
from sdh.curator.messaging.reply import reply
from sdh.curator.server import app
from sdh.curator.store import r

__author__ = 'Fernando Serena'

MAX_CONCURRENT_DELIVERIES = int(app.config.get('PARAMS', {}).get('max_concurrent_deliveries', 8))

log = logging.getLogger('sdh.curator.daemons.delivery')
thp = ThreadPoolExecutor(max_workers=min(8, MAX_CONCURRENT_DELIVERIES))

log.info("""Delivery daemon setup:
                    - Maximum concurrent deliveries: {}""".format(MAX_CONCURRENT_DELIVERIES))


def build_response(rid):
    from sdh.curator.actions import get_instance
    response_class = r.hget('requests:{}'.format(rid), '__response_class')
    if response_class is None:
        raise AttributeError('Cannot create a response for {}'.format(rid))
    (module_name, class_name) = tuple(response_class.split('.'))
    return get_instance(module_name, class_name, rid)


def __deliver_response(rid):
    response = None
    try:
        response = build_response(rid)
        delivery_state = response.sink.delivery
        if delivery_state == 'ready':
            messages = response.build()
            # The creation of a response object may change the corresponding request delivery state
            # (mixing, streaming, etc). The thing is that it was 'ready' before,
            # so it should be something prepared to deliver.
            message, headers = messages.next()  # Actually, this is the trigger
            reply(message, headers=headers, **response.sink.recipient)
            n_messages = 1
            deliver_weight = len(str(message))
            deliver_delta = deliver_weight
            for (message, headers) in messages:
                reply(message, headers=headers, **response.sink.recipient)
                n_messages += 1
                deliver_weight += len(str(message))
                deliver_delta += deliver_weight
                if deliver_delta > 1000:
                    deliver_delta = 0
                    log.info('Delivering response of request {} [{} kB]'.format(rid, deliver_weight / 1000.0))

            deliver_weight /= 1000.0
            log.info('{} messages delivered for request {} [{} kB]'.format(n_messages, rid, deliver_weight))

        elif delivery_state == 'accepted':
            log.error('Request {} should not be marked as deliver-ready, its state is inconsistent'.format(rid))
        else:
            log.info('Response of request {} is being delivered by other means...'.format(rid))
            r.srem('deliveries:ready', rid)
    except StopIteration:   # There was nothing prepared to deliver (Its state may have changed to
                            # 'streaming')
        r.srem('deliveries:ready', rid)
    except (EnvironmentError, AttributeError, Exception), e:
        r.srem('deliveries:ready', rid)
        traceback.print_exc()
        log.warning(e.message)
        if response is not None:
            log.error('Force remove of request {} due to a delivery error'.format(rid))
            response.sink.remove()
        else:
            log.error("Couldn't remove request {}".format(rid))


def __deliver_responses():
    import time

    registered_deliveries = r.scard('deliveries')
    deliveries_ready = r.scard('deliveries:ready')
    log.info("""Delivery daemon started:
                    - Deliveries: {}
                    - Ready: {}""".format(registered_deliveries, deliveries_ready))

    log.info('Delivery daemon started')
    futures = {}
    while True:
        ready = r.smembers('deliveries:ready')
        for rid in ready:
            if rid not in futures:
                log.info('Response delivery of request {} is ready. Preparing...'.format(rid))
                futures[rid] = thp.submit(__deliver_response, rid)

        for obsolete_rid in set.difference(set(futures.keys()), ready):
            if obsolete_rid in futures and futures[obsolete_rid].done():
                del futures[obsolete_rid]

        sent = r.smembers('deliveries:sent')
        for rid in sent:
            r.srem('deliveries:ready', rid)
            r.srem('deliveries', rid)
            try:
                response = build_response(rid)
                response.sink.remove()
                log.info('Request {} was sent and cleared'.format(rid))
            except AttributeError:
                log.warning('Request number {} was deleted by other means'.format(rid))
                pass

        r.delete('deliveries:sent')
        time.sleep(1)


__thread = Thread(target=__deliver_responses)
__thread.daemon = True
__thread.start()
