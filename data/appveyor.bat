REM appveyor.bat
REM Copyright (c) 2018-2019 Pablo Acosta-Serafini
REM See LICENSE for details
REM <<< EXCLUDE
@ECHO OFF
SET CWD=%CD%
python -c "import re, subprocess; lines, _ = subprocess.Popen(['git', 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE).communicate(); print(re.compile('.*@.*/(.*)/.*').match(lines.strip().decode()).groups()[0])" > origin_name.txt
SET /p ORIGIN_NAME=<origin_name.txt
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
python -m pip install --upgrade pip
ECHO Cloning repository
REM git clone --recursive https://%ORIGIN_NAMR%@bitbucket.org/%ORIGIN_NAMR%/sphinxcontrib-shellcheck.git
XCOPY C:\Users\%USERNAME%\sphinxcontrib-shellcheck %TMP_DIR%\sphinxcontrib-shellcheck /E
CD %TMP_DIR%\sphinxcontrib-shellcheck
SET PATH=C:\Program Files\7-Zip;C:\Users\%USERNAME%\bin\curl\bin;%PATH%
ECHO Start of CI output
REM >>> EXCLUDE
REM <<< VERBATIM
REM # yamllint disable rule:document-start
REM # yamllint disable rule:line-length

REM environment:
REM   matrix:
REM     - JOB: "2.7"
REM       INTERP: "py27"
REM       PYVER: "2.7"
REM     - JOB: "3.5"
REM       INTERP: "py35"
REM       PYVER: "3.5"
REM     - JOB: "3.6"
REM       INTERP: "py36"
REM       PYVER: "3.6"
REM     - JOB: "3.7"
REM       INTERP: "py37"
REM       PYVER: "3.7"

REM init:
REM   - echo "PYVER=%PYVER%"

REM install:
REM ###
REM # Set up environment variables
REM ###
REM >>> VERBATIM
SET
python --version
SET REPO_DIR=%CD%
SET RESULTS_DIR=%REPO_DIR%\results
REM ###
REM # Install shellcheck and bash binaries
REM ###
CD %REPO_DIR%
curl --output shellcheck-stable.zip https://storage.googleapis.com/shellcheck/shellcheck-stable.zip
7z -y e shellcheck-stable.zip
MOVE shellcheck-stable.exe shellcheck.exe
SET PATH=%REPO_DIR%;%PATH%
REM ###
REM # Create directories for reports and artifacts
REM ###
IF NOT EXIST "%RESULTS_DIR%\artifacts" mkdir %RESULTS_DIR%\artifacts

REM <<< VERBATIM
REM build_script:
REM >>> VERBATIM
python -m pip install -r%REPO_DIR%\data\requirements.txt

REM <<< VERBATIM
REM test_script:
REM >>> VERBATIM
CD %REPO_DIR%
SET PYTHONPATH=%CD%/sphinxcontrib;%PYTHONPATH%
pytest -s -x -vv tests\test_shellcheck.py

REM <<< VERBATIM
REM on_failure:
REM >>> VERBATIM
7z a %RESULTS_DIR%\artifacts_%INTERP%.zip %RESULTS_DIR%\artifacts\*.*
appveyor PushArtifact %RESULTS_DIR%\artifacts_%INTERP%.zip
REM <<< EXCLUDE
deactivate
CD %CWD%
RMDIR /Q /S %ENV_DIR%
RMDIR /Q /S %TMP_DIR%
REM >>> EXCLUDE
