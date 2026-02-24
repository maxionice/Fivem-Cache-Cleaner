@echo off
:: ============================================================
:: build.bat – Local build script
:: ============================================================
:: Compiles main.py into a single standalone .exe using PyInstaller.
:: Run this script from the project root:
::
::     build.bat
::
:: The compiled executable will appear in:
::     dist\FiveM_Cache_Cleaner.exe
:: ============================================================

echo.
echo  Building FiveM_Cache_Cleaner.exe ...
echo  ============================================================

:: Run PyInstaller with the same flags used in GitHub Actions.
pyinstaller ^
    --onefile ^
    --console ^
    --name "FiveM_Cache_Cleaner" ^
    --distpath dist ^
    --workpath build\work ^
    --specpath build ^
    main.py

:: Check if the build succeeded.
if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] Build failed. See output above for details.
    pause
    exit /b 1
)

echo.
echo  [OK] Build successful!
echo       Output: dist\FiveM_Cache_Cleaner.exe
echo.
pause
