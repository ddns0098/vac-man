FROM python:3.6

COPY . /src/vac_man

RUN pip install -r /src/vac_man/requirements/install.txt

WORKDIR /src/vac_man

EXPOSE 5000
CMD ["python", "run.py"]
