import sys
from PyQt4 import QtGui
import design
import neronet.neroman
import os.path

class ExampleApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        default = os.path.expanduser("~/.neronet/default.yaml")
        pref = os.path.expanduser("~/.neronet/preferences.yaml")
        clust = os.path.expanduser("~/.neronet/clusters.yaml")
        self.tmp = neronet.neroman.Neroman(default, pref, clust)
        self.showHello()

    def showHello(self):
        #self.tmp.status("all")
        text = self.tmp.preferences['name'] +'\n'+ self.tmp.preferences['email']
        self.user.setPlainText(text)
        for cluster in self.tmp.clusters['clusters']:
            address = self.tmp.clusters['clusters'][cluster]['ssh_address']
            atype = self.tmp.clusters['clusters'][cluster]['type']
            text = "%s %s %s\n" % (cluster, address, atype)
            self.clusters.insertPlainText(text)
        for experiment in self.tmp.experiments:
            self.experiments.insertPlainText(experiment + ': ' +
                self.tmp.experiments[experiment]['state'].pop()[0])
        


def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
	main()
