# LLM Server – FastAPI + vLLM on Kubernetes

Ce projet expose une API REST (`/api/chat`) pour interagir avec un modèle de langage via [vLLM](https://github.com/vllm-project/vllm), avec support GPU, batching, sticky session pour KV cache optimisation et mise à l’échelle Kubernetes.

## 🚀 Fonctionnalités

* API REST via FastAPI
* Modèle LLM servi via vLLM
* Sticky session via header pour optimisation KV cache
* Configuration dynamique via Helm
* Logs formattés JSON sur stdout prêts pour collecte
* Monitoring Prometheus (/metrics exposés)
* Test de charge via `wrk`

---

## 📦 Déploiement

### 1. Prérequis

* Kubernetes (testé avec `minikube`)
* Helm ≥ 3.x
* GPU (ou `useGPU: false` pour CPU-only). ⚠️ vLLM très instable sur CPU, nombreuses erreurs relevées et non support de WSL2 + CPU
* NGINX ingress controller ou Traefik configurable (non déployé)

### 2. Images Docker

Deux options sont possibles :

#### a. Utiliser les images pré-construites du dépôt public DockerHub (TinyLlama-1.1B)

```yaml
fastapi.image: docktet/fastapi:v1.1.9
vllm.image.repository: docktet/vllm-tinyllama # ~4 Gb
vllm.image.tag: latest
```

#### b. Construire les images localement (avec choix de modèle)

```bash
docker build -t <nom_de_repo>/<nom_image>:<tag> -f Dockerfile.fastapi .
docker build -t <nom_de_repo>/<nom_image>:<tag> -f Dockerfile.vllm . # Nécessite de placer un modèle supporté vLLM dans /models
```

### 3. Déploiement avec Helm

```bash
helm upgrade --install llm-app ./helm-chart \
  --namespace llm-app --create-namespace
```

#### Exemple de values.yaml :

```yaml
namespace: llm-app

fastapi:
  name: fastapi
  image: docktet/fastapi:v1.1.9 # Image publique avec modèle préchargé 
  serviceAccount:
    name: fastapi
  containerPort: 3000
  replicaCount: 2
  modelDisplayName: "TinyLlama-1.1B" # Nom de modèle affiché dans les réponses
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

vllm:
  name: vllm
  image:
    repository: docktet/vllm-tinyllama # Image publique avec modèle préchargé 
    tag: latest
  port: 8000
  replicaCount: 1
  useGPU: true # Si True, GPU utilisé (nécessite support de Nvidia device plugin)
  resources: # Uniquement si useGPU = false
    requests:
      cpu: "1"
      memory: "4Gi"
    limits:
      cpu: "2"
      memory: "8Gi"

ingress:
  enabled: true # Déploiement ingress pour exposition si true
  type: standard # "traefik" ou "standard"
  className: nginx # Ingress class name (e.g., nginx, traefik)
  host: fastapi.localhost
```

### 4. Nettoyage

```bash
helm uninstall llm-app -n llm-app
kubectl delete namespace llm-app
```

---

## 🌐 Endpoints exposés

| Endpoint    | Description          |
| ----------- | -------------------- |
| `/api/chat` | Interroger le modèle |
| `/metrics`  | Export Prometheus    |
| `/ready`    | Readiness probe      |
| `/healthz`  | Liveness probe       |

---

## 🧹 Architecture – composants principaux

L’application est composée de deux services principaux déployés dans Kubernetes :

* **FastAPI Gateway**

  * Expose `/api/chat`, `/metrics`, `/healthz`, `/ready`
  * Répartit les requêtes vers vLLM via `X-Session-ID`
  * Intègre un client Kubernetes pour découverte dynamique des pods vLLM

* **vLLM Backend**

  * Expose les endpoints OpenAI compatibles (`/v1/chat/completions`, etc.)
  * Effectue la génération de texte avec batching et cache KV GPU
  * Peut être configuré avec ou sans GPU (⚠️ CPU instable)

🔁 Ces services communiquent via le réseau interne du cluster (service Kubernetes).

---

## 🔁 Sticky sessions (optimisation cache)

L’API `/api/chat` utilise une optimisation de cache via les sticky sessions. Le client peut transmettre un en-tête HTTP personnalisé `X-Session-ID`.

Cela permet à FastAPI de router toujours vers le même pod vLLM, assurant la réutilisation du **KV cache** de génération de tokens (mémoire GPU).

* ⚡️ Cela accélère les requêtes multi-turn / itératives.
* 🧠 Si non spécifié, une session aléatoire est générée automatiquement côté FastAPI.
* 🔄 Si vous utilisez un client custom, conservez le même `X-Session-ID` pour les appels suivants.

---

## 📊 Test de charge

Utilise `post.lua` pour générer dynamiquement des prompts variés.

⚠️ Limitation : `wrk` applique un timeout de 2 secondes sur chaque requête.

```bash
./tests/run_load_test.sh
```

Valeurs paramétrables :

```bash
URL="http://fastapi.localhost/api/chat"
DURATION="30s"
THREADS=10
CONNECTIONS=100
SCRIPT="./tests/post.lua"
```

---

## ✍️ Exemple complet de requête avec paramètres

L’API supporte les principaux paramètres de sampling acceptés par vLLM. Voici un exemple :

```bash
curl -X POST http://fastapi.localhost/api/chat \
     -H "Content-Type: application/json" \
     -H "X-Session-ID: session-42" \
     -d '{
           "messages": [
             {"role": "user", "content": "Can you write a short story about a robot who discovers music?"}
           ],
           "temperature": 0.8,
           "top_p": 0.95,
           "top_k": 50,
           "max_tokens": 200,
           "stop": ["</s>", "\n"],
           "presence_penalty": 0.2,
           "frequency_penalty": 0.2,
           "repetition_penalty": 1.1,
           "logprobs": null,
         }'
```

---

## 👤 Auteur

Erwan Lavenant – 2025
