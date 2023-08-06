#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Jan 14 15:59:30 CET 2013

"""Multispectral-Spoof Face Spoofing Database implementation as antispoofing.utils.db.Database."""

import os
import six
from . import __doc__ as long_description
from . import File as MultispectralSpoofingFile, Database as MultispectralSpoofingDatabase
from antispoofing.utils.db import File as FileBase, Database as DatabaseBase

class File(FileBase):

  def __init__(self, f):
    """Initializes this File object with the bob.db.multispectral_spoof.File equivalent"""
    self.__f = f

  def videofile(self, directory=None):
    raise NotImplementedError, "This database does not contain video files"

  def facefile(self, directory=None):

    if directory!=None: 
      directory = os.path.join(directory, 'annotations')
    return self.__f.facefile(directory=directory)
  facefile.__doc__ = FileBase.facefile.__doc__

  def bbx(self, directory=None):
    return self.__f.bbx(directory=directory)
  bbx.__doc__ = FileBase.bbx.__doc__

  def load(self, directory=None, extension='.hdf5'):
    return self.__f.load(directory=directory, extension=extension)
  load.__doc__ = FileBase.bbx.__doc__

  def save(self, data, directory=None, extension='.hdf5'):
    return self.__f.save(data, directory=directory, extension=extension)
  save.__doc__ = FileBase.save.__doc__

  def make_path(self, directory=None, extension=None):
    return self.__f.make_path(directory=directory, extension=extension)
  make_path.__doc__ = FileBase.make_path.__doc__

  def get_client_id(self):
    return self.__f.get_clientid()
  get_client_id.__doc__ = FileBase.get_client_id.__doc__

  def is_real(self):
    return self.__f.is_real()
  is_real.__doc__ = FileBase.is_real.__doc__ 


class Database(DatabaseBase):
  __doc__ = long_description
  
  def __init__ (self, args=None):
    self.__db = MultispectralSpoofingDatabase()
    self.__kwargs = {}
    if args is not None:

      self.__kwargs = {
        'filters': args.multispectralspoof_filters,
      }
  __init__.__doc__ = DatabaseBase.__init__.__doc__

  def create_subparser(self, subparser, entry_point_name):
    from argparse import RawDescriptionHelpFormatter

    ## remove '.. ' lines from rst
    desc = '\n'.join([k for k in self.long_description().split('\n') if k.strip().find('.. ') != 0])

    p = subparser.add_parser(entry_point_name, 
        help=self.short_description(),
        description=desc,
        formatter_class=RawDescriptionHelpFormatter)

    p.add_argument('--filters', type=str, choices=self.__db.filters, dest='multispectralspoof_filters', nargs='+', help='Defines the filters of the videos in the database that are going to be used (if not set return all filters)')

    p.set_defaults(name=entry_point_name)
    p.set_defaults(cls=Database)
        
    return
  create_subparser.__doc__ = DatabaseBase.create_subparser.__doc__

  def name(self):
    from .driver import Interface
    i = Interface()
    return "Multispectral-Spoof Fase Spoofing database (%s)" % i.name()

  def version(self):
    from .driver import Interface
    i = Interface()
    return i.version()

  def short_description(self):
    return 'Multispectral-Spoof Face Spoofing database'
  short_description.__doc__ = DatabaseBase.short_description.__doc__
 
  def long_description(self):
    return Database.__doc__
  long_description.__doc__ = DatabaseBase.long_description.__doc__
 
  def implements_any_of(self, propname):
    if isinstance(propname, (tuple,list)):
      return 'image' in propname
    elif propname is None:
      return True
    elif isinstance(propname, six.string_types):
      return 'image' == propname

    # does not implement the given access protocol
    return False
 
  def __parse_arguments(self):

    filters = self.__kwargs.get('filters', self.__db.filters)
    if not filters: filters = self.__db.filters
    return filters

  def get_test_filters(self):
    raise NotImplementedError, "Test filters have not yet been implemented for this database"
  
  def get_filtered_test_data(self, filter):
    raise NotImplementedError, "Test filters have not yet been implemented for this database"

  def get_all_data(self, group=None):
    __doc__ = DatabaseBase.get_all_data.__doc__
    filters = self.__parse_arguments() 
    allReal   = self.__db.objects(cls='real',filters=filters, groups=group)
    allAttacks  = self.__db.objects(cls='attack',filters=filters, groups=group)

    return [File(f) for f in allReal], [File(f) for f in allAttacks]
  get_all_data.__doc__ = DatabaseBase.get_all_data.__doc__


  def get_train_data(self):
    __doc__ = DatabaseBase.get_train_data.__doc__
    return self.get_all_data('train')
    
  get_train_data.__doc__ = DatabaseBase.get_train_data.__doc__

  def get_devel_data(self):
    __doc__ = DatabaseBase.get_devel_data.__doc__
    return self.get_all_data('devel')
    
  get_devel_data.__doc__ = DatabaseBase.get_devel_data.__doc__

  def get_test_data(self):
    __doc__ = DatabaseBase.get_test_data.__doc__
    return self.get_all_data('test')
    
  get_test_data.__doc__ = DatabaseBase.get_test_data.__doc__

  
