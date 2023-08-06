#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.modeling import ListWrapper, SetWrapper, OrderedDict
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema import ValidationContext
from cocktail.persistence import PersistentObject
from cocktail.html import Element
from cocktail.html.databoundcontrol import data_bound


class Selector(Element):

    name = None
    items = None
    groups = None
    __value = None
    persistent_object = None

    empty_option_displayed = True
    empty_value = ""
    empty_label = None
    grouping = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        data_bound(self)
        self._is_selected = lambda item: False

    def _ready(self):

        Element._ready(self)
        item_translator = None

        if self.member:

            if self.items is None and self.groups is None:
                self.items = self._get_items_from_member(self.member)

            if isinstance(self.member, schema.Collection):
                if self.member.items:
                    item_translator = self.member.items.translate_value
            else:
                item_translator = self.member.translate_value

        self._item_translator = (
            item_translator
            or (lambda item, **kw: translations(item, **kw))
        )

        if (
            self.groups is None
            and self.grouping is not None
            and self.items is not None
        ):
            self.groups = SelectorGroup()

            for item in self.items:
                path = self.grouping(item)

                if not isinstance(path, tuple):
                    path = (path,)

                group = self.groups

                for group_value in path:
                    child = group.get_group_by_value(group_value)
                    if child is None:
                        child = SelectorGroup(group_value)
                        group.append_group(child)
                    group = child

                group.append_item(item)

        if self.value is None:
            self._is_selected = lambda item: item is None
        elif (
            isinstance(
                self.value,
                (list, tuple, set, ListWrapper, SetWrapper)
            )
            and not isinstance(self.member, schema.Tuple)
        ):
            self._is_selected = lambda item: item in self.value
        else:
            self._is_selected = lambda item: item == self.value

        self._fill_entries()

    def _get_items_from_member(self, member):

        if isinstance(member, schema.Collection):
            member = member.items

        context = ValidationContext(
            member,
            self.value,
            persistent_object = self.persistent_object
        )

        return member.get_possible_values(context)

    def _fill_entries(self):

        if self.empty_option_displayed:
            entry = self.create_entry(None)
            self.append(entry)

        if self.groups is not None:
            for group in self.groups.groups:
                self.append(self.create_group(group))
        elif self.items is not None:
            self._create_entries(self.items, self)

    def _create_entries(self, items, container):
        for item in items:
            entry = self.create_entry(item)
            container.append(entry)

    def get_item_value(self, item):

        if item is None and self.empty_value is not None:
            return self.empty_value

        member = (
            self.member
            and (
                isinstance(self.member, schema.Collection)
                and self.member.items
            )
            or self.member
        )

        if member:
            try:
                return member.serialize_request_value(item)
            except:
                pass

        return getattr(item, "id", None) or str(item)

    def get_item_label(self, item):

        if item is None:
            empty_label = self.empty_label

            if not empty_label and self.member:
                empty_label = self.member.translate_value(None)

            if not empty_label:
                empty_label = "---"

            return empty_label

        return self._item_translator(item)

    def is_selected(self, item):
        return self._is_selected(item)

    def create_group(self, group):

        container = Element()
        container.add_class("group")

        container.label = self.create_group_label(group)
        container.append(container.label)

        self._create_entries(group.items, container)
        self._create_nested_groups(group, container)

        return container

    def _create_nested_groups(self, group, container):
        for nested_group in group.groups:
            container.append(self.create_group(nested_group))

    def create_group_label(self, group):
        label = Element()
        label.add_class("group_label")
        label.append(self.get_group_title(group))
        return label

    def get_group_title(self, group):
        return translations(group.value)

    def create_entry(self, item):
        raise TypeError(
            "%s doesn't implement the create_entry() method" % self
        )

    def _get_value(self):
        return self.__value

    def _set_value(self, value):
        self.__value = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the active selection for the selector.
        """)


class SelectorGroup(object):

    def __init__(self, value = None):
        self.__value = value
        self.__groups_list = []
        self.__groups_by_value = {}
        self.__items = []

    @property
    def value(self):
        return self.__value

    @property
    def groups(self):
        return self.__groups_list

    @property
    def items(self):
        return self.__items

    def get_group_by_value(self, value):
        return self.__groups_by_value.get(value)

    def append_group(self, group):
        self.__groups_by_value[group.value] = group
        self.__groups_list.append(group)

    def append_item(self, item):
        self.__items.append(item)

