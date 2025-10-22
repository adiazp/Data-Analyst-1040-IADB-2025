set LOGFILE=Run_All.log
call :LOG > %LOGFILE% 2>&1
exit /B
:LOG
cd /D "%~dp0"
"C:\Program Files\Python314\Scripts\pip.exe" install -r reqs.txt
"C:\Program Files\Python314\python.exe" "IADB_process.py"
"C:\Program Files\R\R-4.4.3\bin\Rscript.exe" "IADB_fit.R"
pause