from qgis.core import QgsCoordinateReferenceSystem
import processing
from qgis.core import *

def pointTo2180(point, sourceCrs, project):
    """zamiana układu na 1992"""
    crsDest = QgsCoordinateReferenceSystem(2180)  # PL 1992
    xform = QgsCoordinateTransform(sourceCrs, crsDest, project)
    point1992 = xform.transform(point)
    return point1992

def createPointsFromPolygon(layer):
    ext = layer.extent()
    params = {
        'TYPE':0,
        # 'EXTENT': '749707.2763195293,756551.6130037877,374593.57733500504,378804.6037195156 [EPSG:2180]',
        'EXTENT':ext,
        'HSPACING':1000,
        'VSPACING':1000,
        'HOVERLAY':0,
        'VOVERLAY':0,
        'CRS':QgsCoordinateReferenceSystem('EPSG:2180'),
        'OUTPUT':'TEMPORARY_OUTPUT'
    }
    proc = processing.run("native:creategrid", params)
    punkty = proc['OUTPUT']

    params = {
        'INPUT': punkty,
        'OVERLAY': layer,
        'OUTPUT': 'TEMPORARY_OUTPUT'}

    proc = processing.run("native:clip", params)
    punkty = proc['OUTPUT']

    params = {
        'INPUT': punkty,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    proc = processing.run("native:multiparttosingleparts", params)
    punkty = proc['OUTPUT']

    punktyList = []
    for feat in punkty.getFeatures():
        punktyList.append(feat.geometry().asPoint())

    return punktyList

