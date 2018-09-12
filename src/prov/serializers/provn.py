from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = 'Trung Dong Huynh'
__email__ = 'trungdong@donggiang.com'
__contributor__ = 'Marcel Parciak'

import io
import logging
logger = logging.getLogger(__name__)

# import needed antlr4 elements, CommonTokenStream will tokenize the input PROV-N document
from antlr4 import CommonTokenStream
# ParseTreeWalker allows to walk through the parsed tokens
from antlr4 import ParseTreeWalker
# InputStream is needed to transform the input stream from BytesIO to a InputStream explicitly
from antlr4 import InputStream

from prov.model import ProvDocument
from prov.serializers import Serializer

# imports for automatically generated classes from antlr
from prov.serializers.antlr_grammars.PROV_NListener import PROV_NListener
from prov.serializers.antlr_grammars.PROV_NParser import PROV_NParser
from prov.serializers.antlr_grammars.PROV_NLexer import PROV_NLexer

# codecs is used to generate a utf-8 string from bytesIO inputs
import codecs
# TODO: used for debug outputs, remove at the end
from pprint import pprint

class ProvNAntlrListener(PROV_NListener):
    """
    An extension of the automatically generated PROV_NListener, based
    on the PROV-N antlr4 grammar provided by @TomasKulhanek on GitHub
    `PROV-N grammar <https://github.com/antlr/grammars-v4/blob/master/prov-n/examples/example4.provn>`_

    For the most part, the class overrides methods automatically
    generated by antlr4 in PROV_NListener.py

    """

    def __init__(self):
        self._doc = None

    @property
    def document(self):
        return self._doc

    def iriToUri(iri):
        """Converts an iri to an uri String. This method enables
        handling iri-references from antlr at a central point.

        :param iri: The IRI to transform
        """
        return iri.getText()[1:-1]

    def getIdentifierFromContext(self, ctx):
        """Retrieves an identifier from an IdentifierContext.
        This method will check which identifier element is
        populated and parse it to a String representation
        suitable to be used as an identifier to create 
        prov elements.

        :param ctx: IdentifierContext which will be used.
        """
        if ctx.PREFX() is not None:
            return ctx.PREFX().getText()
        if ctx.QUALIFIED_NAME() is not None:
            return ctx.QUALIFIED_NAME().getText()

        # TODO: is this possible? If so, how to handle?
        # first solution: return None
        return None

    def enterDocument(self, ctx):
        self._doc = ProvDocument()

    def enterDefaultNamespaceDeclaration(self, ctx):
        self._doc.set_default_namespace(ProvNAntlrListener.iriToUri(ctx.IRI_REF()))

    def enterNamespaceDeclaration(self, ctx):
        self._doc.add_namespace(ctx.PREFX().getText(), ProvNAntlrListener.iriToUri(ctx.namespace().IRI_REF()))

    def enterEntityExpression(self, ctx):
        self._doc.entity(self.getIdentifierFromContext(ctx.identifier()))

class ProvNSerializer(Serializer):
    """PROV-N serializer for ProvDocument

    """
    def serialize(self, stream, **kwargs):
        """
        Serializes a :class:`prov.model.ProvDocument` instance to a
        `PROV-N <http://www.w3.org/TR/prov-n/>`_.

        :param stream: Where to save the output.
        """
        provn_content = self.document.get_provn()
        if isinstance(stream, io.BytesIO):
            provn_content = provn_content.encode('utf-8')
        stream.write(provn_content)

    def deserialize(self, stream, **kwargs):
        """
        Deserializes from a `PROV-N <https://www.w3.org/TR/prov-n/>`_
        representation to a :class:`~prov.model.ProvDocument` instance.

        :param stream: Input data.
        """
        if isinstance(stream, io.BytesIO):
            stream = codecs.decode(stream.getvalue(), encoding='utf-8')
            stream = InputStream(stream)
        if isinstance(stream, io.StringIO):
            stream = InputStream(stream.getvalue())
        lexer = PROV_NLexer(stream)
        tokenStream = CommonTokenStream(lexer)
        parser = PROV_NParser(tokenStream)
        tree = parser.document()
        listener = ProvNAntlrListener()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)
        return listener.document
        #raise NotImplementedError
