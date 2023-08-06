#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Jan 10 18:05:42 CET 2013

"""Bob Database Driver entry-point for the Multispectral-Spoof Face spoofing Database.
"""

import os
import sys
from bob.db.base.driver import Interface as BaseInterface
from . import Database

# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  #from .__init__ import Database
  db = Database()

  objects = db.objects(groups=args.group, cls=args.cls, filters=args.filter)

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for obj in objects:
    output.write('%s\n' % (obj.make_path(directory=args.directory, extension=args.extension),))

  return 0

def checkfiles(args):
  """Checks the existence of the files based on your criteria""" 
    
  #from .__init__ import Database
  db = Database()

  objects = db.objects(groups=args.group, cls=args.cls, filters=args.filter)

  # go through all files, check if they are available on the filesystem
  good = []
  bad = []
  for obj in objects:
    if os.path.exists(obj.make_path(directory=args.directory, extension=args.extension)): good.append(obj)
    else: bad.append(obj)

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  if bad:
    for obj in bad:
      output.write('Cannot find file "%s"\n' % (obj.make_path(directory=args.directory, extension=args.extension),))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(objects), args.directory))

  return 0

class Interface(BaseInterface):

  def name(self):
    return 'multispectral_spoof'

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('bob.db.%s' % self.name())[0].version
    
  def files(self):
    from pkg_resources import resource_filename
    raw_files = ('real.txt',
      'enroll.txt',
      'attack.txt',)
    return [resource_filename(__name__, k) for k in raw_files]  

  def type(self):
    return 'text'

  def add_commands(self, parser):  
    """Add specific subcommands that the action "dumplist" can use"""

    from . import __doc__ as docs
    
    subparsers = self.setup_parser(parser, 
        "Multispectral-Spoof Face Spoofing Database", docs)

    from argparse import SUPPRESS
    
    db = Database()

    # add the dumplist command
    dump_message = "Dumps list of files based on your criteria"
    dump_parser = subparsers.add_parser('dumplist', help=dump_message)
    dump_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('-c', '--class', dest="cls", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.classes)
    dump_parser.add_argument('-g', '--group', dest="group", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups)
    dump_parser.add_argument('-f', '--filter', dest="filter", default=None, help="if given, this value will limit the output files to those belonging to a specific filter. (defaults to '%(default)s')", choices=db.filters)
    dump_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    dump_parser.set_defaults(func=dumplist) #action

    # add the checkfiles command
    check_message = "Check if the files exist, based on your criteria"
    check_parser = subparsers.add_parser('checkfiles', help=check_message)
    check_parser.add_argument('-d', '--directory', dest="directory", default='', help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('-c', '--class', dest="cls", default=None, help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=db.classes)
    check_parser.add_argument('-g', '--group', dest="group", default=None, help="if given, this value will limit the output files to those belonging to a particular group. (defaults to '%(default)s')", choices=db.groups)
    check_parser.add_argument('-f', '--filter', dest="filter", default=None, help="if given, this value will limit the output files to those belonging to a specific filter. (defaults to '%(default)s')", choices=db.filters)
    check_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    check_parser.set_defaults(func=checkfiles) #action
