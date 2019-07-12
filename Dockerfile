FROM nvcr.io/nvidia/tensorflow:19.05-py3

ADD src /src

WORKDIR /src

RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ['python3']

CMD ['app.py']
