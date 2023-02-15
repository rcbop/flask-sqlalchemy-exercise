FROM python:3.11-alpine
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY api .
WORKDIR /app/api
CMD ["flask", "run", "--host", "0.0.0.0"]