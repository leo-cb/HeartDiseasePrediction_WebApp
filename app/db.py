import pymongo
import hashlib
import secrets

def generate_insert_api_key(url="mongodb://mongodb:27017",key=""):
    # generate random api key
    if key == "":
        api_key = secrets.token_urlsafe(32)
    else:
        api_key = key

    # hash the api key
    hash_api_key = hashlib.sha256(api_key.encode()).hexdigest()

    # connect to the local mongodb
    client = pymongo.MongoClient(url)
    db = client["api_keys"] # database
    collection = db["keys"] # collection

    # insert the hash into collection
    api_key_doc = {"hashed_key": hash_api_key}
    result = collection.insert_one(api_key_doc)

    if result.inserted_id:
        return api_key
    else:
        return Exception("Failed to store the API key.")
    
def check_api_key(api_key,url="mongodb://mongodb:27017"):
    # hash the api key
    hash_api_key = hashlib.sha256(api_key.encode()).hexdigest()

    # connect to the local mongodb
    client = pymongo.MongoClient(url)
    db = client["api_keys"] # database
    collection = db["keys"] # collection

    api_key_doc = collection.find_one({"hashed_key": hash_api_key})

    return api_key_doc