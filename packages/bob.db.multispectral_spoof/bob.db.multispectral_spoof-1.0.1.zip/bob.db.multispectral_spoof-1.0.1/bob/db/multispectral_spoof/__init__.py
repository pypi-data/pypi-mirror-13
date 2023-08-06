#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed Jan  9 15:14:32 CET 2013

"""
The Multispectral-Spoof Face Spoofing database is a spoofing attack database which consists of two types of filters for real accesses: Visual Spectra (VS) and Near-Infrared (IR), as well as 4 types of filters of attacks: VS-VS, IR-IR, VS-IR and IR-VS. Each of the attacks is originally recorded in VS or IR, then printed and then recaptured in VS or IR.
"""

import os
import numpy
import string
import six
from bob.db.base import utils
from .models import *
from pkg_resources import resource_filename

class Database(object):

  def __init__(self):  
    from .driver import Interface
    self.info = Interface()
    self.location = resource_filename(__name__, '')
    self.groups = ('train', 'dev', 'test')
    self.classes = ('attack', 'real', 'enroll')
    self.filters = ('ir', 'vs', 'vs_vs', 'vs_ir', 'ir_vs', 'ir_ir')
    self.ids = range(1, 14) + range(15, 23) # client 14 is missing, there is a total of 21 clients, with client ids 1-13 and 15-22
    
  def clients(self, groups=('train', 'dev', 'test')):
    """Give a list of the clients given the specified criteria for the group"""
    # check if groups set are valid
    VALID_GROUPS = self.groups
    groups = self.check_validity(groups, "group", VALID_GROUPS, VALID_GROUPS)
    id_dict = {'train':[2,4,7,9,10,12,16,17,21], 'dev':[1,3,5,6,8,11], 'test':[13,15,18,19,20,22]}
    retval=[]
    for g in groups:
      retval = retval + id_dict[g]
    return retval  

  def check_validity(self, l, obj, valid, default):
      """Checks validity of user input data against a set of valid values"""
      if not l: return default
      elif isinstance(l, six.string_types) or isinstance(l, six.integer_types): return self.check_validity((l,), obj, valid, default) 
      for k in l:
        if k not in valid:
          raise RuntimeError, 'Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid)
      return l

  def get_file(self, pc):
    '''Returns the full file path given the path components pc'''
    from pkg_resources import resource_filename
    return resource_filename(__name__, os.path.join(pc))


  def objects(self, ids=[], groups=None, cls=None, filters=None):
    """Returns a list of unique :py:class:`.File` objects for the specific query by the user.

    Keyword Parameters:

    ids
      The id of the client whose videos need to be retrieved. Should be an integer number in the range 1-13 and 15-22

    groups
      One of the protocolar subgroups of data as specified in the tuple groups, or a
      tuple with several of them ('train','dev','test').  If you set this parameter to an empty string
      or the value None, we use reset it to the default which is to get all.

    cls
      Either "attack", "real", "enroll" or a combination of those (in a
      tuple). Defines the class of data to be retrieved.  If you set this
      parameter to an empty string or the value None, it will be set to the tuple ("real", "attack").

    filters
      Either "ir", "vs", "vs_vs", 'vs_ir', 'ir_ir', 'ir_vs' or any combination of those (in a
      tuple). Defines the type of filter. If you set this
      parameter to the value None, the videos of all filters are returned.

    Returns: A list of :py:class:`.File` objects.
    """

    # check if groups set are valid
    VALID_GROUPS = self.groups
    groups = self.check_validity(groups, "group", VALID_GROUPS, VALID_GROUPS)

    VALID_FILTERS = self.filters

    #import ipdb; ipdb.set_trace()
    if filters != None: # the type of filter depends on the class (different types of filters for real accesses and attacks)
      filters = self.check_validity(filters, "filter", VALID_FILTERS, VALID_FILTERS)
      if cls == None:
        if ('ir' in filters or 'vs' in filters) and 'vs_vs' not in filters and 'vs_ir' not in filters and 'ir_vs' not in filters and 'ir_ir' not in filters :
          VALID_CLASSES = ('real', 'enroll')
        elif ('vs_vs' in filters or 'vs_ir' in filters or 'ir_vs' in filters or 'ir_ir' in filters) and ('ir' not in filters and 'vs' not in filters):
          VALID_CLASSES = ('attack',)
        else:
          VALID_CLASSES = self.classes
      else:
          VALID_CLASSES = self.classes    
    else: 
        filters = self.check_validity(filters, "filter", VALID_FILTERS, VALID_FILTERS)     
        VALID_CLASSES = self.classes
    cls = self.check_validity(cls, "class", VALID_CLASSES, ('real', 'attack'))
    
    VALID_IDS = self.ids
    ids = self.check_validity(ids, "id", VALID_IDS, VALID_IDS)

    #import ipdb; ipdb.set_trace()
    retval = []
    client_ids = self.clients(groups) # train, test, dev
    for g in groups:
      client_ids = self.clients((g,))
      for i in ids:
        if i not in client_ids: continue
        for c in cls: # real, attack, enroll
          f = open(os.path.join(self.location, 'listfiles', c + '.txt'), 'r') # opening the list file
          all_files = [line[:-1] for line in f.readlines()] # omit the newline character \n at the end of line
          for f in filters: 
            if c == 'enroll':
              dirname = os.path.join('real', string.upper(f), 'enroll', g)
            elif c == 'real':
              dirname = os.path.join('real', string.upper(f), g)
            elif c == 'attack':
              dirname = os.path.join('attack', string.upper(string.replace(f,'_','/')), g)
                
            #import ipdb; ipdb.set_trace()    
            fnames = [fn for fn in all_files if string.find(fn, dirname) != -1] #the required filenames
          
            retfnames = [fn for fn in fnames if int(os.path.basename(fn).split('_')[0]) == i] # filtering by required ids
            retval = retval + [File(filename, c, g) for filename in retfnames] 
               
    return retval
        

__all__ = dir()
