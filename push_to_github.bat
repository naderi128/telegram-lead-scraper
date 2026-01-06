@echo off
echo ========================================================
echo      GitHub Push Helper for Telegram Lead Scraper
echo ========================================================
echo.
echo Repo URL: https://github.com/naderi128/telegram-lead-scraper.git
echo.

echo Connecting...
git remote remove origin 2>nul
git remote add origin https://github.com/naderi128/telegram-lead-scraper.git

echo.
echo Pushing code to GitHub...
echo (If a browser window or login prompt appears, please sign in)
echo.
git branch -M main
git push -u origin main

echo.
if %errorlevel% neq 0 (
    echo [ERROR] Push failed. You might need to sign in.
) else (
    echo [SUCCESS] Code pushed! Go deploy it on Streamlit.
)
pause
