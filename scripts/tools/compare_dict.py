# Define a function to load a dictionary from a Python file
def load_dict_from_py_file(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        # Read the file content
        file_content = file.read()
    # Define a local dictionary to capture the local variables after execution
    local_vars = {}
    # Execute the file content, capturing the variables in local_vars
    exec(file_content, {}, local_vars)
    # Return the dictionary of interest, assuming it's named 'podcasts_dict'
    return local_vars['podcasts_dict']

# Load the original and cleaned dictionaries
podcasts_dict = load_dict_from_py_file('podcast_dict.py')
podcasts_dict_cleaned = load_dict_from_py_file('podcasts_dict_cleaned.py')

# Find podcasts present in podcasts_dict but not in podcasts_dict_cleaned
missing_podcasts = [podcast for podcast in podcasts_dict if podcast not in podcasts_dict_cleaned]

# Print the list of missing podcasts
print("Podcasts in the original dictionary but not in the cleaned dictionary:")
for podcast in missing_podcasts:
    print(podcast)
