import json
import xml.etree.ElementTree as ET
import copy
from django.conf import settings

json_file = getattr(settings, 'WMATA_JSON_DUMP', None)
xml_file = getattr(settings, 'WMATA_XML_DUMP', None)

class RealTime(object):

    def __init__(self):
        ET.register_namespace('', 'http://www.wmata.com')
        ET.register_namespace('i', 'http://www.w3.org/2001/XMLSchema-instance')
        self.json_doc = json.load(open(json_file)) if json_file else None
        self.xml_doc = ET.parse(xml_file) if xml_file else None

    def get_realtime_xml(self, stations):
        if self.xml_doc is None:
            return ET.fromstring('<Error>No XML resource has been defined. Please read the installation instructions.</Error>')

        if stations == ['All']:
            return self.xml_doc.getroot()

        new_tree = copy.deepcopy(self.xml_doc.getroot())
        trains = new_tree[0]
        for item in trains[:]:
            code = item.find('{http://www.wmata.com}LocationCode')
            if code is None or code.text not in stations:
              trains.remove(item)
        return new_tree

    def get_realtime_json(self, stations):
        if self.json_doc is None:
            return {"Error": "No JSON resource has been defined. Please read the installation instructions."}

        if stations == ['All']:
            return self.json_doc

        trains = [t for t in self.json_doc['Trains'] if t['LocationCode'] in stations]
        return {'Trains': trains}
