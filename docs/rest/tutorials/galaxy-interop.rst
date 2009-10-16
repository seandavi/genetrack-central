Galaxy integration
==================

GeneTrack_ offers the option of visualizing data stored inside Galaxy_. Users may 
create a visualization inside Galaxy then select and view the results in GeneTrack. 
Finally they may run the genome wide peak prediction tool inside Galaxy. 
See the :doc:`galaxy-tools` for more use-case scenarios.

For this process to work properly both GeneTrack and Galaxy need to be installed 
onto the the same filesystem.  Galaxy will send the full file path 
to GeneTrack (validated via an encrypted message). Administrators
will need to set up matching secret authentication keys in both applications. 

Setup
-----

#. The first step is to install both Galaxy_ and GeneTrack_ according to the 
   instructions and verify that they both work.
#. Establish what domain (url) will both Galaxy and GeneTrack run under.
#. Enable the GeneTrack entries in ``tool_conf.xml``
#. Copy the file ``tool-data\shared\genetrack\genetrack_sites.txt.sample`` to ``genetrack_sites.txt`` 
   under the same directory.  
#. Edit the ``genetrack_sites.txt`` file to point to the url where GeneTrack is running on.
#. Modify the ``universe_wsgi.ini`` file and change the value for the ``tool_secret`` key 
   to a unique value. This value will need to be the same in GeneTrack (see next).
#. Modify your GeneTrack settings module (for example: ``server_settings.py``) such that the value of
   ``GALAXY_TOOL_SECRET`` is the same as above. Also modify the ``GALAXY_TOOL_URL`` setting to 
   point to the domain name that Galaxy runs under. 
#. Add the GeneTrack package to the python import path that Galaxy runs with. 
   To verify that the import can actually take place type::

      python -m genetrack.scripts.test

Your Galaxy instance is now ready to operate with GeneTrack. See the :doc:`galaxy-tools` page for more details.


.. _Galaxy: http://galaxy.psu.edu/
.. _GeneTrack: http://genetrack.bx.psu.edu/
