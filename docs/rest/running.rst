Running Genetrack
=================

Genetrack manager
-----------------

The **GeneTrack** manager is called ``genetrack.bat`` on Windows and ``genetrack.sh`` on Unix type systems
and is located it the main directory. The following commands must be run from a
command shell (terminal). Invoke the manager to see all the options::

     > genetrack.bat 

User or ``genetrack.sh`` on Mac and Unix. Next run the tests to ensure 
that the installation is correct. In a command shell type::

     > genetrack.bat test

Verify that the tests pass. You may pass multiple commands to the manager. 
To initialize your **Genetrack** server and populate it with some demo data you may
write::

     > genetrack.bat init populate 

This initializes **GeneTrack** with the content of the comma separated file stored in
``home/init/initial-users.csv``. You may edit this file and add or remove users from it.
It is used to maintain an initial set of users. At any time you may add a 
new user to this list and rerun the ``init`` command. You can also add users from
the administration interface. When you log into an account that has 
administration access you will see links that point to administration tasks.

If you want to delete all data and reset the system's content run ::

     > genetrack.bat delete

.. warning:: The ``delete`` command removes all data and users stored in **GeneTrack**

To run jobs scheduled by **GeneTrack** execute::

     > genetrack.bat jobs

To start the server run::
     
     > genetrack.bat run

Visit http://127.0.0.1:8080 and log in as `admin`. A password has been generated for you and 
is located in the ``home/SECRET-KEY`` file. Use the content of this file as the password
when logging in as ``admin`` user. The ``populate`` command above has also created 
a number of projects and uploads for the ``admin`` user. Thus upon logging in
this user will see some projects and files belonging to them. This is used to 
allow for an easily evaluation of the capabilities offered by **GeneTrack**.

To **completely reset** your instance run the code below. Note that this 
also runs the jobserver and indexes the files::

     > genetrack.bat delete init populate jobs

