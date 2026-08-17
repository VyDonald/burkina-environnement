#!/bin/sh
set -e

echo "=== Démarrage de l'environnement ==="

# --- 1. Démarrer Fuseki en arrière-plan ---
echo "[1/4] Démarrage de Apache Jena Fuseki..."
/opt/fuseki/fuseki-server --port=3030 &
FUSEKI_PID=$!

# Attendre que Fuseki soit prêt
echo "      Attente de Fuseki..."
for i in $(seq 1 30); do
    if curl -s http://localhost:3030/\$/server > /dev/null 2>&1; then
        echo "      Fuseki prêt !"
        break
    fi
    sleep 1
done

# Vérifier que Fuseki tourne
if ! curl -s http://localhost:3030/\$/server > /dev/null 2>&1; then
    echo "ERREUR: Fuseki n'a pas démarré"
    exit 1
fi

# --- 2. Créer le dataset et charger l'ontologie ---
echo "[2/4] Création du dataset 'environnement'..."
curl -s -X POST 'http://localhost:3030/$/datasets' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'dbName=environnement&dbType=tdb2' \
    > /dev/null 2>&1 || true

echo "[3/4] Chargement de l'ontologie (rdf)..."
curl -s -X POST 'http://localhost:3030/environnement/data' \
    -H 'Content-Type: application/rdf+xml' \
    --data-binary @ontologie_environnement.rdf \
    > /dev/null 2>&1

echo "      Vérification..."
COUNT=$(curl -s 'http://localhost:3030/environnement/query' \
    -H 'Accept: application/sparql-results+json' \
    --data-urlencode 'query=SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }' \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['results']['bindings'][0]['n']['value'])" 2>/dev/null || echo "0")
echo "      Triples chargés: $COUNT"

# --- 3. Démarrer Flask ---
echo "[4/4] Démarrage de l'application Flask..."
export FUSEKI_ENDPOINT="http://localhost:3030/environnement/query"

exec gunicorn app:app \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
