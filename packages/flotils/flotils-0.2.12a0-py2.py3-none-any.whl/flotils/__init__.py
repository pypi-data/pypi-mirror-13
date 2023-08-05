# -*- coding: UTF-8 -*-
"""
An utility package
"""

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2013-16, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.12a0"
__date__ = "2016-01-07"

import logging

from .logable import Logable, ModuleLogable
from .loadable import Loadable, loadJSON, saveJSON, loadJSONFile, saveJSONFile
from .webscraper import WebScraper, \
    WEBConnectException, WEBFileException, WEBParameterException

__all__ = ["logable", "loadable", "webscraper"]
logger = logging.getLogger(__name__)
