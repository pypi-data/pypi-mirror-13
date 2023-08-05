"""
gargoyle
~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from gargoyle.manager import gargoyle

__version__ = '1.1.1'
VERSION = __version__  # old version compat

__all__ = ('gargoyle', 'autodiscover', '__version__', 'VERSION')


def autodiscover():
    """
    Auto-discover INSTALLED_APPS' gargoyle modules and fail silently when
    not present. This forces an import on them to register any gargoyle bits they
    may want.
    """
    import copy
    from django.conf import settings

    from importlib import import_module

    for app in settings.INSTALLED_APPS:
        # Attempt to import the app's gargoyle module.
        before_import_registry = copy.copy(gargoyle._registry)
        try:
            import_module('%s.gargoyle' % app)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            gargoyle._registry = before_import_registry

    # load builtins
    __import__('gargoyle.builtins')
