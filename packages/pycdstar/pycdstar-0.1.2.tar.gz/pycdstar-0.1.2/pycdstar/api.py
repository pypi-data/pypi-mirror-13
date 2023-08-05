"""A client for the REST API of cdstar instances."""
import logging
import json

import requests
from six import string_types

from pycdstar import resource
from pycdstar.config import Config
from pycdstar.exception import CdstarError


log = logging.getLogger(__name__)


class Cdstar(object):
    """The client.

    """
    def __init__(self, cfg=None, service_url=None, user=None, password=None):
        self.cfg = cfg or Config()
        self.service_url = service_url or self.cfg.get('service', 'url')
        user = user or self.cfg.get('service', 'user', default=None)
        password = password or self.cfg.get('service', 'password', default=None)
        self.session = requests.Session()
        if user and password:
            self.session.auth = (user, password)

    def url(self, obj):
        res = self.service_url
        if res.endswith('/'):
            res = res[:-1]
        return res + getattr(obj, 'path', obj)

    def _req(self, path, method='get', json=True, assert_status=200, **kw):
        """Make a request to the API of an cdstar instance.

        :param path: HTTP path.
        :param method: HTTP method.
        :param json: Flag signalling whether the response should be treated as JSON.
        :param assert_status: Expected HTTP response status of a successful request.
        :param kw: Additional keyword parameters will be handed through to the \
        appropriate function of the requests library.
        :return: The return value of the function of the requests library or a decoded \
        JSON object/array.
        """
        if 1:
            kw['verify'] = False

        method = getattr(self.session, method.lower())
        res = method(self.url(path), **kw)

        status_code = res.status_code
        if json:
            try:
                res = res.json()
            except ValueError:
                log.error(res.text[:1000])
                raise
        if assert_status:
            if not isinstance(assert_status, (list, tuple)):
                assert_status = [assert_status]
            if status_code not in assert_status:
                log.error(
                    'got HTTP %s, expected HTTP %s' % (status_code, assert_status))
                log.error(res.text[:1000] if hasattr(res, 'text') else res)
                raise CdstarError('Unexpected HTTP status code', res, status_code)
        return res

    def get_object(self, uid=None):
        return resource.Object(self, uid)

    # def get_collection(self, uid=None):
    #     return resource.Object(self, uid, type='collection')

    def search(self, query, limit=15, offset=0, index=None):
        params = dict(limit=limit, offset=offset)
        if index:
            assert index in ['metadata', 'fulltext']
            params['indexselection'] = index
        if isinstance(query, string_types):
            query = {"query_string": {"query": query}}
        # elif isinstance(query, ElasticQuery):
        #    query = query.dict()
        assert isinstance(query, dict)
        return resource.SearchResults(self, self._req(
            '/search/',
            method='post',
            params=params,
            headers={'content-type': 'application/json'},
            data=json.dumps(query)))

    # def landing(self):
    #     pass

    # def accesscontrol(self):
    #     pass

    # def dariah(self):
    #     pass
