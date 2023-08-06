#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from abc import ABCMeta, abstractmethod
import cherrypy
from simplejson import dumps
from cocktail import schema
from cocktail.schema.expressions import Self
from cocktail.persistence.query import Query
from cocktail.persistence.persistentobject import PersistentClass
from cocktail.controllers.controller import Controller
from cocktail.controllers.requestproperty import request_property


class AutocompleteSource(object):

    __metaclass__ = ABCMeta

    query = None

    def __init__(self, query):
        self.query = query

    @request_property
    @abstractmethod
    def items(self):
        pass

    def apply_search(self, items):
        if self.query:
            items.add_filter(
                Self.search(self.query, match_mode = "prefix")
            )

    def get_entry(self, item):
        return {
            "value": self.get_entry_value(item),
            "label": self.get_entry_label(item)
        }

    @abstractmethod
    def get_entry_value(self, item):
        pass

    @abstractmethod
    def get_entry_label(self, item):
        pass


class MemberAutocompleteSource(AutocompleteSource):

    def __init__(self, member, query = None):
        AutocompleteSource.__init__(self, query)

        if isinstance(member, PersistentClass):
            member = schema.Reference(type = member)

        self.member = member

    @request_property
    def items(self):
        items = self.member.get_possible_values()

        if not isinstance(items, Query):
            items = self.member.type.select()
            items.base_collection = items

        if self.query:
            self.apply_search(items)

        return items

    def get_entry_value(self, item):
        return self.member.serialize_request_value(item)

    def get_entry_label(self, item):
        return self.member.translate_value(item)


class AutocompleteController(Controller):

    member = None
    autocomplete_factory = None

    def __init__(self, autocomplete_factory, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)

        if isinstance(autocomplete_factory, schema.Member):
            member = autocomplete_factory
            autocomplete_factory = (
                lambda query: MemberAutocompleteSource(member, query)
            )

        self.autocomplete_factory = autocomplete_factory

    def __call__(self, query = ""):
        self.query = query
        cherrypy.response.headers["Content-Type"] = "application/json"
        return Controller.__call__(self)

    def render(self):

        source = self.autocomplete_factory(self.query)

        yield u"["

        entry = {}
        glue = u""

        for item in source.items:
            yield glue
            glue = u","
            yield dumps(source.get_entry(item))

        yield u"]"

