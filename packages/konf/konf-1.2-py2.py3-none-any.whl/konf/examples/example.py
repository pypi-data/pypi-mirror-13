# -*- coding: utf-8 -*-


__author__ = 'vartagg'


from konf import Konf

# Filling of variables from config file tokens.yaml in k_ object
k_ = Konf('tokens.yaml')

# Getting variables from k_: first argument is a name of variable (specified in the config),
# second can be a type or validator
SECRET_KEY = k_('secret_key', basestring)
AUTH_TOKEN = k_('auth_token', basestring)

# In the next example is used a validator: list, that must contain
# only objects with basestring type (str or unicode)
CLIENTS = k_('clients', [basestring])

# And dict with two required keys with appropriate types
DELAYS = k_('delays', {'case1': int, 'case2': int})
