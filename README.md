# Syllabus Lambda (Prueba Piloto)

Pruebas piloto CRUD del syllabus empleando AWS SAM.

## Especificaciones Técnicas

### Tecnologías Implementadas y Versiones
* [Python 3.9](https://docs.python.org/3.9/)
* [AWS SAM](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/using-sam-cli.html)


### Variables de Entorno
```shell
SYLLABUS_CRUD_HOST=[direccion de la base de datos]
SYLLABUS_CRUD_PORT=[Puerto de conexión con la base de datos]
SYLLABUS_CRUD_USERNAME=[usuario con acceso a la base de datos]
SYLLABUS_CRUD_PASS=[password del usuario]
SYLLABUS_CRUD_DB=[nombre de la base de datos]
TIMEZONE=[zona horaria]
```

**Nota:**
* [Lista de zona horarias](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)


### Ejecución del Proyecto en Local
```shell
sam build
sam local start-api --env-vars env.json
```
**Ver:**
Para más detalle de las formas de ejecutarlo localmente vea [Uso sam local](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/using-sam-cli-local.html)

### Ejecución Pruebas

Pruebas unitarias
```shell
# En Proceso
```

### Despliegue
```shell
sam build
sam deploy --guided
```
**Ver:** 
Para mayor información para realizar el despliegue vea [Uso sam deploy](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/using-sam-cli-deploy.html).

## Estado CI


## Licencia
