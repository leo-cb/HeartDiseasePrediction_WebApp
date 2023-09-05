from db import generate_insert_api_key
import argparse

parser = argparse.ArgumentParser(description='Generate and insert an API key into the database.')

# add arguments for 'url' and 'key', making them optional with default values as None
parser.add_argument('--url', type=str, default=None, help='The URL for the DB.')
parser.add_argument('--key', type=str, default=None, help='The API key to insert.')

args = parser.parse_args()

try:
    api_key = generate_insert_api_key(args.url, args.key)
    print(f'Inserted API key: {api_key}')
except Exception as e:
    print(f"Error while generating or inserting the api key: {str(e)}")