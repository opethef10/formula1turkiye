FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf8
ENV PYTHONUTF8=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements/base.txt requirements/development.txt ./requirements/

RUN pip install -r ./requirements/development.txt

COPY . .

EXPOSE 8888

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8888" ]
