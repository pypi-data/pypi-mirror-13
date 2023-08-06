#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.member import Member
from cocktail.schema.exceptions import MinItemsError, MaxItemsError


class Tuple(Member):

    type = tuple
    items = ()
    glue = ", "

    def __init__(self, *args, **kwargs):
        Member.__init__(self, *args, **kwargs)
        self.add_validation(self.__class__.tuple_validation_rule)

    def translate_value(self, value):
        if not value:
            return Member.translate_value(self, value)
        else:
            return self.glue.join(
                member.translate_value(item)
                for member, item in zip(self.items, value)
            )

    def tuple_validation_rule(self, value, context):

        if value is not None:

            value_length = len(value)
            expected_length = len(self.items)

            if value_length < expected_length:
                yield MinItemsError(self, value, context, expected_length)

            elif value_length > expected_length:
                yield MaxItemsError(self, value, context, expected_length)

            for item_member, item in zip(self.items, value):
                try:
                    context.enter(item_member, item)
                    for error in item_member.get_errors(item, context):
                        yield error
                finally:
                    context.leave()

