FROM python:3.9-slim as builder

RUN apt-get update \
 && apt-get install -y gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR app
COPY requirements.txt ./
RUN pip install --user --trusted-host pypi.python.org -r requirements.txt
COPY . /app

FROM python:3.9-slim as app

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

WORKDIR /token-price-collector
COPY token-price-collector ./

EXPOSE 8000

CMD ["python3", "main.py"]
