# Plantilla Syllabus

Lambda para generar el documento en PDF del Syllabus, a partir de una plantilla HTML y una 
estructura JSON definida de los datos a renderizar.  

## Especificaciones Técnicas

### Tecnologías Implementadas y Versiones
* [Python 3.9](https://docs.python.org/3.9/)
* [WeasyPrint 54.0](https://pypi.org/project/weasyprint/)
* [Jinja2](https://pypi.org/project/Jinja2/)
* [AWS SAM](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/using-sam-cli.html)
* [AWS SAM CLI](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/install-sam-cli.html)
* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* Opcional (Gestión de versiones de librerias en local) [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)

### Detalles

Para generar el documento PDF lo más aproximado posible a la plantilla requerida y que al 
ingresar la información mantuviera un resultado estético, fue necesario la utilización de 
la librería WeasyPrint en la versión 54.0. Siendo necesario el uso de Docker para crear una 
imagen que tuviera las dependencias requeridas para esta versión, la cual no era soportada 
en las imágenes de Amazon Linux 2.
Dentro del trabajo realizado se encontraron las siguientes fuentes de información que fueron 
de gran ayuda para alcanzar el resultado.

* [Using container image support for AWS Lambda with AWS SAM](https://aws.amazon.com/es/blogs/compute/using-container-image-support-for-aws-lambda-with-aws-sam/)
* [How to Deploy a Lambda Function as a Container Image: Docker + SAM + ECR](https://levelup.gitconnected.com/how-to-deploy-a-lambda-function-as-a-container-image-docker-sam-ecr-2846809f90e1)
* [Creación de funciones de Lambda con Python](https://docs.aws.amazon.com/es_es/lambda/latest/dg/lambda-python.html)

Información para crear una imagen apartir de una imagen base diferente a AWS lambda:
* [Implementar funciones de Python Lambda con imágenes de contenedor](https://docs.aws.amazon.com/es_es/lambda/latest/dg/python-image.html)
* [Containerizing Python Apps for Lambda](https://www.slim.ai/blog/containerized-lambda-in-python-language/)
* [AWS SAM - Lambda - Ruby 3.2 - Container Image](https://github.com/wildomonges/lambda-ruby3.2-container-image/blob/main/Dockerfile)

### Ejecución del Proyecto en Local
```shell
sam build
sam local start-api --env-vars env.json
```

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