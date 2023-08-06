# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt4 import QtGui, QtCore
import numpy
from scipy import interpolate
from guidata.dataset.datatypes import ActivableDataSet
from guidata.dataset.dataitems import FileOpenItem, BoolItem, ButtonItem
import guidata
import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
from  guidata.dataset import datatypes
from guidata.dataset import dataitems
from guidata.dataset.datatypes import DataSet, BeginGroup, EndGroup, ValueProp
from guidata.dataset.dataitems import BoolItem, FloatItem
from pySAXS.guisaxs.qt import plugin
from pySAXS.LS import background
from pySAXS.guisaxs import dataset
prop1 = ValueProp(False)
prop2 = ValueProp(False)

classlist=['ChangeQRange'] #need to be specified

class ChangeQRange(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="Multiply Q Range"
    icon="edit_remove.png"
    
    def execute(self):
        datalist=[]
        if self.parent.backgrounddata is not None:
            datalist=[self.parent.backgrounddata]
        datalist+=self.ListOfDatasChecked()
        
        items = {
        "factorValue": dataitems.FloatItem("Factor : ",0.0,unit=''),
        }
        clz = type("Multiply Q Range :", (datatypes.DataSet,), items)
        self.form = clz()
        if self.form.edit():
            #ok
            self.calculate()
            
    def calculate(self):
        name=self.selectedData
        q=self.data_dict[name].q
        i=self.data_dict[name].i
        error=self.data_dict[name].error
        fn=self.data_dict[name].filename
        self.factorValue=self.form.factorValue
        if self.factorValue!=0.0:
                nq=q*float(self.factorValue)
                self.data_dict[name+'-qranged']=dataset.dataset(name+'-qranged',nq,i,filename=fn,\
                                                   parameters=None,error=error,\
                                                   parent=[name])
                
        self.parent.redrawTheList()
        self.parent.Replot()
            