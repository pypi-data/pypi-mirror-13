__version__ = '0.0.6'
__description__ = 'A tool to install python packages from Github.'
__author__ = 'Filipe Funenga'
__license__ = 'MIT'
from .pipgh import USAGE_MESSAGE, HELP_MESSAGE
__doc__ = USAGE_MESSAGE + u'\n' + HELP_MESSAGE
del USAGE_MESSAGE, HELP_MESSAGE

from .pipgh import main
from .pipgh import search
from .pipgh import install
from .pipgh import show
