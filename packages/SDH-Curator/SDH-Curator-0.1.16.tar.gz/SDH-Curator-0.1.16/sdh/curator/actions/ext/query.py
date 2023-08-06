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
import calendar
import json
import logging
from datetime import datetime

from sdh.curator.actions.core.fragment import FragmentRequest, FragmentAction, FragmentResponse, FragmentSink
from sdh.curator.actions.core.utils import chunks
from sdh.curator.daemons.fragment import FragmentPlugin

__author__ = 'Fernando Serena'

log = logging.getLogger('sdh.curator.actions.query')


class QueryPlugin(FragmentPlugin):
    @property
    def sink_class(self):
        return QuerySink

    def consume(self, fid, (c, s, p, o), graph, *args):
        pass

    def complete(self, fid, *args):
        pass


FragmentPlugin.register(QueryPlugin)


class QueryRequest(FragmentRequest):
    def __init__(self):
        super(QueryRequest, self).__init__()

    def _extract_content(self):
        super(QueryRequest, self)._extract_content()

        q_res = self._graph.query("""SELECT ?node WHERE {
                                        ?node a curator:QueryRequest .
                                    }""")

        q_res = list(q_res)
        if len(q_res) != 1:
            raise SyntaxError('Invalid query request')

        request_fields = q_res.pop()
        if not all(request_fields):
            raise ValueError('Missing fields for query request')
        if request_fields[0] != self._request_node:
            raise SyntaxError('Request node does not match')


class QueryAction(FragmentAction):
    def __init__(self, message):
        self.__request = QueryRequest()
        self.__sink = QuerySink()
        super(QueryAction, self).__init__(message)

    @property
    def sink(self):
        return self.__sink

    @classmethod
    def response_class(cls):
        return QueryResponse

    @property
    def request(self):
        return self.__request

    def submit(self):
        try:
            super(QueryAction, self).submit()
        except Exception as e:
            log.debug('Bad request: {}'.format(e.message))
            self._reply_failure(e.message)


class QuerySink(FragmentSink):
    def _remove(self, pipe):
        super(QuerySink, self)._remove(pipe)

    def __init__(self):
        super(QuerySink, self).__init__()

    def _save(self, action):
        super(QuerySink, self)._save(action)
        if self.backed:
            log.debug('Request {} is already backed'.format(action.request_id))
            self.delivery = 'ready'

    def _load(self):
        super(QuerySink, self)._load()


class QueryResponse(FragmentResponse):
    def __init__(self, rid):
        self.__sink = QuerySink()
        self.__sink.load(rid)
        super(QueryResponse, self).__init__(rid)

    @property
    def sink(self):
        return self.__sink

    def _build(self):
        fragment, _ = self.fragment(result_set=True)
        log.debug('Building a query result for request number {}'.format(self._request_id))

        try:
            variables = filter(lambda x: not x.startswith('_'), map(lambda v: v.lstrip('?'),
                                                                    filter(lambda x: x.startswith('?'),
                                                                           self.sink.preferred_labels)))

            for ch in chunks(fragment, 100):
                result_rows = []
                for t in ch:
                    if any(t):
                        result_row = {v: t[v] for v in variables}
                        result_rows.append(result_row)
                if result_rows:
                    yield json.dumps(result_rows), {'state': 'streaming', 'source': 'store',
                                                    'response_to': self.sink.message_id,
                                                    'submitted_on': calendar.timegm(datetime.now().timetuple()),
                                                    'submitted_by': self.sink.submitted_by}
        except Exception, e:
            log.error(e.message)
            raise
        finally:
            yield '', {'state': 'end'}
