@echo off

:: Check Docker installation and status
docker version >nul 2>&1
if %errorlevel% neq 0 (
	echo Docker is not running or installed.
	pause
    exit /b 1
)

:: Set container name
set "container_name=fiware-temporal"

:: Verify if any container with that name exists
echo Verifying if any container with this prefix exists: %container_name%
docker ps -a --filter "name=%container_name%" --format "{{.Names}}" | findstr /i "%container_name%" >nul 2>&1
if %errorlevel% neq 0 (
    echo Container with "%container_name%" prefix does not exist.
    cd fiwareenv
	docker-compose up -d
	cd ..
) else (
    echo Container with "%container_name%" prefix found.
    cd fiwareenv
	docker-compose up -d
	cd ..
)
echo.
echo Press a button to continue activating Python virtual environment
pause

:: Check if user has permission to activate a virtual environment
powershell -Command "if ((Get-ExecutionPolicy) -ne 'RemoteSigned') { Set-ExecutionPolicy Bypass -Scope CurrentUser -Force }"

:: Attempt to activate virtual environment in either .venv or venv
if exist .\.venv\Scripts\activate.bat (
    call .\.venv\Scripts\activate.bat
) else if exist .\venv\Scripts\activate.bat (
    call .\venv\Scripts\activate.bat
) else (
    echo Virtual environment activation script not found in .venv or venv.
    pause
    exit /b 1
)

:: Verify if the environment was activated successfully
python -c "import sys; print(sys.prefix)" | findstr /i "venv" >nul
if %errorlevel% neq 0 (
    echo "Failed to activate the virtual environment."
    pause
    exit /b 1
) else (
    echo "Virtual environment activated successfully."
    pause
)

echo.
echo Press a button to start the web application
pause
start python udtBackEnd/manage.py runserver
pause

echo.
echo Press a button to start the Python module
pause
call python main.py
