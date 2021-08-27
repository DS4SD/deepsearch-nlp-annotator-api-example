FROM python:3.8-buster AS build

COPY requirements.txt .

RUN pip install -U -r requirements.txt

FROM python:3.8-slim-buster

COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

COPY . .

EXPOSE 5000

CMD ["python", "-m", "nlp_annotator_api.server.app"]
