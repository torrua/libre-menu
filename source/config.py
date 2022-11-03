# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""Configuration file"""
import logging

detailed_format = '%(filename)s [LINE:%(lineno)d] [%(asctime)s] %(levelname)-s %(funcName)s() %(message)s'
short_format = '[%(asctime)s] %(message)s'

logging.basicConfig(
    format=detailed_format,
    level=logging.DEBUG,
    datefmt="%y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)
