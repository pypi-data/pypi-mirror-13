# -*- coding: utf-8 -*-

from django.conf.urls import patterns

from coop_bar.bar import CoopBar


bar = CoopBar()  # This is a Borg

urlpatterns = patterns('')