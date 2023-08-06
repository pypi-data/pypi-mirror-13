import re
import functools
import requests


def _assemble_url(host, version):
    def wrapper_outer(func):
        @functools.wraps(func)
        def wrapper_inner(*args, **kwargs):
            url = func(*args, **kwargs)
            return '{host}/{version}{url}'.format(host=host, version=version, url=url)

        return wrapper_inner

    return wrapper_outer


def _assemble_request(decode_response):
    def wrapper_outer(func):
        @functools.wraps(func)
        def wrapper_inner(*args, **kwargs):
            response = getattr(requests, func.func_name)(*args, **kwargs)
            return decode_response(response)

        return wrapper_inner

    return wrapper_outer


def _request_url(url, path_param, param=None):
    if not param:
        param = {}

    if not path_param:
        path_param = {}

    pattern = re.compile(r'\{\w*\}')
    new_url = url
    for group in pattern.findall(url):
        key = group[1:-1]
        if key not in path_param:
            raise ValueError('path parameter %s not found'%key)

        new_url = new_url.replace('{%s}'%key, str(path_param[key]))

    return new_url


def generate_url(host, version):
    return _assemble_url(host, version)(_request_url)


def generate_request(decode_response, funclist):
    return [_assemble_request(decode_response)(i) for i in funclist]


if __name__ == '__main__':
    host, version, url, cid = 'http://localhost', 'v1', '/wallpaper/{cid}/wallpaper', 1000
    def get():pass
    get, = generate_request(lambda x: 0, [get])
    assert generate_url(host, version)(url, {'cid': cid}) == '{host}/{version}{url}'.format(host=host, version=version, url=url.format(cid=cid))
    assert get('http://baidu.com') == 0
