import urllib.request
from urllib.request import Request, urlopen
from urllib.error import URLError


class MyClient:
    def __init__(self, ipaddress, port, clientname='noname'):
        self.ipaddress = ipaddress
        self.port = port
        self.clientname = clientname

    def _create_request(self, params, page):
        url = 'http://{}:{}'.format(self.ipaddress, self.port)
        if len(page) > 0:
            url = url + page
        req = Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        return req

    def send(self, params, page=''):
        req = self._create_request(params, page)
        body = None
        try:
            with urlopen(req, timeout=10) as res:
                body = res.read()
        except URLError as e:
            print('\tMyClient Err: {}'.format(self.clientname))
            if hasattr(e, 'reason'):
                print('\tWe failed to reach a server')
                print('\tReason: ', e.reason)
            elif hasattr(e, 'code'):
                print('\tThe server couldn\'t fulfill the request.')
                print('\tError code: ', e.code)
        return body


if __name__ == '__main__':
    client = MyClient('192.168.24.61', '54333')
    params = {'PH':'430.0'}
    body = client.send(params, page='')
    #with open('test.jpeg', 'wb') as f:
    #    f.write(body)
