REM wintest.bat
REM Copyright (c) 2018 Pablo Acosta-Serafini
REM See LICENSE for details
REM <<< EXCLUDE
CMD /c powershell.exe -Command "[guid]::NewGuid().ToString()" > uuid.txt
SET /p UUID=<uuid.txt
DEL uuid.txt
SET TMP_DIR=%Temp%\Test_%UUID%
SET ENV_DIR=%Temp%\appveyor_env
ECHO "Build directory=%TMP_DIR%"
MKDIR %TMP_DIR%
ECHO "Going to build directory"
CD %TMP_DIR%
ECHO "Setting environment variables"
SET PYTHON_MAJOR=2
SET INTERP=py37
SET PYVER=3.7
ECHO "Creating virtual environment"
python -m venv %ENV_DIR%
%ENV_DIR%\Scripts\activate.bat
ECHO "Cloning directory"
git clone --recursive https://pmacosta@bitbucket.org/pmacosta/sphinxcontrib-shellcheck.git %TMP_DIR%
IF "%~1" equ ":main" (
  SHIFT /1
  GOTO main
)
CMD /d /c "%~f0" :main %*
DEL %TMP_DIR%
EXIT /b
:main
echo "Start of CI output"
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
FOR %%i IN (%REPO_DIR%) DO @echo %%~ni> pkg_name.txt
SET /p PKG_NAME=<pkg_name.txt
SET PKG_NAME_ALT=sphinxcontrib
%PYTHONCMD% -c "import os, pip; print(os.path.dirname(os.path.realpath(pip.__path__[0])))" > python_site_packages_dir.txt
SET /p PYTHON_SITE_PACKAGES=<python_site_packages_dir.txt
SET REPO_DIR=%CD%
%PYTHONCMD% -c "from __future__ import print_function; import sys; print(sys.prefix)" > extra_dir.txt
SET /p EXTRA_DIR_BASE=<extra_dir.txt
SET EXTRA_DIR=%EXTRA_DIR_BASE%/share/%PKG_NAME%
SET SBIN_DIR=%EXTRA_DIR%\bin
SET RESULTS_DIR=%REPO_DIR%\results
SET SOURCE_DIR=%PYTHON_SITE_PACKAGES%\%PKG_NAME_ALT%
SET TRACER_DIR=%EXTRA_DIR%\docs\support
SET PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%PYTHON_SITE_PACKAGES%\%PKG_NAME_ALT%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
SET COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
SET REQUIREMENTS_FILE=%REPO_DIR%\requirements.txt
SET CITMP=%REPO_DIR%\CITMP
IF NOT EXIST "%CITMP%" MKDIR %CITMP%
SET PYLINT_PLUGINS_DIR=%EXTRA_DIR%\pylint_plugins
ECHO "PYTHONCMD=%PYTHONCMD%"
ECHO "PIPCMD=%PIPCMD%"
ECHO "PYTESTCMD=%PYTESTCMD%"
ECHO "INTERP=%INTERP%"
ECHO "PKG_NAME=%PKG_NAME%"
ECHO "PYTHON_SITE_PACKAGES=%PYTHON_SITE_PACKAGES%"
ECHO "REPO_DIR=%REPO_DIR%"
ECHO "EXTRA_DIR=%EXTRA_DIR%"
ECHO "SBIN_DIR=%SBIN_DIR%"
ECHO "RESULTS_DIR=%RESULTS_DIR%"
ECHO "SOURCE_DIR=%SOURCE_DIR%"
ECHO "TRACER_DIR=%TRACER_DIR%"
ECHO "PYTHONPATH=%PYTHONPATH%"
ECHO "COV_FILE=%COV_FILE%"
ECHO "REQUIREMENTS_FILE=%REQUIREMENTS_FILE%"
ECHO "PYLINT_PLUGINS_DIR=%PYLINT_PLUGINS_DIR%"
REM ###
REM # Install package dependencies
REM ###
CD %REPO_DIR%
%PIPCMD% install -r%REQUIREMENTS_FILE%
%PIPCMD% install codecov
%PIPCMD% freeze
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
ECHO "PKG_VERSION=%PKG_VERSION%"
CD %PYTHON_SITE_PACKAGES%
%PIPCMD% install --upgrade %REPO_DIR%\dist\%PKG_NAME%-%PKG_VERSION%.zip

REM # Write coverage configuration file
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
%PYTHONCMD% -c "from __future__ import print_function; import multiprocessing; print(multiprocessing.cpu_count())" > num_cpus.txt
SET /p NUM_CPUS=<num_cpus.txt
ECHO "NUM_CPUS=%NUM_CPUS%"
REM # Omitted tests are not Windows-specific and are handled by Travis-CI
%PYTHONCMD% %SBIN_DIR%\check_files_compliance.py -tps -d %SOURCE_DIR% -m %EXTRA_DIR%
REM # pylint 1.6.x appears to have a bug in Python 3.6 that is only going to be fixed with Pylint 2.0
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SOURCE_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SBIN_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\tests
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\docs\support
SET DODOCTEST=1
%PYTESTCMD% -n %NUM_CPUS% --collect-only --doctest-glob="*.rst" %EXTRA_DIR%\docs > doctest.log 2>&1 || SET DODOCTEST=0
IF %DODOCTEST%==1 %PYTESTCMD% --doctest-glob="*.rst" %EXTRA_DIR%\docs
SET DODOCTEST=1
%PYTESTCMD% -n %NUM_CPUS% --collect-only --doctest-modules %SOURCE_DIR% > doctest.log 2>&1 || SET DODOCTEST=0
IF %DODOCTEST%==1 %PYTESTCMD% -n %NUM_CPUS% --doctest-modules %SOURCE_DIR%
REM # Coverage tests runs all the unit tests, no need to run the non-coverage
REM # tests since the report is not being used
REM # - pytest -s -vv --junitxml=%RESULTS_DIR%\testresults\pytest.xml
%PYTESTCMD% -n %NUM_CPUS% --cov-config %COV_FILE% --cov %SOURCE_DIR% --cov-report term
REM # Re-building exceptions auto-documentation takes a long time in Appveyor.
REM # They have (and should be) spot-checked every now and then
REM # - python %SBIN_DIR%\build_docs.py -r -t -d %SOURCE_DIR%

REM <<< VERBATIM
REM on_failure:
REM >>> VERBATIM
7z a %EXTRA_DIR%\artifacts_%INTERP%.zip %EXTRA_DIR%\artifacts\*.*
appveyor PushArtifact %EXTRA_DIR%\artifacts_%INTERP%.zip
REM <<< EXCLUDE
EXIT /b
REM >>> EXCLUDE
