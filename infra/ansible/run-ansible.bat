@echo off
REM Batch script to run Ansible commands inside the docker container on Windows (for cmd.exe).

REM Ensure the image is built (will be fast if cached)
docker build -t ansible-control -f "%~dp0Dockerfile.ansible" "%~dp0."

for %%I in ("%~dp0..\..") do set "PROJECT_ROOT=%%~fI"

set "REL_PATH="
if "%CD%" == "%PROJECT_ROOT%" (
    set "REL_PATH="
) else (
    set "CURRENT_DIR=%CD%"
    call set "REL_PATH=%%CURRENT_DIR:%PROJECT_ROOT%\=%%"
)

if defined REL_PATH (
    set "REL_PATH=%REL_PATH:\=/%"
)

REM Set up SSH volume mount if .ssh folder exists in user profile
set SSH_VOLUME=
if exist "%USERPROFILE%\.ssh" (
    set SSH_VOLUME=-v "%USERPROFILE%\.ssh:/root/.ssh:ro"
)

REM Run docker with the arguments
if defined REL_PATH (
    docker run --rm -it -v "%PROJECT_ROOT%:/workspace" -w "/workspace/%REL_PATH%" -v /var/run/docker.sock:/var/run/docker.sock %SSH_VOLUME% ansible-control %*
) else (
    docker run --rm -it -v "%PROJECT_ROOT%:/workspace" -w "/workspace" -v /var/run/docker.sock:/var/run/docker.sock %SSH_VOLUME% ansible-control %*
)
