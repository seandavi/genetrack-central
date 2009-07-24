#!/bin/bash
 
echo '*********************'
echo 'GeneTrack Run Manager'
echo '*********************'
 
echo
echo 'Environment variables:'
echo
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
export DEFAULT_HOME=`dirname $0`
 
#
# The default server home directory
#
export GENETRACK_SERVER_HOME=$DEFAULT_HOME/server
echo GENETRACK_SERVER_HOME=$GENETRACK_SERVER_HOME
 
#
# This is only required when running it with django_admin.py
#
export DJANGO_SETTINGS_MODULE=server.settings
echo DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
 
echo
echo '*********************'
echo
 
# Adding genetrack and the server apps to the python path
export PYTHON_PATH_1=$DEFAULT_HOME:$GENETRACK_SERVER_HOME
 
# Adding libraries to the python path
export PYTHON_PATH_2=$DEFAULT_HOME/library:$DEFAULT_HOME/library/library.zip
 
#
# Appends paths to the python import
#
export PYTHONPATH=$PYTHON_PATH_1:$PYTHON_PATH_2
 
############### if statements

if [ $# == 0 ]
    then echo 'USAGE:'
    echo
    echo 'genetrack.bat init (initializes the database)'
    echo 'genetrack.bat runserver (runs server)'
    echo 'genetrack.bat test (runs all tests)'
    echo 'genetrack.bat docs (generates documentation)'
    echo 'genetrack.bat apidoc (generates API html via epydoc)'
    echo 'genetrack.bat jobrunner (executes the jobrunner)'
    echo 'genetrack.bat editor (load the editor)'§
fi

if [ $1 == init ]
    then echo
    echo '*** Initializing the data ***'
    echo

    if [ $2 == delete ]
        then rm $GENETRACK_SERVER_HOME/data/db/genetrack.db
	rm -rf $GENETRACK_SERVER_HOME/data/storage
	rm -rf $GENETRACK_SERVER_HOME/data/static/cache
    fi
    $PYTHON_EXE $GENETRACK_SERVER_HOME/manage.py syncdb --noinput
    $PYTHON_EXE -m server.scripts.initializer $GENETRACK_SERVER_HOME/data/init/initial-users.csv

fi
 
if [ $1 == runserver ]
    then echo
    echo '*** Starting the test server ***'
    echo
    $PYTHON_EXE $GENETRACK_SERVER_HOME/manage.py syncdb --noinput
    $PYTHON_EXE $GENETRACK_SERVER_HOME/manage.py runserver 127.0.0.1:8080
fi
 
if [ $1 == test ]
    then echo
    echo '*** running django tests'
    echo
    $PYTHON_EXE $GENETRACK_SERVER_HOME/manage.py test
    
    echo 
    echo '*** running server tests'
    echo
    $PYTHON_EXE $DEFAULT_HOME/tests/functional.py $2 $3 $4 $5 $6 $7 $8 $9

    echo
    echo '*** running genetrack tests'
    echo
    $PYTHON_EXE $DEFAULT_HOME/tests/runtest.py $2 $3 $4 $5 $6 $7 $8 $9
fi
 
if [ $1 == editor ]
    then echo
    echo '*** Default editor start ***'
    echo
    $DefaultEditor &
fi
 
if [ $1 == docs ]
    then echo
    echo '*** documentation generation ***'
    echo
    export DOC_DIR=$DEFAULT_HOME/docs/rest
    export BUILD_DIR=$DEFAULT_HOME/docs/html
    export EPYDOC_DIR=$BUILD_DIR/epydoc
    $SPHINX -b html $DOC_DIR $BUILD_DIR
    if [ $1 == apidocs ];
	then $EPYDOC $2 $3 $4 $5 $6 $7 $8 $9 --docformat restructuredtext genetrack -o $EPYDOC_DIR
    fi
fi
 
if [ $1 == jobrunner ]
    then echo
    echo '*** executes jobrunner ***'
    echo
    $PYTHON_EXE $DEFAULT_HOME/server/scripts/jobrunner.py
fi
 
 
if [ $1 == pushdoc ] 
    then echo
    echo '*** pushing docs to webserver ***'
    echo
    $RSYNC docs/html/* rsync -zav --rsh=ssh webserver@atlas.bx.psu.edu:~/www/genetrack.bx.psu.edu
fi
 