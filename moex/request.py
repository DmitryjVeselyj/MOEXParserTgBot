import requests  # TODO async
from .base import MoexObject


class Request(MoexObject):
    def _request_wrapper(self, *args, **kwargs):
        try:
            resp = requests.request(*args, **kwargs)
        except Exception as e:  # TODO good exceptions handling
            raise e

        if 200 <= resp.status_code <= 299:
            return resp

    def get(self, url, params):
        return self._request_wrapper('GET', url, params=params)
