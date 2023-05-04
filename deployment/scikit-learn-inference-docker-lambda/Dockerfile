FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt ./
RUN python3.10 -m pip install -r requirements.txt -t .

COPY ./app/harmony ./
COPY ./app/app.py   ./

CMD ["app.handler"]