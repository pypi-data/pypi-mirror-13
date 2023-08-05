# coding: utf-8
import time
import os
import re

from bottle import request, response, install, get, post, request, response, static_file, error
import requests

'''
from toolbelt.routes.social import *
API_URL=http://localhost:8000
'''

# Called by Satellizer lib + Provider servers
def social_login_callback(provider):
    api_url = os.environ['API_URL']
    code = request.json['code']
    redirect_uri = request.json['redirectUri']
    frontend_link = request.json.get('confirmEmailUrl', '')
    link_user_id = request.json.get('link_user_id', None)
    data = {'code': code, 'redirect_uri': redirect_uri, 'frontend_link': frontend_link, 'link_user_id': link_user_id}
    r = requests.post(api_url + '/auth/{}'.format(provider), data=data)
    if r.status_code == 200 or r.status_code == 201:
        response.status = r.status_code
        return r.json()
    return r.text


@post('/auth/github')
def github_callback():
    return social_login_callback('github')


@post('/auth/google')
def google_callback():
    return social_login_callback('google')


@post('/auth/twitter')
def twitter_callback():
    return social_login_callback('twitter')


@post('/auth/linkedin')
def linkedin_callback():
    return social_login_callback('linkedin')


@post('/auth/facebook')
def facebook_callback():
    return social_login_callback('facebook')


@post('/auth/stackexchange')
def stackexchange_callback():
    return social_login_callback('stackexchange')


@post('/auth/hackhands')
def hackhands_callback():
    return social_login_callback('hackhands')

