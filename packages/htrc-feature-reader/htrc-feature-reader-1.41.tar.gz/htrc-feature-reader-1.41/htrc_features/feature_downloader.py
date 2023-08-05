from __future__ import unicode_literals
import logging

class FeatureDownloader(object):
    
    def __init__(self):
        
        # Test for Rsync
        try:
            subprocess.check_call("rsync", shell=True)
        except:
            logging.error("Rsync doesn't appear to be on your system. "
                    "If you are using Windows, the most common way to use "
                    "Rsync is through Cygwin. Note that this Python call to "
                    "Rsync only works when Python is running for the same "
                    "environment as Rsync is installed."
