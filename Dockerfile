FROM python:3.7-alpine

RUN mkdir /opencravat
COPY opencravat_command_line.py /opencravat/opencravat_command_line.py

RUN pip install requests 

ENTRYPOINT []
