@echo off
REM Download and install Miniconda, then create gnuradio environment

REM Set download URL and file name
set URL=https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe
set INSTALLER=Miniconda3-latest-Windows-x86_64.exe

REM Download Miniconda installer
echo Downloading Miniconda installer...
powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%INSTALLER%'"

REM Check if download was successful
if not exist "%INSTALLER%" (
    echo Failed to download Miniconda installer
    pause
    exit /b 1
)

REM Install Miniconda silently
echo Installing Miniconda...
start /wait "" "%INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3

REM Check if installation was successful
if not exist "%UserProfile%\Miniconda3\Scripts\conda.exe" (
    echo Miniconda installation failed
    pause
    exit /b 1
)

REM Initialize conda for cmd.exe
echo Initializing conda...
call "%UserProfile%\Miniconda3\Scripts\conda.exe" init cmd.exe

REM Create gnuradio environment
echo Creating gnuradio environment...
call "%UserProfile%\Miniconda3\Scripts\conda.exe" create -n gnuradio python=3.9 -y

REM Check if environment was created successfully
call "%UserProfile%\Miniconda3\Scripts\conda.exe" info --envs | findstr gnuradio >nul
if errorlevel 1 (
    echo Failed to create gnuradio environment
    pause
    exit /b 1
)

REM Activate the environment and install GNU Radio packages
echo Activating gnuradio environment and installing packages...
call "%UserProfile%\Miniconda3\Scripts\conda.exe" activate gnuradio
call "%UserProfile%\Miniconda3\Scripts\conda.exe" install -c conda-forge gnuradio gnuradio-iio -y

echo Installation completed successfully!
echo To activate the gnuradio environment, run: conda activate gnuradio
pause