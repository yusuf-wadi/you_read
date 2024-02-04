import subprocess
import os

#youtube url
url = "UZ-hwlKmAPc"
start = "00:00:00"
end = "00:00:10"
# # run batch file capture.bat with arguments
subprocess.run(["capture.bat", url, start, end])

