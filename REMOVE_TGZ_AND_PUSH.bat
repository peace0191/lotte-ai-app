@echo off
echo ========================================================
echo [1/3] Removing ANOTHER LARGE file (deploy.tgz)...
echo ========================================================
git rm --cached -f "deploy.tgz"
echo deploy.tgz >> .gitignore

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
echo Finally go to Streamlit Cloud and click DEPLOY!
echo ========================================================
pause
