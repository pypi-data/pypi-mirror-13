# -*- coding: utf-8 -*-
import re
import logging
import logging.config
import types

from dateutil.parser import parser
from pytz import UTC, timezone

from dateparser.timezone_parser import _tz_offsets


GROUPS_REGEX = re.compile(r'(?<=\\)(\d+|g<\d+>)')
G_REGEX = re.compile(r'g<(\d+)>')


def strip_braces(date_string):
    return re.sub(r'[{}()<>\[\]]+', '', date_string)


def is_dateutil_result_obj_parsed(date_string):
    res = parser()._parse(date_string)
    if not res:
        return False

    def get_value(obj, key):
        value = getattr(obj, key)
        return str(value) if value is not None else ''

    return any([get_value(res, k) for k in res.__slots__])


def wrap_replacement_for_regex(replacement, regex):
    # prepend group to replacement
    replacement = r"\g<1>%s" % increase_regex_replacements_group_positions(replacement, increment=1)

    # append group to replacement
    used_groups = re.compile(regex).groups
    new_group = used_groups + 2  # Consider that we already prepended replacement with one group
    replacement = "%s\\g<%d>" % (replacement, new_group)

    return replacement


def increase_regex_replacements_group_positions(replacement, increment):
    splitted = GROUPS_REGEX.split(replacement)
    for i in range(1, len(splitted), 2):
        group = splitted[i]
        if group.isdigit():
            splitted[i] = str(int(group) + increment)
        else:
            splitted[i] = "g<{}>".format(int(G_REGEX.match(group).group(1)) + increment)
    return u"".join(splitted)


def setup_logging():
    if len(logging.root.handlers):
        return

    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'console': {
                'format': "%(asctime)s %(levelname)s: [%(name)s] %(message)s",
            },
        },
        'handlers': {
            'console': {
                'level': logging.DEBUG,
                'class': "logging.StreamHandler",
                'formatter': "console",
                'stream': "ext://sys.stdout",
            },
        },
        'root': {
            'level': logging.DEBUG,
            'handlers': ["console"],
        },
    }
    logging.config.dictConfig(config)


def get_logger():
    setup_logging()
    return logging.getLogger('dateparser')


def find_date_separator(format):
    m = re.search(r'(?:(?:%[dbBmaA])(\W))+', format)
    if m:
        return m.group(1)


def apply_tzdatabase_timezone(date_time, pytz_string):
    date_time = UTC.localize(date_time)
    usr_timezone = timezone(pytz_string)

    if date_time.tzinfo != usr_timezone:
        date_time = date_time.astimezone(usr_timezone)

    return date_time.replace(tzinfo=None)


def apply_dateparser_timezone(utc_datetime, offset_or_timezone_abb):
    for _, info in _tz_offsets:
        if info['regex'].search(' %s' % offset_or_timezone_abb):
            return utc_datetime + info['offset']


def apply_timezone(datetime, tz_string):
    if 'UTC' in tz_string:
        return datetime

    new_datetime = apply_dateparser_timezone(datetime, tz_string)

    if not new_datetime:
        new_datetime = apply_tzdatabase_timezone(datetime, tz_string)

    return new_datetime


def registry(cls):
    def choose(creator):
        def constructor(cls, *args, **kwargs):
            key = cls.get_key(*args, **kwargs)

            if not hasattr(cls, "__registry_dict"):
                setattr(cls, "__registry_dict", {})
            registry_dict = getattr(cls, "__registry_dict")

            if key not in registry_dict:
                registry_dict[key] = creator(cls, *args)
                setattr(registry_dict[key], 'registry_key', key)
            return registry_dict[key]
        return staticmethod(constructor)

    if not (hasattr(cls, "get_key")
            and isinstance(cls.get_key, types.MethodType)
            and cls.get_key.__self__ is cls):
        raise NotImplementedError("Registry classes require to implement class method get_key")

    setattr(cls, '__new__', choose(cls.__new__))
    return cls
