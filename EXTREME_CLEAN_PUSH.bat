@echo off
echo ========================================================
echo [Final Extreme Clean] Removing ALL large files...
echo ========================================================
git reset --soft HEAD~1
git reset HEAD deploy.tgz
git rm --cached -f deploy.tgz
del /f /q "deploy.tgz"
echo deploy.tgz >> .gitignore
git rm --cached -f *.exe
git rm --cached -f *.zip
git rm --cached -f *.tgz
git rm --cached -f *.tar.gz
git rm --cached -f *.mp4

echo.
echo ========================================================
echo [Re-Commit] Creating a LIGHTWEIGHT commit...
echo ========================================================
git add .
git commit -m "Ultra Clean Push (No Large Files)"

echo.
echo ========================================================
echo [Push] Try again...
echo ========================================================
git push -f origin main
pause
