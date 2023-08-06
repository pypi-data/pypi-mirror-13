#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.stringutils import html_to_plain_text
from cocktail.schema.schemastrings import String


class HTML(String):

    edit_control = "cocktail.html.TinyMCE"

    def extract_searchable_text(self, extractor):
        text = html_to_plain_text(extractor.current.value)
        extractor.feed(text)

