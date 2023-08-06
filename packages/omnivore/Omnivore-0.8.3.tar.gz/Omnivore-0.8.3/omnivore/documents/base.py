import os
import tempfile
import shutil

class BaseParser(object):
    mime = None
    
    # List of supported filename extensions, including the leading ".".  If
    # multiple extensions are supported, put the most common one first so that
    # the file dialog will display that as the default.
    extensions = []
    
    name = "Abstract parser"
    
    def can_parse(self, metadata):
        return metadata.mime == self.mime
    
    def is_valid_extension(self, extension):
        return extension.lower() in self.extensions
    
    def get_pretty_extension_list(self):
        return ", ".join(self.extensions)
    
    def get_file_dialog_wildcard(self):
        # Using only the first extension
        wildcards = []
        if self.extensions:
            ext = self.extensions[0]
            wildcards.append("%s (*%s)|*%s" % (self.name, ext, ext))
        return "|".join(wildcards)
    
    def parse(self, guess):
        raise NotImplementedError
