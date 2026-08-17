FROM eclipse-temurin:17-jre-alpine AS fuseki-stage

ARG FUSEKI_VERSION=5.5.0
RUN apk add --no-cache curl tar bash \
    && curl -fsSL "https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-${FUSEKI_VERSION}.tar.gz" \
       -o /tmp/fuseki.tar.gz \
    && tar -xzf /tmp/fuseki.tar.gz -C /opt \
    && mv /opt/apache-jena-fuseki-${FUSEKI_VERSION} /opt/fuseki \
    && rm /tmp/fuseki.tar.gz \
    && chmod +x /opt/fuseki/fuseki-server

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless curl procps \
    && rm -rf /var/lib/apt/lists/*

COPY --from=fuseki-stage /opt/fuseki /opt/fuseki

RUN useradd -m -u 1000 appuser \
    && mkdir -p /opt/fuseki/run/configuration \
    && chown -R appuser:appuser /opt/fuseki/run

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 5000

USER appuser

CMD ["./start.sh"]
