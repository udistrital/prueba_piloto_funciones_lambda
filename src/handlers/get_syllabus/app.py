import json
import os
from pymongo import MongoClient

SYLLABUS_CRUD_HOST = os.environ.get('SYLLABUS_CRUD_HOST')
SYLLABUS_CRUD_PORT = os.environ.get('SYLLABUS_CRUD_PORT')
SYLLABUS_CRUD_USERNAME = os.environ.get('SYLLABUS_CRUD_USERNAME')
SYLLABUS_CRUD_PASS = os.environ.get('SYLLABUS_CRUD_PASS')
SYLLABUS_CRUD_DB = os.environ.get('SYLLABUS_CRUD_DB')


def connect_db(database: str):
    try:
        # With password
        if SYLLABUS_CRUD_USERNAME and SYLLABUS_CRUD_PASS:
            uri = f"mongodb://{SYLLABUS_CRUD_USERNAME}:{SYLLABUS_CRUD_PASS}@" \
                  f"{SYLLABUS_CRUD_HOST}:{SYLLABUS_CRUD_PORT}/{SYLLABUS_CRUD_DB}"
        else:
            # Without password
            uri = "mongodb://localhost:27017/prueba_piloto_lambda_db"
            # uri = f"mongodb://{SYLLABUS_CRUD_HOST}:{SYLLABUS_CRUD_PORT}/{SYLLABUS_CRUD_DB}"

        client = MongoClient(uri)
        db = client[database]
        print("Connection Successful")
        return db
    except Exception as ex:
        print("Error Connection")
        print(ex)
        return None


def close_connect_db(client):
    try:
        client.close()
    except Exception as ex:
        print("Error close connection")
        print(ex)


def lambda_handler(event, context):
    # print(event)
    # print(context)
    return {"statusCode": 200,
            "body": json.dumps({"message": "find!"})}
