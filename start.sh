#!/bin/sh
set -e

echo "=== Demarrage de l'environnement ==="

# --- 1. Demarrer Fuseki en arriere-plan ---
echo "[1/4] Demarrage de Apache Jena Fuseki..."
FUSEKI_BASE="/tmp/fuseki-run"
mkdir -p "$FUSEKI_BASE/configuration"
export FUSEKI_BASE
/opt/fuseki/fuseki-server --port=3030 &

# Attendre que Fuseki soit pret
echo "      Attente de Fuseki..."
READY=0
for i in $(seq 1 40); do
    if curl -s "http://localhost:3030/\$/server" > /dev/null 2>&1; then
        echo "      Fuseki pret !"
        READY=1
        break
    fi
    sleep 1
done

if [ "$READY" -eq 0 ]; then
    echo "ERREUR: Fuseki n'a pas demarre"
    exit 1
fi

# --- 2. Creer le dataset et charger l'ontologie ---
echo "[2/4] Creation du dataset 'environnement'..."
curl -s -X POST "http://localhost:3030/\$/datasets" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "dbName=environnement&dbType=tdb2" \
    > /dev/null 2>&1 || true

echo "[3/4] Chargement de l'ontologie (rdf)..."
curl -s -X POST "http://localhost:3030/environnement/data" \
    -H "Content-Type: application/rdf+xml" \
    --data-binary @ontologie_environnement.rdf \
    > /dev/null 2>&1

echo "      Verification..."
COUNT=$(curl -s "http://localhost:3030/environnement/query" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['results']['bindings'][0]['n']['value'])" 2>/dev/null || echo "0")
echo "      Triples charges: $COUNT"

# --- 3. Demarrer Flask ---
echo "[4/4] Demarrage de l'application Flask..."
export FUSEKI_ENDPOINT="http://localhost:3030/environnement/query"
APP_PORT="${PORT:-5000}"

exec gunicorn app:app \
    --bind "0.0.0.0:${APP_PORT}" \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
