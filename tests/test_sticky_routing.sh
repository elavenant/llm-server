#!/bin/bash

BASE_URL="http://fastapi.localhost/api/chat"
SESSION_COUNT=5               # Nombre de sessions différentes
REQUESTS_PER_SESSION=3        # Nombre d'appels par session
PAYLOAD='{"messages":[{"role":"user","content":"hi"}]}'

generate_random_session_id() {
  echo "sess-$RANDOM-$RANDOM"
}

for s in $(seq 1 $SESSION_COUNT); do
  SESSION_ID=$(generate_random_session_id)
  echo "=== Session #$s | Session ID: $SESSION_ID ==="

  for i in $(seq 1 $REQUESTS_PER_SESSION); do
    RESPONSE=$(curl -s -X POST "$BASE_URL" \
      -H "Content-Type: application/json" \
      -H "X-Session-ID: $SESSION_ID" \
      -d "$PAYLOAD")

    MODEL=$(echo "$RESPONSE" | jq -r '.model // "mock-model"')

    if [[ "$MODEL" == "mock-model" ]]; then
      echo "  [$i] ➡️ MOCK"
    else
      echo "  [$i] ✅ REAL ($MODEL)"
    fi
  done

  echo
done
