FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements/prod.txt

EXPOSE 80
EXPOSE 443

CMD ["python", "-m", "bereal.main"]
