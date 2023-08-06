import sys
import logging
from contextlib import contextmanager

from typing import TypeVar, Any, Dict, Union

_log = logging.getLogger(__name__)
_log.debug('Imported')


class DSLDict(dict):
    _REPR_PRETTY = False

    def __getattr__(self, item: Any) -> Any:
        return self[item]

    def __setattr__(self, key: Any, value: Any) -> None:
        self[key] = value

    def __add__(self, other: Union[Dict, TypeVar('.dslbase.DSLBase')]) -> \
            TypeVar('DSLDict'):
        _log.debug('DSLDict.__add__: self=%r, other=%r', self, other)

        if not isinstance(other, dict):
            if hasattr(other, 'to_dict') and callable(other.to_dict):
                other = other.to_dict()
            else:
                raise NotImplementedError(
                    'Unsupported operand "+" for types {0} and {1}'.format(
                        type(self),
                        type(other)
                    ))

        self.update(other)
        return self

    @property
    def should_repr_pretty(self):
        return getattr(sys, '_LOGCONF_REPR_PRETTY', False)

    def format_repr(self, nested=False):
        if self.should_repr_pretty:
            from pprint import PrettyPrinter
            pprinter = PrettyPrinter(compact=True)

            _repr = pprinter.pformat(dict(self))
        else:
            _repr = '{0!r}'.format(dict(self))

        if nested:
            return 'DSLDict({0})'.format(_repr)
        else:
            return '<DSLDict {0}>'.format(_repr)

    def __repr__(self) -> str:
        return self.format_repr(nested=False)


@contextmanager
def pretty_repr():
    try:
        original_value = sys._LOGCONF_REPR_PRETTY
        attr_exists = True
    except AttributeError:
        original_value = None
        attr_exists = False

    sys._LOGCONF_REPR_PRETTY = True

    yield

    if attr_exists:
        sys._LOGCONF_REPR_PRETTY = original_value
    else:
        del sys._LOGCONF_REPR_PRETTY
