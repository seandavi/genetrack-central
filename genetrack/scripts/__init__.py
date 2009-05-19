"""
GeneTrack standalone scripts
============================

Note that each of these scripts exposes a full API and may be run in multiple ways. 
As independent scripts invoked via a shell command::

    python bed2genetrack.py

As python modules invoked via the python module loader::

    python -m genetrack.scripts.bed2genetrack

Or in other python scripts::

>>>
>>> from genetrack.scripts import bed2genetrack
>>> bed2genetrack( input_name, output_name, shift=0)
>>>

Most scripts take command line options of various types.

"""