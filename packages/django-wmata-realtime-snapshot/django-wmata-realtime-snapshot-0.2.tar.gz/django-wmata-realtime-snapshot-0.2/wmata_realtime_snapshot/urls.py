from django.conf.urls import patterns, url

# "All" or "A01,B02,C03,..."
station_csv_regex = "All|([A-Z]\d+\d+)(,[A-Z]\d+\d+)*)"

urlpatterns = patterns('wmata_realtime_snapshot.views',
                       url(r'^StationPrediction.svc/json/GetPrediction/(?P<codes>(%s)$' % station_csv_regex, 'wmata_realtime_json_view'),
                       url(r'^StationPrediction.svc/GetPrediction/(?P<codes>(%s)$' % station_csv_regex, 'wmata_realtime_xml_view'),
                      )
