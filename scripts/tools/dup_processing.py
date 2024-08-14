import pandas as pd

# Load the Excel file
df = pd.read_excel(r'H:\\results.xlsx')
print(df.columns)

# Filter the dataframe to include only the relevant columns
df = df[['Title', 'MMS ID', 'Series']]

# Find duplicates in the 'title' column
duplicate_titles = df[df.duplicated(['Title'], keep=False)]

# Sort by title to group duplicates together
duplicate_titles.sort_values('Title', inplace=True)

# Create list of lists for each duplicate pair
# Each element in the list is [title, mms_id, series]
duplicates_list = duplicate_titles.values.tolist()

# Print the result
for item in duplicates_list:
    print(item)
