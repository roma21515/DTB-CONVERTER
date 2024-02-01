@echo off
color e
cls

cd WorkDir

del work.img
del dtb_offsets.txt

cd..

del your_new_file.img

rmdir /s /q dtb

echo All Work Files was Cleaned
timeout /t 3 /nobreak >nul