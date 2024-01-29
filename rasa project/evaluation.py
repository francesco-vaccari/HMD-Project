import subprocess

# List of commands to execute
commands = [
    "rasa test nlu --config config.yml alternative_config.yml --runs 1 --percentages 0 --out nlu_comparison",
    "rasa train --config config.yml --fixed-model-name main",
    "rasa train --config alternative_config.yml --fixed-model-name alternative",
    "rasa test core -m models/main.tar.gz --stories test_stories.yml --out core_main"
    "rasa test core -m models/alternative.tar.gz --stories test_stories.yml --out core_alternative"
]

# Open a log file in append mode
with open("log.txt", "a") as log_file:
    # Iterate over each command
    for command in commands:
        # Execute the command and capture the output
        print(f"Executing command: {command}")
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            # Write the command and its output to the log file
            log_file.write(f"Command: {command}\n")
            log_file.write(f"Output:\n{output}\n")
        except subprocess.CalledProcessError as e:
            # If there's an error, write it to the log file
            log_file.write(f"Command: {command}\n")
            log_file.write(f"Error: {e.output}\n")
        # Separate each command's output in the log file
        log_file.write("="*50 + "\n")
