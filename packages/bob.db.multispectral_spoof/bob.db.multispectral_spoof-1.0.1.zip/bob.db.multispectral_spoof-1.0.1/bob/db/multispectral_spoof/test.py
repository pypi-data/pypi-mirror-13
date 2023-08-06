#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Thu Jan 10 18:27:00 CET 2013
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the Multispectral-Spoof database.
"""

import os, sys
import unittest
from . import Database

class NIRDatabaseTest(unittest.TestCase):
  """Performs various tests on the Multispectral-Spoof Face Spoofing database."""  

  
  def test01_dumplist(self):
    from bob.db.base.script.dbmanage import main
    self.assertEqual(main('multispectral_spoof dumplist --self-test'.split()), 0)

  def test02_checkfiles(self):
    from bob.db.base.script.dbmanage import main
    self.assertEqual(main('multispectral_spoof checkfiles --self-test'.split()), 0)
  
  def test03_manage_files(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('multispectral_spoof files'.split()), 0)
  
  def test04_query_obj(self):
    db = Database()
    
    fobj = db.objects()
    self.assertEqual(len(fobj), 4263) # number of all the images in the database (the enrollemnt data are not calculated)

    
    fobj = db.objects(cls='real')
    self.assertEqual(len(fobj), 1253) # number of real access images
    
    fobj = db.objects(cls='attack')
    self.assertEqual(len(fobj), 3010) # number of attack images in the database
    
    fobj = db.objects(cls='enroll')
    self.assertEqual(len(fobj), 209) # number of enrollment images in the database
    
    fobj = db.objects(cls='real', filters='vs')
    self.assertEqual(len(fobj), 630)
    
    fobj = db.objects(cls='real', filters='vs_vs')
    self.assertEqual(len(fobj), 0) 
    
    fobj = db.objects(cls='enroll', filters='vs_ir')
    self.assertEqual(len(fobj), 0) 
    
    fobj = db.objects(cls='real', groups='train', filters='vs')
    self.assertEqual(len(fobj), 270)
    
    fobj = db.objects(cls='real', groups='train', ids=1)
    self.assertEqual(len(fobj), 0) 
    
    fobj = db.objects(cls='real', groups='test', filters='ir', ids=22)
    self.assertEqual(len(fobj), 30)
    
    fobj = db.objects(cls='attack', filters='ir_ir')
    self.assertEqual(len(fobj), 744)
    
    fobj = db.objects(cls='attack', filters='ir')
    self.assertEqual(len(fobj), 0) 
    
    fobj = db.objects(cls='attack', filters='vs_ir', groups='train', ids=1)
    self.assertEqual(len(fobj), 0) 
    
    fobj = db.objects(cls='attack', filters='ir_vs', groups='dev', ids=1)
    self.assertEqual(len(fobj), 36)
    
    fobj = db.objects(filters=('ir', 'ir_ir'))
    self.assertEqual(len(fobj), 1367)  
 
    fobj = db.objects(filters=('ir', 'ir_vs'), ids=1)
    self.assertEqual(len(fobj), 66)
    
    
  def test05_query_obj(self):
    db = Database()
    
    fobj = db.objects(cls='attack', filters='vs_ir', ids=1)[0]
    self.assertFalse(fobj.is_real())
    self.assertEqual(fobj.get_filter(), 'vs_ir')
    self.assertTrue(fobj.is_visual_spectra_sample())
    self.assertFalse(fobj.is_visual_spectra_filter())
    self.assertEqual(fobj.get_clientid(), 1)
    self.assertEqual(fobj.get_orig_image_id(), 3)
    self.assertEqual(fobj.get_condition_id(), 2)
    fobj = db.objects(cls='real', filters='vs', ids=1)[0]
    self.assertEqual(fobj.get_orig_image_id(), None)
    self.assertEqual(fobj.get_condition_id(), 1)
    #self.assertTrue(os.path.exists(fobj.facefile()))
    
