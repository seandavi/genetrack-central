GeneTrack Installation
======================

On **Windows** installation is very straightforward. All packages are available 
as binary installers, no compilation is necessary. Download then double click each package. 
Some of them need to be unpacked and copied to the ``library`` folder.

On **Unix** type systems we recommend that you use a *package manager* (``apt-get``, ``yum`` on Linux 
or ``ports`` for MaxOSX) to install the proper dependecies for 
the **python** instance that you wish to use. When compiled separately 
you may need to add the ``HDF`` to the library load path like so ::

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/ialbert/usr/hdf5

See bottom of the page for :ref:`os-x-tips`.

Software requirements
---------------------

#. You will need to install the `Python <http://www.python.org/>`_ programming language of version *2.5* or higher.

#. Install `numpy <http://numpy.scipy.org/>`_. Make sure it matches the python version you have installed.

#. Install `pytables <http://www.pytables.org>`_. Make sure it matches the python version you have installed.

#. Install `git <http://git-scm.com/>`_ and check out the repository::

      git clone git://github.com/ialbert/genetrack-central.git
   
   We will provide downloadable packages later.

#. Install `django <http://www.djangoproject.com/>`_. 
   It is sufficent to download the compressed archive, unpack it then 
   place the ``django`` folder in ``library`` folder of the ``genetrack``
   distribution (installed above)

#. Install `chartdirector <http://www.advsofteng.com/download.html>`_ . You will need to 
   download the package that corresponds to your python version, 
   then move the library modules into the library folder of **GeneTrack**. When done the ``library`` folder
   will need to contain the file called ``pychartdir.py`` (and a few others like ``chartdir.dll`` or ``chartdir.so`` etc).
   For ``Unix`` type systems you will need to unpack the content of this
   :download:`fonts.tar.gz <static/fonts.tar.gz>` file in the ``library`` directory.
   
Running Genetrack
-----------------

The **GeneTrack** manager is called ``genetrack.bat`` on Windows and ``genetrack.sh`` on Unix type systems
and is located it the main directory. You will need to run the following commands from a
command shell (terminal). Invoke it to see all the options::

     genetrack.bat

First one should run the tests to ensure that the installation is correct.
In a command shell navigate to the genetrack distribution and type::

     genetrack.bat test

Three types of tests must pass. Django tests, functional tests and genetrack internal tests. 
Verify that all of them pass. Now run::

     genetrack.bat init

To populate the system with some data run (*this should be run from genetrack.bat*) make sure the environment is set up properly)::

     python tests/populate.py

If you want to delete all data and reset the system's content run ::

     genetrack.bat init delete

.. warning:: The command above deletes all data stored in **GeneTrack**

To start the server run::
     
     genetrack.bat runserver

Visit http://127.0.0.1:8080 and log in as `admin`. A password has been generated for you and 
is located in the ``home/SECRET-KEY`` file. You may edit and replace the content of this file 
with something easier to remember then delete the content and repopulate.

To run jobs scheduled by **GeneTrack** execute::

     genetrack.bat jobrunner

.. _os-x-tips:

Mac OSX tips
------------

**GeneTrack** runs well on OSX. Set up is not complicated
but somewhat tedious as several steps need to be followed in order and 
familiarity with basic system administration may be necessary:

  1. Install `XCode <http://developer.apple.com/tools/xcode/index.html>`_ on your Mac. 
     These are developer tools created by Apple you will need to register (free).

  2. Install `Macports <http://www.macports.org/>`_
  
  3. The following is using ``Macports`` to install binaries. From
     a terminal install ``python2.6``, ``numpy``, ``setuptools`` like so::
        
        $ sudo port install python26
        $ sudo port install py26-setuptools
        $ sudo port install py26-numpy
           
  4. Install ``hdf`` then ``pytables`` and the latter will ask us to 
     specify the location of the location of the HDF libraries. For that we need to write::
     
        $ sudo port install hdf5-18
        $ export HDF5_DIR=/opt/local
        $ easy_install-2.6 tables
  
  5. install django and bx-python::
  
        $ easy_install django
        
See above for details on running **GeneTrack**    

