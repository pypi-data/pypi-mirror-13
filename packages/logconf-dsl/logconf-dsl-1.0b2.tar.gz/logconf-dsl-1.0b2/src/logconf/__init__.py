import logging
import logging.config

from typing import Dict, Any, Iterable, Union, Mapping

from logconf.utils import DSLDict
from logconf.dsl import DSLBase
from logconf.dsl import (
    Loggers, Logger, RootLogger,
    Handlers, Handler,
    Formatters, Formatter
)

_log = logging.getLogger(__name__)
_log.debug('Imported')

Simple = Union[str, int, bool, float]


def configure(*args, **kwargs):
    config = logconf(*args, **kwargs)
    logging.config.dictConfig(config)


def C(*dsl_expressions: Iterable[Union[DSLDict, DSLBase]],
      **kwargs: Mapping[str, Union[DSLDict, DSLBase, Simple]]) -> Dict:

    arguments = DSLDict()
    if len(dsl_expressions):
        arguments = sum(dsl_expressions, arguments)

    return arguments + DSLDict(**kwargs)


def logconf(*dsl_expressions: Iterable[Union[DSLDict, DSLBase]],
            **kwargs: Mapping[str, Union[DSLDict, DSLBase, Simple]]) -> Dict:

    normalized = normalize_recursive(C(*dsl_expressions, **kwargs))
    normalized.setdefault('version', 1)

    return normalized


def normalize_recursive(start: Any) -> Any:
    _log.debug('to_dict_recursive: start=%r', start)
    if isinstance(start, (DSLBase, dict)):
        if isinstance(start, DSLBase):
            _log.debug('is DSLBaser: %r', start)
            start = start.to_dict()

        return {k: normalize_recursive(v) for k, v in start.items()}
    elif isinstance(start, list):
        return [normalize_recursive(i) for i in start]
    else:
        return start


if __name__ == '__main__':
    import json
    import logging.config

    from logconf.utils import pretty_repr

    with pretty_repr():
        logging.basicConfig(level=logging.DEBUG)

        a = logconf(
            Handlers(
                Handler('logging.StreamHandler', logging.DEBUG, 'verbose',
                        'verbose'),
                console=Handler(
                    klass='logging.StreamHandler'
                )
            ) +
            RootLogger(
                logging.DEBUG,
                ['console']
            ) +
            Loggers(
                Logger('logconf.dsl', logging.DEBUG, ['console']),
                foo=Logger(level=logging.DEBUG, handlers=['console'])
            )
        )

        logging.config.dictConfig(a)

        print(json.dumps(a, indent=4))
