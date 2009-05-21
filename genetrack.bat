@echo off

echo.
echo *********************
echo GeneTrack run manager
echo *********************
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
rem (the directory that contains this batch script)
rem
set DEFAULT_HOME=%~dp0

rem
rem The default server home directory
rem
set GENETRACK_SERVER_HOME=%DEFAULT_HOME%\server
echo GENETRACK_SERVER_HOME=%GENETRACK_SERVER_HOME%

rem
rem This is only required when running it with django_admin.py
rem 
set DJANGO_SETTINGS_MODULE=server.settings
echo DJANGO_SETTINGS_MODULE=%DJANGO_SETTINGS_MODULE%


rem Adding genetrack and the server apps to the python path
set PYTHON_PATH_1=%DEFAULT_HOME%;%GENETRACK_SERVER_HOME%

rem Adding libraries to the python path
set PYTHON_PATH_2=%DEFAULT_HOME%\library;%DEFAULT_HOME%\library\library.zip

rem Adding the development version of bx python 
rem not needed if you have it already installed
set PYTHON_PATH_3=%DEFAULT_HOME%\..\bx-dev\bx-python-psu\lib

rem
rem Appends paths to the python import
rem
set PYTHONPATH=%PYTHONPATH%;%PYTHON_PATH_1%;%PYTHON_PATH_2%;%PYTHON_PATH_3%

if "%1"=="runserver" goto :runserver
if "%1"=="test" goto :test
if "%1"=="editor" goto :editor
if "%1"=="docs" goto :docs
if "%1"=="apidoc" goto :docs
if "%1"=="jobrunner" goto :jobrunner


rem  internal use, pushes the docs to the public server
if "%1" == "pushdoc" goto :pushdoc

echo.
echo USAGE:
echo.
echo     genetrack.bat runserver  (runs server)
echo     genetrack.bat test       (runs all tests)
echo     genetrack.bat docs       (generates documentation)
echo     genetrack.bat apidoc     (generates API html via epydoc)
echo     genetrack.bat editor     (starts the editor in environment)
echo     genetrack.bat jobrunner  (executes the jobrunner)

goto :eof

:runserver
echo.
echo *** Starting the test server ***
echo.
%PYTHON_EXE% %GENETRACK_SERVER_HOME%\manage.py syncdb
%PYTHON_EXE% %GENETRACK_SERVER_HOME%\manage.py runserver 127.0.0.1:8080
goto :eof

:test
echo.
echo *** running the tests
echo.
%PYTHON_EXE% %DEFAULT_HOME%\tests\runtest.py %2 %3 %4 %5 %6 %7 %8 %9
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
goto :eof

:docs
echo.
echo *** documentation generation ***
echo.
set DOC_DIR=%DEFAULT_HOME%\docs\rest
set BUILD_DIR=%DEFAULT_HOME%\docs\html
set EPYDOC_DIR=%BUILD_DIR%\epydoc
sphinx-build -b html %DOC_DIR% %BUILD_DIR%
if "%1"=="apidoc" epydoc %2 %3 %4 %5 %6 %7 %8 %9 --docformat restructuredtext genetrack -o %EPYDOC_DIR% 
goto :eof

:jobrunner
echo.
echo *** executes jobrunner ***
echo.
%PYTHON_EXE% %DEFAULT_HOME%\genetrack\scripts\jobrunner.py %$
goto :eof

:pushdoc
echo.
echo *** pushing docs to webserver ***
echo.
rsync docs/html/* rsync -zav --rsh=ssh html/ webserver@atlas.bx.psu.edu:~/www/genetrack.bx.psu.edu
goto :eof
