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
        club = self.get_club_info(ops['club_id'])
        self.render('ops/index.html',
                ops=ops,
                club=club)


class ProfileEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])
        self.render('ops/profile-edit.html',
                ops=ops,
                club=club,
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


# 景区标签
class OpsFranchiseTagsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])
        # league_id = league_id
        # counter = self.get_counter(league_id)

        club_id = ops['club_id']
        logging.info("got club_id",club_id)

        # 查询一个加盟商所有的tags
        url = API_DOMAIN + "/api/clubs/"+ club_id +"/categories"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers,)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        franchise_tags = data['rs']

        # 景区分类tags
        category_id = '757ee072a02511e7b7f600163e023e51'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        hot_franchise_tags = data['rs']

        for tag in hot_franchise_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        # 景区特色tags
        category_id = '0c511b26a1e011e7943000163e023e51'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        product_tags = data['rs']

        for tag in product_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        # 景区适合对象tags
        category_id = 'b1fb3e94a1e011e7943000163e023e51'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        line_tags = data['rs']

        for tag in line_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        # 旺季季节tags
        category_id = '6955a40eb96911e7a70e00163e023e51'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        hot_time_tags = data['rs']

        for tag in hot_time_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        # 闭馆季节tags
        category_id = 'dffc1ee4b96911e7a70e00163e023e51'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        close_time_tags = data['rs']

        for tag in close_time_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        # 旅游时长tags
        category_id = '9a2f440eb96911e7a70e00163e023e51'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        duration_tags = data['rs']

        for tag in duration_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        self.render('ops/ops-franchise-tags.html',
                ops=ops,
                club=club,
                club_id=club_id,
                hot_franchise_tags=hot_franchise_tags,
                product_tags=product_tags,
                line_tags=line_tags,
                hot_time_tags=hot_time_tags,
                close_time_tags=close_time_tags,
                duration_tags=duration_tags,
                access_token=access_token,
                api_domain=API_DOMAIN,
                franchise_tags=franchise_tags)


# 供应商标签
class OpsSupplierTagsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])
        # league_id = league_id
        # counter = self.get_counter(league_id)

        club_id = ops['club_id']
        logging.info("got club_id",club_id)

        # 查询一个供应商所有的tags
        url = API_DOMAIN + "/api/clubs/"+ club_id +"/categories"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers,)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        franchise_tags = data['rs']

        # 特色产品tags
        category_id = '8bc87862b98811e7805e00163e045306'
        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        product_tags = data['rs']

        for tag in product_tags:
            tag['category_id'] = category_id
            tag['selected'] = False
            for franchise_tag in franchise_tags:
                if tag['_id'] == franchise_tag['level2_category_id']:
                    tag['selected'] = True
                    break

        self.render('ops/ops-supplier-tags.html',
                ops=ops,
                club = club,
                club_id=club_id,
                product_tags=product_tags,
                access_token=access_token,
                api_domain=API_DOMAIN,
                franchise_tags=franchise_tags)


class OperatorsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])

        self.render('ops/operators.html',
                ops=ops,
                club=club,
                club_id=ops['club_id'],
                access_token=access_token,
                api_domain=API_DOMAIN)


class TodoListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])
        self.render('ops/todo-list.html',
                ops=ops,
                club=club,
                club_id=ops['club_id'],
                api_domain=API_DOMAIN)


class ArticlesCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])
        self.render('article/create.html',
                ops=ops,
                club=club,
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
        club = self.get_club_info(ops['club_id'])

        params = {"filter":"club", "club_id":ops['club_id'], "status":"draft", "type":0}
        url = url_concat(API_DOMAIN+"/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        articles = data['rs']

        self.render('article/draft.html',
                ops=ops,
                club=club,
                access_token=access_token,
                club_id=ops['club_id'],
                articles=articles,
                api_domain=API_DOMAIN)


class ArticlesPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])

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
                club=club,
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

        url = API_DOMAIN+"/api/articles/" + article_id + "/categories"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got categories response=[%r]", response.body)
        data = json_decode(response.body)
        article_categories = data['rs']

        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])

        self.render('article/edit.html',
                ops=ops,
                club=club,
                club_id=ops['club_id'],
                access_token=access_token,
                article=article,
                article_categories=article_categories,
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
        club = self.get_club_info(ops['club_id'])

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
        club = self.get_club_info(ops['club_id'])

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
                club=club,
                club_id=ops['club_id'],
                multimedias=multimedias,
                api_domain=API_DOMAIN)


class MomentsImagesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])

        self.render('moment/images.html',
                ops=ops,
                club=club,
                club_id=ops['club_id'],
                api_domain=API_DOMAIN)


class MomentsUploadImagesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        ops = self.get_ops_info()
        club = self.get_club_info(ops['club_id'])

        self.render('moment/upload-image.html',
                ops=ops,
                club=club,
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
        club = self.get_club_info(ops['club_id'])

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
                club=club,
                club_id=ops['club_id'],
                multimedias=multimedias,
                api_domain=API_DOMAIN)
