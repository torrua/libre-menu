@echo off
taskkill /IM "swriter.exe" /F 2>nul
taskkill /IM "soffice.exe" /F 2>nul
taskkill /IM "soffice.bin" /F 2>nul

@echo on
"C:\Program Files\LibreOffice\program\python.exe" source\oxt_generator.py /wait
"C:\Program Files\LibreOffice\program\unopkg.exe" add -f "builds\lomenu_0.0.1.oxt" /wait

@echo off
taskkill /IM "swriter.exe" /F 2>nul
taskkill /IM "soffice.exe" /F 2>nul
taskkill /IM "soffice.bin" /F 2>nul

@echo on
start "" "C:\Program Files\LibreOffice\program\soffice.exe" -writer -norestore -nologo
REM pause
