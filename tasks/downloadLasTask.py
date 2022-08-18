import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from .. import service_api, utils



class DownloadLasTask(QgsTask):
    """QgsTask pobierania LAS"""

    def __init__(self, description, lasList, folder, iface):
        super().__init__(description, QgsTask.CanCancel)
        self.lasList = lasList
        self.folder = folder
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.iface = iface

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        total = len(self.lasList)

        for las in self.lasList:
            QgsMessageLog.logMessage('start ' + las.url)
            fileName = las.url.split("/")[-1]
            service_api.retreiveFile(url=las.url, destFolder=self.folder)
            self.setProgress(self.progress() + 100 / total)

        # utworz plik csv z podsumowaniem
        self.createCsvReport()

        utils.openFile(self.folder)

        if self.isCanceled():
            return False
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        if result:
            QgsMessageLog.logMessage('sukces')
            self.iface.messageBar().pushMessage("Sukces", "Udało się! Dane LAS zostały pobrane.",
                                                level=Qgis.Success, duration=0)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane LAS nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()

    def createCsvReport(self):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        csvFilename = 'pobieracz_las_%s.txt' % date

        with open(os.path.join(self.folder, csvFilename), 'w') as csvFile:
            naglowki = [
                'nazwa_pliku',
                'format',
                'godlo',
                'aktualnosc',
                'dokladnosc_pozioma',
                'dokladnosc_pionowa',
                'uklad_wspolrzednych_plaskich',
                'uklad_wspolrzednych_wysokosciowych',
                'caly_arkusz_wypelniony_trescia',
                'numer_zgloszenia_pracy',
                'aktualnosc_rok'
            ]
            csvFile.write(','.join(naglowki)+'\n')
            for las in self.lasList:
                fileName = las.url.split("/")[-1]
                csvFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                    fileName,
                    las.format,
                    las.godlo,
                    las.aktualnosc,
                    las.charakterystykaPrzestrzenna,
                    las.bladSredniWysokosci,
                    las.ukladWspolrzednych,
                    las.ukladWysokosci,
                    las.calyArkuszWyeplnionyTrescia,
                    las.numerZgloszeniaPracy,
                    las.aktualnoscRok
                ))