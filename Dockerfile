FROM python:3.10-bullseye
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "serve.py"]