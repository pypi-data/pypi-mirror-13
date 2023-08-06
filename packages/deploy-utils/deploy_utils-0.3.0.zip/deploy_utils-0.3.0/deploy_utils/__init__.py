import os

__import__('pkg_resources').declare_namespace(__name__)


BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
