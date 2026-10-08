import subprocess #built-in Python module that allows one Python program to execute other programs and commands


# Create or update the SQL views

#-X prevents personal psql startup settings from interfering.
#-d steam_data identifies our database.
#-f identifies the SQL file.
#-v ON_ERROR_STOP=1 makes psql stop and return an error if a SQL statement fails.
subprocess.run(
    ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", "steam_data",
     "-f", "sql/create_views.sql"],
    check=True
)

#This tells Python to execute the existing extraction script
subprocess.run(
    ["python", "src/extract.py"],
    check=True
)
subprocess.run(
    ["python", "src/load.py"],
    check=True
)

subprocess.run(
    ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", "steam_data",
     "-f", "sql/validate_data.sql"],
    check=True
)