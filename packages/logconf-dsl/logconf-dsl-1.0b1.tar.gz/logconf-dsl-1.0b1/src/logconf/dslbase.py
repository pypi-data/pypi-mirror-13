import logging

from typing import TypeVar, Dict

from .utils import DSLDict

_log = logging.getLogger(__name__)
_log.debug('Imported')


class DSLBase:
    wrap_with_key = None
    discard_if_none = ('propagate', 'handlers')

    def __init__(self):
        self.data = DSLDict()

    def init_data(self, **kwargs):
        self.data = DSLDict(**kwargs)

    @staticmethod
    def discard_item(k, v):
        """
        Called by DSLBase.filter_data with `k, v = self.data[i]` in order to
        assemble the final dict structure.

        :param k: data key
        :param v: data value
        :return: True to discard item, False or None to keep item
        """
        return

    def filter_data(self):
        for item in self.data.items():
            if self.discard_item(*item):
                _log.debug('discard item=%r', item)
                continue

            key, value = item
            # Throw away items whose key is in self.discard_if_none
            if key in self.discard_if_none and value is None:
                continue

            yield item

    def to_dict(self) -> DSLDict:
        """
        Get the dict representation of a DSLBase instance.
        """
        _log.debug('%s.to_dict: self.data=%r',
                   self.__class__.__name__,
                   self.data)

        if not isinstance(self.data, DSLDict):
            _log.warning('self.data=%r is not an instance of DSLDict',
                         self.data)

        if self.wrap_with_key is not None:
            _log.debug('self.wrap_with_key=%r', self.wrap_with_key)
            return DSLDict({
                self.wrap_with_key: DSLDict(self.filter_data())
            })

        return DSLDict(self.filter_data())

    def __add__(self, other: TypeVar('DSLBase')):
        other_repr = None
        if isinstance(other, DSLBase):
            other_repr = other.data.format_repr(nested=True)
        elif isinstance(other, DSLDict):
            other_repr = other.format_repr(nested=True)
        elif isinstance(other, dict):
            other_repr = repr(other)

        _log.debug('%s__add__: %r + %r',
                   self.__class__.__name__,
                   self.data.format_repr(nested=True),
                   other_repr)

        if isinstance(other, DSLDict):
            _log.debug('Using DSLBase\'s __add__ implementation')
            return other + self

        return self.to_dict() + other.to_dict()

    def __repr__(self):
        return '<{} data={}>'.format(self.__class__.__name__,
                                     self.data.format_repr(nested=True))


class LogConf(DSLBase):
    def __init__(self, formatters=None, handlers=None, loggers=None,
                 root=None, version=1):
        super(LogConf, self).__init__()
        self.data += dict(formatters=formatters,
                          handlers=handlers,
                          loggers=loggers,
                          root=root,
                          version=version)
