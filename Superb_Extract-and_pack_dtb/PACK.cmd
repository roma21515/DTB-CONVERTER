@echo off
color a
cls

cd WorkDir

python pack-dtb.py

timeout /t 6 /nobreak >nul
