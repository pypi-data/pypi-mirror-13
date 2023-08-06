# -*- coding: utf-8 -*-
"""
app definition
"""

from django import VERSION

if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class DjalohaAppConfig(AppConfig):
        name = 'djaloha'
        verbose_name = "DjAloha"
