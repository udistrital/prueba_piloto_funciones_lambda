# Delete (logic) syllabus

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

import pytz
from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import MongoClient

SYLLABUS_CRUD_HOST = os.environ.get('SYLLABUS_CRUD_HOST')
SYLLABUS_CRUD_PORT = os.environ.get('SYLLABUS_CRUD_PORT')
SYLLABUS_CRUD_USERNAME = os.environ.get('SYLLABUS_CRUD_USERNAME')
SYLLABUS_CRUD_PASS = os.environ.get('SYLLABUS_CRUD_PASS')
SYLLABUS_CRUD_DB = os.environ.get('SYLLABUS_CRUD_DB')
TIMEZONE = os.environ.get('TIMEZONE')
COLLECTION = "syllabus"

print(SYLLABUS_CRUD_DB)


def local_now():
    return datetime.now(tz=pytz.timezone(TIMEZONE))


class DeleteSyllabusModel(BaseModel):
    activo: Optional[bool] = Field(default=False)
    fecha_modificacion: Optional[datetime] = Field(default=local_now())


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


def format_delete_response(message: str, status_code: int, success: bool):
    if success:
        return {"statusCode": status_code,
                "body": json.dumps({
                    "Success": success,
                    "Status": status_code,
                    "Message": message
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
        # Create structure to update (delete logic)
        syllabus_data = DeleteSyllabusModel().__dict__
        client = connect_db_client()
        if client:
            filter_ = {"_id": ObjectId(syllabus_id)}
            print("Connecting database ...")
            syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
            print("Connection database successful")
            print("Deleting syllabus")
            result = syllabus_collection.update_one(
                filter_,
                {"$set": syllabus_data})
            print(f"Deleted syllabus {syllabus_id}")
            if result.modified_count:
                return format_delete_response(
                    "Deleted syllabus",
                    204,
                    True
                )
            else:
                close_connect_db(client)
        return format_delete_response(
            "Error deleting syllabus!",
            403,
            False)
    except Exception as ex:
        print("Error updating syllabus")
        print(f"Detail: {ex}")
        close_connect_db(client)
        return format_delete_response(
            "Error deleting syllabus!",
            403,
            False)
