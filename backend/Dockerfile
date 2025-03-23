FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN apt update \
  && apt install -y graphviz libgraphviz-dev \
  && rm -rf /var/lib/apt/lists/* \
  && pip install -r requirements.txt

COPY . /app/

RUN chmod +x entrypoint.sh \
  && apt update \
  && apt install -y gettext \
  && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
