REM wintest.bat
REM Copyright (c) 2018 Pablo Acosta-Serafini
REM See LICENSE for details
REM <<< EXCLUDE
@ECHO OFF
SET CWD=%CD%
CMD /c powershell.exe -Command "[guid]::NewGuid().ToString()" > uuid.txt
SET /p UUID=<uuid.txt
DEL uuid.txt
SET TMP_DIR=%Temp%\Test_%UUID%
SET ENV_DIR=%Temp%\appveyor_env
ECHO Build directory=%TMP_DIR%
MKDIR %TMP_DIR%
ECHO Going to build directory
CD %TMP_DIR%
ECHO Setting environment variables
SET PYTHON_MAJOR=2
SET INTERP=py37
SET PYVER=3.7
ECHO Creating virtual environment
python -m venv %ENV_DIR%
CALL %ENV_DIR%\Scripts\activate.bat
ECHO Cloning repository
REM git clone --recursive https://pmacosta@bitbucket.org/pmacosta/sphinxcontrib-shellcheck.git
XCOPY C:\Users\%USERNAME%\sphinxcontrib-shellcheck %TMP_DIR%\sphinxcontrib-shellcheck /E
CD %TMP_DIR%\sphinxcontrib-shellcheck
SET PATH=C:\Program Files\7-Zip;C:\Users\%USERNAME%\bin\curl\bin;%PATH%
ECHO Start of CI output
REM >>> EXCLUDE
REM <<< VERBATIM
REM install:
REM ###
REM # Set up environment variables
REM ###
REM >>> VERBATIM
SET
SET PYTHONCMD=python
SET PYTESTCMD=pytest
SET SHELLCHECK_TEST_ENV=1
SET PIPCMD=%PYTHONCMD% -m pip
%PYTHONCMD% -c "import os; print(os.path.basename(os.getcwd()))" > pkg_name.txt
SET /p PKG_NAME=<pkg_name.txt
%PYTHONCMD% -c "import os; print(os.path.basename(os.getcwd()).split('-')[0])" > pkg_name_alt.txt
SET /p PKG_NAME_ALT=<pkg_name_alt.txt
%PYTHONCMD% -c "import os, pip; print(os.path.dirname(os.path.realpath(pip.__path__[0])))" > python_site_packages_dir.txt
SET /p PYTHON_SITE_PACKAGES=<python_site_packages_dir.txt
SET REPO_DIR=%CD%
%PYTHONCMD% -c "from __future__ import print_function; import sys; print(sys.prefix)" > extra_dir.txt
SET /p EXTRA_DIR_BASE=<extra_dir.txt
SET EXTRA_DIR=%EXTRA_DIR_BASE%\share\%PKG_NAME%
SET SBIN_DIR=%EXTRA_DIR%\bin
SET RESULTS_DIR=%REPO_DIR%\results
SET SOURCE_DIR=%PYTHON_SITE_PACKAGES%\%PKG_NAME_ALT%
SET TRACER_DIR=%EXTRA_DIR%\docs\support
ECHO %PYTHONPATH%
SET PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%PYTHON_SITE_PACKAGES%\%PKG_NAME_ALT%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
SET COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
SET CITMP=%REPO_DIR%\CITMP
IF NOT EXIST "%CITMP%" MKDIR %CITMP%
SET PYLINT_PLUGINS_DIR=%EXTRA_DIR%\pylint_plugins
ECHO PYTHONCMD=%PYTHONCMD%
ECHO PIPCMD=%PIPCMD%
ECHO PYTESTCMD=%PYTESTCMD%
ECHO INTERP=%INTERP%
ECHO PKG_NAME=%PKG_NAME%
ECHO PKG_NAME_ALT=%PKG_NAME_ALT%
ECHO PYTHON_SITE_PACKAGES=%PYTHON_SITE_PACKAGES%
ECHO REPO_DIR=%REPO_DIR%
ECHO EXTRA_DIR=%EXTRA_DIR%
ECHO SBIN_DIR=%SBIN_DIR%
ECHO RESULTS_DIR=%RESULTS_DIR%
ECHO SOURCE_DIR=%SOURCE_DIR%
ECHO TRACER_DIR=%TRACER_DIR%
ECHO PYTHONPATH=%PYTHONPATH%
ECHO COV_FILE=%COV_FILE%
ECHO PYLINT_PLUGINS_DIR=%PYLINT_PLUGINS_DIR%
REM ###
REM # Install package dependencies
REM ###
CD %REPO_DIR%
%PIPCMD% install codecov
%PIPCMD% freeze
REM ###
REM # Install shellcheck and bash binaries
REM ###
curl --output shellcheck-stable.zip https://storage.googleapis.com/shellcheck/shellcheck-stable.zip
7z -y e shellcheck-stable.zip
MOVE shellcheck-stable.exe shellcheck.exe
SET PATH=%REPO_DIR%;%PATH%
REM ###
REM # Create directories for reports and artifacts
REM ###
IF NOT EXIST "%RESULTS_DIR%\\testresults" mkdir %RESULTS_DIR%\testresults
IF NOT EXIST "%RESULTS_DIR%\\codecoverage" mkdir %RESULTS_DIR%\codecoverage
IF NOT EXIST "%RESULTS_DIR%\\artifacts" mkdir %RESULTS_DIR%\artifacts

REM <<< VERBATIM
REM build_script:
REM ###
REM # Install package
REM ###
REM >>> VERBATIM
TYPE %REPO_DIR%\MANIFEST.in
%PYTHONCMD% setup.py sdist --formats=zip
TIMEOUT /t 5
REM # Change directory away from repository, otherwise pip does not install package
SET SHELLCHECK_CI_ENV=1
%PYTHONCMD% -c "import os, sys; sys.path.append(os.path.realpath('.'));import setup; print(setup.__version__)" > version.txt
SET SHELLCHECK_CI_ENV=
SET /p PKG_VERSION=<version.txt
ECHO PKG_VERSION=%PKG_VERSION%
CD %PYTHON_SITE_PACKAGES%
%PIPCMD% install --upgrade %REPO_DIR%\dist\%PKG_NAME%-%PKG_VERSION%.zip
REM # Write coverage configuration file
ECHO # .coveragerc_CI to control coverage.py during Appveyor runs > %COV_FILE%
ECHO [report] >> %COV_FILE%
ECHO show_missing = True >> %COV_FILE%
ECHO [run] >> %COV_FILE%
ECHO branch = True >> %COV_FILE%
ECHO data_file = %EXTRA_DIR%\.coverage_%INTERP% >> %COV_FILE%
ECHO include = %SOURCE_DIR%\shellcheck.py >> %COV_FILE%
ECHO omit = %SOURCE_DIR%\websupport\* >> %COV_FILE%
ECHO [xml] >> %COV_FILE%
ECHO output = %RESULTS_DIR%\codecoverage\coverage.xml >> %COV_FILE%
REM ###
%PYTHONCMD% %SBIN_DIR%\coveragerc_manager.py 'ci' 1 %INTERP% %PYTHON_SITE_PACKAGES%
TYPE %COV_FILE%
REM ###
REM # Change to tests sub-directory to mimic Tox conditions
REM ###
CD %EXTRA_DIR%\tests

REM <<< VERBATIM
REM test_script:
REM ###
REM # Run tests
REM ###
REM >>> VERBATIM
%PYTHONCMD% %SBIN_DIR%\check_files_compliance.py -tps -d %SOURCE_DIR% -m %EXTRA_DIR%
CD %SOURCE_DIR%
for %%i in (*.py) do pylint --rcfile=%EXTRA_DIR%\.pylintrc --ignore=websupport -f text --ignore=websupport -r no %%i
CD %SBIN_DIR%
for /r %%i in (*.py) do pylint --rcfile=%EXTRA_DIR%\.pylintrc -f text -r no %%i
CD %EXTRA_DIR%\tests
for /r %%i in (*.py) do pylint --rcfile=%EXTRA_DIR%\.pylintrc -f text -r no %%i
REM ###
CD %EXTRA_DIR%\tests
SET DODOCTEST=1
%PYTESTCMD% --collect-only --doctest-glob="*.rst" %EXTRA_DIR%\docs > doctest.log 2>&1 || SET DODOCTEST=0
IF %DODOCTEST%==1 %PYTESTCMD% --doctest-glob="*.rst" %EXTRA_DIR%\docs
SET DODOCTEST=1
%PYTESTCMD% --collect-only --doctest-modules %SOURCE_DIR% > doctest.log 2>&1 || SET DODOCTEST=0
IF %DODOCTEST%==1 %PYTESTCMD% --doctest-modules %SOURCE_DIR%
%PYTESTCMD% --cov-config %COV_FILE% --cov %SOURCE_DIR% --cov-report term

REM <<< VERBATIM
REM on_failure:
REM >>> VERBATIM
7z a %EXTRA_DIR%\artifacts_%INTERP%.zip %EXTRA_DIR%\artifacts\*.*
appveyor PushArtifact %EXTRA_DIR%\artifacts_%INTERP%.zip
REM <<< EXCLUDE
deactivate
CD %CWD%
RMDIR /Q /S %ENV_DIR%
RMDIR /Q /S %TMP_DIR%
REM >>> EXCLUDE
