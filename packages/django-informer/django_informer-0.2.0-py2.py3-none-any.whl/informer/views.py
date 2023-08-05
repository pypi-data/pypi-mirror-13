# coding: utf-8

"""
informer views
"""

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings

from informer.checker.base import BaseInformer, InformerException
from informer.models import Raw


class DefaultView(View):
    """
    Default view used for Angular JS web application
    """
    template = 'django-informer-index.html'

    def get(self, request):
        """
        GET /informer/
        """

        interval = getattr(settings, 'DJANGO_INFORMER_PREVENT_SAVE_UNTIL', 0)

        data = {
            'URL': reverse('default-informer'),
            'INTERVAL': interval
        }

        return render(request, self.template, data, content_type='text/html')


class DiscoverView(View):
    """
    Discover URL's from each informer registered on settings
    """

    def get(self, request):
        """
        GET /informer/discover/
        """

        DJANGO_INFORMERS = getattr(settings, 'DJANGO_INFORMERS', ())

        informers = []

        for namespace, classname in DJANGO_INFORMERS:
            name = classname.replace('Informer', '').lower()
            urlname = 'informer-%s' % name

            informer = {
                'name': name,
                'url': reverse(urlname)
            }

            informers.append(informer)

        return JsonResponse({'result': informers})


class InformerView(View):
    """
    Get results from a specific Informer
    """

    def get(self, request, namespace, classname):
        """
        GET /informer/:name/
        """

        result = {
            'name': classname,
            'operational': None,
            'measures': [],
            'message': 'pending'
        }

        try:
            cls = BaseInformer.get_class(namespace, classname)

            informer = cls()

            measures = cls.get_measures()
            measures = [measure.replace('check_', '') for measure in measures]

            operational, message = informer.check_availability()

            result['operational'] = operational
            result['message'] = message
            result['measures'] = measures
        except InformerException as error:
            result['message'] = '%s' % error

        return JsonResponse(result)


class MeasureView(View):
    """
    Get result from a specific measure
    """

    def get(self, request, namespace, classname, measure):
        """
        GET /informer/:informer/:measure/
        """
        try:
            indicator = classname.replace('Informer', '')
            fields = ['id', 'indicator', 'measure', 'date', 'value']

            data = Raw.objects.filter(
                indicator=indicator, measure=measure).values(*fields)

            result = list(data)
        except Exception as error:
            return JsonResponse({'result': '%s' % error})
        else:
            return JsonResponse({'result': result})
