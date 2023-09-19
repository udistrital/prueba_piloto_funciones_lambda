FROM public.ecr.aws/lambda/python:3.9-x86_64

RUN yum update -y

RUN yum install -y redhat-rpm-config  \
    python-devel  \
    python-pip  \
    python-setuptools  \
    python-pillow \
    python-wheel  \
    python-cffi  \
    libffi-devel  \
    python3-brotli \
    cairo  \
    pango  \
    gdk-pixbuf2

COPY app.py requirements.txt ./
RUN pip3 install -r requirements.txt
CMD ["app.lambda_handler"]