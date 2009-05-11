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
rem Default home directory will be the parent of the directory
rem that contains this batch script, change it as needed
rem
set BATCH_SCRIPT_DIR=%~dp0
set DEFAULT_HOME=%BATCH_SCRIPT_DIR%..

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

rem 
rem A few extra python paths  
rem
set PTYHON_PATH_1=%DEFAULT_HOME%\library;%DEFAULT_HOME%\library\library.zip

rem
rem Adding the development version of bx python on our machine
rem not needed if you have it installed otherwise
rem 
set PTYHON_PATH_2=%DEFAULT_HOME%;%DEFAULT_HOME%\..\bx-python-psu\lib


rem
rem Appends paths to the python import
rem
set PYTHONPATH=%PYTHONPATH%;%PYTHON_PATH_1%;%PYTHON_PATH_2%

if "%1"=="runserver" goto :runserver
if "%1"=="test" goto :test
if "%1"=="editor" goto :editor
if "%1"=="sphinx" goto :sphinx
if "%1"=="apidoc" goto :sphinx

echo.
echo USAGE:
echo.
echo     genetrack.bat runserver  (runs server)
echo     genetrack.bat test       (runs all tests)
echo     genetrack.bat sphinx     (generates documentation)
echo     genetrack.bat apidoc     (generates API html via epydoc)
echo     genetrack.bat editor     (starts the editor in environment)
echo     genetrack.bat jobrunner  (executes the jobrunner)

goto :eof

:runserver
echo.
echo *** Starting the test server ***
echo.
%PYTHON_EXE% %GENETRACK_SERVER_HOME%\manage.py runserver 127.0.0.1:8080
goto :eof

:test
echo.
echo *** running the tests
echo.
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

:sphinx
echo.
echo *** documentation generation ***
echo.
set DOC_DIR=%DEFAULT_HOME%\docs\rest
set BUILD_DIR=%DEFAULT_HOME%\docs\html
set EPYDOC_DIR=%BUILD_DIR%\epydoc
sphinx-build -b html %DOC_DIR% %BUILD_DIR%
if "%1"=="apidoc" epydoc --docformat restructuredtext genetrack -o %EPYDOC_DIR%
goto :eof

:jobrunner
echo.
echo *** executes jobrunner ***
echo.
%PYTHON_EXE% %DEFAULT_HOME%\genetrack\scripts\jobrunner.py %$
goto :eof