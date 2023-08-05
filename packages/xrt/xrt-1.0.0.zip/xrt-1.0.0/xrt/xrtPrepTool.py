# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 16:21:40 2015

@author: Roman Chernikov
"""

import sys
sys.path.append(r"d:\rt4")

from PyQt4 import QtGui, QtCore#, uic
#from copy import deepcopy
#import numpy as np
import inspect
import re

import xrt.backends.raycing
import xrt.backends.raycing.sources
import xrt.backends.raycing.screens
import xrt.backends.raycing.materials
import xrt.backends.raycing.oes
import xrt.backends.raycing.apertures

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rsources
import xrt.backends.raycing.screens as rscreens
import xrt.backends.raycing.materials as rmats
import xrt.backends.raycing.oes as roes
import xrt.backends.raycing.apertures as rapts
import xrt.plotter as xrtplot
import xrt.runner as xrtrun


from functools import partial

#class Other(object):
#    def __init__(self, x, y):
#        self.x = x
#        self.y = y
#    def __repr__(self):
#        return '(%s, %s)' % (self.x, self.y)

class xrtPrepTool(QtGui.QWidget):

    def __init__(self):

        super(xrtPrepTool, self).__init__()
        self.setAcceptDrops(True)
        #self.accessibleName = "xrtGUI 1.0"
        self.tabs = QtGui.QTabWidget()

        self.xrtModules = ['rsources', 'rscreens', 'rmats', 'roes', 'rapts',
                            'raycing', 'xrtplot', 'xrtrun']

        btnGen = QtGui.QPushButton('Generate Code', self)
        btnGen.clicked.connect(self.generateCode)
        btnAlign = QtGui.QPushButton('Align Beamline', self)
        btnAlign.clicked.connect(self.AlignBeam)

        self.objectFlag = QtCore.Qt.ItemFlags(-33)
        self.paramFlag = QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled |\
                                             ~QtCore.Qt.ItemIsEditable |\
                                             QtCore.Qt.ItemIsSelectable)
        self.valueFlag = QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled |\
                                             QtCore.Qt.ItemIsEditable |\
                                             QtCore.Qt.ItemIsSelectable)
        self.checkFlag = QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled |\
                                             ~QtCore.Qt.ItemIsEditable |\
                                             QtCore.Qt.ItemIsUserCheckable |\
                                             QtCore.Qt.ItemIsSelectable)

        self.beamLineModel = QtGui.QStandardItemModel()
        BLName = QtGui.QStandardItem("beamLine")
        BLName.setFlags(self.paramFlag)
        self.beamLineModel.appendRow(BLName)
        self.rootBLItem = self.beamLineModel.item(0,0)

        self.boolModel = QtGui.QStandardItemModel()
        self.boolModel.appendRow(QtGui.QStandardItem('False'))
        self.boolModel.appendRow(QtGui.QStandardItem('True'))


        self.materialsModel = QtGui.QStandardItemModel()
        #self.materialsModel.appendRow(QtGui.QStandardItem("materials"))
        self.rootMatItem = self.materialsModel.invisibleRootItem()
        self.addValue(self.materialsModel.invisibleRootItem(), "None")

        self.beamModel = QtGui.QStandardItemModel()
        self.beamModel.appendRow(QtGui.QStandardItem("None"))
        self.rootBeamItem = self.beamModel.item(0,0)

        self.fluxDataModel = QtGui.QStandardItemModel()
        self.fluxDataModel.appendRow(QtGui.QStandardItem("auto"))
        for rfName, rfObj in inspect.getmembers(raycing):
            if rfName.startswith('get_') and\
                rfName != "get_output":
                flItem = QtGui.QStandardItem(rfName.replace("get_",''))
                self.fluxDataModel.appendRow(flItem)

        self.fluxKindModel = QtGui.QStandardItemModel()
        for flKind in ['total','power','s','p','+45','-45','left','right']:
            flItem = QtGui.QStandardItem(flKind)
            self.fluxKindModel.appendRow(flItem)

        self.aspectModel = QtGui.QStandardItemModel()
        for aspect in ['equal','auto']:
            aspItem = QtGui.QStandardItem(aspect)
            self.aspectModel.appendRow(aspItem)

        self.rayModel = QtGui.QStandardItemModel()
        for ray in ['Good','Out','Over','Alive']:
            rayItem = QtGui.QStandardItem(ray)
            #rayItem.setFlags(self.checkFlag)
            rayItem.setCheckable(True)
            rayItem.setCheckState(QtCore.Qt.Checked)
            self.rayModel.appendRow(rayItem)

        self.plotModel = QtGui.QStandardItemModel()
        self.plotModel.appendRow(QtGui.QStandardItem("plots"))
        self.rootPlotItem = self.plotModel.item(0,0)

        self.runModel = QtGui.QStandardItemModel()
        self.runModel.appendRow(QtGui.QStandardItem("RayTracing Parameters"))
        self.rootRunItem = self.runModel.item(0,0)

        self.tree = QtGui.QTreeView()
        self.matTree = QtGui.QTreeView()
        self.plotTree = QtGui.QTreeView()
        self.runTree = QtGui.QTreeView()

        self.BLTab = QtGui.QWidget()
        self.MatTab = QtGui.QWidget()
        self.PlotTab = QtGui.QWidget()
        self.RunTab = QtGui.QWidget()

        hViewBox = QtGui.QHBoxLayout()
        #hViewBox.addStretch(1)
        hButtonBox = QtGui.QHBoxLayout()
        hButtonBox.addStretch(1)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hViewBox)
        vbox.addLayout(hButtonBox)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 1000, 600)

        self.tabs.addTab(self.BLTab,"Beamline")
        self.tabs.addTab(self.MatTab,"Materials")
        self.tabs.addTab(self.PlotTab,"Plots")
        self.tabs.addTab(self.RunTab,"RayTracing")


        blbox = QtGui.QHBoxLayout()
        plotbox = QtGui.QHBoxLayout()
        runbox = QtGui.QHBoxLayout()
        matbox = QtGui.QHBoxLayout()
        blbox.addWidget(self.tree)
        matbox.addWidget(self.matTree)
        plotbox.addWidget(self.plotTree)
        runbox.addWidget(self.runTree)

        self.BLTab.setLayout(blbox)
        self.MatTab.setLayout(matbox)
        self.PlotTab.setLayout(plotbox)
        self.RunTab.setLayout(runbox)

        hViewBox.addWidget(self.tabs)
        hButtonBox.addWidget(btnAlign)
        hButtonBox.addWidget(btnGen)

        # runTree view
        self.runTree.setModel(self.runModel)
        self.runTree.setAlternatingRowColors(True)
        self.runTree.setSortingEnabled(False)
        self.runTree.setHeaderHidden(False)
        self.runTree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.runTree.model().setHorizontalHeaderLabels(['Parameter',
                                                        'Value',
                                                        'Description'])
        for name, obj in inspect.getmembers(xrtrun):
            if inspect.isfunction(obj) and name == "run_ray_tracing":
                if inspect.getargspec(obj)[3] is not None:
                    self.addObject(self.runTree,
                                   self.rootRunItem,
                                   '{0}.{1}'.format(xrtrun.__name__,name))
                    for arg, argVal in zip(inspect.getargspec(obj)[0],
                                            inspect.getargspec(obj)[3]):
                        if str.lower(arg) == "plots":
                            argVal = self.rootPlotItem.text()
                        if str.lower(arg) == "beamline":
                            argVal = self.rootBLItem.text()
                        self.addParam(self.runTree, self.rootRunItem,
                                      arg, argVal)
        self.addCombo(self.runTree, self.rootRunItem)
        self.runTree.expand(self.rootRunItem.index())
        self.runTree.setColumnWidth(0,self.runTree.sizeHintForColumn(0))
        self.runTree.setColumnWidth(1,self.runTree.sizeHintForColumn(1))


        # plotTree view
        self.plotTree.setModel(self.plotModel)
        self.plotTree.setAlternatingRowColors(True)
        self.plotTree.setSortingEnabled(False)
        self.plotTree.setHeaderHidden(False)
        self.plotTree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.plotTree.model().setHorizontalHeaderLabels(['Parameter',
                                                         'Value',
                                                         'Description'])
        self.plotTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.plotTree.customContextMenuRequested.connect(self.plotMenu)

        # materialsTree view
        self.matTree.setModel(self.materialsModel)
        self.matTree.setAlternatingRowColors(True)
        self.matTree.setSortingEnabled(False)
        self.matTree.setHeaderHidden(False)
        self.matTree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.matTree.model().setHorizontalHeaderLabels(['Parameter',
                                                         'Value',
                                                         'Description'])
        self.matTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.matTree.customContextMenuRequested.connect(self.matMenu)


        # BLTree view
        self.tree.setModel(self.beamLineModel)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)
        self.tree.setHeaderHidden(False)
        #self.tree.setDragEnabled(True)
        #self.tree.setDropEnabled(True)
        self.tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.tree.model().setHorizontalHeaderLabels(['Parameter',
                                                     'Value',
                                                     'Description'])
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)

        #self.tree.setDragDropMode(4)
        #self.tree.setDragEnabled(True)
        #self.tree.setDefaultDropAction(QtCore.Qt.DropAction(2))
        #self.rootBLItem.setDropEnabled(True)
        #self.rootBLItem.setDragEnabled(False)
        #self.beamLineModel.invisibleRootItem().setDropEnabled(False)
        #self.beamLineModel.invisibleRootItem().setDragEnabled(False)


        elprops = self.addProp(self.rootBLItem, 'properties')
        for name, obj in inspect.getmembers(raycing):
            if inspect.isclass(obj) and name=="BeamLine":
                for namef, objf in inspect.getmembers(obj):
                    if inspect.ismethod(objf) and\
                       namef=="__init__" and\
                       inspect.getargspec(objf)[3] is not None:
                        self.addObject(self.tree,
                                       self.rootBLItem,
                                       '{0}.{1}'.format(raycing.__name__,name))
                        for arg, argVal in zip(inspect.getargspec(objf)[0][1:],
                                                inspect.getargspec(objf)[3]):
                            self.addParam(self.tree, elprops, arg, argVal)

        self.tree.expand(self.rootBLItem.index())
        self.tree.setColumnWidth(0,self.tree.sizeHintForColumn(0))

    def setIBold(self, item):
        eFont = item.font()
        eFont.setBold(True)
        item.setFont(eFont)

    def addObject(self, view, parent, obj):
        child0 = QtGui.QStandardItem('_object')
        child1 = QtGui.QStandardItem(str(obj))
        child0.setFlags(self.objectFlag)
        child1.setFlags(self.objectFlag)
        child0.setDropEnabled(False)
        child0.setDragEnabled(False)
        child1.setDropEnabled(False)
        child1.setDragEnabled(False)
        parent.appendRow([child0, child1])
        view.setRowHidden(child0.index().row(), parent.index(), True)
        return child0, child1

    def addParam(self, view, parent, paramName, value):
        """Add a pair of Parameter-Value Items"""
        child0 = QtGui.QStandardItem(str(paramName))
        child0.setFlags(self.paramFlag)
        child1 = QtGui.QStandardItem(str(value))
        child1.setFlags(self.valueFlag)
        child0.setDropEnabled(False)
        child0.setDragEnabled(False)
        child1.setDropEnabled(False)
        child1.setDragEnabled(False)
        parent.appendRow([child0, child1])
        return child0, child1

    def addProp(self, parent, propName):
        """Add non-editable Item"""
        child0 = QtGui.QStandardItem(str(propName))
        child0.setFlags(self.paramFlag)
        child0.setDropEnabled(False)
        child0.setDragEnabled(False)
        parent.appendRow(child0)
        return child0

    def addValue(self, parent, value):
        """Add editable Item"""
        child0 = QtGui.QStandardItem(str(value))
        child0.setFlags(self.valueFlag)
        child0.setDropEnabled(False)
        child0.setDragEnabled(False)
        parent.appendRow(child0)
        return child0

    def addElement(self, name, obj):

        for i in range(99):
            elementName = str(name) + '{:02d}'.format(i+1)
            dupl = False
            for ibm in range(self.rootBLItem.rowCount()):
                if str(self.rootBLItem.child(ibm,0).text())==str(elementName):
                    dupl = True
            if not dupl: break

        elementItem = self.addValue(self.rootBLItem, elementName)
        elementItem.setDragEnabled(True)
        #elementItem.setDropEnabled(False)
        elprops = self.addProp(elementItem, 'properties')
        self.addObject(self.tree, elementItem, obj)

        for arg, argVal in self.getParams(obj):
            self.addParam(self.tree, elprops, arg, argVal)

        self.addCombo(self.tree, elementItem)
        self.tree.expand(self.rootBLItem.index())
        self.setIBold(elementItem)
        self.tree.expand(elementItem.index())
        self.tree.setCurrentIndex(elementItem.index())
        self.tree.setColumnWidth(0,self.tree.sizeHintForColumn(0))

    def getParams(self, obj):
        args = []
        argVals = []
        #checkParentInit = True
        for parent in (inspect.getmro(eval(obj)))[:-1]:
            for namef, objf in inspect.getmembers(parent):
                if inspect.ismethod(objf):
                    if namef=="__init__" and\
                        inspect.getargspec(objf)[3] is not None:
                        for arg, argVal in zip(inspect.getargspec(objf)[0][1:],
                                                inspect.getargspec(objf)[3]):
                            if arg=='bl': argVal=self.rootBLItem.text()
                            if not arg in args:
                                args.append(arg)
                                argVals.append(argVal)
                    if namef=="__init__" or namef.endswith("pop_kwargs"):
                        #print parent.__name__, namef
                        kwa = re.findall("(?<=kwargs\.pop).*?\)",
                                     inspect.getsource(objf),re.S)
                        if len(kwa)>0:
                            kwa = [re.split(",", str.strip(kwline,"\n ()"), 
                                            maxsplit=1) for kwline in kwa]
                            for kwline in kwa:
                                arg = str.strip(kwline[0],"\' ")
                                if len(kwline)>1:
                                    argVal = str.strip(kwline[1],"\' ")
                                else:
                                    argVal = "None"
                                if not arg in args:
                                    args.append(arg)
                                    argVals.append(argVal)
        return zip(args, argVals)


    def addMethod(self, name, parentItem, fdoc):
        elstr = str(parentItem.text())
        fdoc = str.split(fdoc[0].replace("Returned values: ",''),",")

        methodItem = self.addProp(parentItem, str.split(name,".")[-1])
        methodProps = self.addProp(methodItem, 'parameters')
        obj = eval(name)
        self.addObject(self.tree, methodItem, name)

        if inspect.getargspec(obj)[3] is not None:
            for arg, argVal in zip(inspect.getargspec(obj)[0][1:],
                                    inspect.getargspec(obj)[3]):
                if arg=='bl': argVal=self.rootBLItem.text()
                child0, child1 = self.addParam(self.tree, methodProps,
                                               arg, argVal)

        methodOut = self.addProp(methodItem, 'output')
        for outstr in fdoc:
            outval = str.strip(outstr)

            for i in range(99):
                beamName = '{0}{1}{2:02d}'.format(elstr, outval, i+1)
                dupl = False
                for ibm in range(self.beamModel.rowCount()):
                    if str(self.beamModel.index(ibm,0).data(0))==str(beamName):
                        dupl = True
                if not dupl: break

            child0, child1 = self.addParam(self.tree, methodOut, outval,
                                           beamName)
            self.beamModel.appendRow(QtGui.QStandardItem(beamName))

        self.addCombo(self.tree,methodItem)
        self.tree.expand(methodItem.index())
        self.tree.expand(methodOut.index())
        self.tree.expand(methodProps.index())
        self.tree.setCurrentIndex(methodProps.index())
        self.tree.setColumnWidth(0,self.tree.sizeHintForColumn(0))
        self.tree.setColumnWidth(1,self.tree.sizeHintForColumn(1))

    def addPlot(self):
        for i in range(99):
            plotName = 'Plot{:02d}'.format(i+1)
            dupl = False
            for ibm in range(self.rootPlotItem.rowCount()):
                if str(self.rootPlotItem.child(ibm,0).text())==str(plotName):
                    dupl = True
            if not dupl: break

        plotItem = self.addValue(self.rootPlotItem, plotName)

        for name, obj in inspect.getmembers(xrtplot):
            if name=="XYCPlot" and inspect.isclass(obj):
                self.addObject(self.plotTree, plotItem,
                               '{0}.{1}'.format(xrtplot.__name__,name))
                for namef, objf in inspect.getmembers(obj):
                    if inspect.ismethod(objf):
                        if namef=="__init__" and inspect.getargspec(objf)[3] is not None:
                            for arg, arg_def in zip(inspect.getargspec(objf)[0][1:],inspect.getargspec(objf)[3]):
                                child0 = QtGui.QStandardItem(str(arg))
                                child0.setFlags(self.paramFlag)
                                if len(re.findall("axis",str.lower(arg)))>0:
                                    plotItem.appendRow(child0)
                                    for name2, obj2 in inspect.getmembers(xrtplot):
                                        if name2=="XYCAxis" and inspect.isclass(obj2):
                                            self.addObject(self.plotTree,
                                                           child0,
                                                           '{0}.{1}'.format(xrtplot.__name__,name2))
                                            for namef2, objf2 in inspect.getmembers(obj2):
                                                if inspect.ismethod(objf2):
                                                    if namef2=="__init__" and inspect.getargspec(objf2)[3] is not None:
                                                        for arg2, arg_def2 in zip(inspect.getargspec(objf2)[0][1:],
                                                                                  inspect.getargspec(objf2)[3]):
                                                            self.addParam(self.plotTree, child0, arg2, arg_def2)
                                else:
                                    if str(arg) == 'title':
                                        arg_value = plotItem.text()
                                    else:
                                        arg_value = arg_def
                                    self.addParam(self.plotTree, plotItem,
                                                  arg, arg_value)
        self.addCombo(self.plotTree,plotItem)
        self.setIBold(plotItem)
        self.plotTree.expand(self.rootPlotItem.index())
        self.plotTree.expand(plotItem.index())
        self.plotTree.setCurrentIndex(plotItem.index())
        self.plotTree.setColumnWidth(0,self.plotTree.sizeHintForColumn(0))
        self.plotTree.setColumnWidth(1,self.plotTree.sizeHintForColumn(1))

    def addMaterial(self, name, obj):

        for i in range(99):
            matName = str(name) + '{:02d}'.format(i+1)
            dupl = False
            for ibm in range(self.rootMatItem.rowCount()):
                if str(self.rootMatItem.child(ibm,0).text())==str(matName):
                    dupl = True
            if not dupl: break

        matItem = self.addValue(self.rootMatItem, matName)
        matProps = self.addProp(matItem, 'properties')
        self.addObject(self.matTree, matItem, obj)

        #for parent in (inspect.getmro(eval(obj)))[:-1]:
        #    for namef, objf in inspect.getmembers(parent):
        #        if inspect.ismethod(objf):
        #            if namef=="__init__" and\
        #                inspect.getargspec(objf)[3] is not None:
        #                for arg, argVal in zip(inspect.getargspec(objf)[0][1:],
        #                                        inspect.getargspec(objf)[3]):
        #                    #if arg=='bl': argVal=self.rootBLItem.text()
        for arg, argVal in self.getParams(obj):
            self.addParam(self.matTree, matProps, arg, argVal)
        self.addCombo(self.matTree, matItem)
        self.matTree.expand(self.rootMatItem.index())
        self.matTree.expand(matItem.index())
        self.matTree.setCurrentIndex(matItem.index())
        self.matTree.setColumnWidth(0,self.tree.sizeHintForColumn(0))

    def moveItem(self, mvDir, view, item):
        oldRowNumber = item.index().row()
        statusExpanded = view.isExpanded(item.index())
        parent = item.parent()
        self.flattenElement(view, item)
        newItem = parent.takeRow(oldRowNumber)
        parent.insertRow(oldRowNumber + mvDir, newItem)
        self.addCombo(view, newItem[0])
        view.setExpanded(newItem[0].index(),statusExpanded)


    def deleteElement(self, view, item):
        while item.hasChildren():
            iItem = item.child(0,0)
            if item.child(0,1) is not None:
                iWidget = view.indexWidget(item.child(0,1).index())
                if iWidget is not None:
                    if item.text()=="output" and\
                        iWidget.model()==self.beamModel:
                        self.beamModel.takeRow(iWidget.currentIndex())
            self.deleteElement(view, iItem)
        else:
            item.parent().takeRow(item.index().row())

    def flattenElement(self, view, item):
        if item.hasChildren():
            for ii in range(item.rowCount()):
                iItem = item.child(ii,0)
                if item.child(ii,1) is not None:
                    iWidget = view.indexWidget(item.child(ii,1).index())
                    if iWidget is not None:
                        item.child(ii,1).setText(iWidget.currentText())
                        #view.setIndexWidget(item.child(ii,1).index(),None)
                self.flattenElement(view, iItem)
        else:
            pass

    def addCombo(self, view, item):
        if item.hasChildren():
            itemTxt = str(item.text())
            for ii in range(item.rowCount()):
                child0 = item.child(ii,0)
                child1 = item.child(ii,1)
                if child1 is not None:
                    value = child1.text()
                    paramName = str(child0.text())
                    iWidget = view.indexWidget(child1.index())
                    if iWidget is None:
                        if isinstance(self.getVal(value),bool):
                            combo = QtGui.QComboBox()
                            combo.setModel(self.boolModel)
                            combo.setCurrentIndex(combo.findText(value))
                            view.setIndexWidget(child1.index(),combo)
                        if len(re.findall("beam",str.lower(paramName)))>0 and\
                            str.lower(paramName)!=str('beamline') and\
                            str.lower(paramName)!=str('filamentbeam'):
                            combo = QtGui.QComboBox()
                            combo.setModel(self.beamModel)
                            combo.setCurrentIndex(combo.findText(value))
                            view.setIndexWidget(child1.index(),combo)
                            if str.lower(str(item.text())) == "output":
                                combo.setEditable(True)
                                combo.setInsertPolicy(2)
                        elif len(re.findall("material",str.lower(paramName)))>0:
                            combo = QtGui.QComboBox()
                            combo.setModel(self.materialsModel)
                            combo.setCurrentIndex(combo.findText(value))
                            view.setIndexWidget(child1.index(),combo)
                        elif len(re.findall("data",str.lower(paramName)))>0 and\
                            len(re.findall("axis",str.lower(itemTxt)))>0:
                            combo = QtGui.QComboBox()
                            combo.setModel(self.fluxDataModel)
                            combo.setCurrentIndex(combo.findText(value))
                            view.setIndexWidget(child1.index(),combo)
                        elif len(re.findall("fluxkind",str.lower(paramName)))>0:
                            combo = QtGui.QComboBox()
                            combo.setModel(self.fluxKindModel)
                            combo.setCurrentIndex(combo.findText(value))
                            view.setIndexWidget(child1.index(),combo)
                        elif len(re.findall("aspect",str.lower(paramName)))>0:
                            combo = QtGui.QComboBox()
                            combo.setModel(self.aspectModel)
                            combo.setCurrentIndex(combo.findText(value))
                            combo.setEditable(True)
                            combo.setInsertPolicy(3)
                            view.setIndexWidget(child1.index(),combo)
                        #elif len(re.findall("rayflag",str.lower(paramName)))>0:
                        #    combo = QtGui.QListWidget()
                            #combo = QtGui.QComboBox()
                            #combo.setModel(self.rayModel)
                        #    for ir in range(self.rayModel.rowCount()):
                        #        combo.addItem(QtGui.QListWidgetItem(self.rayModel.item(ir).text()))
                            #combo.setEditable(True)
                            #combo.setCurrentIndex(combo.findText(value))
                         #   view.setIndexWidget(child1.index(),combo)
                self.addCombo(view, child0)
        else:
            pass

    def openMenu(self, position):

        indexes = self.tree.selectedIndexes()

        level = 100
        if len(indexes) > 0:
            level = 0
            selIndex = indexes[0]
            index = indexes[0]
            selectedItem = self.beamLineModel.itemFromIndex(selIndex)
            selText = selectedItem.text()
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QtGui.QMenu()
        if level == 0 or level == 100:
            menusrc = menu.addMenu(self.tr("Add Source"))
            menuoe = menu.addMenu(self.tr("Add OE"))
            menuapt = menu.addMenu(self.tr("Add Aperture"))
            menuscr = menu.addMenu(self.tr("Add Screen"))
            for tsubmenu, tmodule in zip([menusrc,menuoe,menuapt,menuscr],
                                         [rsources,roes,rapts,rscreens]):
                for elname, tobj in inspect.getmembers(tmodule):
                    if inspect.isclass(tobj):
                        objName = '{0}.{1}'.format(tmodule.__name__,
                                                   tobj.__name__)
                        tsubmenu.addAction(elname,
                                           partial(self.addElement,elname,
                                                   objName))
        elif level == 1 and selText != "properties":
            tsubmenu = menu.addMenu(self.tr("Add method"))
            menu.addSeparator()

            if selIndex.row() > 2:
                menu.addAction("Move Up",partial(self.moveItem, -1,
                                                 self.tree,
                                                 selectedItem))
            if selIndex.row() < selectedItem.parent().rowCount()-1:
                menu.addAction("Move Down",partial(self.moveItem, 1,
                                                   self.tree,
                                                   selectedItem))
            menu.addSeparator()
            deleteActionName = "Remove " + str(selectedItem.text())
            menu.addAction(deleteActionName, partial(self.deleteElement,
                                                     self.tree,
                                                     selectedItem))

            for ic in range(selectedItem.rowCount()):
                if selectedItem.child(ic,0).text()=="_object":
                    elstr = str(selectedItem.child(ic,1).text())
                    break
            #elcls=eval(str.split(elstr,"'")[1])
            elcls = eval(elstr)
            for namef, objf in inspect.getmembers(elcls):
                if inspect.ismethod(objf) and not str(namef).startswith("_"):
                    fdoc = objf.__doc__
                    if fdoc is not None:
                        objfNm = '{0}.{1}'.format(elstr,
                                                   objf.__name__)
                        fdoc = re.findall(r"Returned values:.*", fdoc)
                        if len(fdoc) > 0:
                            tsubmenu.addAction(namef,
                                               partial(self.addMethod, objfNm,
                                                       selectedItem, fdoc))
        elif level == 2 and selText != "properties":
            deleteActionName = "Remove " + str(selText)
            menu.addAction(deleteActionName, partial(self.deleteElement,
                                                     self.tree,
                                                     selectedItem))
            #pass

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def plotMenu(self, position):

        indexes = self.plotTree.selectedIndexes()
        level = 100
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            selectedItem = self.plotModel.itemFromIndex(index)
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QtGui.QMenu()

        if level == 0 or level == 100:
            menu.addAction(self.tr("Add Plot"),self.addPlot)
        elif level == 1:
            deleteActionName = "Remove " + str(selectedItem.text())
            menu.addAction(deleteActionName, partial(self.deleteElement,
                                                     self.plotTree,
                                                     selectedItem))
        else:
            pass

        menu.exec_(self.plotTree.viewport().mapToGlobal(position))


    def matMenu(self, position):

        indexes = self.matTree.selectedIndexes()
        level = 100
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            selectedItem = self.materialsModel.itemFromIndex(index)
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QtGui.QMenu()

        matMenu = menu.addMenu(self.tr("Add Material"))
        for mName, obj in inspect.getmembers(rmats):
            if inspect.isclass(obj):
                objName = '{0}.{1}'.format(rmats.__name__,
                                           mName)
                matMenu.addAction(mName, partial(self.addMaterial,mName,
                                           objName))

        if level == 0:
            menu.addSeparator()
            deleteActionName = "Remove " + str(selectedItem.text())
            menu.addAction(deleteActionName, partial(self.deleteElement,
                                                     self.matTree,
                                                     selectedItem))
        else:
            pass

        menu.exec_(self.matTree.viewport().mapToGlobal(position))

    def getVal(self, value):
        try:
            return eval(str(value))
        except:
            return str(value)

    def quotize(self, value):
        if isinstance(self.getVal(value), str):
            value = 'r\'{}\''.format(value)
        return str(value)

    def quotizeAll(self, value):
        return str('r\'{}\''.format(value))

    def generateCode(self):

        self.flattenElement(self.tree, self.rootBLItem)
        self.flattenElement(self.matTree, self.rootMatItem)
        self.flattenElement(self.plotTree, self.rootPlotItem)
        self.flattenElement(self.runTree, self.rootRunItem)

        BLName = str(self.rootBLItem.text())
        fullCode = ""
        codeHeader = """# -*- coding: utf-8 -*-\n\"\"\"\n
__author__ = \"Konstantin Klementiev\", \"Roman Chernikov\"
__date__ =\n\nCreated with xrtPrepTool\n\n\"\"\"\n\n"""
        codeDeclarations = """\n"""

        codeBuildBeamline = "\ndef build_beamline():\n"
        codeBuildBeamline += '\t{0} = {1}.BeamLine()\n\n'.format(BLName,
            raycing.__name__) #WARNING!!! No BL parameters enumerated

        codeRunProcess = 'def run_process({}):\n\n'.format(BLName)
        codeMain = "def main():\n"
        codeMain += '\t{} = build_beamline()\n'.format(BLName)
        codeMain += "\tplots = []"
        codeFooter = """\n\n
if __name__ == '__main__':
    main()
        """
        for ie in range(self.rootMatItem.rowCount()):
            if str(self.rootMatItem.child(ie,0).text()) != "None":
                matItem = self.rootMatItem.child(ie,0)
                ieinit = ""
                for ieph in range(matItem.rowCount()):
                    if matItem.child(ieph,0).text() == '_object':
                        elstr = str(matItem.child(ieph,1).text())
                        ieinit = elstr + "(" + ieinit
                        break
                        #for parent in (inspect.getmro(eval(elstr)))[:-1]:
                        #    for namef, objf in inspect.getmembers(parent):
                        #        if inspect.ismethod(objf):
                        #            if namef=="__init__" and\
                        #                inspect.getargspec(objf)[3] is not None:
                        #                initObj = objf #WARNING! Takes only the last object
                for ieph in range(matItem.rowCount()):
                    if matItem.child(ieph,0).text() != '_object':
                        if matItem.child(ieph,0).text() == 'properties':#class properties
                            pItem = matItem.child(ieph,0)
                            for iep, arg_def in zip(range(pItem.rowCount()),
                                                          list(zip(*self.getParams(elstr))[1])):
                                paraname = str(pItem.child(iep,0).text())
                                paravalue = pItem.child(iep,1).text()
                                if str(paravalue) != str(arg_def):
                                    ieinit += '{0}={1},'.format(paraname,
                                                                paravalue)
                codeDeclarations += '{0} = {1})\n'.format(matItem.text(),
                    str.rstrip(ieinit,","))



        for ie in range(self.rootBLItem.rowCount()):
            if self.rootBLItem.child(ie,0).text() != "properties" and\
                self.rootBLItem.child(ie,0).text() != "_object":
                tItem = self.rootBLItem.child(ie,0)
                ieinit = ""
                ierun = ""
                for ieph in range(tItem.rowCount()):
                    if tItem.child(ieph,0).text() == '_object':
                        elstr = str(tItem.child(ieph,1).text())
                        ieinit = elstr + "(" + ieinit
                        #for parent in (inspect.getmro(eval(elstr)))[:-1]:
                        #    for namef, objf in inspect.getmembers(parent):
                        #        if inspect.ismethod(objf):
                        #            if namef=="__init__" and\
                        #                inspect.getargspec(objf)[3] is not None:
                        #                initObj = objf
                        #                parentObj = parent

                for ieph in range(tItem.rowCount()):
                    if tItem.child(ieph,0).text() != '_object':
                        if tItem.child(ieph,0).text() == 'properties':#class properties
                            pItem = tItem.child(ieph,0)
                            for iep, arg_def in zip(range(pItem.rowCount()),
                                                          list(zip(*self.getParams(elstr))[1])):
                                paraname = pItem.child(iep,0).text()
                                paravalue = pItem.child(iep,1).text()
                                if str(paravalue) != str(arg_def):
                                    ieinit += str(paraname)+"="+str(paravalue)+","
                        elif tItem.child(ieph,0).text() != '_object': #class method
                            pItem = tItem.child(ieph,0)
                            for namef, objf in inspect.getmembers(eval(elstr)):
                                if inspect.ismethod(objf) and\
                                    namef== pItem.text():
                                        methodObj = objf
                            for imet in range(pItem.rowCount()):
                                if pItem.child(imet,0).text() == 'parameters':
                                    mItem = pItem.child(imet,0)
                                    for iep, arg_def in zip(range(mItem.rowCount()),
                                                                  inspect.getargspec(methodObj)[3]):
                                        paraname = mItem.child(iep,0).text()
                                        paravalue = mItem.child(iep,1).text()
                                        if str(paravalue) != str(arg_def):
                                            ierun += str(paraname)+"="+str(paravalue)+","
                                elif pItem.child(imet,0).text() == 'output':
                                    mItem = pItem.child(imet,0)
                                    paraOutput = ""
                                    for iep in range(mItem.rowCount()):
                                        paravalue = mItem.child(iep,1).text()
                                        paraOutput += str(paravalue)+", "
                            codeRunProcess += '\t{0} = {1}.{2}.{3}({4})\n'.format(paraOutput.rstrip(', '),
                                BLName, tItem.text(), pItem.text(), ierun.rstrip(','))


                codeBuildBeamline += '\t{0}.{1} = {2})\n'.format(BLName,
                     str(tItem.text()), ieinit.rstrip(','))
        codeBuildBeamline += "\treturn beamLine\n\n"
        codeRunProcess += "\toutDict = {"
        for ibm in range(self.beamModel.rowCount()):
            beamName = str(self.beamModel.item(ibm,0).text())
            if beamName != "None":
                codeRunProcess += '\'{0}\': {0},\n\t\t'.format(beamName)
        codeRunProcess = codeRunProcess.rstrip(",\n\t\t") + "}\n"
        codeRunProcess += "\treturn outDict\n\n"
        codeRunProcess += '{}.run_process = run_process\n'.format(xrtrun.__name__)


        for ie in range(self.rootPlotItem.rowCount()):
            ieinit = "\n\tplot = "
            tItem = self.rootPlotItem.child(ie,0)
            for ieph in range(tItem.rowCount()):
                if tItem.child(ieph,0).text() == '_object':
                    elstr = str(tItem.child(ieph,1).text())
                    ieinit += elstr + "("
                    for parent in (inspect.getmro(eval(elstr)))[:-1]:
                        for namef, objf in inspect.getmembers(parent):
                            if inspect.ismethod(objf):
                                if namef=="__init__" and inspect.getargspec(objf)[3] is not None:
                                    obj = objf
            for iepm, arg_def in zip(range(tItem.rowCount()-1),
                                          inspect.getargspec(obj)[3]):
                iep = iepm + 1
                if tItem.child(iep,0).text() != '_object':
                    pItem = tItem.child(iep,0)
                    if pItem.hasChildren():
                        for ieax in range(pItem.rowCount()):
                            if pItem.child(ieax,0).text() == '_object':
                                axstr = str(pItem.child(ieax,1).text())
                                ieinit = ieinit.rstrip("\n\t\t")
                                ieinit += "\n\t\t" + str(tItem.child(iep,0).text()) +\
                                    "="+ axstr + "("
                                for parentAx in (inspect.getmro(eval(axstr)))[:-1]:
                                    for namefAx, objfAx in inspect.getmembers(parentAx):
                                        if inspect.ismethod(objfAx):
                                            if namefAx=="__init__" and inspect.getargspec(objfAx)[3] is not None:
                                                objAx = objfAx
                        for ieaxm, arg_defAx in zip(range(pItem.rowCount()-1),
                                                      inspect.getargspec(objAx)[3]):
                            ieax = ieaxm + 1
                            paraname = pItem.child(ieax,0).text()
                            paravalue = pItem.child(ieax,1).text()
                            if paraname == "data" and paravalue != "auto":
                                paravalue = '{0}.get_{1}'.format(raycing.__name__,
                                                                paravalue)
                                ieinit += '{0}={1},'.format(paraname,paravalue)
                            if str(paravalue) != str(arg_defAx):
                                ieinit += '{0}={1},'.format(paraname,
                                                       self.quotize(paravalue))
                        ieinit = ieinit.rstrip(",") + "),\n\t\t"
                    else:
                        paraname = str(tItem.child(iep,0).text())
                        paravalue = tItem.child(iep,1).text()
                        if str(paravalue) != str(arg_def):
                            if paraname=="fluxKind":
                                ieinit += '{0}={1},'.format(paraname,
                                                   self.quotizeAll(paravalue))
                            else:
                                ieinit += '{0}={1},'.format(paraname,
                                                   self.quotize(paravalue))
            codeMain += ieinit.rstrip(",") + ")\n"
            codeMain += "\tplots.append(plot)\n"



        for ie in range(self.rootRunItem.rowCount()):
            if self.rootRunItem.child(ie,0).text() == '_object':
                elstr = str(self.rootRunItem.child(ie,1).text())
                codeMain += "\t" + elstr + "("
                objrr = eval(elstr)
                break
        #codeMain += "\t" + elstr + "("
        ieinit = ""
        for iem, argVal in zip(range(self.rootRunItem.rowCount()-1),
                                    inspect.getargspec(objrr)[3]):
            ie = iem + 1
            if self.rootRunItem.child(ie,0).text() != '_object':
                paraname = self.rootRunItem.child(ie,0).text()
                paravalue = self.rootRunItem.child(ie,1).text()
                if paraname == "plots":
                    paravalue = self.rootPlotItem.text()
                if str(paravalue) != str(argVal):
                    ieinit += str(paraname) + "=" + str(paravalue) + ",\n\t\t"

        codeMain += ieinit.rstrip(",\n\t\t") + ")\n"

        fullCode = codeDeclarations + codeBuildBeamline +\
            codeRunProcess + codeMain + codeFooter
        for xrtAlias in self.xrtModules:
            fullModName = (eval(xrtAlias)).__name__
            fullCode = str.replace(fullCode, fullModName, xrtAlias)
            codeHeader += 'import {0} as {1}\n'.format(fullModName, xrtAlias)
            #print xrt_alias, (eval(xrt_alias)).__name__
        fullCode = codeHeader + fullCode
        print fullCode

    def AlignBeam(self):
        print "self.beamModel.removeRow(1)"




if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    ex = xrtPrepTool()
    ex.setWindowTitle('xrtPrepTool')
    ex.show()
    sys.exit(app.exec_())