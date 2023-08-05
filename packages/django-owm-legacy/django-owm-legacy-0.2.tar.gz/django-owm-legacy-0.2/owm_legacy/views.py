import hashlib

from django.shortcuts import get_object_or_404
from django_netjsonconfig.models import Config
from django_netjsonconfig.utils import send_file

from .utils import forbid_unallowed


def get_config_md5(request, key):
    """
    returns md5 of configuration bytes
    """
    forbid_unallowed(request)
    config = get_object_or_404(Config, key__iexact=key)
    return send_file(key, config.checksum)


def get_config(request, key):
    """
    returns md5 of configuration bytes
    """
    forbid_unallowed(request)
    config = get_object_or_404(Config, key__iexact=key)
    return send_file(filename='{0}.tar.gz'.format(config.name),
                     contents=config.generate().getvalue())
