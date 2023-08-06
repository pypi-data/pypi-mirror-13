import json
import warnings

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    python_version = 3
except:
    from urllib2 import Request, urlopen
    from urllib import urlencode
    python_version = 2

BASE_URL = "https://www.kimonolabs.com"

class Kimono(object):
    def __init__(self, api_id, kimmodify=False, api_key=None, api_token=None):
        self.api_id = api_id
        self.api_key = api_key
        self.api_token = api_token
        self.kimmodify = kimmodify

    def get_api_url(self, query_params={}):
        if self.kimmodify:
            query_params['kimmodify'] = 1
        if self.api_key:
            query_params['apikey'] = self.api_key
        return "{base_url}/api/{api_id}/?{params}".format(base_url=BASE_URL,
                                                          api_id=self.api_id,
                                                          params=urlencode(query_params))

    def get_kimonoapi_url(self, endpoint, query_params={}):
        return "{base_url}/kimonoapis/{api_id}/{endpoint}/?{params}".format(base_url=BASE_URL,
                                                                           api_id=self.api_id,
                                                                           endpoint=endpoint,
                                                                           params=urlencode(query_params))

    def request(self, url, data=None):
        req = Request(url)
        if data is not None:
            data = json.dumps(data)
            req.add_header('Content-Type', 'application/json')
        res = urlopen(req, data=data)
        results = json.loads(res.read().decode('utf-8')) 
        return results

    @property
    def api_url(self):
        warnings.warn("This function is deprecated.")
        return self.get_api_url()

    def fetch(self):
        return self.request(self.get_api_url())

    @property
    def data(self):
        return self.fetch()

    def start_crawl(self):
        data = {'apikey': self.api_key}
        return self.request(self.get_kimonoapi_url('startcrawl'), data)

    def update(self, **kwargs):
        data = {'apikey': self.api_key}
        data.update(kwargs)
        return self.request(self.get_kimonoapi_url('update'), data)
