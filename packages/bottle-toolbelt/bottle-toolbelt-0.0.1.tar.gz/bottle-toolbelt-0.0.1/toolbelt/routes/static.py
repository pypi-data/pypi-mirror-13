# coding: utf-8
import os
import re

import bottle


STATIC_FILE_PATTERN = re.compile('.*\.(js|css|jpg|jpeg|gif|png|ico|svg|ttf|woff)$')
STATIC_DIR = os.getenv('STATIC_DIR', './dist')
STATIC_INDEX = os.getenv('STATIC_INDEX', 'index.html')


# Must be independent because CORS issue with http -> https redirection on root path
@get('/')
def index():
    return bottle.static_file(STATIC_INDEX, root=STATIC_DIR)


@error(404)
def error404(error):
    if STATIC_FILE_PATTERN.match(bottle.request.path):
        return
    # AngularJS html5mode handler
    bottle.response.status = 200
    return bottle.static_file(STATIC_INDEX, root=STATIC_DIR)


# This must be the last route
@get('/<filepath:path>')
def static(filepath=None):
    if filepath.endswith('.gz'):
        bottle.response.add_header('Content-Encoding', 'gzip')
    return bottle.static_file(filepath, root=STATIC_DIR)
