#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from time import time, mktime
from datetime import datetime, date, timedelta
from cocktail.modeling import DictWrapper, getter
from cocktail.styled import styled

missing = object()

class Cache(DictWrapper):

    expiration = None
    entries = None
    enabled = True
    updatable = True
    verbose = False

    def __init__(self, load = None):
        entries = {}
        DictWrapper.__init__(self, entries)
        self.__entries = entries

        if load is not None:
            self.load = load

    def _drop_expired(self):

        if self.expiration:

            oldest_creation_time = time() - self.expiration

            for key, entry in self.__entries.items():
                if entry.creation < oldest_creation_time:
                    del self[key]

    def request(self, key, expiration = None, invalidation = None):
        try:
            return self.get_value(key, invalidation = invalidation)
        except KeyError:
            if self.verbose:
                print styled("CACHE: Generating", "white", "red", "bold"),
                print key
            value = self.load(key)
            if self.enabled:
                self.set_value(key, value, expiration)
            return value

    def get_value(self, key, default = missing, invalidation = None):
        if self.enabled:
            entry = self.__entries.get(key, None)

            if entry is not None:

                if self.updatable \
                and not self._is_current(entry, invalidation, self.verbose):
                    if default is missing:
                        raise ExpiredEntryError(entry)
                else:
                    if self.verbose:
                        print styled("CACHE: Recovering", "white", "green", "bold"),
                        print key
                    return entry.value

        if default is missing:
            raise KeyError("Undefined cache key: %s" % repr(key))

        return default

    def set_value(self, key, value, expiration = None):
        if self.verbose:
            print styled("CACHE: Storing", "white", "pink", "bold"),
            print key,
            if expiration is None:
                print
            else:
                print styled("expiration:", "pink"), expiration
        self.__entries[key] = CacheEntry(key, value, expiration)

    def load(self, key):
        pass

    def __delitem__(self, key):
        entry = self.__entries.get(key)
        if entry:
            self._entry_removed(entry)
        else:
            raise KeyError(key)

    def pop(self, key, default = missing):
        entry = self.__entries.get(key)
        if entry is None:
            if default is missing:
                raise KeyError(key)
            return default
        else:
            del self.__entries[key]
            self._entry_removed(entry)
            return entry

    def clear(self):
        entries = self.__entries.values()
        self.__entries.clear()
        for entry in entries:
            self._entry_removed(entry)

    def _is_current(self, entry, invalidation = None, verbose = False):

        # Expiration
        if entry.has_expired(default_expiration = self.expiration):
            if verbose:
                print styled("CACHE: Entry expired", "white", "brown", "bold"), entry.key,
                if entry.expiration is None:
                    print self.expiration
                else:
                    print entry.expiration

            return False

        # Invalidation
        if callable(invalidation):
            invalidation = invalidation()

        if invalidation is not None:
            if isinstance(invalidation, datetime):
                invalidation = mktime(invalidation.timetuple())
            if invalidation > entry.creation:
                if verbose:
                    print styled("CACHE: Entry invalidated", "white", "brown", "bold"),
                    print entry.key, invalidation
                return False

        return True

    def _entry_removed(self, entry):
        pass


class CacheEntry(object):

    def __init__(self, key, value, expiration = None):
        self.key = key
        self.value = value
        self.creation = time()
        self.expiration = expiration

    def has_expired(self, default_expiration = None):

        expiration = self.expiration

        if expiration is None:
            expiration = default_expiration

        if expiration is None:
            return False

        elif isinstance(expiration, int):
            return time() - self.creation >= expiration

        elif isinstance(expiration, datetime):
            return datetime.now() >= expiration

        elif isinstance(expiration, date):
            return date.today() >= expiration

        elif isinstance(expiration, timedelta):
            return time() - self.creation >= expiration.total_seconds()


class ExpiredEntryError(KeyError):

    def __init__(self, entry):
        KeyError.__init__(self, "Cache key expired: %s" % entry.key)
        self.entry = entry

