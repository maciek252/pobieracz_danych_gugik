import urllib
import requests
import os, time
import xml.etree.ElementTree as ET
from time import sleep
from lxml import etree
import urllib3
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject, QgsDataProvider, QgsVectorFileWriter, QgsCoordinateTransformContext
import re
from owslib.wfs import WebFeatureService
# import urllib2
from xml.etree import ElementTree
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings


class WfsEgib:
    def save_xml(self, folder, url):

        # r = requests.get(url)
        # root = etree.parse(r, etree.HTMLParser())
        # print(root)

        try:
            r = requests.get(url)
            # root = etree.parse(r, etree.HTMLParser())
            # print(etree.tostring(root))
            if str(r.status_code) == '404':
                print("Plik nie istnieje " + url)
            else:
                with open(folder + 'egib_wfs.xml', 'wb') as f:
                    f.write(r.content)
        except requests.exceptions.SSLError:
            disable_warnings(InsecureRequestWarning)
            print("Weryfikacja certyfikatu strony nie powiodła się. Nie można uzyskać lokalnego certyfikatu wystawcy.")
            print("Czy chcesz pobrać dane na własną odpowiedzialność?")
            r = requests.get(url, verify=False)
            if str(r.status_code) == '404':
                print("Plik nie istnieje " + url)
            else:
                with open(folder + 'egib_wfs.xml', 'wb') as f:
                    f.write(r.content)
        except IOError:
            print("Błądddddd zapisu pliku " + url)
        except requests.exceptions.ConnectionError:
            print("cos nie tak z requests " + url)

    def praca_na_xml(self, folder, url, teryt):
        self.save_xml(folder, url)

        # print("url2: ", url)
        # data = open(folder + 'egib_wfs.xml', "r")
        # data = data.read()
        # string = '<Name>(.+?)</Name>'
        # for word in data.split():
        #     # print("word: ", word)
        #     layer = re.search(string, word)
        #     # print("layer: ", layer)
        #     if layer is not None:
        #         uri = f"{url.split('?')[0]}?request=getFeature&version=1.1.0&service=WFS&typename={layer.group(1)}"
        #         print("layer_uri: ", uri)
        #         layer = QgsVectorLayer(uri, teryt+"_"+layer.group(1), "WFS")
        #         QgsProject.instance().addMapLayer(layer)

        ns = etree.parse(folder + 'egib_wfs.xml')

        # pi = ns.xpath("//processing-instruction()")[0]
        # ns = pi.parseXSL()
        ns = ns.getroot().nsmap
        # ns['xmlns:xlink'] = ns.pop('xlink')
        if None in ns:
            ns['xmlns'] = ns.pop(None)
        print(ns)

        tree = ET.parse(folder + 'egib_wfs.xml')
        root = tree.getroot()

        print(root)
        name_layers = []
        setWgs84BoundingBoxEast = []
        setWgs84BoundingBoxSouth = []
        setWgs84BoundingBoxWest = []
        setWgs84BoundingBoxNorth  = []

        if 'ewns' in root.find('./xmlns:FeatureTypeList/xmlns:FeatureType/xmlns:Name', ns).text:
            print("znalaziono ewns")
            ns['ewns'] = 'http://xsd.geoportal2.pl/ewns'
            print("ewns: ", root.find('./xmlns:FeatureTypeList/xmlns:FeatureType/xmlns:Name', ns))

        for child in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
            name = child.find('xmlns:Name', ns)
            print("name.text: ", name.text)
            # print("name.text: ", name.text)
            name_layers.append(name.text)
            print("name_layers: ", name_layers)

        if 'ewns:' in name_layers[0]:
            prefix = 'ewns'
        elif 'ms:' in name_layers[0]:
            prefix = 'ms'
        # elif 'wms_chorzow_dzialki' in name_layers[0]:
        #     prefix = 'wms_chorzow_dzialki'
        else:
            prefix = None

        print("prefix: ", prefix)

        print('ns: ', ns)

        for bbox in root.findall('./xmlns:WGS84BoundingBox', ns):
            for lowercorner in bbox.findall('./xmlns:LowerCorner', ns):
                setWgs84BoundingBoxEast.append(lowercorner.text.split(' ')[0])
                setWgs84BoundingBoxSouth.append(lowercorner.text.split(' ')[1])
            for uppercorner in bbox.findall('./xmlns:UpperCorner', ns):
                setWgs84BoundingBoxWest.append(uppercorner.text.split(' ')[0])
                setWgs84BoundingBoxNorth.append(uppercorner.text.split(' ')[1])

        # print("setWgs84BoundingBoxNorth: ", setWgs84BoundingBoxNorth)

        # for layer in name_layers:
        #     if 'ewns' in layer:
        #         uri = f"{url.split('?')[0]}?request=getFeature&version=1.1.0&service=WFS&typename={layer}"
        #         print("layer_uri: ", uri)
        #         vlayer = QgsVectorLayer(uri, teryt + "_" + layer, "WFS")
        #         QgsProject.instance().addMapLayer(vlayer)
        #         print("path: ", folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')
        #         QgsVectorFileWriter.writeAsVectorFormat(vlayer, (folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml').absoluteFilePath(), 'utf-8', layer.crs().isGeographic(), driverName='GML')
        #         # ', "UTF-8", "epsg:2180"
        #         return name_layers is None
        #     else:
        #         return name_layers





        # print('ns', ns)

        # name_layers = []
        # for child in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
        #     name = child.find('xmlns:Name', ns)
        #     name_layers.append(name.text)

        # name_layers = []
        # for child in root.findall('./xmlns:FeatureTypeList/xmlns:FeatureType', ns):
        #     name = child.find('xmlns:Name', ns)
        #     name_layers.append(name.text)

        # dla powiatów, które posiadają zdefiniowany prefix wfs
        # for child in root.findall('./wfs:FeatureTypeList/wfs:FeatureType', ns):
        #     name = child.find('wfs:Name', ns)
        #     name_layers.append(name.text)

        # print(root)
        # for child in root.findall('wfs:FeatureTypeList', ns):
        #     print(child)
        #     for featureType in child.findall('wfs:FeatureType', ns):
        #         print(featureType)
        #         name = featureType.find('wfs:Name', ns)
        #         name_layers.append(name.text)

        return name_layers, setWgs84BoundingBoxEast, setWgs84BoundingBoxSouth, setWgs84BoundingBoxWest, setWgs84BoundingBoxNorth, prefix

    def save_gml(self, folder, url, teryt):
        # self.praca_na_xml(folder, url, teryt)
        name_layers, setWgs84BoundingBoxEast, setWgs84BoundingBoxSouth, setWgs84BoundingBoxWest, setWgs84BoundingBoxNorth, prefix = self.praca_na_xml(folder, url, teryt)
        print("prefix: ", prefix)
        # if name_layers is None:
        #     return 0

        print(name_layers)
        url_main = url.split('?')[0]

        for layer in name_layers:
            # if len(setWgs84BoundingBoxEast) < 1:
            if prefix == 'ewns':
                url_gml = url_main + f"?service=WFS&request=GetFeature&version=2.0.0&srsName=urn:ogc:def:crs:EPSG::2180&typeNames={layer}&namespaces=xmlns(ewns,http://xsd.geoportal2.pl/ewns)"
            elif prefix == 'ms':
                url_gml = url_main + f"?service=WFS&request=GetFeature&version=1.0.0&srsName=urn:ogc:def:crs:EPSG::2180&typeNames={layer}&namespaces=xmlns(ms,http%3A%2F%2Fmapserver.gis.umn.edu%2Fmapserver)"
            else:
                url_gml = url_main + '?request=getFeature&version=2.0.0&service=WFS&srsName=urn:ogc:def:crs:EPSG::2180&typename=' + layer
            # else:
            #     if prefix == 'ewns':
            #         url_gml = url_main + f"?service=WFS&request=GetFeature&version=1.0.0&srsName=urn:ogc:def:crs:EPSG::4326&typeNames={layer}&namespaces=xmlns(ewns,http://xsd.geoportal2.pl/ewns)" + '&bbox=' + setWgs84BoundingBoxEast + ',' + setWgs84BoundingBoxSouth + ',' + setWgs84BoundingBoxWest + ',' + setWgs84BoundingBoxNorth
            #     elif prefix == 'ms':
            #         url_gml = url_main + f"?service=WFS&request=GetFeature&version=2.0.0&srsName=urn:ogc:def:crs:EPSG::4326&typeNames={layer}&namespaces=xmlns(ms,http://mapserver.gis.umn.edu/mapserver)" + '&bbox=' + setWgs84BoundingBoxEast + ',' + setWgs84BoundingBoxSouth + ',' + setWgs84BoundingBoxWest + ',' + setWgs84BoundingBoxNorth
            #     else:
            #         url_gml = url_main + '?request=getFeature&version=2.0.0&service=WFS&typename=' + layer + '&bbox=' + setWgs84BoundingBoxEast + ',' + setWgs84BoundingBoxSouth + ',' + setWgs84BoundingBoxWest + ',' + setWgs84BoundingBoxNorth

            print(url_gml)
            sleep(1)
            try:
                r = requests.get(url_gml)
                # while True:

                if str(r.status_code) == '404':
                    print("Plik nie istnieje" + teryt + '_' + layer)
                else:
                    with open(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml', 'wb') as f:
                        f.write(r.content)
                        print(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')
                    size = os.path.getsize(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')
                    if size <= 1000:  # 341:
                        print('Za mały rozmiar pliku : 1kb lub 0kb')

            except requests.exceptions.SSLError:
                disable_warnings(InsecureRequestWarning)
                print("Weryfikacja certyfikatu strony nie powiodła się. Nie można uzyskać lokalnego certyfikatu wystawcy.")
                print("Czy chcesz pobrać dane na własną odpowiedzialność?")
                r = requests.get(url, verify=False)
                if str(r.status_code) == '404':
                    print("Plik nie istnieje" + teryt + '_' + layer)
                else:
                    with open(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml', 'wb') as f:
                        f.write(r.content)
                    size = os.path.getsize(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')
                    if size <= 1000:  # 341:
                        print('Za mały rozmiar pliku : 1kb lub 0kb')

            except IOError:
                print("Błądąąąą zapisu pliku" + teryt + '_' + layer)
                print(folder)
                print(folder + teryt + '_' + layer.split(':')[-1] + '_egib_wfs_gml.gml')

                # uri = url_gml
                # layer = QgsVectorLayer(uri, layer, "WFS")
                # QgsProject.instance().addMapLayer(layer)
                # aa = str(layer.split(':')[-1])
                # QgsVectorFileWriter.writeAsVectorFormat(layer, str(folder + teryt + '_' + aa + '_egib_wfs_gml.gml'), 'utf-8', driverName='GML')

            except requests.exceptions.ConnectionError:
                print("Błąd requests dla warstwy " + teryt + '_' + layer)

    def main(self, teryt, wfs, folder):

        num_error_exists_file = 0
        try:
            path = os.path.join(folder, teryt + "_wfs_egib/")
            os.mkdir(path)
        except FileExistsError:
            while FileExistsError is True:
                num_error_exists_file = num_error_exists_file + 1
                path = os.path.join(folder, teryt + "_wfs_egib_" + str(num_error_exists_file) + "/")
                os.mkdir(path)
        print("Directory '% s' created" % path)
        self.save_gml(path, wfs, teryt)

if __name__ == '__main__':
    wfsEgib = WfsEgib()
    dictionary1 = {'1206': 'https://wms.powiat.krakow.pl:1518/iip/ows?service=WFS&request=GetCapabilities',
                   '2471': 'https://wms.sip.piekary.pl/piekary-egib?service=WFS&request=GetCapabilities',
                   '2061': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2061?service=WFS&request=GetCapabilities',
                   '0213': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0213?service=WFS&request=GetCapabilities',
                   '2402': 'https://bielski-wms.webewid.pl/us/wfs/sip?service=WFS&request=GetCapabilities',
                   '0220': 'https://trzebnicki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1811': 'https://mielec.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3003': 'https://wms.geodezjagniezno.pl/gniezno-egib?service=WFS&request=GetCapabilities',
                   '3030': 'https://wms.wrzesnia.powiat.pl/wrzesnia-egib?service=WFS&request=GetCapabilities',
                   '1465': 'https://wms2.um.warszawa.pl/geoserver/wfs/wms?service=WFS&request=GetCapabilities',
                   '0809': 'https://giportal.powiat-zielonogorski.pl/zielonagora-egib?service=WFS&request=GetCapabilities',
                   '1437': 'http://zuromin-powiat.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1606': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1606?service=WFS&request=GetCapabilities',
                   '2403': 'https://cieszyn.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2002': 'https://bialystok.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2601': 'https://geodezja.powiat.busko.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0464': 'https://geoportal.wloclawek.eu/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0808': 'https://giportal2.powiat.swiebodzin.pl/swiebodzin-egib?service=WFS&request=GetCapabilities',
                   '0216': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0216?service=WFS&request=GetCapabilities',
                   '2472': 'https://rudaslaska.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3019': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3019?service=WFS&request=GetCapabilities',
                   '1661': 'https://wms.um.opole.pl/opole-egib?service=WFS&request=GetCapabilities',
                   '1809': 'https://lubaczow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1817': 'https://sanocki.webewid.pl:4443/us/wfs/sip?service=WFS&request=GetCapabilities',
                   '1814': 'https://sip.powiatprzeworsk.pl:4443/us/wfs/sip/?service=WFS&request=GetCapabilities',
                   '1802': 'https://brzozowski.webewid.pl:4443/us/wfs/sip/?service=WFS&request=GetCapabilities',
                   '1601': 'https://imapa.brzeg-powiat.pl/brzeg-egib?service=WFS&request=GetCapabilities',
                   '1605': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1605?service=WFS&request=GetCapabilities',
                   '3002': 'https://wms.czarnkowsko-trzcianecki.pl/czarnkowskotrzcianecki-egib?service=WFS&request=GetCapabilities',
                   '0811': 'https://zary.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1861': 'https://krosno-wms.webewid.pl/us/wfs/sip?service=WFS&request=GetCapabilities',
                   '1609': 'https://geodezja.powiatopolski.pl/ggp?service=WFS&request=GetCapabilities',
                   '1604': 'http://185.108.68.134/kluczbork-egib?service=WFS&request=GetCapabilities',
                   '1813': 'https://powiat-przemysl.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0462': 'http://geoportal.grudziadz.pl/ggp?service=WFS&request=GetCapabilities',
                   '2408': 'https://mapa.mikolowski.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2479': 'http://wfs.geoportal.zory.pl/gugik?service=WFS&request=GetCapabilities',
                   '2469': 'https://services.gugik.gov.pl/cgi-bin/2469?service=WFS&request=GetCapabilities',
                   '1815': 'https://spropczyce.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1819': 'https://strzyzowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1608': 'https://ikerg.powiatoleski.pl/olesno-egib?service=WFS&request=GetCapabilities',
                   '1818': 'https://stalowawola.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2661': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2661?service=WFS&request=GetCapabilities',
                   '1801': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1801?service=WFS&request=GetCapabilities',
                   '0410': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0410?service=WFS&request=GetCapabilities',
                   '1812': 'https://powiat-nisko.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0403': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0403?service=WFS&request=GetCapabilities',
                   '0461': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0461?service=WFS&request=GetCapabilities',
                   '0414': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0414?service=WFS&request=GetCapabilities',
                   '2213': 'https://wms.powiatstarogard.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1602': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1602?service=WFS&request=GetCapabilities',
                   '0419': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0419?service=WFS&request=GetCapabilities',
                   '0405': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0405?service=WFS&request=GetCapabilities',
                   '1820': 'https://tarnobrzeski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0261': 'http://geoportal.jeleniagora.pl/ggp?service=WFS&request=GetCapabilities',
                   '0416': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0416?service=WFS&request=GetCapabilities',
                   '3006': 'https://services.gugik.gov.pl/cgi-bin/3006?service=WFS&request=GetCapabilities',
                   '0411': 'https://radziejow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3025': 'https://wms.powiatsredzki.pl/srodawlkp-egib?service=WFS&request=GetCapabilities',
                   '1863': 'https://osrodek.erzeszow.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0408': 'https://lipno.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2812': 'https://powiat-nowomiejski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0463': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0463?service=WFS&request=GetCapabilities',
                   '1804': 'https://jaroslawski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2607': 'https://ostrowiec.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1810': 'https://lancut.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2611': 'https://starachowice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2803': 'https://powiatdzialdowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0412': 'https://rypin.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0404': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0404?service=WFS&request=GetCapabilities',
                   '0417': 'https://wabrzezno.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0407': 'https://inowroclawski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1607': 'https://wms-egib.powiat.nysa.pl/nysa-egib?service=WFS&request=GetCapabilities',
                   '3020': 'https://wms.geo.net.pl/pleszew-egib?service=WFS&request=GetCapabilities',
                   '1808': 'https://lezajsk.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0206': 'https://wms.podgik.jgora.pl/jeleniagora-egib?service=WFS&request=GetCapabilities',
                   '2463': 'https://e-odgik.chorzow.eu/arcgis/services/chorzow_egib/serwer?service=WFS&request=GetCapabilities',
                   '1610': 'https://ikerg2.powiatprudnicki.pl/prudnik-egib?service=WFS&request=GetCapabilities',
                   '1412': 'https://wms.epodgik.pl/cgi-bin/minsk?service=WFS&request=GetCapabilities',
                   '3021': 'https://ikerg.podgik.poznan.pl/wms-poznanski?service=WFS&request=GetCapabilities',
                   '3215': 'https://szczecinecki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '0409': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0409?service=WFS&request=GetCapabilities',
                   '2811': 'https://powiatnidzicki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0862': 'https://gis.um.zielona-gora.pl/arcgis/services/zielona_gora_egib/serwer?service=WFS&request=GetCapabilities',
                   '1805': 'https://jasielski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2605': 'https://konskie.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2461': 'https://ikerg.bielsko-biala.pl/cgi-bin/bielsko?service=WFS&request=GetCapabilities',
                   '1806': 'https://kolbuszowa.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1816': 'https://powiatrzeszowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0210': 'https://iegib.powiatluban.pl/luban-egib?service=WFS&request=GetCapabilities',
                   '1611': 'https://mapy.powiatstrzelecki.pl/ggp?service=WFS&request=GetCapabilities',
                   '1204': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1204?service=WFS&request=GetCapabilities',
                   '0406': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0406?service=WFS&request=GetCapabilities',
                   '0402': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0402?service=WFS&request=GetCapabilities',
                   '3061': 'https://ikerg.um.kalisz.pl/kalisz-egib?service=WFS&request=GetCapabilities',
                   '1421': 'https://wms.epodgik.pl/cgi-bin/pruszkow?service=WFS&request=GetCapabilities',
                   '0663': 'https://gis.lublin.eu/opendata/wfs?service=WFS&request=GetCapabilities',
                   '1807': 'https://krosnienski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2205': 'https://kartuski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2808': 'https://powiatketrzynski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0604': 'https://hrubieszow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1202': 'https://brzesko.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0661': 'https://bialapodlaska.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2411': 'https://raciborz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2263': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2263?service=WFS&request=GetCapabilities',
                   '2477': 'http://sit.umtychy.pl/isdp/gs/ows/default/wfs4?service=WFS&request=GetCapabilities',
                   '0223': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0223?service=WFS&request=GetCapabilities',
                   '0219': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0219?service=WFS&request=GetCapabilities',
                   '1862': 'https://przemysl.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0264': 'https://iwms.zgkikm.wroc.pl/wroclaw-egib?service=WFS&request=GetCapabilities',
                   '1212': 'https://olkuski.webewid.pl:4434/iip/ows?service=WFS&request=GetCapabilities',
                   '3064': 'https://portal.geopoz.poznan.pl/wmsegib?service=WFS&request=GetCapabilities',
                   '0262': 'https://mapy.legnica.eu/mapserv/262011/geoportal/?service=WFS&request=GetCapabilities',
                   '1219': 'https://wielicki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1006': 'https://lodzkiwschodni.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0215': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0215?service=WFS&request=GetCapabilities',
                   '1419': 'https://powiat-plock.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1015': 'https://powiat-skierniewice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2814': 'https://powiatolsztynski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1001': 'http://belchatow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1218': 'https://wadowicki.webewid.pl:20443/iip/ows?service=WFS&request=GetCapabilities',
                   '2815': 'https://ostroda.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2806': 'https://wms.epodgik.pl/cgi-bin/gizycko?service=WFS&request=GetCapabilities',
                   '0418': 'https://wloclawek.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0614': 'https://pulawy.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2817': 'https://szczytno.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3213': 'https://slawienski.webewid.pl:4443/iip/ows?service=WFS&request=GetCapabilities',
                   '3001': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3001?service=WFS&request=GetCapabilities',
                   '0804': 'http://212.109.136.187/nowasol-egib?service=WFS&request=GetCapabilities',
                   '2818': 'https://powiatgoldap.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1203': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1203?service=WFS&request=GetCapabilities',
                   '2810': 'https://wms.epodgik.pl/cgi-bin/mragowo?service=WFS&request=GetCapabilities',
                   '2014': 'https://powiatzambrowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2807': 'https://ilawa.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2805': 'https://powiatelk.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2861': 'http://wms.umelblag.pl/elblag-wms?service=WFS&request=GetCapabilities',
                   '2819': 'https://wms.epodgik.pl/cgi-bin/wegorzewo?service=WFS&request=GetCapabilities',
                   '0225': 'https://iegib.powiat.zgorzelec.pl/zgorzelec-egib?service=WFS&request=GetCapabilities',
                   '0608': 'https://powiatlubartowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2606': 'https://opatow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2802': 'https://powiat-braniewo.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2414': 'https://sbl.webewid.pl:8443/us/wfs/sip?service=WFS&request=GetCapabilities',
                   '3218': 'https://wms.powiatlobeski.pl/lobez-egib?service=WFS&request=GetCapabilities',
                   '3204': 'https://goleniowski.webewid.pl:6443/iip/ows?service=WFS&request=GetCapabilities',
                   '0413': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0413?service=WFS&request=GetCapabilities',
                   '2801': 'https://powiatbartoszyce.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2476': 'https://swietochlowice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0610': 'https://leczna.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2813': 'https://olecko.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2462': 'https://sitplan.um.bytom.pl/isdp/gs/ows/wfs?service=WFS&request=GetCapabilities',
                   '3217': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3217?service=WFS&request=GetCapabilities',
                   '2262': 'https://pc73.miasto.gdynia.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2212': 'https://wms.powiat.slupsk.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2465': 'https://geoportal-wms.dg.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '0662': 'https://wms.epodgik.pl/cgi-bin/mchelm?service=WFS&request=GetCapabilities',
                   '3203': 'https://drawski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2610': 'https://services.gugik.gov.pl/cgi-bin/2610?service=WFS&request=GetCapabilities',
                   '1004': 'https://leczycki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0609': 'https://powiatlubelski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2809': 'https://powiatlidzbarski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0612': 'https://opolelubelskie.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0401': 'https://mapa.aleksandrow.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1217': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1217?service=WFS&request=GetCapabilities',
                   '1603': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1603?service=WFS&request=GetCapabilities',
                   '0212': 'https://ikerg.powiatlwowecki.pl/lwowekslaski-egib?service=WFS&request=GetCapabilities',
                   '3214': 'https://ikerg2.powiatstargardzki.eu/stargard-egib?service=WFS&request=GetCapabilities',
                   '3201': 'https://bialogardzki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2609': 'https://sandomierz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3209': 'https://koszalinski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '3009': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3009?service=WFS&request=GetCapabilities',
                   '3263': 'http://77.88.191.50/swinoujscie?service=WFS&request=GetCapabilities',
                   '0207': 'https://wms.kamienna-gora.pl/kamiennagora-egib?service=WFS&request=GetCapabilities',
                   '1408': 'https://powiat-legionowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3212': 'https://ikerg.pyrzyce.pl/pyrzyce-egib?service=WFS&request=GetCapabilities',
                   '1213': 'https://oswiecimski.webewid.pl:4422/iip/ows?service=WFS&request=GetCapabilities',
                   '1432': 'https://wms.pwz.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '3262': 'https://wms.e-osrodek.szczecin.pl/szczecin-egib?service=WFS&request=GetCapabilities',
                   '0201': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0201?service=WFS&request=GetCapabilities',
                   '2409': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2409?service=WFS&request=GetCapabilities',
                   '0222': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0222?service=WFS&request=GetCapabilities',
                   '0806': 'https://fsd.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0810': 'https://zaganski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2467': 'https://jastrzebie.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3013': 'https://leszczynski.webewid.pl:543/iip/ows?service=WFS&request=GetCapabilities',
                   '0801': 'https://powiatgorzowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3202': 'https://ikerg.geopowiatchoszczno.pl/choszczno-egib?service=WFS&request=GetCapabilities',
                   '1463': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1463?service=WFS&request=GetCapabilities'}
    dictionary2 = {'3018': 'https://wms.spostrzeszow.pl/ostrzeszow-egib?service=WFS&request=GetCapabilities',
                   '3017': 'https://ikerg.powiat-ostrowski.pl/ostrow-egib?service=WFS&request=GetCapabilities',
                   '3208': 'https://kolobrzeski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '0606': 'https://powiatkrasnostawski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3014': 'https://wms.epodgik.pl/cgi-bin/miedzychod?service=WFS&request=GetCapabilities',
                   '1061': 'https://mapa.lodz.pl/OGC/LODZ?service=WFS&request=GetCapabilities',
                   '0226': 'https://wms.powiat-zlotoryja.pl/zlotoryja-egib?service=WFS&request=GetCapabilities',
                   '1404': 'https://gostynin.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3022': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3022?service=WFS&request=GetCapabilities',
                   '2413': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2413?service=WFS&request=GetCapabilities',
                   '3062': 'https://ikerg.kosit.konin.eu/konin-egib?service=WFS&request=GetCapabilities',
                   '1864': 'https://tarnobrzeg.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3010': 'https://konin.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3012': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3012?service=WFS&request=GetCapabilities',
                   '0620': 'https://powiatzamojski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3007': 'https://kalisz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3029': 'https://ikerg.powiatwolsztyn.pl/wolsztyn-egib?service=WFS&request=GetCapabilities',
                   '1427': 'https://sierpc.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1428': 'https://sochaczew.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2214': 'https://wms.powiat.tczew.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '3023': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3023?service=WFS&request=GetCapabilities',
                   '2478': 'http://siot.um.zabrze.pl/arcgis/services/zabrze_egib/serwer?service=WFS&request=GetCapabilities',
                   '2466': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2466?service=WFS&request=GetCapabilities',
                   '3024': 'https://wms.szamotuly.com.pl/szamotuly-egib?service=WFS&request=GetCapabilities',
                   '0605': 'https://janow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1803': 'https://debica.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2604': 'https://geoportal.powiat.kielce.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3026': 'http://77.65.26.91/srem-egib?service=WFS&request=GetCapabilities',
                   '3027': 'https://iegib.powiat.turek.pl/cgi-bin/turek_egib?service=WFS&request=GetCapabilities',
                   '3005': 'http://185.209.71.51/grodziskwlkp-egib?service=WFS&request=GetCapabilities',
                   '3015': 'https://wms.powiatnowotomyski.pl/nowytomysl-egib?service=WFS&request=GetCapabilities',
                   '0209': 'https://legnicki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2473': 'https://services.gugik.gov.pl/cgi-bin/2473?service=WFS&request=GetCapabilities',
                   '2612': 'https://staszow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1438': 'https://wms.epodgik.pl/cgi-bin/zyrardow?service=WFS&request=GetCapabilities',
                   '3261': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3261?service=WFS&request=GetCapabilities',
                   '2862': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2862?service=WFS&request=GetCapabilities',
                   '2202': 'https://chojnicki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '3063': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3063?service=WFS&request=GetCapabilities',
                   '2474': 'https://siemianowice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1414': 'https://nowodworski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1420': 'https://plonski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1422': 'https://przasnysz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1005': 'https://lowicz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0218': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0218?service=WFS&request=GetCapabilities',
                   '1435': 'https://powiat-wyszkowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1405': 'https://grodzisk.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1821': 'https://lesko.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0203': 'https://glogow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1063': 'https://skierniewice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1007': 'https://opoczno.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0202': 'https://geoportal.pow.dzierzoniow.pl/ggp?service=WFS&request=GetCapabilities',
                   '3031': 'https://ikerg.zlotow-powiat.pl/cgi-bin/zlotow-darmowe?service=WFS&request=GetCapabilities',
                   '2210': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2210?service=WFS&request=GetCapabilities',
                   '2415': 'https://sip.powiatwodzislawski.pl:8080/wodzislaw-egib?service=WFS&request=GetCapabilities',
                   '2009': 'https://sejny.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1464': 'https://siedlce.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1424': 'https://powiatpultuski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1425': 'https://radom.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3008': 'https://ikerg.powiatkepno.pl/kepno-egib?service=WFS&request=GetCapabilities',
                   '3028': 'http://ikerg.wagrowiec.pl/cgi-bin/wagrowiec-egib?service=WFS&request=GetCapabilities',
                   '2816': 'https://powiatpiski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0208': 'https://geoportal.powiat.klodzko.pl/ggp?service=WFS&request=GetCapabilities',
                   '3210': 'http://213.76.166.254/mysliborz-egib?service=WFS&request=GetCapabilities',
                   '0211': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0211?service=WFS&request=GetCapabilities',
                   '0205': 'https://jawor.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1416': 'https://ostrowmaz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2264': 'https://wms.um.sopot.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '3016': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3016?service=WFS&request=GetCapabilities',
                   '3004': 'http://77.65.50.130/gostyn-egib?service=WFS&request=GetCapabilities',
                   '1205': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1205?service=WFS&request=GetCapabilities',
                   '0214': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0214?service=WFS&request=GetCapabilities',
                   '2215': 'https://wms.epodgik.pl/cgi-bin/wejherowo?service=WFS&request=GetCapabilities',
                   '3211': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3211?service=WFS&request=GetCapabilities',
                   '0607': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0607?service=WFS&request=GetCapabilities',
                   '3216': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/3216?service=WFS&request=GetCapabilities',
                   '1409': 'https://powiatlipsko.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0224': 'https://zabkowicki.webewid.pl:444/iip/ows?service=WFS&request=GetCapabilities',
                   '2470': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2470?service=WFS&request=GetCapabilities',
                   '3206': 'https://gryfinski.webewid.pl:4439/iip/ows?service=WFS&request=GetCapabilities',
                   '2464': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2464?service=WFS&request=GetCapabilities',
                   '1411': 'https://makow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2602': 'https://jedrzejow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2006': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2006?service=WFS&request=GetCapabilities',
                   '0221': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0221?service=WFS&request=GetCapabilities',
                   '2013': 'https://wysokomazowiecki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1436': 'https://zwolenpowiat.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0603': 'https://chelmski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1207': 'https://limanowski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '2406': 'https://mapy.powiatklobucki.pl/ggp?service=WFS&request=GetCapabilities',
                   '2261': 'https://ewid-wms.gdansk.gda.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1417': 'https://powiat-otwocki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3207': 'https://ikerg.powiatkamienski.pl/kamien?service=WFS&request=GetCapabilities',
                   '0861': 'https://geoportal.wms.um.gorzow.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1423': 'https://przysucha.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1462': 'https://wms-ggk.plock.eu:4443/iip/ows?service=WFS&request=GetCapabilities',
                   '2003': 'https://powiatbielski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1418': 'https://wms.epodgik.pl/cgi-bin/piaseczno?service=WFS&request=GetCapabilities',
                   '1261': 'https://msip.um.krakow.pl/arcgis/services/ZSOZ/EGIB_udostepnianie/MapServer/WFSServer?service=WFS&request=GetCapabilities',
                   '0602': 'https://bilgorajski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1016': 'https://powiat-tomaszowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0204': 'https://gora.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0217': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0217?service=WFS&request=GetCapabilities',
                   '2407': 'http://83.17.150.14/lubliniec-egib?service=WFS&request=GetCapabilities',
                   '2804': 'https://ikerg.powiat.elblag.pl/elblaski-egib?service=WFS&request=GetCapabilities',
                   '2010': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2010?service=WFS&request=GetCapabilities',
                   '1008': 'https://pabianice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2063': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2063?service=WFS&request=GetCapabilities',
                   '2004': 'https://starostwograjewo.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1410': 'https://losice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3205': 'https://ikerg.podgikgryfice.pl/gryfice-egib?service=WFS&request=GetCapabilities',
                   '2011': 'https://powiatsokolski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2008': 'https://monki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0664': 'https://zamosc.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2401': 'https://ikerg.powiat.bedzin.pl/bedzin-egib?service=WFS&request=GetCapabilities',
                   '1214': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1214?service=WFS&request=GetCapabilities',
                   '2005': 'https://hajnowka.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1403': 'https://wms.epodgik.pl/cgi-bin/garwolin?service=WFS&request=GetCapabilities',
                   '0415': 'https://torunski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1401': 'https://bialobrzegi.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0611': 'https://powiatlukowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1426': 'https://powiatsiedlecki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1209': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1209?service=WFS&request=GetCapabilities',
                   '2012': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2012?service=WFS&request=GetCapabilities',
                   '0803': 'https://powiat-miedzyrzecki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0812': 'https://wschowa.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2203': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2203?service=WFS&request=GetCapabilities',
                   '0616': 'https://ryki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2608': 'https://pinczow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0615': 'https://powiatradzynski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1430': 'https://szydlowiecpowiat.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1413': 'https://powiatmlawski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1215': 'https://powiatsuski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1019': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1019?service=WFS&request=GetCapabilities',
                   '2209': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2209?service=WFS&request=GetCapabilities',
                   '0807': 'https://sulecin.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1003': 'https://lask.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1010': 'https://piotrkow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1013': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1013?service=WFS&request=GetCapabilities',
                   '0601': 'https://powiatbialski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0613': 'http://parczew.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2206': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2206?service=WFS&request=GetCapabilities',
                   '2208': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2208?service=WFS&request=GetCapabilities',
                   '1415': 'https://powiatostrolecki.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0619': 'https://wms.epodgik.pl/cgi-bin/wlodawa?service=WFS&request=GetCapabilities',
                   '1406': 'https://grojec.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1211': 'https://nowotarski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0617': 'https://powiatswidnik.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2211': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2211?service=WFS&request=GetCapabilities',
                   '1062': 'https://ikerg.piotrkow.pl/piotrkow-egib?service=WFS&request=GetCapabilities',
                   '1002': 'https://powiatkutno.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2207': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2207?service=WFS&request=GetCapabilities',
                   '1433': 'https://wms.epodgik.pl/cgi-bin/wegrow?service=WFS&request=GetCapabilities',
                   '2001': 'https://wms.epodgik.pl/cgi-bin/augustow?service=WFS&request=GetCapabilities',
                   '2216': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2216?service=WFS&request=GetCapabilities',
                   '2204': 'https://gdanski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1461': 'https://ostroleka.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1429': 'https://powiat-sokolowski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2404': 'https://czestochowa.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1012': 'https://radomszczanski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0265': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/0265?service=WFS&request=GetCapabilities',
                   '2603': 'https://kazimierzaw.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2405': 'https://gliwicki.webewid.pl:4443/iip/ows?service=WFS&request=GetCapabilities',
                   '2410': 'https://pszczynski-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1020': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1020?service=WFS&request=GetCapabilities',
                   '1262': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1262?service=WFS&request=GetCapabilities',
                   '1210': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1210?service=WFS&request=GetCapabilities',
                   '1402': 'https://ciechanow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1201': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1201?service=WFS&request=GetCapabilities',
                   '1009': 'https://pajeczno.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1011': 'https://poddebice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1407': 'https://kozienicepowiat.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '3011': 'https://iegib.powiatkoscian.pl/cgi-bin/koscian?service=WFS&request=GetCapabilities',
                   '1018': 'https://wieruszow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1263': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/1263?service=WFS&request=GetCapabilities',
                   '2412': 'https://services.gugik.gov.pl/cgi-bin/2412?service=WFS&request=GetCapabilities',
                   '0618': 'https://tomaszowlubelski.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2417': 'https://zywiecki-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1208': 'https://miechow.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2201': 'https://bytowski.webewid.pl:4433/iip/ows?service=WFS&request=GetCapabilities',
                   '2475': 'https://mapy.geoportal.gov.pl/wss/ext/PowiatoweBazyEwidencjiGruntow/2475?service=WFS&request=GetCapabilities',
                   '1021': 'https://brzeziny.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1014': 'https://sieradz.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '1434': 'https://wms.epodgik.pl/cgi-bin/wolomin?service=WFS&request=GetCapabilities',
                   '1216': 'https://webewid.powiat.tarnow.pl:20443/iip/ows?service=WFS&request=GetCapabilities',
                   '2468': 'https://jaworzno-wms.webewid.pl/iip/ows?service=WFS&request=GetCapabilities',
                   '1017': 'https://wielun.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '2613': 'https://wloszczowa.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0805': 'https://slubice.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities',
                   '0802': 'https://wms.powiatkrosnienski.pl/krosno-egib?service=WFS&request=GetCapabilities',
                   '2416': 'https://ikerg.zawiercie.powiat.pl/powiatzawiercianski-egib?service=WFS&request=GetCapabilities'}
    # dictionary = {'1206': 'https://wms.powiat.krakow.pl:1518/iip/ows?service=WFS&request=GetCapabilities', '2471': 'https://wms.sip.piekary.pl/piekary-egib?service=WFS&request=GetCapabilities'}
    # dictionary = {'1206': 'http://wfs.geoportal.zory.pl/gugik?service=WFS&request=GetCapabilities'}
    folder = "C:\wtyczka aktualizacja\probne/"
    # print(wfsEgib.main("1206", 'https://wms.powiat.krakow.pl:1518/iip/ows?service=WFS&request=GetCapabilities', folder))
    print(wfsEgib.main("2613", 'https://mielec.geoportal2.pl/map/geoportal/wfs.php?service=WFS&request=GetCapabilities', folder))
    # print(wfsEgib.main("2613", 'https://wms.powiatstarogard.pl/iip/ows?service=WFS&request=GetCapabilities', folder))

