# -*- coding: utf-8 -*-
"""utilities"""

from django import VERSION

if VERSION >= (1, 9, 0):
    from django.apps import apps
    get_model = apps.get_model
else:
    from django.db.models import get_model

from djaloha.forms import DjalohaForm


def extract_forms_args(data):
    """get the form arguments from POST data"""
    forms_args = []
    for field in data:
        if field.find('djaloha') == 0:
            args = field.split("__")
            if len(args) > 4:
                app_name = args[1]
                model_name = args[2]
                model_class = get_model(app_name, model_name)
                field_name = args[-1]
                lookup = {}
                for (key, value) in zip(args[3:-1:2], args[4:-1:2]):
                    lookup[key] = value
                forms_args.append((model_class, lookup, field_name))
    return forms_args


def make_forms(forms_args, data):
    """make Djaloha forms"""
    forms = []
    for (model_class, lookup, field_name) in forms_args:
        forms.append(DjalohaForm(model_class, lookup, field_name, data=data))
    return forms
