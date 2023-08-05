'''
Created on Sep 28, 2015

@author: andrei
'''

import cPickle as pickle
import glob
import sys
import os
from abc import ABCMeta, abstractmethod

import tools.auxiliary as auxiliary

class PersistentDictionaryAbstract():
    '''
    An abstract class for the persistence module.
    All inherited classes have a dictionary field `dic`.
    In the inherited classes it is required to implement the `add_item` method depending on the class role.
    '''
    __metaclass__ = ABCMeta

    def __init__(self):
        self.dic = {}
    
    def list_keys(self):
        '''
        List the dictionary.
        '''
        return self.dic.keys()
    
    def get_item(self, key):
        '''
        Get an item from the dictionary.
        '''
        try:
            value = self.dic[key]
        except KeyError:
            raise
        
        return value
    
    @abstractmethod
    def add_item(self, key, value=None):
        pass

class PersistentDictionaryCollection(PersistentDictionaryAbstract):
    '''
    The class operates with a dictionary of the persistent dictionaries.
    '''
    def __init__(self, dir_path):
        '''
        `dir_path` - path to a directory where the persistent dictionaries will be stored  
        '''
        
        #call parent constructor
        super(PersistentDictionaryCollection, self).__init__()
        
        self.dir_path = dir_path
        self.file_ext = '.pkl'
        
        #if the directory does not exist yet create it
        auxiliary.make_dirs(os.path.dirname(self.dir_path))
        #load already existing dictionaries
        self._init_existing_dics()
        
    def _init_existing_dics(self):
        '''
        Check the directory for pickle files, and load dictionaries if they exist.
        '''
        
        #get a list of files with the `file_ext` extention
        pkl_files = glob.glob(os.path.join(self.dir_path, '*' + self.file_ext))
        
        for pkl_file in pkl_files:
            #file_name without extension
            file_name = os.path.basename(pkl_file)[:-len(self.file_ext)]
            
            self.dic[file_name] = PersistentDictionary(file_name, os.path.join(self.dir_path, self._construct_file_name_ext(file_name)))
            
    def _construct_file_name_ext(self, name):
        '''
        Concatenate provided file name with `file_ext` extension, and return the resulting string.
        '''
        
        return name + self.file_ext
            
    def add_item(self, key, value=None):
        '''
        Create new `PersistentDictionary` and add it to `dic` with `key` key
        '''
        
        self.dic[key] = PersistentDictionary(key, os.path.join(self.dir_path, self._construct_file_name_ext(key)))
        
    def add_to_item(self, key, child_key, child_value):
        '''
        Add `child_key` : `child_value` pair to a persistent dictionary with the key `key`
        '''
        
        if key not in self.dic:
            self.dic[key] = PersistentDictionary(key, os.path.join(self.dir_path, self._construct_file_name_ext(key)))
        
        self.dic[key].add_item(child_key, child_value)

class PersistentDictionary(PersistentDictionaryAbstract):
    '''
    The class is responsible for keeping the dictionary persistent with the file system. 
    On the file system, the dictionary is stored in a pickle file.
    '''
    
    def __init__(self, key, file_path):
        '''
        `key` - in the "outside" code the object is known by this id.
        `file_path` - path to the pickle file where the dictionary is stored.
        '''
        
        #call parent constructor
        super(PersistentDictionary, self).__init__()
        
        self.key = key
        self.file_path = file_path
        
        #load the dictionary from a file if the file is already presented on the file system
        self._load_from_file()
        
    def _load_from_file(self):
        '''
        Read the predefined file and retrieve the dictionary from it if the file exists.
        '''
        try:
            self.dic = pickle.load(open(self.file_path, "rb" ))
        except Exception:
            pass
        
    #TODO: 
    # Implement a more advanced mechanism for updating data in the file.
    # Current implementation rewrites the whole file each time you change the dictionary.  
    def save_dic(self):
        '''
        Save the dictionary to the predefined file on the file system.
        '''
        pickle.dump(self.dic, open(self.file_path, "wb"))
    
    def add_item(self, key, value=None):
        '''
        Add `key` : `value` pair to the dictionary and save the changes to the file system. 
        '''
        self.dic[key] = value
        
        #save changes on the file system
        self.save_dic()
