# Put syllabus

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


class SyllabusModel(BaseModel):
    espacio_academico_id: int
    justificacion: str
    objetivo_general: str
    objetivos_especificos: List
    resultados_aprendizaje: List
    articulacion_resultados_aprendizaje: str
    contenido: Dict
    estrategias: List
    evaluacion: Dict
    bibliografia: List
    seguimiento: List
    activo: bool = Field(default=True)
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


def parse_body(event) -> tuple:
    try:
        return json.loads(event["body"]), None
    except Exception as ex:
        return None, ex


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
        data, error = parse_body(event)
        if error is None:
            # Validate structure
            syllabus_data = SyllabusModel(**data).__dict__
            print(syllabus_data)
            client = connect_db_client()
            filter_ = {"_id": ObjectId(syllabus_id)}
            if client:
                print("Connecting database ...")
                syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
                print("Connection database successful")
                print("Updating syllabus")
                result = syllabus_collection.update_one(
                    filter_,
                    {"$set": syllabus_data})
                print(f"Updated syllabus {syllabus_id}")
                if result:
                    syllabus = syllabus_collection.find_one(filter_)
                    return format_response(
                        syllabus,
                        "Updated syllabus",
                        200,
                        True)
                else:
                    close_connect_db(client)
            return format_response(
                {},
                "Error updating syllabus!",
                403,
                False)
    except Exception as ex:
        print("Error updating syllabus")
        print(f"Detail: {ex}")
        close_connect_db(client)
        return format_response(
            {},
            "Error updating syllabus!",
            403,
            False)
