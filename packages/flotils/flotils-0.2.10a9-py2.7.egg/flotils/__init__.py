# -*- coding: UTF-8 -*-
"""
An utility package
"""

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2013-15, Florian JUNG"
__license__ = "MIT"
__version__ = '0.2.10a9'
__date__ = "2015-12-29"

import logging

from .logable import Logable, ModuleLogable

__all__ = ["logable"]
logger = logging.getLogger(__name__)
