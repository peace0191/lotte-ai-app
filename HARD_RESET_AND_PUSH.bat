@echo off
echo ========================================================
echo [Hard Reset] Cleaning up commit history completely...
echo ========================================================
git reset --soft HEAD~1
git reset HEAD data/Docker_Desktop_Installer.exe
git rm --cached -f data/Docker_Desktop_Installer.exe
del /f /q "data\Docker_Desktop_Installer.exe"
echo data/Docker_Desktop_Installer.exe >> .gitignore

echo.
echo ========================================================
echo [Re-Commit] Creating a clean commit...
echo ========================================================
git add .
git commit -m "Clean Deployment (Without Large Files)"

echo.
echo ========================================================
echo [Final Push] Uploading again...
echo ========================================================
git push -f origin main

echo.
echo ========================================================
echo Now check if upload is 100% COMPLETE!
echo ========================================================
pause
