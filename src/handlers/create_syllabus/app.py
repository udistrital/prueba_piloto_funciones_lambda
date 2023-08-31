# Post syllabus

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

import pytz
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
    proyecto_curricular_id: int
    plan_estudios_id: int
    justificacion: Optional[str] = None
    objetivo_general: Optional[str] = None
    objetivos_especificos: Optional[List] = None
    resultados_aprendizaje: Optional[List] = None
    articulacion_resultados_aprendizaje: Optional[str] = None
    contenido: Optional[Dict] = None
    estrategias: Optional[List] = None
    evaluacion: Optional[Dict] = None
    bibliografia: Optional[List] = None
    seguimiento: Optional[List] = None
    sugerencias: Optional[str] = None
    recursos_educativos: Optional[str] = None
    practicas_academicas: Optional[str] = None
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default=local_now())
    fecha_modificacion: Optional[datetime] = None


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
        data, error = parse_body(event)
        if error is None:
            # Validate structure
            syllabus_data = SyllabusModel(**data).__dict__
            client = connect_db_client()
            if client:
                print("Connecting database ...")
                syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
                print("Connection database successful")
                print("Inserting new syllabus")
                result = syllabus_collection.insert_one(syllabus_data)
                print("Created new syllabus")
                if result:
                    new_syllabus_id = result.inserted_id
                    new_syllabus = syllabus_collection.find_one(new_syllabus_id)
                    close_connect_db(client)
                    return format_response(
                        new_syllabus,
                        "Created syllabus",
                        201,
                        True)
                else:
                    close_connect_db(client)
                    return format_response(
                        {},
                        "Syllabus was not created",
                        400,
                        False)
            return format_response(
                {},
                "Error registering new syllabus!",
                500,
                False)
    except Exception as ex:
        print("Error creating register syllabus")
        print(f"Detail: {ex}")
        close_connect_db(client)
        return format_response(
            {},
            f"Error registering new syllabus! Detail: {ex}",
            500,
            False)
