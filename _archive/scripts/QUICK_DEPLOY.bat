@echo off
echo ========================================================
echo [1/3] Adding changes to Git...
echo ========================================================
git add .

echo.
echo ========================================================
echo [2/3] Committing changes...
echo ========================================================
git commit -m "Update UI navigation and dashboard buttons"

echo.
echo ========================================================
echo [3/3] Pushing to GitHub...
echo ========================================================
git push origin main

echo.
echo ========================================================
echo DONE! The app has been updated on GitHub.
echo Streamlit Cloud will automatically rebuild and deploy the changes.
echo Please wait 1-2 minutes and refresh the app link.
echo ========================================================
pause
