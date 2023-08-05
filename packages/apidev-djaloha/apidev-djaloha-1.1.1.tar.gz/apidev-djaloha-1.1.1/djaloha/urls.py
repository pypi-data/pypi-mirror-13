# -*- coding:utf-8 -*-
"""urls"""

from django.conf.urls import patterns, url
from djaloha.views import aloha_init

urlpatterns = patterns('',
    url(r'^djaloha/aloha-config.js', aloha_init, name='aloha_init'),
)
