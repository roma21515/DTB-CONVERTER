@echo off
color a
cls

set filename=%~n1%~x1

copy %1 work.img

python extract-dtb.py work.img

pause

