from __future__ import absolute_import, unicode_literals

__all__ = ['VERSION']


try:
    import pkg_resources
    VERSION = pkg_resources.get_distribution('django-dropimages').version
except Exception:
    VERSION = 'unknown'


# Code that discovers files or modules in INSTALLED_APPS imports this module.
# Reference URLpatterns with a string to avoid the risk of circular imports.

urls = 'django_dropimages.urls', 'djdropimages', 'djdropimages'


default_app_config = 'django_dropimages.apps.DropImagesConfig'
