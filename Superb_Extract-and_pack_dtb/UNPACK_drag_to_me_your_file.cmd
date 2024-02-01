@echo off
color a
cls

set filename=%~n1%~x1

copy %1 WorkDir\work.img

cd WorkDir

python extract-dtb.py work.img

timeout /t 6 /nobreak >nul

