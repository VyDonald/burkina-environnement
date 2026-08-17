FROM eclipse-temurin:17-jre-alpine AS fuseki

# Télécharger Apache Jena Fuseki
ARG FUSEKI_VERSION=4.10.0
RUN apk add --no-cache curl tar bash \
    && curl -fsSL "https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-${FUSEKI_VERSION}.tar.gz" \
       -o /tmp/fuseki.tar.gz \
    && tar -xzf /tmp/fuseki.tar.gz -C /opt \
    && mv /opt/apache-jena-fuseki-${FUSEKI_VERSION} /opt/fuseki \
    && rm /tmp/fuseki.tar.gz

# --- Étape 2 : Python ---
FROM python:3.12-slim

# Installer Java (nécessaire pour Fuseki)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless curl procps \
    && rm -rf /var/lib/apt/lists/*

# Copier Fuseki depuis l'étape précédente
COPY --from=fuseki /opt/fuseki /opt/fuseki

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Rendre les scripts exécutables
RUN chmod +x start.sh

# Créer le répertoire de données Fuseki
RUN mkdir -p /opt/fuseki/run/configuration && chown -R appuser:appuser /opt/fuseki/run

EXPOSE 5000

USER appuser

CMD ["./start.sh"]
