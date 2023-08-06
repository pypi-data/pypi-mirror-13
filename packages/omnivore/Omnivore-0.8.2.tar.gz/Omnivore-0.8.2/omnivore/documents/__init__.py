# All built-in recognizer plugins should be listed in this file so that the
# application can import this single file and determine the default plugins.
# In addition, a list of plugins is expected so that the framework can import
# all built-in plugins at once.
#
# A cog script is included to automatically generate the expected code. Test with::
#
#    cog.py __init__.py
#
# which prints to standard output. To place the generated code in the file, use::
#
#    cog.py -r __init__.py
#
# Note that the cog script works when called from the top directory (.i.e.  at
# the same level as the omnivore directory) or this directory.

# [[[cog
#import os
#import sys
#import inspect
#import imp
#
#from envisage.api import Plugin
#
#cwd = os.getcwd()
#cog.msg("working dir : %s" % cwd)
#path = os.path.dirname(os.path.join(cwd, cog.inFile))
#cog.msg("scanning dir: %s" % path)
#top = os.path.abspath(os.path.join(path, "../../..")) # so absolute imports of omnivore will work
#sys.path.append(top)
#cog.msg("top dir     : %s" % top)
#import glob
#cog.outl("parsers = []")
#source_files = glob.glob(os.path.join(path, "*.py"))
#source_files.sort()
#for filename in source_files:
#    if filename.endswith("__init__.py"):
#        continue
#    modname = filename.rstrip(".py").split("/")[-1]
#    module = imp.load_source(modname, filename)
#    members = inspect.getmembers(module, inspect.isclass)
#    names = []
#    for name, cls in members:
#        if hasattr(cls, 'can_parse') and not name.startswith("Base"):
#            # make sure class is from this module and not an imported dependency
#            if cls.__module__.startswith(modname):
#                names.append(name)
#    if names:
#       cog.outl("from %s import %s" % (modname, ", ".join(names)))
#       for name in names:
#           cog.outl("parsers.append(%s())" % name)
# ]]]*/
parsers = []
# [[[end]]]

import os

import logging
log = logging.getLogger(__name__)
progress_log = logging.getLogger("progress")

def get_document(guess):
    from omnivore.utils.file_guess import FileGuess
    
    for parser in parsers:
        log.debug("trying parser %s" % parser.name)
        if parser.can_parse(guess.metadata):
            log.debug(" loading using parser %s!" % parser.name)
            document = parser.parse_guess(guess)
            log.debug(" loaded layers: \n  %s" % "\n  ".join([str(a) for a in layers]))
            return parser, document
    return None, None
