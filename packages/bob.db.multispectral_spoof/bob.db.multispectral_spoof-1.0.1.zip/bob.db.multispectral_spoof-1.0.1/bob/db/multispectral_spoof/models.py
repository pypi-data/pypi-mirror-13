#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed Jan  9 15:23:51 CET 2013
import os
import bob.io.base
import bob.db.base
import numpy

class File(object):
  """ Generic file container """

  def __init__(self, filename, cls, group):

    self.filename = filename
    self.cls = cls # 'attack' or 'real'
    self.group = group # 'train', 'dev' or 'test's
    
  def __repr__(self):
    return "File('%s')" % self.filename

  def get_file(self, pc):
    '''Returns the full file path given the path components pc'''
    from pkg_resources import resource_filename
    return resource_filename(__name__, os.path.join(pc))

  def make_path(self, directory=None, extension=None):
    """Wraps this files' filename so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """

    if not directory: directory = ''
    if not extension: extension = ''
    return os.path.join(directory, self.filename + extension)
    
  def is_real(self):
    """True if the file belongs to a real access, False otherwise """

    return bool(self.cls == 'real')
    
  def get_filter(self):
    """The type of filter. Can be 'vs or 'ir' for real accesses and 'vs_vs, 'ir_ir, 'vs_ir' and 'ir_vs' for attacks"""
    
    basename = os.path.basename(self.filename) 
    if self.is_real():
      if int(basename.split('_')[1]) == 0:
        return 'vs'
      else:
        return 'ir'  
    else: # an attack
      for f in ['vs_vs', 'vs_ir', 'ir_vs', 'ir_ir']:
        if basename.find(f) != -1:
          return f
    
  def get_orig_image_id(self):
    """The ID of the original image used to perform the spoofing attack. It is the second stem of the basename for the spoofing attacks and can be 1, 2 or 3. Returns None for real access files"""
    
    basename = os.path.basename(self.filename) 
    if self.is_real():
      return None
    else: # an attack
      return int(basename.split('_')[1])
    
  def get_condition_id(self):
    """The ID of the recording condition. It is the fourth stem of the basename for the real accesses and the fifth for spoofing attacks. For real access files it can have values from 1-6, for spoofing attacks from 1-3"""
    
    basename = os.path.basename(self.filename) 
    if self.is_real():
      return int(basename.split('_')[3])
    else: # an attack
      return int(basename.split('_')[4])  
    
  def is_visual_spectra_filter(self):
    """True if the file belongs to an image recorded in VS (refers whether the final filter is taken in VS, which means VS filter for the recaptured images in the case of attacks)"""
    
    return bool(self.get_filter() in ['vs', 'vs_vs', 'ir_vs'])
    
  def is_visual_spectra_sample(self):
    """True if the file belongs to an image sample in VS (refers whether the initial filter is taken in VS, which means VS filter for the original images in the case of attacks)"""
    
    return bool(self.get_filter() in ['vs', 'vs_vs', 'vs_ir'])  
      

  def get_clientid(self):
    """The ID of the client. That is the first stem of the basename of the filename"""

    return int(os.path.basename(self.filename).split('_')[0]) # the identity stem of the basename of the filename


  def imagefile(self, directory=None):
    """Wraps this files' filename so that a complete path to an image file is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.
      
    Returns a string containing the newly generated file path.
    """
    if directory == None: directory=''
        
    return self.make_path(directory, '.pgm')    
    

  def facefile(self, directory=None):
    """Returns the path to the companion face bounding-box file

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.
      
    Returns a string containing the face file path.
    """

    if directory == None: directory=''
        
    return self.make_path(directory, '.pos')    
    
  
  def bbx(self, directory=None, offset=30): #!!!!!!! THIS NEEDS TO BE REWRITTEN
    """Reads the file containing the face annotations for the current file

    Keyword parameters:

    directory
      A directory name that will be prepended to the final filepaths where the
      face annotations are located, if not on the current directory.

    Returns:
      A :py:class:`numpy.ndarray` containing information about the face bounding boxes in the videos. The dimension of this object is 1x5. The five columns of the
      :py:class:`numpy.ndarray` are (all integers):

      * 0 (int)
      * Bounding box top-left X coordinate (int)
      * Bounding box top-left Y coordinate (int)
      * Bounding box width (int)
      * Bounding box height (int)

    """
    annot = numpy.loadtxt(self.facefile(directory), skiprows=1, dtype=int)
    
    topx = annot[12,0] - offset # X coordinate of point 13
    topy = annot[13,1] - offset # Y coordinate of point 14 
    width = annot[15,0] - annot[12,0] + offset # X coordinates of points 13 and 16
    height = annot[11,1] - annot[13,1] + offset # Y coordinates of points 12 and 14
    
    bbx = numpy.ndarray([1,5], dtype=int)
    bbx[0,:] = numpy.array([topx, topy, width, height])
    return bbx
 

  def load(self, directory=None, extension='.hdf5'):
    """Loads the data at the specified location and using the given extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      [optional] If not empty or None, this directory is prefixed to the final
      file destination

    extension
      [optional] The extension of the filename - this will control the type of
      output and the codec for saving the input blob.
    """
    return bob.io.base.load(self.make_path(directory, extension))


  def save(self, data, directory=None, extension='.hdf5'):
    """Saves the input data at the specified location and using the given
    extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      If not empty or None, this directory is prefixed to the final file
      destination

    extension
      The extension of the filename - this will control the type of output and
      the codec for saving the input blob.
    """

    path = self.make_path(directory, extension)
    bob.io.base.create_directories_safe(os.path.dirname(path))
    bob.io.base.save(data, path)



