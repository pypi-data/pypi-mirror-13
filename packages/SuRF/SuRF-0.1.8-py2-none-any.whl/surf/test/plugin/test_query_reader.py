# coding=UTF-8
""" Module for SPARQL generation tests. """
import logging

from unittest import TestCase
import warnings

from surf import ns
from surf.plugin.query_reader import RDFQueryReader

class TestQueryReader(TestCase):
    """ Tests for query_reader module. """
    
    def test_convert_unicode_exception(self):
        """ Test RDFQueryReader.convert() handles exceptions with unicode. """

        class MyQueryReader(RDFQueryReader):
            # We want convert() to catch an exception.
            # Cannot override __convert and throw from there,
            # but we know __convert calls _to_table... 
            def _to_table(self, _):
                warnings.simplefilter("ignore")
                raise Exception(u"This is unicode: ā")
            
        logging.disable(logging.ERROR)
        MyQueryReader().convert(None)
        logging.disable(logging.NOTSET)
