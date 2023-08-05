# coding: utf-8
import time
import os
import re

import bottle


def safe_bottle(callback):
    '''
    from toolbelt.middleware import safe_bottle
    bottle.install(safe_bottle)
    '''
    def wrapper(*args, **kwargs):
        body = callback(*args, **kwargs)
        bottle.response.headers['Server'] = ')'
        bottle.response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        bottle.response.headers['X-Content-Type-Options'] = 'nosniff'
        bottle.response.headers['X-XSS-Protection'] = '1; mode=block'
        bottle.response.headers['Content-Language'] = 'en'
        return body
    return wrapper


def benchmark(callback):
    '''
    from toolbelt.middleware import benchmark
    bottle.install(benchmark)
    '''
    def wrapper(*args, **kwargs):
        start = time.time()
        body = callback(*args, **kwargs)
        end = time.time()
        bottle.response.headers['X-Exec-Time'] = str(end - start)
        return body
    return wrapper


def redirect_http_to_https(callback):
    '''
    from toolbelt.middleware import redirect_http_to_https
    bottle.install(redirect_http_to_https)
    '''
    def wrapper(*args, **kwargs):
        scheme = bottle.request.urlparts[0]
        if scheme == 'http':
            bottle.redirect(bottle.request.url.replace('http', 'https', 1))
        else:
            return callback(*args, **kwargs)
    return wrapper


def cors(callback):
    '''
    from toolbelt.middleware import cors
    from toolbelt.middleware import cors_options
    bottle.install(cors)
    '''
    def wrapper(*args, **kwargs):
        if bottle.request.method == 'OPTIONS':
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-XSRF-Token'
        else:
            # CORS
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-XSRF-Token'
            if callback:
                body = callback(*args, **kwargs)
                return body
    return wrapper


def parse_AcceptLanguage(acceptLanguage):
    'en-US,en;q=0.8,pt;q=0.6'
    if not acceptLanguage:
        return [('en', '1')]
    languages_with_weigths = acceptLanguage.strip().split(',')
    map(lambda s: s.strip, languages_with_weigths)
    locale_q_pairs = []
    for language in languages_with_weigths:
        try:
            if language.split(';')[0].strip() == language:
                # no q => q = 1
                locale_q_pairs.append((language.strip(), '1'))
            else:
                locale = language.split(';')[0].strip()
                q = language.split(';')[1].split('=')[1]
                locale_q_pairs.append((locale, q))
        except IndexError:
            pass
    if locale_q_pairs:
        return sorted(locale_q_pairs, key=lambda v: v[1], reverse=True)
    else:
        return [('en', '1')]


def simple_langs(acceptLanguage):
    'parse the Accept-Language header'
    langs = parse_AcceptLanguage(acceptLanguage)
    langs = [l[0][0:2] for l in langs]
    langs = filter(None, langs)
    langs = filter(str, langs)
    if langs:
        return list(set(langs))
    else:
        return ['en']


def lang(callback):
    '''
    from toolbelt.middleware import lang
    bottle.install(lang)
    '''
    def wrapper(*args, **kwargs):
        # Language headers/cookies
        language = simple_langs(bottle.request.headers.get('Accept-Language', None))[0]
        if not bottle.request.get_cookie('language', None):
            bottle.response.set_cookie('language', language)
        bottle.response.headers['Content-Language'] = language
        if callback:
            body = callback(*args, **kwargs)
            return body
    return wrapper


def https_safe_api_cors_lang_bench(callback):
    '''
    from toolbelt.middleware import https_safe_api_cors_lang_bench
    from toolbelt.middleware import cors_options
    bottle.install(https_safe_api_cors_lang_bench)
    '''
    def wrapper(*args, **kwargs):
        if bottle.request.method == 'OPTIONS':
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-XSRF-Token'
        else:
            scheme = bottle.request.urlparts[0]
            if scheme == 'http' and False:
                return bottle.redirect(bottle.request.url.replace('http', 'https', 1))
            else:
                bottle.response.headers['Server'] = ')'
                bottle.response.headers['X-Frame-Options'] = 'SAMEORIGIN'
                bottle.response.headers['X-Content-Type-Options'] = 'nosniff'
                bottle.response.headers['X-XSS-Protection'] = '1; mode=block'
                # CORS
                bottle.response.headers['Access-Control-Allow-Origin'] = '*'
                bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
                bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-XSRF-Token'
                # API
                if bottle.request.urlparts[2].startswith('/api'):
                    bottle.response.content_type = 'application/json'
                # First visit
                if not bottle.request.get_cookie('visited', None):
                    bottle.response.set_cookie('visited', 'yes')
                # Language headers/cookies
                language = simple_langs(bottle.request.headers.get('Accept-Language', None))[0]
                if not bottle.request.get_cookie('language', None):
                    bottle.response.set_cookie('language', language)
                bottle.response.headers['Content-Language'] = language
                if callback:
                    start = time.time()
                    body = callback(*args, **kwargs)
                    end = time.time()
                    bottle.response.headers['X-Exec-Time'] = str(end - start)
                    return body
    return wrapper


# Enable OPTIONS for all routes
@bottle.route('/<:re:.*>', method='OPTIONS')
def cors_options(*args, **kwargs):
    pass
