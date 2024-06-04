import pandas as pd
import tarfile
import json
import os

# Extracting JSON files from tar.gz
with tarfile.open('input.tar.gz', 'r:gz') as tar:
    tar.extractall(path='input_data')


# Function to read JSONs into a DataFrame, handling subfolders
def read_json_files(directory):
    data_frames = []
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        # Verifying the data structure
                        if isinstance(data, list):
                            if all(isinstance(item, dict) for item in data):
                                df = pd.DataFrame(data)
                                data_frames.append(df)
                            else:
                                print(
                                    f"Invalid data structure in the file (not all items are dictionaries).): {file_path}")
                        elif isinstance(data, dict):
                            df = pd.DataFrame([data])  # Converting a single dictionary into a DataFrame row
                            data_frames.append(df)
                        else:
                            print(
                                f"Invalid data structure in the file (not a list or dictionary): {file_path}")
                            print(f"File content {file_path}: {data}")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Error reading the JSON file: {file_path} - {str(e)}")

    if not data_frames:
        raise ValueError(
            "No data was read from the JSON files. Please verify if the JSON files are formatted correctly.")

    return pd.concat(data_frames, ignore_index=True)


# Listing the files in the directory for debugging
print("Files in the 'input_data' folder:", os.listdir('input_data/input'))

# Reading the JSON files
df = read_json_files('input_data')

# Checking the read data
print("Columns in the DataFrame:", df.columns)
print("First lines of the DataFrame:", df.head())

# Relevant columns
relevant_columns = ['artist', 'grossUSD', 'numTicketsSold', 'ticketPriceFrom',
                    'ticketPriceTo']
df = df[relevant_columns]

# Extracting information from the 'artist' field
df['artist_id'] = df['artist'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
df['artist_name'] = df['artist'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
df['artist_url'] = df['artist'].apply(lambda x: x.get('url') if isinstance(x, dict) else None)

# Removing the original 'artist' column now that we have extracted the relevant data.
df = df.drop(columns=['artist'])

# Identification and marking of outliers
# Here we use the IQR method to identify outliers.
Q1 = df['grossUSD'].quantile(0.25)
Q3 = df['grossUSD'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df['outlier_yn'] = (df['grossUSD'] < lower_bound) | (df['grossUSD'] > upper_bound)

# Save the resulting DataFrame
df.to_csv('output_data.csv', index=False)