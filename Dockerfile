FROM python:3.11-alpine
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN apk add --no-cache postgresql-client && pip install -r requirements.txt
COPY api /app/api
RUN cd /app/api && pip install -e .
CMD ["flask", "run", "--host", "0.0.0.0"]