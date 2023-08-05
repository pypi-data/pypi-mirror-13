# -*- coding: utf-8 -*-
"""
apps
"""

from django import VERSION

if VERSION > (1, 7, 0):
    from django.apps import AppConfig

    class ColorboxAppConfig(AppConfig):
        name = 'colorbox'
        verbose_name = "Colorbox"
