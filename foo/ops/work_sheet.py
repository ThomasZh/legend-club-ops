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
        ops = self.get_myinfo_basic()
        self.render('ops/index.html',
                ops=ops)


class ProfileEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        ops = self.get_myinfo_basic()
        self.render('ops/profile-edit.html',
                ops=ops)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        nickname = self.get_argument("nickname", "")
        avatar = self.get_argument("avatar", "")
        logging.info("try update myinfo nickname:[%r] avatar:[%r]", nickname, avatar)

        url = "http://api.7x24hs.com/api/myinfo"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode({"nickname":nickname, "avatar":avatar})
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)

        self.redirect("/")


class OperatorsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_myinfo_basic()

        self.render('ops/operators.html',
                ops=ops,
                club_id=CLUB_ID)


class TodoListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_myinfo_basic()

        self.render('ops/todo-list.html',
                ops=ops,
                club_id=CLUB_ID)


class ArticlesCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_myinfo_basic()

        self.render('article/create.html',
                ops=ops,
                club_id=CLUB_ID)


class ArticlesDraftHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        params = {"filter":"club", "club_id":CLUB_ID, "status":"draft", "type":0}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)

        ops = self.get_myinfo_basic()

        self.render('article/draft.html',
                ops=ops,
                club_id=CLUB_ID,
                articles=articles)


class ArticlesPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        params = {"filter":"club", "club_id":CLUB_ID, "status":"publish"}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)

        # activity['beginTime'] = timestamp_datetime(long(activity['beginTime'] / 1000))

        for article in articles:
            article['publish_time'] = timestamp_datetime(long(article['publish_time']))

        ops = self.get_myinfo_basic()

        self.render('article/publish.html',
                ops=ops,
                club_id=CLUB_ID,
                articles=articles)


class ArticlesEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        article_id = self.get_argument("id", "")
        logging.info("get article_id=[%r] from argument", article_id)

        url = "http://api.7x24hs.com/api/articles/"+article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        article = json_decode(response.body)

        ops = self.get_myinfo_basic()

        self.render('article/edit.html',
                ops=ops,
                club_id=CLUB_ID,
                article=article)


class MomentsAllHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        # multimedia
        params = {"filter":"club", "club_id":CLUB_ID, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        ops = self.get_myinfo_basic()

        self.render('moment/all.html',
                ops=ops,
                club_id=CLUB_ID,
                multimedias=multimedias)


class MomentsImagesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        # multimedia
        params = {"filter":"club", "club_id":CLUB_ID, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        ops = self.get_myinfo_basic()

        self.render('moment/images.html',
                ops=ops,
                club_id=CLUB_ID,
                multimedias=multimedias)


class MomentsVideosHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        # multimedia
        params = {"filter":"club", "club_id":CLUB_ID, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        ops = self.get_myinfo_basic()

        self.render('moment/videos.html',
                ops=ops,
                club_id=CLUB_ID,
                multimedias=multimedias)
