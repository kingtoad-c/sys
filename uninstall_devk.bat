@echo off
setlocal
title Uninstalling .devk handler...

:: Define launcher path
set "launcher_path=%SystemRoot%\devk_launcher.bat"

:: Delete the batch launcher
if exist "%launcher_path%" (
    echo Deleting launcher: %launcher_path%
    del /f /q "%launcher_path%"
) else (
    echo Launcher not found: %launcher_path%
)

:: Remove registry entries
echo Removing registry keys for .devk...

reg delete "HKEY_CLASSES_ROOT\.devk" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\devkfile" /f >nul 2>&1

echo.
echo ✅ .devk handler uninstalled successfully.
pause
endlocal
