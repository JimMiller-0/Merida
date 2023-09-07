FROM python:3
COPY . /Merida
WORKDIR /Merida
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV PROJECT_ID=merida-397714
ENV LOCATION=us-central1
ENV INSTANCE_HOST 127.0.0.1
ENV DB_USER postgres
ENV DB_PASS <password>
ENV DB_NAME merida-db
ENV DB_PORT 5432
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

