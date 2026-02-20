@echo off
echo ========================================================
echo [FULL DEPLOY] Pushing ALL local changes to GitHub...
echo ========================================================

echo.
echo [1/4] Checking current status...
git status

echo.
echo [2/4] Adding ALL files...
git add -A

echo.
echo [3/4] Committing ALL changes...
git commit -m "Full deploy: dashboard buttons + ui chatbot nav v4.7"

echo.
echo [4/4] Pushing to GitHub...
git push origin main

echo.
echo ========================================================
echo [DONE] All local code has been pushed to GitHub.
echo Wait 2-3 minutes, then open:
echo https://lotte-ai-app.streamlit.app/
echo.
echo VERIFY: Look for v4.7 in the header
echo VERIFY: Scroll down to see 4 buttons in a row
echo ========================================================
pause
