# Get one syllabus

import json
import os

from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING

SYLLABUS_CRUD_HOST = os.environ.get('SYLLABUS_CRUD_HOST')
SYLLABUS_CRUD_PORT = os.environ.get('SYLLABUS_CRUD_PORT')
SYLLABUS_CRUD_USERNAME = os.environ.get('SYLLABUS_CRUD_USERNAME')
SYLLABUS_CRUD_PASS = os.environ.get('SYLLABUS_CRUD_PASS')
SYLLABUS_CRUD_DB = os.environ.get('SYLLABUS_CRUD_DB')

ORDER_LABEL = {
    "desc": DESCENDING,
    "asc": ASCENDING
}


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


def format_specific_values(result):
    if result.get("_id"):
        result["_id"] = str(result["_id"])
    if result.get("fecha_creacion"):
        result["fecha_creacion"] = str(result["fecha_creacion"])
    if result.get("fecha_modificacion"):
        result["fecha_modificacion"] = str(result["fecha_modificacion"])
    return result


def format_response(result, message: str, status_code: int, success: bool):
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
    if isinstance(result, list):
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


def get_query(query_str: str) -> dict:
    query_total = {}
    for cond in query_str.split(","):
        kv = cond.split(":", 1)
        if len(kv) == 2:
            k, v = kv
        else:
            k, v = kv[0], None
        query_total[k] = v
    return query_total


def get_sort_by(query_params) -> list:
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
    try:
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
            return query_params_result, "Without params"
    except Exception as ex:
        print("Error in parse_query_params")
        print(ex)
        return {}, ex


def lambda_handler(event, context):
    client = None
    try:
        client = connect_db_client()
        if client:
            print("Connecting database ...")
            syllabus_collection = client[str(SYLLABUS_CRUD_DB)]["syllabus"]
            print("Connection database successful")
            query_complement, err = parse_query_params(event)
            if err is None:
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
                    close_connect_db(client)
            else:
                return format_response(
                    {},
                    "Error service GetAll: The request contains an incorrect parameter or no record exists",
                    404,
                    True)
        return format_response(
            {},
            "Error get syllabus!",
            403,
            False)
    except Exception as ex:
        print("Error get syllabus")
        print(f"Detail: {ex}")
        close_connect_db(client)
        return format_response(
            {},
            "Error get syllabus!",
            403,
            False)
