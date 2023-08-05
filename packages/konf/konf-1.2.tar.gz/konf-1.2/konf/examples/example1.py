# -*- coding: utf-8 -*-


__author__ = 'vartagg'


from konf import Konf
import good

k_ = Konf('images_service.yaml')

URL = k_('url', good.Url())
STATIC_SAVE_DIR = k_('/var/www/static/img', good.IsDir())
