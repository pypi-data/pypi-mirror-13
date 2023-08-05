# coding: utf-8

"""
informer factories
"""

import factory
import factory.fuzzy

from informer.models import Raw


class RawFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Raw

    indicator = factory.fuzzy.FuzzyChoice(['Database', 'Cache', 'REST'])
    measure = factory.fuzzy.FuzzyChoice(['time', 'level', 'volume'])
    value = factory.fuzzy.FuzzyDecimal(0.5, 42.7)
