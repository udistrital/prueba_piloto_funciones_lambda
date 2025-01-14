# CRUD syllabus
# Get one, Get All, Post, Put and Delete endpoints

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

import pytz
from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, DESCENDING, errors

# Required environment variables
SYLLABUS_CRUD_HOST = os.environ.get('SYLLABUS_CRUD_HOST')
SYLLABUS_CRUD_PORT = os.environ.get('SYLLABUS_CRUD_PORT')
SYLLABUS_CRUD_USERNAME = os.environ.get('SYLLABUS_CRUD_USERNAME')
SYLLABUS_CRUD_PASS = os.environ.get('SYLLABUS_CRUD_PASS')
SYLLABUS_CRUD_DB = os.environ.get('SYLLABUS_CRUD_DB')
TIMEZONE = os.environ.get('TIMEZONE')
COLLECTION = "syllabus"
print(SYLLABUS_CRUD_DB)

ORDER_LABEL = {
    "desc": DESCENDING,
    "asc": ASCENDING
}


# Modelo de datos Syllabus
def local_now():
    """Datetime por Timezone"""
    return datetime.now(tz=pytz.timezone(TIMEZONE))


class SyllabusModel(BaseModel):
    """Modelo de datos del Syllabus"""
    syllabus_code: Optional[str] = None
    version: Optional[int] = 0
    syllabus_actual: Optional[bool] = False
    espacio_academico_id: int
    proyecto_curricular_ids: List[int]
    plan_estudios_ids: List[int]
    justificacion: Optional[str] = None
    objetivo_general: Optional[str] = None
    objetivos_especificos: Optional[List] = None
    resultados_aprendizaje: Optional[List] = None
    articulacion_resultados_aprendizaje: Optional[str] = None
    contenido: Optional[Dict] = None
    estrategias: Optional[List] = None
    evaluacion: Optional[Dict] = None
    bibliografia: Optional[Dict] = None
    seguimiento: Optional[Dict] = None
    sugerencias: Optional[str] = None
    recursos_educativos: Optional[str] = None
    practicas_academicas: Optional[str] = None
    vigencia: Optional[Dict] = None
    idioma_espacio_id: Optional[List] = None
    tercero_id: Optional[int] = 0
    activo: bool = Field(default=True)


class SyllabusCreationModel(SyllabusModel):
    fecha_creacion: datetime = Field(default=local_now())
    fecha_modificacion: Optional[datetime] = None


class SyllabusUpdateModel(SyllabusModel):
    fecha_modificacion: Optional[datetime] = Field(default=local_now())


class DeleteSyllabusModel(BaseModel):
    activo: Optional[bool] = Field(default=False)
    fecha_modificacion: Optional[datetime] = Field(default=local_now())


def connect_db_client():
    """Genera el cliente para establecer la conexión con la base de datos"""
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
    """Permite cerrar la conexión a la base de datos en caso que la conexión exista"""
    try:
        print("Closing client DB")
        if client:
            client.close()
    except Exception as ex:
        print("Error close Client DB")
        print(f"Detail: {ex}")


def parse_body(event) -> tuple:
    """
    Deserialización de parámetros de entrada que tengan body.
    Por ejemplo, peticiones POST, PUT o DELETE
    """
    try:
        return json.loads(event["body"]), None
    except Exception as ex:
        return None, ex


def get_query(query_str: str) -> dict:
    """
    Transforma el query string de entrada en un diccionario con filtros para
    realizar la consulta a la base de datos
    Ejemplo:
        query=espacio_academico_id:1,proyecto_curricular_id:375, ...
    """
    query_total = {}
    int_fields = ['version',
                  'espacio_academico_id',
                  'proyecto_curricular_id',
                  'plan_estudios_id'
                  ]
    key_map = {
        "proyecto_curricular_id": "proyecto_curricular_ids",
        "plan_estudios_id": "plan_estudios_ids"
    }
    keys_map = list(key_map.keys())
    for cond in query_str.split(","):
        kv = cond.split(":", 1)
        if len(kv) == 2:
            k, v = kv
            if v == 'false':
                v = False
            elif v == 'true':
                v = True

            if k in int_fields:
                v = int(v)
            elif k == 'syllabus_code':
                v = uuid.UUID(v)

            if k == "_id":
                v = ObjectId(v)
        else:
            k, v = kv[0], None

        if k in keys_map:
            k = key_map[k]
            v = {
                "$in": [v]
            }
        query_total[k] = v
    return query_total


def get_sort_by(query_params) -> list:
    """
    Transforma el query params sortby en la lista de consulta sort
    para la base de datos combinando el sortby con el order (ASCENDENTE,
    DESCENDENTE)
    Ejemplo:
        sortby=espacio_academico_id, ...
        order=asc, ...
    """
    sort_by_total = []
    if query_params.get("sortby"):
        sort_by_list = str(query_params.get("sortby")).split(",")
        if query_params.get("order"):
            order_list = str(query_params.get("order")).split(",")
            if len(order_list) == 1:
                # Default ASCENDING
                order_label = ORDER_LABEL.get(query_params.get("order"), ASCENDING)
                sort_by_total = [(e, order_label) for e in sort_by_list]
            elif len(order_list) == len(sort_by_list):
                for i, e in enumerate(sort_by_list):
                    order_label = ORDER_LABEL.get(order_list[i], ASCENDING)
                    sort_by_total.append((e, order_label))
            else:
                # Default ASCENDING
                sort_by_total = [(e, ASCENDING) for e in sort_by_list]
    return sort_by_total


def parse_query_params(event) -> tuple:
    """
    Organiza los query params query, fields, sortby, order, limit, offset generando
    la estructura para realizar la consulta a base de datos
    """
    try:
        print("event: ", event)
        query_params_result = {
            "limit": 10
        }
        query_params = event["queryStringParameters"]
        if isinstance(query_params, dict):
            # query: k:v, k: v
            if query_params.get("query"):
                query_params_result["filter"] = get_query(str(query_params.get("query")))

            # fields: col1, col2, entity.col3
            if query_params.get("fields"):
                query_params_result["projection"] = str(query_params.get("fields")).split(",")

            # sortby: col1,col2
            # order: desc,asc
            if query_params.get("sortby"):
                query_params_result["sort"] = get_sort_by(query_params)

            # limit: 10 (default is 10)
            if query_params.get("limit"):
                query_params_result["limit"] = int(query_params.get("limit"))

            # offset: 0 (default is 0)
            if query_params.get("offset"):
                query_params_result["skip"] = int(query_params.get("offset"))

            return query_params_result, None
        else:
            return query_params_result, None
    except Exception as ex:
        print("Error in parse_query_params")
        print(ex)
        return {}, ex


def set_version(syllabus_data: dict, syllabus_collection):
    """
    Calcula el versionado de los syllabus por syllabus_code
    """
    try:
        if syllabus_data.get("syllabus_code"):
            syllabus_code = str(syllabus_data.get("syllabus_code"))
            query = {
                "syllabus_code": uuid.UUID(syllabus_code)
            }
            total = syllabus_collection.count_documents(query)
            syllabus_data["version"] = total + 1
        else:
            syllabus_data["version"] = 1
    except Exception as ex:
        print(f"Error assigning version. Details:  {str(ex)}")


def update_old_syllabus(syllabus_data: dict, syllabus_collection):
    try:
        if syllabus_data.get("syllabus_code"):
            syllabus_code = str(syllabus_data.get("syllabus_code"))
            query = {
                "syllabus_code": uuid.UUID(syllabus_code)
            }
            syllabus_collection.update_many(
                query,
                {
                    "$set": {"syllabus_actual": False}
                }
            )
    except Exception as ex:
        print(f"Error updating old syllabus. Details:  {str(ex)}")


# Formato de respuestas
def format_specific_values(result):
    """
    Convierte valores con tipo de dato específico a un formato que
    pueda ser respondido como JSON.
    Ejemplo:
        ObjectId -> str
        datetime -> str
        UUID -> str
    """
    if result.get("_id"):
        result["_id"] = str(result["_id"])
    if result.get("fecha_creacion"):
        result["fecha_creacion"] = str(result["fecha_creacion"])
    if result.get("fecha_modificacion"):
        result["fecha_modificacion"] = str(result["fecha_modificacion"])
    if result.get("syllabus_code"):
        result["syllabus_code"] = str(result["syllabus_code"])
    return result


def format_response(result, message: str, status_code: int, success: bool):
    """
    Crea la estructura de respuesta con los campos:
        statusCode: código HTTP
        body: JSON con la siguiente estructura
            Success: Campo booleano que indica si fue exitosa (true) o no la petición
            Status: código HTTP
            Message: mensaje descriptivo del resultado de la petición
            Data: No es agregado en caso de un error en las peticiones, contiene una lista
                o diccionario con el resultado de la petición entrante.
    """
    if isinstance(result, dict):
        if success:
            result = format_specific_values(result)

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
    elif isinstance(result, list):
        result_total = []
        if success:
            for res in result:
                result_total.append(format_specific_values(res))
            return {"statusCode": status_code,
                    "body": json.dumps({
                        "Success": success,
                        "Status": status_code,
                        "Message": message,
                        "Data": result_total
                    })}
        else:
            return {"statusCode": status_code,
                    "body": json.dumps({
                        "Success": success,
                        "Status": status_code,
                        "Message": message
                    })}
    elif result is None:
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


def create_syllabus(syllabus_data, syllabus_collection):
    try:
        if syllabus_data.get("syllabus_code"):
            syllabus_data["syllabus_code"] = uuid.UUID(syllabus_data.get("syllabus_code"))
        else:
            syllabus_data["syllabus_code"] = uuid.uuid4()
        set_version(syllabus_data, syllabus_collection)
        update_old_syllabus(syllabus_data, syllabus_collection)

        syllabus_data["syllabus_actual"] = True
        print("Inserting new syllabus")
        result = syllabus_collection.insert_one(syllabus_data)
        print("Created new syllabus")
        if result:
            new_syllabus_id = result.inserted_id
            new_syllabus = syllabus_collection.find_one(new_syllabus_id)
            return format_response(
                new_syllabus,
                "Created syllabus",
                201,
                True)
        else:
            return format_response(
                {},
                "Syllabus was not created",
                400,
                False)
    except errors.NetworkTimeout as nex:
        print("Error querying all syllabus")
        print(f"Detail: {nex}")
        return format_response(
            {},
            "Error registering new syllabus! Detail: Network Timeout",
            500,
            False)
    except errors.ServerSelectionTimeoutError as sst_err:
        print("Error querying all syllabus")
        print(f"Detail: {sst_err}")
        return format_response(
            {},
            "Error registering new syllabus! Detail: Server Selection Timeout Error",
            500,
            False)
    except Exception as ex:
        print("Error creating register syllabus")
        print(f"Detail: {ex}")
        return format_response(
            {},
            "Error registering new syllabus! Detail: general error, for more details check the logs",
            500,
            False)


def update_syllabus(syllabus_id, syllabus_data, syllabus_collection):
    try:
        filter_ = {"_id": ObjectId(syllabus_id)}
        print("Updating syllabus")
        result = syllabus_collection.update_one(
            filter_,
            {"$set": syllabus_data})
        if result.modified_count:
            print(f"Updated syllabus {syllabus_id}")
            syllabus = syllabus_collection.find_one(filter_)
            return format_response(
                syllabus,
                "Updated syllabus",
                200,
                True)
        else:
            return format_response(
                {},
                "Syllabus not updated",
                400,
                False)
    except errors.NetworkTimeout as nex:
        print("Error querying all syllabus")
        print(f"Detail: {nex}")
        return format_response(
            {},
            "Error updating syllabus! Detail: Network Timeout",
            500,
            False)
    except errors.ServerSelectionTimeoutError as sst_err:
        print("Error querying all syllabus")
        print(f"Detail: {sst_err}")
        return format_response(
            {},
            "Error updating syllabus! Detail: Server Selection Timeout Error",
            500,
            False)
    except Exception as ex:
        print("Error updating syllabus")
        print(f"Detail: {ex}")
        return format_response(
            {},
            "Error updating syllabus! Detail: general error, for more details check the logs",
            500,
            False)


def delete_syllabus(syllabus_id, syllabus_data, syllabus_collection):
    try:
        filter_ = {"_id": ObjectId(syllabus_id)}
        print("Deleting syllabus")
        result = syllabus_collection.update_one(
            filter_,
            {"$set": syllabus_data})
        print(f"Deleted syllabus {syllabus_id}")
        if result.modified_count:
            return format_response(
                None,
                "Deleted syllabus",
                204,
                True
            )
        else:
            return format_response(
                None,
                "Syllabus not deleted",
                400,
                False)
    except errors.NetworkTimeout as nex:
        print("Error querying all syllabus")
        print(f"Detail: {nex}")
        return format_response(
            {},
            "Error deleting syllabus! Detail: Network Timeout",
            500,
            False)
    except errors.ServerSelectionTimeoutError as sst_err:
        print("Error querying all syllabus")
        print(f"Detail: {sst_err}")
        return format_response(
            {},
            "Error deleting syllabus! Detail: Server Selection Timeout Error",
            500,
            False)
    except Exception as ex:
        print("Error deleting syllabus")
        print(f"Detail: {ex}")
        return format_response(
            {},
            "Error deleting syllabus! Detail: general error, for more details check the logs",
            500,
            False)


def get_all_syllabus(query_complement, syllabus_collection):
    try:
        print("Query")
        print(query_complement)
        syllabus = list(syllabus_collection.find(**query_complement))
        print(f"Consulted record.")
        if syllabus:
            print("Syllabus found!")
            return format_response(
                syllabus,
                "Request successful",
                200,
                True)
        else:
            print("Syllabus not found!")
            return format_response(
                [],
                "Request successful",
                200,
                True)
    except errors.NetworkTimeout as nex:
        print("Error querying all syllabus")
        print(f"Detail: {nex}")
        return format_response(
            {},
            "Error querying all syllabus! Detail: Network Timeout",
            500,
            False)
    except errors.ServerSelectionTimeoutError as sst_err:
        print("Error querying all syllabus")
        print(f"Detail: {sst_err}")
        return format_response(
            {},
            "Error querying all syllabus! Detail: Server Selection Timeout Error",
            500,
            False)
    except Exception as ex:
        print("Error querying all syllabus")
        print(f"Detail: {ex}")
        return format_response(
            {},
            "Error querying all syllabus! Detail: general error, for more details check the logs",
            500,
            False)


def get_one_syllabus(syllabus_code, syllabus_collection):
    try:
        syllabus = syllabus_collection.find_one({
            "syllabus_code": uuid.UUID(syllabus_code),
            "syllabus_actual": True
        })
        print(f"Consulted record.")
        if syllabus:
            print("Syllabus found!")
            print(syllabus)
            print(type(syllabus))
            return format_response(
                syllabus,
                "Syllabus OK",
                200,
                True)
        else:
            print("Syllabus not found!")
            return format_response(
                {},
                "Syllabus Not Found",
                404,
                False)
    except Exception as ex:
        print("Error querying a syllabus")
        print(f"Detail: {ex}")
        return format_response(
            {},
            "Error querying a syllabus! Detail: general error, for more details check the logs",
            500,
            False)


def lambda_handler(event, context):
    client = None
    try:
        http_method = event['httpMethod']
        if http_method == 'POST':
            data, error = parse_body(event)
            if error is None:
                # Validate structure
                syllabus_data = SyllabusCreationModel(**data).__dict__
                client = connect_db_client()
                if client:
                    syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
                    response = create_syllabus(syllabus_data, syllabus_collection)
                    close_connect_db(client)
                    return response

                return format_response(
                    {},
                    "Error registering new syllabus!",
                    500,
                    False)
            else:
                print(error)
                return format_response(
                    {},
                    "Error registering new syllabus! Detail: Error in input data",
                    500,
                    False)
        elif http_method == 'PUT':
            data, error = parse_body(event)
            if error is None:
                # Validate structure
                syllabus_id = event["pathParameters"]["id"]
                syllabus_data = SyllabusUpdateModel(**data).__dict__
                syllabus_data["fecha_modificacion"] = local_now()
                client = connect_db_client()
                if client:
                    syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
                    response = update_syllabus(syllabus_id, syllabus_data, syllabus_collection)
                    close_connect_db(client)
                    return response

                return format_response(
                    {},
                    "Error updating syllabus!",
                    500,
                    False)
            else:
                print(error)
                return format_response(
                    {},
                    "Error updating syllabus! Detail: Error in input data",
                    500,
                    False)
        elif http_method == 'DELETE':
            syllabus_id = event["pathParameters"]["id"]
            print(syllabus_id)
            # Create structure to update (delete logic)
            syllabus_data = DeleteSyllabusModel().__dict__
            client = connect_db_client()
            if client:
                syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
                response = delete_syllabus(syllabus_id, syllabus_data, syllabus_collection)
                close_connect_db(client)
                return response

            return format_response(
                None,
                "Error deleting syllabus!",
                500,
                False)
        elif http_method == 'GET':
            client = connect_db_client()
            if client:
                syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
                if 'pathParameters' in event and event['pathParameters'] is not None:
                    syllabus_code = event["pathParameters"]["id"]
                    print(syllabus_code)
                    response = get_one_syllabus(syllabus_code, syllabus_collection)
                    close_connect_db(client)
                    return response
                else:
                    query_complement, err = parse_query_params(event)
                    if err is None:
                        response = get_all_syllabus(query_complement, syllabus_collection)
                        close_connect_db(client)
                        return response
                    else:
                        return format_response(
                            {},
                            "Error service GetAll: The request contains an incorrect parameter or no record exists",
                            404,
                            True)
            return format_response(
                {},
                "Error get syllabus!",
                500,
                False)
        else:
            close_connect_db(client)
            return format_response(
                {},
                f"HTTP method not allowed",
                500,
                False)
    except Exception as ex:
        print("Error in syllabus request")
        print(f"Detail: {ex}")
        close_connect_db(client)
        return format_response(
            {},
            f"Error in syllabus request! Detail: {ex}",
            500,
            False)
