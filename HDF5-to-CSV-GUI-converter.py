import tkinter as tk
from tkinter import filedialog
import h5py as h5
import numpy as np
import glob
import sys
from PyQt5.QtCore import QDate, QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def file_location():
    print('Please select the HDF5 file using the dialog window')
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()

def file_destination():
    root = tk.Tk()
    root.withdraw()
    print('Select the path for file saving')
    file_path =  filedialog.asksaveasfilename(initialdir = "file_path",title = "Select file",filetypes = (("CSV files","*.CSV"),("all files","*.*")))
    if not file_path.endswith(('.csv','.xls','.txt','.dat')):
        file_path += '.csv'
    return(file_path)

def visitfile(file):
    keys = []
    sizes = []
    file.visit(keys.append)
    for key in keys:
        size = np.array(file[key]).shape
        if len(size) == 1:
            size = np.array(file[key])[:, np.newaxis].shape
        sizes.append(size)
    return(keys, sizes)

class VerifyDialog(QDialog):
    def __init__(self, parent=None):
        print("This tool will allow you to open HDF5 files, select data and create CSV file")
        print("Selected data must be the same length (width can vary) to be concatenated into one table !")
        self.file = h5.File(file_location(), 'a')
        keys, sizes = visitfile(self.file)
        self.keys = keys
        self.sizes = sizes
        super(VerifyDialog, self).__init__(parent)

        self.listWidget = QListWidget()
        maxlenkey = len(max(keys, key=len))
        maxlennb =  len(str(len(keys)))
        for i in range(len(keys)):
            fillingspaces1 = (1 + maxlennb - len(str(i))) * " "
            fillingspaces2 = (1 + maxlenkey - len(keys[i])) * " "
            item = QListWidgetItem(str(i) + fillingspaces1 + keys[i] + fillingspaces2 + str(sizes[i]))
            item.setFont(QFont("Courier", 10))
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)

        runButton = QPushButton("Run")
        runButton.clicked.connect(self.exec)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.listWidget, 1)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(runButton)
        buttonsLayout.addWidget(cancelButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle("HDF5 to CSV converter")
        self.show()

    def exec(self):
        names = []
        tupleres = []
        for index in range(self.listWidget.count()):
            if self.listWidget.item(index).checkState() == Qt.Checked:
                tupleres.append(np.array(self.file[self.keys[index]]))
                for j in range(self.sizes[index][1]):
                    names.append(self.keys[index] + str(j))
        print("The following header will be used : ")
        print(names)

        try :
            result = np.column_stack(tupleres)
        except :
            print("Tables won't concatenate ! Please make sure that tables have the same length (width can differ)")
        file_path =  file_destination()

        print('Writing CSV file... This can take up to 1 hour')
        dest = open(file_path, 'wb')
        np.savetxt(dest, np.array(names)[:, None].T, delimiter=";" , fmt="%s")
        np.savetxt(dest, result, delimiter=";" , fmt="%s")
        print('Done !')
        self.close()

if __name__=="__main__":
    app = QApplication(sys.argv)
    dialog = VerifyDialog()
    sys.exit(app.exec_())
