'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''

class TemplateView(object):
    
    def __init__(self, viewType):
        self.viewType = viewType
        
    def getView(self, viewType=None):
        if not viewType:
            viewType = self.viewType
        if viewType == 'form':
            pass
        elif viewType == 'tree_tree':
            pass
        elif viewType == 'tree_list':
            pass
        elif viewType == 'search':
            pass
        
        
        
        