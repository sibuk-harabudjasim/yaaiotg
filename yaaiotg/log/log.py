# -*- coding: utf-8 -*-
import logging
import os


def init():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s: %(message)s',
        level=logging.DEBUG if os.getenv("DEBUG", "0") != "0" else logging.INFO
    )


__author__ = 'manitou'
