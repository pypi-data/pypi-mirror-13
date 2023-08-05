# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from future.standard_library import install_aliases
install_aliases()
from builtins import *
# Needs requests library for HTTP and os library for system calls
import requests
import os

# This srcipt downloads the raasaft/own/, tutorials/ and replication/ 
# directories for raaSAFT into the current directory.

def main():
    # Test for internet
    try:
        requests.head("http://dx.doi.org/")
    except ConnectionError:
        print("Error: you must be connected to the internet.")
        return 1

    # Test for git
    if os.system("git --version") > 0:
        print('Error: please install "git" with your system package manager.')
        return 2
    
    # "Random" filename for temporary repo
    dirname = "rsftj23u9u12"
    
    # Get repo from github
    os.system('git clone https://bitbucket.org/asmunder/raasaft.git '+dirname)

    # Move the desired folders here
    os.system('mv '+dirname+'/replication/ .')
    os.system('mv '+dirname+'/tutorials/ .') 
    os.system('mv '+dirname+'/mysaft/ .') 

    # Delete archive and finish
    os.system('rm -rf '+dirname)
    print("Success: raaSAFT folders have been created in this directory.")
    return 0
