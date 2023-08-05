# coding: utf-8

"""
django informer checker base
"""

import logging
from importlib import import_module

from informer.models import post_check


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Django Infomer')


class InformerException(Exception):
    """
    A class to deal with exceptions.
    """
    pass


class BaseInformer(object):
    """
    A (base) class to serve as infrastructure to new 'Informers'.
    """

    def __str__(self):
        return u'A small and explicit description from informer.'

    def __new__(cls, *args, **kwargs):
        """
        On instantiation, the trigger's is added.
        """
        measures = cls.get_measures()

        for measure in measures:
            func = getattr(cls, measure)
            setattr(cls, measure, save(func))

        # Bind 'run all' on default check.
        func = getattr(cls, 'check_availability')
        setattr(cls, 'check_availability', run(func))

        return super(BaseInformer, cls).__new__(cls)

    def check_availability(self):
        """
        Each informer need check the availability from resource or service.
        """
        raise NotImplementedError

    @staticmethod
    def get_class(namespace, classname):
        """
        Dynamic import from Informer
        """
        try:
            module = import_module(namespace)
            cls = getattr(module, classname)
        except ImportError:
            raise InformerException(
                '%s is unknown or undefined.' % classname)
        except AttributeError:
            raise InformerException(
                'The %s does not exists on %s.' % (classname, namespace))
        except Exception as error:
            raise InformerException(
                'A general exception occurred: %s.' % error)

        if not issubclass(cls, BaseInformer):
            raise InformerException('%s is not a Informer.' % classname)

        return cls

    @classmethod
    def get_measures(cls):
        """
        Get measures
        """
        return [attr for attr in dir(cls) if attr.startswith('check_')]


def save(func):
    """
    When a verification is done, the signal to save data is sent.
    """
    def trigger(cls, *args, **kwargs):
        measure = func.__name__
        values = func(cls)

        if measure not in cls.get_measures():
            return values

        post_check.send(sender=cls, measure=measure, value=values[0])

        message = ' %s (%s) collected values %s'
        message %= (measure, cls.__class__.__name__, values)

        logger.info(message)

        return values

    return trigger


def run(func):
    """
    When 'check availability' is called, all others run on cascade.
    """
    def trigger(cls, *args, **kwargs):
        values = func(cls)

        measures = cls.get_measures()
        measures.remove('check_availability')  # Remove to avoid double run.

        for measure in measures:
            getattr(cls, measure)()

        return values

    return trigger
