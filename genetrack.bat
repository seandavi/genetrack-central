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
set PYTHON_PATH_2=%GENETRACK_HOME%library;%GENETRACK_HOME%library\library.zip

rem Adding the development version of bx python 
rem not needed if you have it already installed
set PYTHON_PATH_3=%GENETRACK_HOME%..\bx-dev\bx-python-psu\lib

rem
rem Appends paths to the python import
rem
set PYTHONPATH=%PYTHON_PATH_1%;%PYTHON_PATH_2%;%PYTHON_PATH_3%

if "%1"=="runserver" goto :runserver
if "%1"=="init" goto :init
if "%1"=="test" goto :test
if "%1"=="editor" goto :editor
if "%1"=="docs" goto :docs
if "%1"=="apidocs" goto :docs
if "%1"=="jobrunner" goto :jobrunner

rem  internal use, pushes the docs to the public server
if "%1" == "pushdoc" goto :pushdoc

echo USAGE:
echo.
echo     genetrack.bat init       (initializes the database)
echo     genetrack.bat runserver  (runs server)
echo     genetrack.bat test       (runs all tests)
echo     genetrack.bat docs       (generates documentation)
echo     genetrack.bat apidocs    (generates API html via epydoc)
echo     genetrack.bat jobrunner  (executes the jobrunner)
echo     genetrack.bat editor     (load the editor in the environment, win32)

goto :eof

:init
echo.
echo *** Initializing the data ***
echo.

rem skipping delete
if NOT "%2" == "delete" goto :skipdelete
echo *** Deleting existing data ***
del %GENETRACK_SERVER_HOME%\db\genetrack.db
rmdir /Q /S %GENETRACK_SERVER_HOME%\storage
rmdir /Q /S %GENETRACK_SERVER_HOME%\static\cache

: skipdelete
%PYTHON_EXE% %DJANGO_MANAGER% syncdb --noinput --settings=%DJANGO_SETTINGS_MODULE%
%PYTHON_EXE% -m genetrack.server.scripts.initializer %GENETRACK_SERVER_HOME%\init\initial-users.csv
goto :eof

:runserver
echo.
echo *** Starting the test server ***
echo.
%PYTHON_EXE% %DJANGO_MANAGER% syncdb --noinput --settings=%DJANGO_SETTINGS_MODULE%
%PYTHON_EXE% %DJANGO_MANAGER% runserver 127.0.0.1:8080 --settings=%DJANGO_SETTINGS_MODULE%
goto :eof

:test
echo.
echo *** running django tests
echo.
%PYTHON_EXE% %DJANGO_MANAGER% test --settings=server_settings

echo.
echo *** running server tests
echo.
%PYTHON_EXE% %GENETRACK_TESTDIR%\functional.py %2 %3 %4 %5 %6 %7 %8 %9

echo.
echo *** running genetrack tests
echo.
%PYTHON_EXE% %GENETRACK_TESTDIR%\runtest.py %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

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
echo *** documentation generation ***
echo.
set DOC_DIR=%GENETRACK_HOME%\docs\rest
set BUILD_DIR=%GENETRACK_HOME%\docs\html
set EPYDOC_DIR=%BUILD_DIR%\epydoc
sphinx-build -b html %DOC_DIR% %BUILD_DIR%
if "%1"=="apidocs" epydoc %2 %3 %4 %5 %6 %7 %8 %9 --docformat restructuredtext genetrack -o %EPYDOC_DIR% 
goto :eof

:jobrunner
echo.
echo *** executes jobrunner ***
echo.
%PYTHON_EXE% %GENETRACK_JOBRUNNER% %$
goto :eof

:pushdoc
echo.
echo *** pushing docs to webserver ***
echo.
rsync docs/html/* rsync -zav --rsh=ssh webserver@atlas.bx.psu.edu:~/www/genetrack.bx.psu.edu
goto :eof
