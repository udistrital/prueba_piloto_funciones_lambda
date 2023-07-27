import json
import os
import uuid
from typing import List, Dict

from pydantic import BaseModel, Field
from pymongo import MongoClient

SYLLABUS_CRUD_HOST = os.environ.get('SYLLABUS_CRUD_HOST')
SYLLABUS_CRUD_PORT = os.environ.get('SYLLABUS_CRUD_PORT')
SYLLABUS_CRUD_USERNAME = os.environ.get('SYLLABUS_CRUD_USERNAME')
SYLLABUS_CRUD_PASS = os.environ.get('SYLLABUS_CRUD_PASS')
SYLLABUS_CRUD_DB = os.environ.get('SYLLABUS_CRUD_DB')
COLLECTION = "syllabus"
client: MongoClient


class SyllabusModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)
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


def connect_db_client():
    try:
        # With password
        if SYLLABUS_CRUD_USERNAME and SYLLABUS_CRUD_PASS:
            uri = f"mongodb://{SYLLABUS_CRUD_USERNAME}:{SYLLABUS_CRUD_PASS}@" \
                  f"{SYLLABUS_CRUD_HOST}:{SYLLABUS_CRUD_PORT}/"
        else:
            # Without password
            uri = "mongodb://172.17.0.1:27017/"
            # uri = f"mongodb://{SYLLABUS_CRUD_HOST}:{SYLLABUS_CRUD_PORT}/{SYLLABUS_CRUD_DB}"

        client = MongoClient(uri)
        print("Connection Successful")
        return client
    except Exception as ex:
        print("Error Connection")
        print(ex)
        return None


def parse_body(event) -> tuple:
    try:
        return json.loads(event["body"]), None
    except Exception as ex:
        return None, ex


def close_connect_db(client):
    try:
        print("Closing connection db")
        client.close()
    except Exception as ex:
        print("Error close connection")
        print(ex)


def lambda_handler(event, context):
    try:
        data, error = parse_body(event)
        if error is None:
            # Validate structure
            syllabus_data = SyllabusModel(**data).__dict__
            client = connect_db_client()
            if client:
                print(SYLLABUS_CRUD_DB)
            syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
            print("Syllabus data", syllabus_data)
            result = syllabus_collection.insert_one(syllabus_data)
            if result:
                new_syllabus_id = result.inserted_id
                new_syllabus = syllabus_collection.find_one(new_syllabus_id)
                new_syllabus["_id"] = str(new_syllabus["_id"])
                return {"statusCode": 201,
                        "body": json.dumps({
                            "message": "Created!",
                            "data": SyllabusModel(**new_syllabus).__dict__
                        })}
            else:
                return {"statusCode": 400,
                        "body": json.dumps({"message": "Error registering new syllabus!"})}
    except Exception as ex:
        print("Error creating register syllabus")
        print(ex)
        if client:
            close_connect_db(client)
