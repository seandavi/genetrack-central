#!/bin/bash
 
echo '*********************'
echo 'GeneTrack Run Manager'
echo '*********************'
#
# set the python executable
#
export PYTHON_EXE=python
echo 'PYTHON='$PYTHON_EXE
 
#
# Setting environment variables
#
# Default home directory of the genetrack installation
#
# (the directory that contains this batch script)
#
if [ -z "$GENETRACK_HOME" ]; then
   export GENETRACK_HOME=`dirname $0`
fi

#
# The default server home directory
#
export GENETRACK_SERVER_HOME=$GENETRACK_HOME/home
echo GENETRACK_SERVER_HOME=$GENETRACK_SERVER_HOME

export HOSTNAME=`hostname -f`
export PORT=8080

export DJANGO_ADMIN=$GENETRACK_HOME/genetrack/server/manage.py
export TEST_DIR=$GENETRACK_HOME/tests
#
# This is only required when running it with django_admin.py
#
export DJANGO_SETTINGS_MODULE=server_settings
echo DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
echo '*********************'
 
# Adding genetrack and the server apps to the python path
export PYTHON_PATH_1=$GENETRACK_HOME:$GENETRACK_SERVER_HOME
 
# Adding libraries to the python path
export PYTHON_PATH_2=$GENETRACK_HOME/library:$GENETRACK_HOME/library/library.zip:$GENETRACK_HOME/library/chartdirector
 
#
# Appends paths to the python import
#
export PYTHONPATH=$PYTHON_PATH_1:$PYTHON_PATH_2
 
############### if statements

if [ $# == 0 ]; then
        echo Usage:
	echo '   $ genetrack.sh <command>'
	echo ''
	echo 'Multiple commands may be used in the same line:'
	echo '    $ genetrack.sh init populate jobs'
	echo ''
	echo 'Commands:'
	echo '    init       initializes the database'
	echo '    test       runs all tests'
    echo '    functest   runs functional tests'
    echo '    djangotest runs the django tests'
	echo '    docs       generates documentation'
	echo '    api        generates API html via epydoc'
	echo '    jobs       executes the jobrunner'
	echo '    run        runs server'
	echo '    delete     deletes all data in GeneTrack'
	echo '    populate   populates the system with test data'
fi

while (( "$#" )); do

if [ "$1" = "delete" ]; then 
    echo
    echo '*** Deleting all data ***'
    echo
    rm -f  $GENETRACK_SERVER_HOME/db/genetrack.db
    rm -rf $GENETRACK_SERVER_HOME/storage
    rm -rf $GENETRACK_SERVER_HOME/static/cache
fi

if [ "$1" = "init" ]; then 
    echo
    echo '*** Initializing the data ***'
    echo
    $PYTHON_EXE $DJANGO_ADMIN syncdb --noinput --settings=server_settings
    $PYTHON_EXE -m genetrack.server.scripts.initializer $GENETRACK_SERVER_HOME/init/initial-users.csv
fi

if [ "$1" = "populate" ]; then 
    echo
    echo '*** Populating GeneTrack ***'
    echo
    $PYTHON_EXE $TEST_DIR/populate.py
fi

if [ "$1" = "jobs" ]; then 
    echo
    echo '*** Running the jobs ***'
    echo
    $PYTHON_EXE genetrack/server/scripts/jobrunner.py
fi

if [ "$1" = "docs" ]; then 
    echo ''
    echo '*** Generating main documentation ***'
    echo ''
    export DOC_DIR=$GENETRACK_HOME/docs/rest
    export BUILD_DIR=$GENETRACK_HOME/docs/html
    export EPYDOC_DIR=$BUILD_DIR/epydoc
	sphinx-build -b html $DOC_DIR $BUILD_DIR
fi

if [ "$1" = "api" ]; then 
    echo ''
    echo '*** Generating api documentation ***'
    echo ''
    export BUILD_DIR=$GENETRACK_HOME/docs/html
    export EPYDOC_DIR=$BUILD_DIR/epydoc
	epydoc --parse-only --docformat restructuredtext genetrack -o $EPYDOC_DIR
fi

if [ "$1" = "run" ]; then 
    echo ''
    echo '*** Running webserver ***'
    echo ''
    $PYTHON_EXE $DJANGO_ADMIN syncdb --noinput --settings=$DJANGO_SETTINGS_MODULE
    $PYTHON_EXE $DJANGO_ADMIN runserver $HOSTNAME:$PORT --settings=$DJANGO_SETTINGS_MODULE
fi

if [ "$1" = "djangotest" ]; then 
    echo ''
    echo '*** Running django tests ***'
    echo ''
    $PYTHON_EXE $DJANGO_ADMIN test --settings=$DJANGO_SETTINGS_MODULE

fi

if [ "$1" = "functest" ]; then 
    echo ''
    echo '*** Running functional tests ***'
    echo ''
    $PYTHON_EXE $TEST_DIR/functional.py
fi

if [ "$1" = "test" ]; then 
    echo ''
    echo '*** Running genetrack tests ***'
    echo ''
    $PYTHON_EXE $TEST_DIR/runtest.py
fi

shift
done


