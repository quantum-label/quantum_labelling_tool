FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libglib2.0-0 \
    libffi-dev \
    netcat-openbsd

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

COPY ./code /app/code
COPY quantum /app/quantum
COPY static /app/static
COPY staticfiles /app/staticfiles
COPY templates /app/templates
COPY webapp /app/webapp
COPY manage.py /app/

EXPOSE 8000

# Copy and setup entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use entrypoint script instead of running migrations at build time
CMD ["/entrypoint.sh"]
