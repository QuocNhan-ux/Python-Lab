from pathlib import Path

# Location of security logs
log_file = Path("sample_auth.log")

# Read each line in the file
with log_file.open("r") as file:
    for line in file:
        if "Failed Password" in line:
            print(line.strip())

