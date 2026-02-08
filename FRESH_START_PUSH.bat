@echo off
echo ========================================================
echo [TOTAL NUKE] Deleting .git and starting fresh...
echo ========================================================
rmdir /s /q .git

echo.
echo ========================================================
echo [New Init] Initializing fresh Git repository...
echo ========================================================
git init
git branch -M main
git remote add origin https://github.com/peace0191/lotte-ai-app.git

echo.
echo ========================================================
echo [Add Files] Adding only CODE files...
echo ========================================================
git add .
git reset data/Docker_Desktop_Installer.exe
git reset deploy.tgz
git reset *.mp4
git reset *.exe
git reset *.zip
git reset *.tgz

echo data/Docker_Desktop_Installer.exe >> .gitignore
echo deploy.tgz >> .gitignore
echo *.mp4 >> .gitignore
echo *.exe >> .gitignore
echo *.zip >> .gitignore
echo *.tgz >> .gitignore
echo outputs/ >> .gitignore
echo services/assets/bgm/ >> .gitignore

echo.
echo ========================================================
echo [Commit] Creating a clean first commit...
echo ========================================================
git commit -m "Fresh Start - Lotte AI App"

echo.
echo ========================================================
echo [Force Push] Uploading CLEAN code...
echo ========================================================
git push -f origin main
pause
