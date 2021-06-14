echo off

:start
aws lambda update-event-source-mapping --uuid "9323a69d-76e0-489a-aa2f-b1dd1973072d" --enabled
time /T
:: 1080
powershell -nop -c "& {sleep 1080}"
aws lambda update-event-source-mapping --uuid "9323a69d-76e0-489a-aa2f-b1dd1973072d" --no-enabled
time /T
:: 900
powershell -nop -c "& {sleep 900}"
goto start