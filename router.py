# _*_ coding: utf-8_*_
#
# genral application route config:
# simplify the router config by dinamic load class
# by lwz7512
# @2016/05/17

import tornado.web

from foo import comm
from foo.auth import auth_email
from foo.auth import auth_phone
from foo.ops import work_sheet


def map():

    config = [

        (r'/', getattr(work_sheet, 'OpsIndexHandler')),

        (r'/ops/auth/email/login', getattr(auth_email, 'AuthEmailLoginHandler')),
        (r'/ops/auth/email/register', getattr(auth_email, 'AuthEmailRegisterHandler')),
        (r'/ops/auth/email/forgot-pwd', getattr(auth_email, 'AuthEmailForgotPwdHandler')),
        (r'/ops/auth/email/reset-pwd', getattr(auth_email, 'AuthEmailResetPwdHandler')),
        (r'/ops/auth/welcome', getattr(auth_email, 'AuthWelcomeHandler')),
        (r'/ops/auth/logout', getattr(auth_email, 'AuthLogoutHandler')),
        (r'/ops/auth/phone/login', getattr(auth_phone, 'AuthPhoneLoginHandler')),
        (r'/ops/auth/phone/register', getattr(auth_phone, 'AuthPhoneRegisterHandler')),
        (r'/ops/auth/phone/verify-code', getattr(auth_phone, 'AuthPhoneVerifyCodeHandler')),
        (r'/ops/auth/phone/lost-pwd', getattr(auth_phone, 'AuthPhoneLostPwdHandler')),

        (r'/ops', getattr(work_sheet, 'OpsIndexHandler')),
        (r'/ops/profile/edit', getattr(work_sheet, 'ProfileEditHandler')),
        (r'/ops/operators', getattr(work_sheet, 'OperatorsHandler')),
        (r'/ops/todo-list', getattr(work_sheet, 'TodoListHandler')),
        (r'/ops/articles/create', getattr(work_sheet, 'ArticlesCreateHandler')),
        (r'/ops/articles/draft', getattr(work_sheet, 'ArticlesDraftHandler')),
        (r'/ops/articles/publish', getattr(work_sheet, 'ArticlesPublishHandler')),
        (r'/ops/articles/edit', getattr(work_sheet, 'ArticlesEditHandler')),

        # comm
        ('.*', getattr(comm, 'PageNotFoundHandler'))

    ]

    return config
