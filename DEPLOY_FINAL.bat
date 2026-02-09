@echo off
echo ========================================================
echo [FINAL ATTEMPT] Updating GitHub to trigger Streamlit build...
echo ========================================================
git add .
git commit -m "Update visual version to v4.6 (Force Refresh)"
git push origin main
echo.
echo [SUCCESS] Code pushed. Please wait 1-2 minutes.
echo.
echo [CHECKPOINT] Go to https://lotte-ai-app.streamlit.app/
echo Look for text: "v4.6 (최신반영됨)"
echo If you see this text, the buttons should also be updated.
echo.
pause
