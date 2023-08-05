from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page
from xml.etree import ElementTree
from .realtime import RealTime

realtime = RealTime()
timeout = getattr(settings, 'WMATA_REALTIME_CACHE_TIMEOUT', 60*30)

@cache_page(timeout)
def wmata_realtime_json_view(request, codes):
    result = realtime.get_realtime_json(codes.split(','))
    return JsonResponse(result)


@cache_page(timeout)
def wmata_realtime_xml_view(request, codes):
    result = realtime.get_realtime_xml(codes.split(','))
    return HttpResponse(ElementTree.tostring(result), content_type='application/xml')
