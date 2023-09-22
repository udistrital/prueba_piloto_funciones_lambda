# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.9 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY app.py ${FUNCTION_DIR}
COPY requirements.txt .

# Install the function's dependencies
RUN pip install \
    -r requirements.txt \
    --target ${FUNCTION_DIR} \
        awslambdaric

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Pass the name of the function handler as an argument to the runtime
CMD ["app.lambda_handler"]