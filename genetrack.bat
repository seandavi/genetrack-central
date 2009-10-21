@echo off

echo.
echo *********************
echo GeneTrack Run Manager
echo *********************
echo.
echo Environment variables:
echo.
rem
rem set the python executable
rem
set PYTHON_EXE=C:\Python25\python.exe -tu
echo PYTHON=%PYTHON_EXE%

rem
rem Setting environment variables
rem
rem Default home directory of the genetrack installation
rem
rem (extracts the directory name that contains this batch script)
rem
set GENETRACK_HOME=%~dp0

rem
rem The default server home directory
rem

set GENETRACK_SERVER_HOME=%GENETRACK_HOME%home
echo GENETRACK_HOME=%GENETRACK_HOME%
echo GENETRACK_SERVER_HOME=%GENETRACK_SERVER_HOME%

rem
rem This is only required when running it with django_admin.py
rem 
set DJANGO_SETTINGS_MODULE=server_settings
echo DJANGO_SETTINGS_MODULE=%DJANGO_SETTINGS_MODULE%

rem
rem setting some handy shortcuts
rem
set DJANGO_MANAGER=%GENETRACK_HOME%genetrack\server\manage.py
set GENETRACK_JOBRUNNER=%GENETRACK_HOME%genetrack\server\scripts\jobrunner.py
set GENETRACK_TESTDIR=%GENETRACK_HOME%tests

echo.
echo *********************
echo.

rem Adding genetrack and the server apps to the python path
set PYTHON_PATH_1=%GENETRACK_HOME%;%GENETRACK_SERVER_HOME%

rem Adding libraries to the python path
set PYTHON_PATH_2=%GENETRACK_HOME%library;%GENETRACK_HOME%library\library.zip;%GENETRACK_HOME%library\chartdirector 

rem Adding the development version of bx python 
rem not needed if you have it already installed
set PYTHON_PATH_3=%GENETRACK_HOME%..\bx-dev\bx-python-psu\lib

rem
rem Appends paths to the python import
rem
set PYTHONPATH=%PYTHON_PATH_1%;%PYTHON_PATH_2%;%PYTHON_PATH_3%

if (%1)==() goto :usage

:top
   if (%1)==() goto :eof
   if "%1"=="run" goto :run
   if "%1"=="init" goto :init
   if "%1"=="delete" goto :delete
   if "%1"=="populate" goto :populate
   if "%1"=="test" goto :test
   if "%1"=="djangotest" goto :djangotest
   if "%1"=="functest" goto :functest
   if "%1"=="editor" goto :editor
   if "%1"=="docs" goto :docs
   if "%1"=="api" goto :api
   if "%1"=="jobs" goto :jobs
   if "%1"=="push" goto :push
   goto :usage
   :back
   shift
goto :top

rem  internal use, pushes the docs to the public server
if "%1" == "pushdoc" goto :pushdoc

:usage

echo USAGE:
echo.
echo     genetrack.bat command
echo.
echo Where command can be any of:
echo     init, docs, api, test, jobrunner, runserver
echo.
echo Multiple commands may be used in the same line:
echo     genetrack.bat init populate jobrunner
echo.
echo Commands:
echo     init      initializes the database
echo     test      runs genetrack tests
echo     functest  runs genetrack functional tests
echo     docs      generates documentation
echo     api       generates API html via epydoc
echo     jobs      executes the jobrunner
echo     run       runs server
echo     delete    deletes all data in GeneTrack
echo     populate  populates the system with test data

goto :eof

:init
echo.
echo *** Initializing the data ***
echo.
%PYTHON_EXE% %DJANGO_MANAGER% syncdb --noinput --settings=%DJANGO_SETTINGS_MODULE%
%PYTHON_EXE% -m genetrack.server.scripts.initializer %GENETRACK_SERVER_HOME%\init\initial-users.csv
goto :back

:delete
echo.
echo *** Deleting all data ***
echo.
del %GENETRACK_SERVER_HOME%\db\genetrack.db
rmdir /Q /S %GENETRACK_SERVER_HOME%\storage
rmdir /Q /S %GENETRACK_SERVER_HOME%\static\cache
goto :back

:populate
echo.
echo *** Populating all data ***
echo.
%PYTHON_EXE% tests/populate.py
goto :back

:jobs
echo.
echo *** Executes jobrunner ***
echo.
%PYTHON_EXE% %GENETRACK_JOBRUNNER% %$
goto :back

:run
echo.
echo *** Starting the test server ***
echo.
%PYTHON_EXE% %DJANGO_MANAGER% syncdb --noinput --settings=%DJANGO_SETTINGS_MODULE%
%PYTHON_EXE% %DJANGO_MANAGER% runserver 127.0.0.1:8000 --settings=%DJANGO_SETTINGS_MODULE%
goto :eof

:test
echo.
echo *** Running genetrack tests
echo.
%PYTHON_EXE% %GENETRACK_TESTDIR%\runtest.py %2 %3 %4 %5 %6 %7 %8 %9
goto :back

:functest
echo.
echo *** Running functional tests
echo.
%PYTHON_EXE% %GENETRACK_TESTDIR%\functional.py %2 %3 %4 %5 %6 %7 %8 %9
goto :back

:djangotest
echo.
echo *** Running django tests
echo.
%PYTHON_EXE% %DJANGO_MANAGER% test --settings=server_settings
goto :back

:editor
rem 
rem Starts the windows editor with the proper environment variables set
rem Create a shortcut to this
rem 
echo.
echo *** windows editor start ***
echo.

cmd /c "c:\Program Files\EditPlus 2\editplus.exe"

REM cmd /c "C:\Program Files\ActiveState Komodo Edit 5\komodo.exe"

goto :eof

:docs
echo.
echo *** Main documentation generation ***
echo.
set DOC_DIR=%GENETRACK_HOME%\docs\rest
set BUILD_DIR=%GENETRACK_HOME%\docs\html
set EPYDOC_DIR=%BUILD_DIR%\epydoc
sphinx-build -b html %DOC_DIR% %BUILD_DIR%
if "%1"=="apidocs" epydoc %2 %3 %4 %5 %6 %7 %8 %9 --docformat restructuredtext genetrack -o %EPYDOC_DIR% 
goto :back

:api
echo.
echo *** API documentation generation ***
echo.
set DOC_DIR=%GENETRACK_HOME%\docs\rest
set BUILD_DIR=%GENETRACK_HOME%\docs\html
set EPYDOC_DIR=%BUILD_DIR%\epydoc
epydoc %2 %3 %4 %5 %6 %7 %8 %9 --docformat restructuredtext genetrack -o %EPYDOC_DIR% 
goto :back

:push
echo.
echo *** Pushing docs to webserver ***
echo.
rsync docs/html/* rsync -zav --rsh=ssh webserver@atlas.bx.psu.edu:~/www/genetrack.bx.psu.edu
goto :eof
