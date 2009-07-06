GeneTrack Installation
======================

GeneTrack requires python2.5 or higher, numpy, pytables and chartdirector.
This latter is installed automatically.

Windows
-------

The installation on windows is the easiest. Download the
genetrack-dependencies.zip file, unpack it and install each of the programs. We even
include python2.5 for you (skip it if you have already installed
python).

In a command shell navigate to the genetrack distribution and type:

     genetrack.bat test
    
    
Mac OSX
-------

GeneTrack runs well on OS-X, the task is not complicated
but several steps need to be followed:

  1. Install XCode on your Mac (these are developer tools created by Apple)
  2. Install Macports from:
  
  3. The following is using Macports to install binaries. From
     a terminal install python2.6, numpy, setuptools and hdf5-18 like so:
        
        sudo port install python26
        sudo port install py26-setuptools
        sudo port install py26-numpy
           
  4. Now we need to install hdf then pytables and the latter needs us to specify the location of
     the location of the HDF libraries. For that we need to write:
     
        sudo port install hdf5-18
        export HDF5_DIR=/opt/local
        easy_install-2.6 tables
  
Run genetrack.sh test to verify that everything works.

Linux/Unix
----------

Follow the instructions given for Mac OSX but replace the 'port' program
with the package manager for your platform. You may be able to install
pytables directly.

