
# Imports
# =======

from os import path
from ..Base import ExoCanvas, ExoBase
from PyQt4 import QtGui, QtCore
from random import shuffle
import logging


#-----------------------------------------------------------------------------#

# Regression Visuals Widget
# ========== ======= ======


class RegrVis(ExoBase):

    def __init__(self, parent, visuals):
        super().__init__(parent)
        self.regr  = visuals['Regr Line']
        self.acc   = visuals['Accuracy']
        self._feat = 0
        layout = self.createLayout()
        self.initUI(layout)
        
    
    def initUI(self, layout):
        super().initUI(layout, scroll=False)
        self.plotCombo.currentIndexChanged[int].connect(self.rePlot)
        self.sld.valueChanged[int].connect(self.changeValue)
        self.refrBtn.clicked.connect(self.rePlot)
        
    
    def createLayout(self):
        # Class-wide variables
        n_samp, n_feat = self.regr[0].shape
        self._n_samp = n_samp
        self._frac = 1
        
        # Build Combo
        self.plotCombo = QtGui.QComboBox()
        for i in range(n_feat):
            lab = [unic[int(j)] for j in str(i)]
            lab = ''.join(['x', *lab])
            self.plotCombo.addItem(lab)
        self.plotCombo.setStatusTip('Draw regression line for variable.')
        
        # Refresh Button
        self.refrBtn = QtGui.QPushButton('Refresh')
        self.refrBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.refrBtn.setStatusTip('Resample points to plot.')
        hboxRefr = self.hcenter(self.refrBtn)
        
        # Build labels
        plotLab = QtGui.QLabel('Independent Variable')
        plotLab.setStatusTip('Draw regression line for variable.')
        plotLab.setObjectName('FormLabel')
        pointsLab = QtGui.QLabel('Points to Plot')
        pointsLab.setObjectName('FormLabel')

        # Build Slider
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setSliderPosition(99)
        self.sld.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sld.setStatusTip('Change the number of points to plot.')

        # Build Legend
        labColor1 = QtGui.QLabel('Orange')
        labColor2 = QtGui.QLabel('Blue')
        labColor1.setObjectName('FormLabel')
        labColor2.setObjectName('FormLabel')

        labL1 = QtGui.QLabel('Predicted Values')
        labL2 = QtGui.QLabel('Actual Values')

        formLegend = QtGui.QFormLayout()
        formLegend.addRow(labColor1, labL1)
        formLegend.addRow(labColor2, labL2)
        formLegend.setLabelAlignment(QtCore.Qt.AlignLeft)
        formLegend.setVerticalSpacing(15)
        formLegend.setHorizontalSpacing(25)
        vboxLegend = self.vcenter(formLegend)

        # Build parameter layout
        formPara1 = QtGui.QFormLayout()
        formPara1.addRow(plotLab, self.plotCombo)
        formPara1.setLabelAlignment(QtCore.Qt.AlignRight)
        formPara1.setVerticalSpacing(15)
        formPara1.setHorizontalSpacing(25)
        
        formPara2 = QtGui.QFormLayout()
        formPara2.addRow(pointsLab, self.sld)
        formPara2.setLabelAlignment(QtCore.Qt.AlignRight)
        formPara2.setVerticalSpacing(15)
        formPara2.setHorizontalSpacing(25)
        
        hboxPara1 = self.hboxCreate(20, formPara1, 40, vboxLegend, 20)
        vboxPara = self.vboxCreate(hboxPara1, 30, formPara2)
        hboxPara = self.hboxCreate(50, vboxPara, 50)

        # Build Regr line layout
        self.regrCanvas = RegrCanvas(self)
        self.regrCanvas.setFixedSize(850, 500)
        self.rePlot(0)

        # Build Regression line Card
        vboxRegr = self.vboxCreate(self.hcenter(self.regrCanvas), hboxPara,
                hboxRefr)
        vboxRegr.setSpacing(30)
        regrCard = self.createCard('Regression Line', vboxRegr)

        # Build Accuracy card
        r2Lab = QtGui.QLabel(str(round(self.acc, 6)))
        r2Lab.setObjectName('Accuracy')
        r2Card = self.createCard('Coefficient of Determination', self.hcenter(r2Lab))
        
        return self.createCardLayout(r2Card, regrCard)
    
    
    def rePlot(self, ind=-1):
        sender = self.sender()
        random = False
        if sender is self.plotCombo:
            self._feat = ind
            logging.info('RegrVis:plotCombo index ' + str(self._feat) +
                ' selected.')
        elif sender is self.refrBtn:
            random = True
        num = round(self._n_samp * self._frac)
        x = self.regr[0]
        x = x[:,self._feat]
        y = self.regr[1]
        self.regrCanvas.updatePlot(x, y, num, self._feat, random)

    
    def changeValue(self, value):
        logging.info('RegrVis:Slider value changed to ' + str(value) + '.')
        self._frac = (value+1)/100
        self.rePlot()


    def saveVisual(self):
        home = path.expanduser('~')
        dname = QtGui.QFileDialog.getExistingDirectory(self, 'Save Folder',
            home)
        num = round(self._n_samp * self._frac)
        y = self.regr[1]
        for btn in self.plotButtons:
            feat = self.plotButtons.index(btn)
            x = self.regr[0][:,feat]
            self.regrCanvas.updatePlot(x, y, num, feat)
            self.regrCanvas.save(dname, feat)

        self.parent().parent().stat.showMessage('Visuals Saved')
        logging.info('RegrVis:Visuals Saved')
        


#-----------------------------------------------------------------------------#

# Regression Line Canvas
# ========== ==== ======


class RegrCanvas(ExoCanvas):
    
    def __init__(self, parent=None):
        super().__init__(parent, 75)
        self.figure.subplots_adjust(left=0.04, bottom=0.07, top=0.965,
                right=0.985)
        self.axes.set_ylabel('y')
        self.axes.hold(False)
        
        
    def updatePlot(self, x, y, num, i, random=False):
        self.axes.set_xlabel('x' + str(i))
        self.axes.set_ylabel('y')
        points = []
        for tup in zip(x, *y):
            points.append(tup)
        if random:
            shuffle(points)
        points = points[:num]
        points.sort()
        del(x)
        del(y)
        x = []
        y = [[],[]]
        for i, tup in enumerate(points):
            x.append(tup[0])
            y[0].append(tup[1])
            y[1].append(tup[2])
        self.axes.plot(x, y[0], '-', color='#000000')
        self.axes.hold(True)
        self.axes.plot(x, y[1], '-', color='#FF4D00')
        self.axes.hold(False)
        self.draw()
        
    
    def save(self, dname, i):
        figname = 'X' + str(i)
        super().save(dname, figname)    
        

#-----------------------------------------------------------------------------#

# Unicode Subscript
# ======= =========


unic = ['\u2080', '\u2081', '\u2082', '\u2083', '\u2084',
        '\u2085', '\u2086', '\u2087', '\u2088', '\u2089']


#-----------------------------------------------------------------------------#