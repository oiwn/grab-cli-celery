import logging
import importlib


logger = logging.getLogger(__name__)


def module_import(name):
    if not isinstance(name, str):
        return name

    if '.' not in name:
        return importlib.import_module(name)

    parts = name.split('.')
    for i in reversed(range(1, len(parts))):
        mod_name = '.'.join(parts[:i])
        attrs = parts[i:]

        try:
            obj = importlib.import_module(mod_name)
        except ImportError as ex:
            logger.warning(ex)
            continue

        for attr in attrs:
            try:
                obj = getattr(obj, attr)
            except AttributeError as ex:
                logger.warning(ex)
                break
        else:
            return obj

        continue
    else:
        raise ImportError("Can't resolve: {}".format(name))
