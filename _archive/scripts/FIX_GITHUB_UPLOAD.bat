@echo off
echo ========================================================
echo Checking GitHub Upload Status...
echo ========================================================
git status
echo.
git branch -v
echo.
git remote -v
echo.

echo ========================================================
echo [Retrying Upload] Force Pushing Code...
echo ========================================================
git add .
git commit -m "Force Update for Deployment" 
git branch -M main
git push -f origin main

echo.
echo ========================================================
echo If you see ANY error messages above (red text), let me know.
echo If it says "Everything up-to-date" or similar success, 
echo try clicking "Deploy" on Streamlit again.
echo ========================================================
pause
