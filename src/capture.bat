@ECHO off

ECHO.
SET url=%1
SET start=%2
SET end= %3
:: name the output based on the start and end time
yt-dlp -f mp4 %url% --download-sections "*%start%-%end%" -o "%start%-%end%.mp4"

:End