@echo off
echo ========================================================
echo [1/3] Removing LARGE files (Docker Installer)...
echo ========================================================
git rm --cached -f "data/Docker_Desktop_Installer.exe"
echo data/Docker_Desktop_Installer.exe >> .gitignore

echo.
echo ========================================================
echo [2/3] Cleaning up commit history...
echo ========================================================
git commit --amend -CHEAD

echo.
echo ========================================================
echo [3/3] Retrying Push to GitHub...
echo ========================================================
git push -f origin main

echo.
echo ========================================================
echo If you see "Everything up-to-date" or success messages,
echo Go back to Streamlit Cloud and click DEPLOY!
echo ========================================================
pause
