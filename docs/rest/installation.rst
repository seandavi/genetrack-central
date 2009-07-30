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

      > git clone git://github.com/ialbert/genetrack-central.git
   
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
and is located it the main directory. You will need to run all the following commands from a
command shell (terminal). Invoke the manager to see all the options::

     > genetrack.bat (or genetrack.sh)

First run the tests to ensure that the installation is correct.
In a command shell type::

     > genetrack.bat test

Three types of tests must pass. Django tests, functional tests and genetrack internal tests. 
Verify that all of them pass. 

You may pass multiple commands to the manager. 
To initialize your **Genetrack** server and populate it with some data you'll
have to write::

     > genetrack.bat init populate 

This initializes **GeneTrack** with the content of the comma separated file stored in
``home/init/initial-users.csv``. You may edit this file and add or remove users from it.
It is used to maintain an initial set of users. At any time you may add a 
new user to this list and rerun ``init`` command. You can also add users from
the administration interface. When you log into an account that has 
administration access you will see links that point to administration tasks.

If you want to delete all data and reset the system's content run ::

     > genetrack.bat delete

.. warning:: The ``delete`` command removes all data and users stored in **GeneTrack**

To completely reset your instance run the code below. Note that this 
also runs the jobserver and indexes the files that were populated before::

     > genetrack.bat delete init populate jobs

To start the server run::
     
     > genetrack.bat run

Visit http://127.0.0.1:8080 and log in as `admin`. A password has been generated for you and 
is located in the ``home/SECRET-KEY`` file. You may edit and replace the content of this file 
with something easier to remember then delete the content and repopulate. The ``populate`` command
adds project to the ``admin`` user.

To run jobs scheduled by **GeneTrack** execute::

     > genetrack.bat jobs

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

