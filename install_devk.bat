@echo off
setlocal
title Installing .devk handler...

:: Set target batch path in System32
set "launcher_path=%SystemRoot%\devk_launcher.bat"

echo Creating devk launcher at: %launcher_path%

:: Create the devk launcher
> "%launcher_path%" (
    echo @echo off
    echo REM os == windows
    echo REM name == update v1.0
    echo REM req == python
    echo REM creator == kingtoad-c
    echo REM source == github
    echo set "driver_file=%%~nx1"
    echo title %%driver_file%%
    echo echo Starting program: %%driver_file%%
    echo cls
    echo curl -s https://raw.githubusercontent.com/kingtoad-c/sys/refs/heads/main/logic.py ^| python - "%%driver_file%%"
    echo set /p "enter=click enter to finish..."
)

:: Add registry entries for .devk extension
echo Registering .devk file association...

reg add "HKEY_CLASSES_ROOT\.devk" /ve /d "devkfile" /f >nul
reg add "HKEY_CLASSES_ROOT\devkfile\shell\open\command" /ve /d "\"%launcher_path%\" \"%%1\"" /f >nul

echo.
echo .devk files will now open with the devk launcher!
echo You can now double-click any .devk file to run it.
pause
endlocal
