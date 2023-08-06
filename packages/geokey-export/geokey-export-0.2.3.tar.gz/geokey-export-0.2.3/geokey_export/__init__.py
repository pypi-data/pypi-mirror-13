from geokey.extensions.base import register


VERSION = (0, 2, 3)
__version__ = '.'.join(map(str, VERSION))

register(
    'geokey_export',
    'Export',
    display_admin=True,
    superuser=False,
    version=__version__
)
