import logging
import typing

from typing import Optional, Union, Iterable, Dict

from .dslbase import DSLBase
from .utils import DSLDict

_log = logging.getLogger(__name__)


class ItemWrapper(DSLBase):
    def __init__(self,
                 *args: Iterable[DSLBase],
                 **kwargs: Dict[str, DSLBase]):
        _log.debug('%s.__init__(args=%r, kwargs=%r)',
                   self.__class__.__name__,
                   args,
                   kwargs)
        super(ItemWrapper, self).__init__()

        arguments = DSLDict(
            **{k: v.disable_wrap(True).to_dict()
               for k, v in kwargs.items()})

        if len(args):
            arguments = sum(args, arguments)

        self.init_data(**arguments)


class NameWrappedItem(DSLBase):
    @staticmethod
    def discard_item(k, v):
        return k == 'name'

    def disable_wrap(self, disable: bool):
        _log.debug('%s.disable_wrap(%r): self=%r',
                   self.__class__.__name__,
                   disable,
                   self)
        if disable:
            setattr(self, '_wrapping_disabled', True)
        else:
            delattr(self, '_wrapping_disabled')

        return self

    @property
    def wrap_with_key(self):
        if getattr(self, '_wrapping_disabled', None):
            return None

        return self.data.get('name')


class Formatters(ItemWrapper):
    wrap_with_key = 'formatters'


class Formatter(NameWrappedItem):
    def __init__(self,
                 name=None,
                 format=None):
        super(Formatter, self).__init__()
        self.init_data(
            name=name,
            format=format
        )


class Handlers(ItemWrapper):
    wrap_with_key = 'handlers'


class Handler(NameWrappedItem):
    def __init__(self,
                 name: Optional[str]=None,
                 klass: Optional[str]=None,
                 formatter: Optional[str]=None,
                 level: Optional[Union[str, int]]=None,
                 **kwargs):
        super(Handler, self).__init__()
        kwargs.update({'class': klass})
        self.init_data(
            **dict(
                level=level,
                formatter=formatter,
                name=name,
                **kwargs
            ))


class Loggers(ItemWrapper):
    wrap_with_key = 'loggers'


class Logger(NameWrappedItem):
    def __init__(self, name=None, level=logging.NOTSET,
                 handlers=None,
                 propagate=None):
        super(Logger, self).__init__()
        self.init_data(name=name,
                       level=level,
                       handlers=handlers,
                       propagate=propagate)


class RootLogger(Logger):
    """
    Helper for Logger('root', ...)
    """
    def __init__(self,
                 level: Optional[Union[str, int]]=None,
                 handlers: Optional[Iterable[str]]=None):
        super(RootLogger, self).__init__('root', level, handlers)
