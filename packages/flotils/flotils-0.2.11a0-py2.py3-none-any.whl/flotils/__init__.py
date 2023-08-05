# -*- coding: UTF-8 -*-
"""
An utility package
"""

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2013-15, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.11a0"
__date__ = "2015-12-31"

import logging

from .logable import Logable, ModuleLogable
from .loadable import Loadable, loadJSON, saveJSON, loadJSONFile, saveJSONFile

__all__ = ["logable", "loadable"]
logger = logging.getLogger(__name__)
