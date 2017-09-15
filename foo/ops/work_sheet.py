#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 7x24hs.com
# thomas@7x24hs.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import tornado.web
import logging
import time
import sys
import os
import uuid
import smtplib
import hashlib
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
from bson import json_util
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import *
from tornado.httputil import url_concat
from bson import json_util
import qcloud_video

from comm import *
from global_const import *


class OpsIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        ops = self.get_ops_info()
        self.render('ops/index.html',
                ops=ops)


class ProfileEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        self.render('ops/profile-edit.html',
                ops=ops,
                access_token=access_token,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        nickname = self.get_argument("nickname", "")
        avatar = self.get_argument("avatar", "")
        logging.info("try update myinfo nickname:[%r] avatar:[%r]", nickname, avatar)

        url = API_DOMAIN+"/api/myinfo"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode({"nickname":nickname, "avatar":avatar})
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)

        self.redirect("/ops/profile/edit")


class OperatorsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        logging.info("ops>>>> %r",ops)

        self.render('ops/operators.html',
                ops=ops,
                club_id=ops['club_id'],
                access_token=access_token,
                api_domain=API_DOMAIN)


class TodoListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()

        self.render('ops/todo-list.html',
                ops=ops,
                club_id=ops['club_id'],
                api_domain=API_DOMAIN)


class ArticlesCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        self.render('article/create.html',
                ops=ops,
                club_id=ops['club_id'],
                access_token=access_token,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)


class ArticlesDraftHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        params = {"filter":"club", "club_id":ops['club_id'], "status":"draft", "type":0}
        url = url_concat(API_DOMAIN+"/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        articles = data['rs']

        self.render('article/draft.html',
                ops=ops,
                access_token=access_token,
                club_id=ops['club_id'],
                articles=articles,
                api_domain=API_DOMAIN)


class ArticlesPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()

        params = {"filter":"club", "club_id":ops['club_id'], "status":"publish"}
        url = url_concat(API_DOMAIN+"/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        articles = data['rs']

        # activity['beginTime'] = timestamp_datetime(long(activity['beginTime'] / 1000))

        for article in articles:
            article['publish_time'] = timestamp_datetime(long(article['publish_time']))

        self.render('article/publish.html',
                ops=ops,
                club_id=ops['club_id'],
                articles=articles,
                api_domain=API_DOMAIN)


class ArticlesEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        article_id = self.get_argument("id", "")
        logging.info("get article_id=[%r] from argument", article_id)

        url = API_DOMAIN+"/api/articles/"+article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        article = data['rs']

        ops = self.get_ops_info()

        self.render('article/edit.html',
                ops=ops,
                club_id=ops['club_id'],
                access_token=access_token,
                article=article,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)


class VendorEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        
        url = API_DOMAIN+"/api/clubs/"+ops['club_id']
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        club = data['rs']
        if not club.has_key('img'):
            club['img'] = ''
        if not club.has_key('paragraphs'):
            club['paragraphs'] = ''

        self.render('ops/ops-edit.html',
                ops=ops,
                club_id=ops['club_id'],
                club=club,
                access_token=access_token,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)

# 地理位置
class VendorPositionHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        params = {"filter":"detail"}
        url = url_concat(API_DOMAIN+"/api/clubs/"+ops['club_id'],params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        club = data['rs']
        geo_x = club['gcj02']['x']
        geo_y = club['gcj02']['y']

        self.render('ops/ops-position.html',
                ops=ops,
                club_id=ops['club_id'],
                club=club,
                access_token=access_token,
                api_domain=API_DOMAIN,
                geo_x=geo_x,
                geo_y=geo_y)


# 客流量
class VendorPassengerFlowHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        params = {"filter":"detail"}
        url = url_concat(API_DOMAIN+"/api/clubs/"+ops['club_id'],params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        club = data['rs']

        self.render('ops/passenger-flow.html',
                ops=ops,
                club_id=ops['club_id'],
                club=club,
                access_token=access_token,
                api_domain=API_DOMAIN)


# 停车场信息
class VendorParkingHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        params = {"filter":"detail"}
        url = url_concat(API_DOMAIN+"/api/clubs/"+ops['club_id'],params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        club = data['rs']
        geo_x = club['gcj02']['x']
        geo_y = club['gcj02']['y']

        self.render('ops/ops-parking.html',
                ops=ops,
                club_id=ops['club_id'],
                club=club,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN)


class MomentsAllHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()

        # multimedia
        params = {"filter":"club", "club_id":ops['club_id'], "idx":0, "limit":20}
        url = url_concat(API_DOMAIN+"/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        multimedias = data['rs']

        self.render('moment/all.html',
                ops=ops,
                club_id=ops['club_id'],
                multimedias=multimedias,
                api_domain=API_DOMAIN)


class MomentsImagesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()

        self.render('moment/images.html',
                ops=ops,
                club_id=ops['club_id'],
                api_domain=API_DOMAIN)


class MomentsUploadImagesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()

        self.render('moment/upload-image.html',
                ops=ops,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET,
                access_token=access_token,
                club_id=ops['club_id'])


class MomentsVideosHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()

        # multimedia
        params = {"filter":"club", "club_id":ops['club_id'], "idx":0, "limit":20}
        url = url_concat(API_DOMAIN+"/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        multimedias = data['rs']

        for multimedia in multimedias:
            multimedia['publish_time'] = timestamp_datetime(long(multimedia['publish_time']))

        self.render('moment/videos.html',
                ops=ops,
                club_id=ops['club_id'],
                multimedias=multimedias,
                api_domain=API_DOMAIN)
