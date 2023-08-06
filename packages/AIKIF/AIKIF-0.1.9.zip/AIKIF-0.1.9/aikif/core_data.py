#!/usr/bin/python3
# -*- coding: utf-8 -*-
# core_data.py
import os
    
class CoreData(object):
    """
    Base class for all core data objects
    """
    def __init__(self, name, data=None, parent=None):
        """ 
        define an object with a name
        """
        self.name = name
        self.data = data    # can be as detailed or simple as needed
        self.parent = parent
        self.child = []
        self.links = []
        
    def __str__(self):
        return self.name
    
    def format_csv(self, delim=',', qu='"'):
        """
        Prepares the data in CSV format
        """
        res = qu + self.name + qu + delim
        for d in self.data:
            res += qu + str(d) + qu + delim
        return res + '\n'
        
    def format_dict(self, delim=':', qu="'"):
        """
        Prepares the data as a dictionary with column headers
        TODO - get variable names of data[] as strings for hdr
        """
        res = 'name' + delim + qu + self.name + qu + ','
        for num, d in enumerate(self.data):
            res += 'col' + str(num) + delim + qu + str(d) + qu + ','
        return res
        
    def drill_down(self):
        """ 
        this WALKS down the tree to get the LIST of 
        nodes at the detail level (see expand to actually
        add the list of nodes
        
        TODO = processes need to be recalculated
        """
        return self.child_nodes
        
    def drill_up(self):  
        """
        returns the parent note - opposite of drill down
        TODO = processes need to be recalculated
        """
        return self.parent
    
    def expand(self, process, child_nodes):
        """
        this expands a current node by defining ALL the 
        children for that process
        TODO = processes need to be recalculated
        """
        #print('TODO: process check = ', process)
        #print(self.name, ' expanded to ->', child_nodes)
        self.child_nodes = []   # reset ??
        for n in child_nodes:
            self.child_nodes.append(Object(n, parent=self))

    def contract(self, process):
        """
        this contracts the current node to its parent and 
        then either caclulates the params and values if all 
        child data exists, OR uses the default parent data.
        (In real terms it returns the parent and recalculates)
        TODO = processes need to be recalculated
        """
        print('TODO: process check = ', process)
        print(self.name, ' contracted to ->', self.parent)
        return self.parent
    
    def get_child_by_name(self, name):
        """
        find the child object by name and return the object
        """
        for c in self.child_nodes:
            if c.name == name:
                return c
        return None
        
    def links_to(self, other, tpe):
        """
        adds a link from this thing to other thing
        using type (is_a, has_a, uses, contains, part_of)
        """
        if self.check_type(tpe):
            self.links.append(self.name, other, tpe)
        else:
            raise Exception('aikif.core_data cannot process this object type')
        
    def check_type(self, tpe):
        """
        TODO - fix this, better yet work out what the hell
        you are trying to do here.
        returns the type of object based on type string
        """
        valid_types = ['Object', 'Event', 'Location', 'Character', 'Process']
        for v in valid_types:
            if tpe == v:
                return True
        return False
        

class Object(CoreData):
    def __init__(self, name, data=None, parent=None):
        """
        Objects currently dont have any additional 
        data properties
        """
        CoreData.__init__(self, name, data, parent)
    
class Event(CoreData):
    def __init__(self, name, data=None, parent=None):
        """
        Events have a simple data structure
        date, category, remind_time, event
        """
        #data = [date, category, details]
        
        CoreData.__init__(self, name, data, parent)
        
    def __str__(self):
        return CoreData.__str__(self)
    
class Location(CoreData):
    def __init__(self, name, data=None, parent=None):
        """
        Locations are physical or virtual places
        data = ['Name', 'Phys|Virt', 'Location']
        """
        
        CoreData.__init__(self, name, data, parent)
        
    def __str__(self):
        return CoreData.__str__(self)
    
    
class Charater(CoreData):
    pass
    
class Process(CoreData):
    pass
    
class CoreTable(object):
    """
    Class to manage the collection of multiple CoreData 
    objects. Keeps everything as a list of objects such
    as Events, Locations, Objects, etc and handles the 
    saving, loading and searching of information.
    """
    def __init__(self, fldr, tpe, user, header):
        self.type = tpe
        self.user = user
        self.fldr = fldr
        self.table = []    # list of data - eg events, locations, etc
        self.header = header # mod_core.Event('Name', 'Date', 'Journal', 'Details')
        
    def __str__(self):
        res = ''
        res += ' type = ' + self.type + '\n'
        res += ' user = ' + self.user + '\n'
        res += ' fldr = ' + self.fldr + '\n'
        for e in self.table:
            res += e.format_csv()
        return res
    
    def get_filename(self, year):
        """
        returns the filename
        """
        res = self.fldr + os.sep + self.type + year + '.' + self.user 
        return res
    
    def add(self, e):
        self.table.append(e)

    def find(self, txt):
        result = []
        for e in self.table:
            if txt in e.data[0]:
                result.append(e)
                #print(e)
        return result
    
    def save(self):
        """
        save table to folder in appropriate files
        NOTE - ONLY APPEND AT THIS STAGE - THEN USE DATABASE
        """
            
        for e in self.table: 
            fname = self.get_filename('2015')
            with open(fname, 'a') as f:
                f.write(e.format_csv())
 
    def generate_diary(self):
        """
        extracts event information from core tables into diary files
        """
        print('TODO - generate diary files from Event rows only')
        for r in self.table:
            print('DIARY row of type('  + str(type(r)) + ') = ', r)
        
