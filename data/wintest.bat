REM wintest.bat
REM Copyright (c) 2018 Pablo Acosta-Serafini
REM See LICENSE for details
REM <<< EXCLUDE
set PYTHON_MAJOR=2
set INTERP=py27
set PYVER=2.7
REM >>> EXCLUDE
REM <<< VERBATIM
REM install:
REM ###
REM # Set up environment variables
REM ###
REM >>> VERBATIM
set
set PYTHONCMD=python
set PIPCMD=pip
set PYTESTCMD=py.test
set SHELLCHECK_TEST_ENV=1
set REPO_DIR=%CD%
for %%i in (%REPO_DIR%) do @echo %%~ni> pkg_name.txt
set /p PKG_NAME=<pkg_name.txt
set RESULTS_DIR=%REPO_DIR%\results
set REQUIREMENTS_FILE=%REPO_DIR%\requirements.txt
set CITMP=%REPO_DIR%\CITMP
set PYLINT_PLUGINS_DIR=%EXTRA_DIR%\pylint_plugins
if not exist "%CITMP%" mkdir %CITMP%
echo "INTERP=%INTERP%"
echo "PKG_NAME=%PKG_NAME%"
echo "PYTHONCMD=%PYTHONCMD%"
echo "PIPCMD=%PIPCMD%"
echo "PYTESTCMD=%PYTESTCMD%"
echo "REPO_DIR=%REPO_DIR%"
echo "RESULTS_DIR=%RESULTS_DIR%"
echo "REQUIREMENTS_FILE=%REQUIREMENTS_FILE%"
echo "CITMP=%CITMP%"
echo "PYLINT_PLUGINS_DIR=%PYLINT_PLUGINS_DIR%"
REM ###
REM # Install tools and dependencies of package dependencies
REM ###
set PATH=C:\\Miniconda-x64;C:\\Miniconda-x64\\Scripts;%PATH%
conda update -y conda
conda create -y --name %INTERP% python=%PYVER%
activate %INTERP%
which python
ps: wget https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
python get-pip.py
pip install --upgrade pip wheel
pip install --upgrade --ignore-installed setuptools
which python
which pip
pip --version
python -c "import os, pip; print(os.path.dirname(os.path.realpath(pip.__path__[0])))" > python_site_packages_dir.txt
set /p PYTHON_SITE_PACKAGES=<python_site_packages_dir.txt
set VIRTUALENV_DIR=C:\Miniconda-x64\envs\%INTERP%
set BIN_DIR=%VIRTUALENV_DIR%\Scripts
set SOURCE_DIR=%PYTHON_SITE_PACKAGES%\%PKG_NAME%
set EXTRA_DIR=%VIRTUALENV_DIR%\share\%PKG_NAME%
set SBIN_DIR=%EXTRA_DIR%\sbin
set PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
set TRACER_DIR=%EXTRA_DIR%\docs\support
set COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
echo "PYTHON_SITE_PACKAGES=%PYTHON_SITE_PACKAGES%"
echo "VIRTUALENV_DIR=%VIRTUALENV_DIR%"
echo "BIN_DIR=%BIN_DIR%"
echo "SOURCE_DIR=%SOURCE_DIR%"
echo "EXTRA_DIR=%EXTRA_DIR%"
echo "SBIN_DIR=%SBIN_DIR%"
echo "PYTHONPATH=%PYTHONPATH%"
echo "TRACER_DIR=%TRACER_DIR%"
echo "COV_FILE=%COV_FILE%"
REM ###
REM # Install package dependencies
REM ###
set OLD_PTYHON_PATH=%PYTHONPATH%
set PYTHONPATH=%REPO_DIR%;%REPO_DIR%\sbin;%PYTHONPATH%
cd %REPO_DIR%
pip install -r%REQUIREMENTS_FILE%
pip freeze
REM ###
REM # Create directories for reports and artifacts
REM ###
if not exist "%RESULTS_DIR%\\testresults" mkdir %RESULTS_DIR%\testresults
if not exist "%RESULTS_DIR%\\codecoverage" mkdir %RESULTS_DIR%\codecoverage
if not exist "%RESULTS_DIR%\\artifacts" mkdir %RESULTS_DIR%\artifacts

REM <<< VERBATIM
REM build_script:
REM ###
REM # Install package
REM ###
REM >>> VERBATIM
type %REPO_DIR%\MANIFEST.in
python setup.py sdist --formats=zip
timeout /t 5
REM # Change directory away from repository, otherwise pip does not install package
set PYTHONPATH=%OLD_PTYHON_PATH%
set SHELLCHECK_CI_ENV=1
python -c "import os, sys; sys.path.append(os.path.realpath('.'));import setup; print(setup.__version__)" > version.txt
set SHELLCHECK_CI_ENV=
set /p PKG_VERSION=<version.txt
echo "PKG_VERSION=%PKG_VERSION%"
cd %PYTHON_SITE_PACKAGES%
pip install --upgrade %REPO_DIR%\dist\%PKG_NAME%-%PKG_VERSION%.zip

REM # Write coverage configuration file
REM ###
python %SBIN_DIR%\coveragerc_manager.py 'ci' 1 %INTERP% %PYTHON_SITE_PACKAGES%
type %COV_FILE%
REM ###
REM # Change to tests sub-directory to mimic Tox conditions
REM ###
cd %EXTRA_DIR%\tests

REM <<< VERBATIM
REM test_script:
REM ###
REM # Run tests
REM ###
REM >>> VERBATIM
python -c "from __future__ import print_function; import multiprocessing; print(multiprocessing.cpu_count())" > num_cpus.txt
SET /p NUM_CPUS=<num_cpus.txt
ECHO "NUM_CPUS=%NUM_CPUS%"
REM # Omitted tests are not Windows-specific and are handled by Travis-CI
python %SBIN_DIR%\check_files_compliance.py -tps -d %SOURCE_DIR% -m %EXTRA_DIR%
REM # pylint 1.6.x appears to have a bug in Python 3.6 that is only going to be fixed with Pylint 2.0
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SOURCE_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SBIN_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\tests
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\docs\support
set DODOCTEST=1
pytest -n %NUM_CPUS% --collect-only --doctest-glob="*.rst" %EXTRA_DIR%\docs > doctest.log 2>&1 || set DODOCTEST=0
if %DODOCTEST%==1 pytest --doctest-glob="*.rst" %EXTRA_DIR%\docs
set DODOCTEST=1
pytest -n %NUM_CPUS% --collect-only --doctest-modules %SOURCE_DIR% > doctest.log 2>&1 || set DODOCTEST=0
if %DODOCTEST%==1 pytest -n %NUM_CPUS% --doctest-modules %SOURCE_DIR%
REM # Coverage tests runs all the unit tests, no need to run the non-coverage
REM # tests since the report is not being used
REM # - pytest -s -vv --junitxml=%RESULTS_DIR%\testresults\pytest.xml
pytest -n %NUM_CPUS% --cov-config %COV_FILE% --cov %SOURCE_DIR% --cov-report term
REM # Re-building exceptions auto-documentation takes a long time in Appveyor.
REM # They have (and should be) spot-checked every now and then
REM # - python %SBIN_DIR%\build_docs.py -r -t -d %SOURCE_DIR%

REM <<< VERBATIM
REM on_failure:
REM >>> VERBATIM
7z a %EXTRA_DIR%\artifacts_%INTERP%.zip %EXTRA_DIR%\artifacts\*.*
appveyor PushArtifact %EXTRA_DIR%\artifacts_%INTERP%.zip
