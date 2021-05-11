echo off

:start
aws lambda update-event-source-mapping --uuid "9323a69d-76e0-489a-aa2f-b1dd1973072d" --enabled
time /T
powershell -nop -c "& {sleep 700}"
aws lambda update-event-source-mapping --uuid "9323a69d-76e0-489a-aa2f-b1dd1973072d" --no-enabled
time /T
powershell -nop -c "& {sleep 900}"
goto start