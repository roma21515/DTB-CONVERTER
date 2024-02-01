@echo off
color e
cls

del work.img
del your_new_file.img
del dtb_offsets.txt
rmdir /s /q dtb

echo All Work Files was Cleaned
timeout /t 3 /nobreak >nul