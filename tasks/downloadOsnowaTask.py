import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
)
from .. import service_api, utils
import requests


class DownloadOsnowaTask(QgsTask):
    """QgsTask pobierania PRG"""

    def __init__(self, description, folder, teryt_powiat, typ, iface):

        super().__init__(description, QgsTask.CanCancel)
        self.folder = folder
        self.exception = None
        self.teryt_powiat = teryt_powiat
        self.typ = typ
        self.iface = iface

    def run(self):
        list_url = []
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        # total = len(self.nmtList)

        for typ in self.typ:
            url = f"https://integracja.gugik.gov.pl/osnowa/?teryt={self.teryt_powiat}&typ={typ}"
            r = requests.get(url, verify=False)
            if str(r.status_code) == '200':
                QgsMessageLog.logMessage('pobieram ' + url)
                # fileName = self.url.split("/")[-2]
                # print(self.folder)
                service_api.retreiveFile(url=url, destFolder=self.folder)
                # self.setProgress(self.progress() + 100 / total)

        utils.openFile(self.folder)
        if self.isCanceled():
            return False
        return True

    def finished(self, result):

        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces",
                                                "Udało się! Dane podstawowej osnowy geodezyjnej zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane podstawowej osnowy geodezyjnej nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
