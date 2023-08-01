FROM python:3.11

RUN mkdir script

ADD requirments.txt .
ADD src script/src

RUN pip install -r requirments.txt

WORKDIR /script/src

CMD ["python", "main.py"]