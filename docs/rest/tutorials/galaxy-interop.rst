Galaxy interoperability
=======================

GeneTrack_ offers the option of visualizing data stored inside Galaxy_. Users may 
create a visualization inside Galaxy then select and view the results in GeneTrack. 
Finally they may run the genome wide peak prediction tool back inside Galaxy. 
See the :doc:`galaxy-tutorial` for more use-case scenarios.

For this process to work properly both GeneTrack and Galaxy need to be installed 
onto the the same filesystem.  Galaxy will send the full file path 
to GeneTrack (validated via an encrypted message). Administrators
will need to set up matching secret authentication keys in both applications. 

Basic setup
-----------

#. The first step is to install both Galaxy_ and GeneTrack_ according to the 
   instructions and verify that they both work.
#. Establish what domain (URL) will both Galaxy and GeneTrack run under.
#. Copy the file ``tool-data\shared\genetrack\genetrack_sites.txt.sample`` to ''genetrack_sites.txt`` 
   under the same directory.  Edit this file to point to the url where GeneTrack is running on.
#. Modify the ``universe_wsgi.ini`` file and change the value for the ``tool_secret`` key 
   to a unique value (make it a long string). This value will need to be the same in GeneTrack (see next).
#. Modify your GeneTrack settings module (for example: yoursetting.py) such that the value of
   ``GALAXY_TOOL_SECRET`` is the same as above. Also modify the ``GALAXY_TOOL_URL`` name to 
   have the same domain name that Galaxy runs as. This will be the url that GeneTrack will
   use to submit the job.
#. Add the GeneTrack package to the python import path that Galaxy runs with. 
   The goal is to allow python to import the GeneTrack package within 
   the tools that it runs. To verify that the import can actually take place type::

   python -m genetrack.scripts.test



.. _Galaxy: http://galaxy.psu.edu/
.. _GeneTrack: http://genetrack.bx.psu.edu/
