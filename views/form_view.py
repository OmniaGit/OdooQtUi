'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import xml.etree.ElementTree as ElementTree
import utilsView


class FormView(object):
    def __init__(self, arch, fieldsNameTypeRel):
        self.arch = arch
        self.fieldsNameTypeRel = fieldsNameTypeRel

    def computeArchRecursion(self, parent):
            for childElement in parent:
                childTag = childElement.tag
                if childTag == 'sheet':
                    self.computeArchRecursion(childElement)
                elif childTag == 'header':
                    print 'header'
                elif childTag == 'div':
                    self.computeArchRecursion(childElement)
                elif childTag == 'group':
                    self.computeArchRecursion(childElement)
                elif childTag == 'field':
                    fieldObj = utilsView.computeField(childElement, self.fieldsNameTypeRel)

    def computeArch(self):
        if self.arch:
            etreeObj = ElementTree.fromstring(self.arch)
            self.computeArchRecursion(etreeObj)

    def loadIds(self, odooIds):
        for odooId in odooIds:
            pass
            break
