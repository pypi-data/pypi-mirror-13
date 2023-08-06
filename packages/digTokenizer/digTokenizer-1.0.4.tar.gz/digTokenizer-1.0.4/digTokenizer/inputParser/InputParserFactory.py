#!/usr/bin/env python

from JSONParser import JSONParser

class ParserFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_parser(config, text_format=None, **kwargs):
        parser = JSONParser(config, **kwargs)
        return parser
