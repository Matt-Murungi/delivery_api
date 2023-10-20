FROM python:3.7.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
COPY entrypoint.sh /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . ./

EXPOSE 8000
# RUN chmod +x entrypoint.sh
# ENTRYPOINT ["sh", "entrypoint.sh"]

# Collect static files
RUN python3 app/manage.py collectstatic --noinput

#RUN python3 app/manage.py migrate


CMD python3 app/manage.py runserver 0.0.0.0:8000