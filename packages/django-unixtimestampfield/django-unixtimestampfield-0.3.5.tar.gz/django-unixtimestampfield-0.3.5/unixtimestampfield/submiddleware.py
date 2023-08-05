# -*- coding: utf-8 -*-

from django.conf import settings

USF_DATETIME, USF_TIMESTAMP, USF_DEFAULT = 'usf_datetime', 'usf_timestamp', 'usf_default'

USF_FORMAT = getattr(settings, 'USF_FORMAT', USF_DEFAULT)
if USF_FORMAT not in [USF_DATETIME, USF_TIMESTAMP, USF_DEFAULT]:
    USF_FORMAT = USF_DEFAULT


def field_value_middleware(field, value, usf_format=USF_FORMAT):

    if usf_format == USF_DEFAULT:
        return field.to_timestamp(value) if field.use_numeric else field.to_datetime(value)

    if usf_format == USF_DATETIME:
        return field.to_datetime(value)

    if usf_format == USF_TIMESTAMP:
        return field.to_timestamp(value)

    raise ValueError('USF_FORMAT: %s should not in optional values')
