GeneTrack Installation
======================

For **Windows** all packages are available as binaries, no compilation is necessary.
Download and double click each package. Some of them need to moved to the ``library`` folder.

On **Unix** type systems we recommend that you use a package manager 
to install the proper dependecies for the **python** instance that you wish to use.
You may need to add the ``HDF library`` to the library load path like so ::

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/ialbert/usr/hdf5

Installation
------------

#. You will need to install `python <http://www.python.org/>`_ version 2.5 or higher

#. Install `numpy <http://numpy.scipy.org/>`_. Make sure it matches the python version you have installed

#. Install `pytables <http://www.pytables.org>`_. Make sure it matches the python version you have installed

#. Install git and check out the repository::

      git clone git://github.com/ialbert/genetrack-central.git

#. Install `django <http://www.djangoproject.com/>`_. 
   It is sufficent to download the compressed archive, unpack it then 
   place the ``django`` folder in ``library`` folder of ``genetrack`` (see below)

#. Install `chartdirector <http://www.advsofteng.com/download.html>`_ . You will need to 
   download the package that corresponds to your python version, 
   then unpack the library into the library folder of GeneTrack. The ``library`` folder
   will need to contain the file called ``pychardir.py``

Running Genetrack
-----------------

In a command shell navigate to the genetrack distribution and type::

     genetrack.bat test

Three types of tests must pass. Django tests, functional tests and genetrack internal tests. 
Verify that all of them pass. Now run::

     genetrack.bat init

To populate the system with some data run (*this should be run from genetrack.bat*) make sure the environment is set up properly)::

     python tests/populate.py

If you want to delete all data and reset the system's content run::

     genetrack.bat init delete

Now run::
     
     genetrack runserver

Go to http://127.0.0.1:8080 and log in as `admin`. The password has been generated for you and 
is located in the ``home/SECRET-KEY`` file.

To run jobs scheduled by GeneTrack execute::

     genetrack jobrunner


Mac OSX tips:
-------------

GeneTrack runs well on OS-X, the task is not complicated
but several steps need to be followed:

  1. Install XCode on your Mac (these are developer tools created by Apple)
  2. Install Macports from:
  
  3. The following is using Macports to install binaries. From
     a terminal install python2.6, numpy, setuptools and hdf5-18 like so::
        
        sudo port install python26
        sudo port install py26-setuptools
        sudo port install py26-numpy
           
  4. Now we need to install hdf then pytables and the latter needs us to specify the location of
     the location of the HDF libraries. For that we need to write::
     
        sudo port install hdf5-18
        export HDF5_DIR=/opt/local
        easy_install-2.6 tables
  
  5. install django and bx-python::
  
        easy_install django
        easy_install genetrack
        
Navigate to a folder and verify that everything works::
    
    genetrack.sh test

