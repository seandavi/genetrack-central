export PYTHON_EXE=python
export GENETRACK_HOME=`pwd`
export GENETRACK_SERVER_HOME=$GENETRACK_HOME/home
export DJANGO_SETTINGS_MODULE=server_settings
 
# Adding genetrack and the server apps to the python path
export PYTHON_PATH_1=$GENETRACK_HOME:$GENETRACK_SERVER_HOME
 
# Adding libraries to the python path
export PYTHON_PATH_2=$GENETRACK_HOME/library:$GENETRACK_HOME/library/library.zip:export PYTHON_PATH_2=$GENETRACK_HOME/library:$GENETRACK_HOME/library/library.zip:$GENETRACK_HOME/library/chartdirector
 
#
# Appends paths to the python import
#
export PYTHONPATH=$PYTHON_PATH_1:$PYTHON_PATH_2
