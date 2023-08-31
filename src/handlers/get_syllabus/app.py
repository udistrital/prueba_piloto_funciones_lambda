# Get one syllabus

import json
import os

from bson import ObjectId
from pymongo import MongoClient

SYLLABUS_CRUD_HOST = os.environ.get('SYLLABUS_CRUD_HOST')
SYLLABUS_CRUD_PORT = os.environ.get('SYLLABUS_CRUD_PORT')
SYLLABUS_CRUD_USERNAME = os.environ.get('SYLLABUS_CRUD_USERNAME')
SYLLABUS_CRUD_PASS = os.environ.get('SYLLABUS_CRUD_PASS')
SYLLABUS_CRUD_DB = os.environ.get('SYLLABUS_CRUD_DB')


def connect_db_client():
    try:
        # With password
        if SYLLABUS_CRUD_USERNAME and SYLLABUS_CRUD_PASS:
            uri = f"mongodb://{SYLLABUS_CRUD_USERNAME}:{SYLLABUS_CRUD_PASS}@" \
                  f"{SYLLABUS_CRUD_HOST}:{SYLLABUS_CRUD_PORT}/"
        else:
            # Without password
            uri = f"mongodb://{SYLLABUS_CRUD_HOST}:{SYLLABUS_CRUD_PORT}/"

        client = MongoClient(uri, uuidRepresentation='standard')
        print("Client DB Successful")
        return client
    except Exception as ex:
        print("Error Client DB")
        print(f"Detail: {ex}")
        return None


def close_connect_db(client):
    try:
        print("Closing client DB")
        if client:
            client.close()
    except Exception as ex:
        print("Error close Client DB")
        print(f"Detail: {ex}")


def format_response(result, message: str, status_code: int, success: bool):
    if isinstance(result, dict):
        if success:
            if result.get("_id"):
                result["_id"] = str(result["_id"])
            if result.get("fecha_creacion"):
                result["fecha_creacion"] = str(result["fecha_creacion"])
            if result.get("fecha_modificacion"):
                result["fecha_modificacion"] = str(result["fecha_modificacion"])

            return {"statusCode": status_code,
                    "body": json.dumps({
                        "Success": success,
                        "Status": status_code,
                        "Message": message,
                        "Data": result
                    })}
        else:
            return {"statusCode": status_code,
                    "body": json.dumps({
                        "Success": success,
                        "Status": status_code,
                        "Message": message
                    })}


def lambda_handler(event, context):
    client = None
    try:
        syllabus_id = event["pathParameters"]["id"]
        print(syllabus_id)
        client = connect_db_client()
        if client:
            print("Connecting database ...")
            syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
            print("Connection database successful")
            syllabus = syllabus_collection.find_one({
                "_id": ObjectId(syllabus_id)
            })
            print(f"Consulted record.")
            if syllabus:
                print("Syllabus found!")
                print(syllabus)
                print(type(syllabus))
                close_connect_db(client)
                return format_response(
                    syllabus,
                    "Syllabus OK",
                    200,
                    True)
            else:
                print("Syllabus not found!")
                close_connect_db(client)
                return format_response(
                    {},
                    "Syllabus Not Found",
                    404,
                    False)
        return format_response(
            {},
            "Error get syllabus!",
            500,
            False)
    except Exception as ex:
        print("Error get syllabus")
        print(f"Detail: {ex}")
        close_connect_db(client)
        return format_response(
            {},
            f"Error get syllabus! Detail: {ex}",
            500,
            False)
