#!/bin/bash

# Configuration
URL="http://fastapi.localhost/api/chat"
DURATION="30s"
THREADS=10
CONNECTIONS=100
SCRIPT="./tests/post.lua"

echo "🚀 Lancement du test de charge avec wrk"
echo "🔗 URL: $URL"
echo "📌 Durée: $DURATION"
echo "🧵 Threads: $THREADS | 🔄 Connexions: $CONNECTIONS"
echo ""

# Vérification du fichier Lua
if [ ! -f "$SCRIPT" ]; then
  echo "❌ Fichier Lua '$SCRIPT' introuvable."
  exit 1
fi

# Exécution du test
RESULT=$(wrk -t"$THREADS" -c"$CONNECTIONS" -d"$DURATION" -s "$SCRIPT" "$URL" 2>&1)

# Extraction des données
REQS=$(echo "$RESULT" | grep "Requests/sec" | awk '{print $2}')
LATENCY_LINE=$(echo "$RESULT" | grep -E "Latency[[:space:]]+[0-9\.]+[a-z]+[[:space:]]+[0-9\.]+[a-z]+[[:space:]]+[0-9\.]+[a-z]+")
LAT_AVG=$(echo "$LATENCY_LINE" | awk '{print $2}')
LAT_MAX=$(echo "$LATENCY_LINE" | awk '{print $4}')
SOCKET_ERRORS=$(echo "$RESULT" | grep "Socket errors:" | sed 's/Socket errors: //')

# Résumé
echo "📊 Résultats du test wrk"
echo "-----------------------------"
echo "🌐 URL:             $URL"
echo "⏱️ Durée:           $DURATION"
echo "🔁 Requêtes/sec:    ${REQS:-n/a}"
echo "⏱️ Latence moy.:    ${LAT_AVG:-n/a}"
echo "⏱️ Latence max:     ${LAT_MAX:-n/a}"
echo "❌ Erreurs socket:  ${SOCKET_ERRORS:-0}"
echo "-----------------------------"
