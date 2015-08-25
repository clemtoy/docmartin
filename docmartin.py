# -*- coding: utf-8 -*-
"""
Created on Mon Aug 03 09:54:20 2015

@author: Clement Michard
"""
import inspect
import re

class Markdown:
    
    def __init__(self, main_module, public_only, *modules):
        self.main_module = main_module
        self.public_only = public_only
        self.modules = modules
        self.f = None
        
    def write(self):
        with open('README.md', 'w') as f:
            self.f = f
            self.title(1, "Social network of movie characters")
            self.paragraph(self.main_module.__doc__)
            for module in self.modules:
                self.doc(f, module)
           
     
    def title(self, level, string):
        print >>self.f, '{0} {1}'.format('#' * level, string)


    def paragraph(self, string):
        for s in re.split(r'\n *\n', string):
            print >>self.f, s, '\n'
    
    
    def item(self, string):
        print >>self.f, '-', string
        
        
    def doc(self, f, module):
        self.title(2, module.__name__)
        if module.__doc__:
            descr = module.__doc__.split('\n\n', 1)
            self.paragraph('**{0}**'.format(descr[0]))
            if len(descr) > 1:
                self.paragraph(descr[1])
        functions = inspect.getmembers(module, lambda fct: inspect.isfunction(fct) and fct.__module__ == module.__name__)
        if functions:
            self.title(3, 'Functions')
        for fctname, fct in functions:            
            self.func(fctname, fct, level=4)
        classes = inspect.getmembers(module, lambda c: inspect.isclass(c) and c.__module__ == module.__name__)
        for classname, classobj in classes:
            bases = ' ({0})'.format(', '.join(b.__name__ for b in classobj.__bases__)) if classobj.__bases__ else ''
            self.title(3, 'class ' + classname + bases)
            if classobj.__doc__:
                for p, part in enumerate(re.split(r'\n *\n', classobj.__doc__)):
                    if p is 0:
                        self.paragraph('**{0}**'.format(part))
                    else:
                        attr, lst = part.split('\n', 1)
                        self.title(4, attr.replace(' ' * 4, '').rstrip(':'))
                        self.parse(lst)
                        self.paragraph('')
                        
            methods = inspect.getmembers(classobj, predicate=inspect.ismethod)
            if methods:
                self.title(4, 'Methods')
                for methodname, method in methods:
                    self.func(methodname, method)
                        
            staticfunctions = inspect.getmembers(classobj, predicate=inspect.isfunction)
            if staticfunctions:
                self.title(4, 'Static functions')
                for funcname, func in staticfunctions:
                    self.func(funcname, func, static=True)
              
              
    def isprivate(self, method):
        return method.__name__[:2] == '__' and method.__name__[-2:] != '__'
                
                
    def func(self, methodname, method, static=False, level=5):
        #static = ' *(static)*' if static else ''
        if self.public_only and self.isprivate(method): return
        self.title(level, method.__name__) # + static)
        self.paragraph(self.signature(method))
        self.parse(method.__doc__)
        
        
    def signature(self, method):
        allargs = inspect.getargspec(method)
        if allargs.defaults:
            defaults = ('-*-',) * (len(allargs.args) - len(allargs.defaults)) + allargs.defaults
        else:
            defaults = ('-*-',) * len(allargs.args)
        formatstrarg = lambda d: "'{0}'".format(d) if isinstance(d, str) else d
        formatarg = lambda a,d: '{0}={1}'.format(a, formatstrarg(d)) if d != '-*-' else a
        args = ', '.join(formatarg(a,d) for a, d in zip(allargs.args, defaults))
        varargs = ', *' + allargs.varargs if allargs.varargs else ''
        if not args:
            varargs = varargs[2:]
        return '`{0}({1}{2})`'.format(method.__name__, args, varargs)
        
        
    def parse(self, doc):
        if doc:
            lines = doc.split('\n')
            for line in lines:
                addline = False
                line = line.replace(' ' * 4, '')
                if ' -- ' in line:
                    arg, descr = line.split(' -- ')
                    self.item('`{0}` {1}'.format(arg, descr))
                    addline = True
                else:
                    if addline:
                        self.paragraph('')
                        addline = False
                    self.paragraph(line)
        else:
            self.paragraph('No documentation')
