'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.ElementTree as ElementTree


class FormView(object):
    def __init__(self, arch, model, fields, viewName, field_parent):
        self.arch = arch
        self.model = model
        self.fields = fields
        self.viewName = viewName
        self.field_parent = field_parent
    
    def computeArchRecursion(self, parent):
            for childElement in parent:
                childTag = childElement.tag
                if childTag == 'sheet':
                    print 'sheet'
                elif childTag == 'header':
                    print 'header'
                elif childTag == 'div':
                    print 'div'
                elif childTag == 'group':
                    print 'group'
                elif childTag == 'field':
                    print 'field'
                self.computeArchRecursion(childElement)
    
    def computeArch(self):
        if self.arch:
            etreeObj = ElementTree.fromstring(self.arch)
            self.computeArchRecursion(etreeObj)
                

    def loadId(self, odooId):
        pass
    
    