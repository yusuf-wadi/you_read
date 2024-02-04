@ECHO off

ECHO.
SET url=%1
SET start=%2
SET end= %3
:: name the output based on the vID and the start and end time, reformatted to have no spaces or colons or any special characters especially colons
SET start_formatted=%start::=%
SET end_formatted=%end::=%
SET output=%url:~32,11%_%start_formatted%_%end_formatted%
:: write file name to a text file
ECHO %output% > "output\output_%url%.txt"
yt-dlp -f mp4 %url% --download-sections "*%start%-%end%" -o "output/%output%.mp4"
:: get one single frame from the video
ffmpeg -i "output/%output%.mp4" -ss 00:00:01.000 -vframes 1 -y "output/%output%.jpg"
:: delete the video
DEL "output/%output%.mp4"

:End