# -*- coding: utf-8 -*-
"""
Customizable tool bar
"""

from django import VERSION

if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class CoopBarAppConfig(AppConfig):
        name = 'coop_bar'
        verbose_name = "coop Bar"
