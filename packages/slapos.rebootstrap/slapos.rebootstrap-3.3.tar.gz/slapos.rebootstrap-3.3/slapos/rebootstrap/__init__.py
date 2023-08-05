##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import zc.buildout
import sys
import logging
import subprocess

def extension(buildout):
  Rebootstrap(buildout)()

class Rebootstrap:
  def __init__(self, buildout):
    self.logger = logging.getLogger(__name__)
    self.buildout = buildout
    # fetch section to build python, obligatory
    self.python_section = (
      buildout['buildout'].get('python') or \
      buildout['rebootstrap']['section']
    ).strip()
    self.wanted_python = buildout[self.python_section]['executable']

    # query for currently running python
    self.running_python = sys.executable

  def __call__(self):
    if self.running_python != self.wanted_python:
      self.install_section()
      self.reboot()

  def reboot(self):
    message = """
************ REBOOTSTRAP: IMPORTANT NOTICE ************
bin/buildout is being reinstalled right now, as new python:
  %(wanted_python)s
is available, and buildout is using another python:
  %(running_python)s
Buildout will be restarted automatically to have this change applied.
************ REBOOTSTRAP: IMPORTANT NOTICE ************
""" % dict(wanted_python=self.wanted_python,
    running_python=self.running_python)
    self.logger.info(message)
    args = map(zc.buildout.easy_install._safe_arg, sys.argv)
    env = os.environ
    env['ORIG_PYTHON'] = sys.executable
    os.execve(self.wanted_python, [self.wanted_python] + args, env)

  def install_section(self):
    env = os.environ
    if not os.path.exists(self.wanted_python):
      self.logger.info('Installing section %r to provide %r' % (
        self.python_section, self.wanted_python))
      args = map(zc.buildout.easy_install._safe_arg, sys.argv)
      if 'install' in args:
        args =  args[:args.index('install')]

      # remove rebootstrap extension, which is not needed in rebootstrap part
      extension_list = self.buildout['buildout']['extensions'].split()
      extension_list = [q.strip() for q in extension_list if q.strip() != \
          __name__]
      # rerun buildout with only neeeded section to reuse buildout
      # ability to calcuate all dependency
      args.extend([
        # install only required section with dependencies
        'buildout:parts=%s' % self.python_section,
        # do not load this extension
        'buildout:extensions=%s' % ' '.join(extension_list),
      ])
      self.logger.info('Rerunning buildout to install section %s with '
        'arguments %r.'% (self.python_section, args))
      process = subprocess.Popen(args)
      process.wait()
      if process.returncode != 0:
        raise zc.buildout.UserError('Error during installing python '
          'provision section.')
    if not os.path.exists(self.wanted_python):
      raise zc.buildout.UserError('Section %r directed to python executable:\n'
          '%r\nUnfortunately even after installing this section executable was'
          ' not found.\nThis is section responsibility to provide python (eg. '
          'by compiling it).' % (self.python_section, self.wanted_python))

_uninstall_part_orig = zc.buildout.buildout.Buildout._uninstall_part
def _uninstall_part(self, part, installed_part_options):
  _uninstall_part_orig(self, part, installed_part_options)
  try:
    location = self[part].get('location')
  except zc.buildout.buildout.MissingSection:
    return
  if location and sys.executable.startswith(location):
    message = """
************ REBOOTSTRAP: IMPORTANT NOTICE ************
%r part that provides the running Python is uninstalled.
Buildout will be restarted automatically with the original Python.
************ REBOOTSTRAP: IMPORTANT NOTICE ************
""" % part
    self._logger.info(message)
    if getattr(self, 'dry_run', False):
      sys.exit()
    args = map(zc.buildout.easy_install._safe_arg, sys.argv)
    env = os.environ
    orig_python = env['ORIG_PYTHON']
    os.execve(orig_python, [orig_python] + args, env)
zc.buildout.buildout.Buildout._uninstall_part = _uninstall_part
