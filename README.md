# 🧠 LLM Server – FastAPI + vLLM on Kubernetes

Ce projet expose une API REST (`/api/chat`) pour interagir avec un modèle de langage via [vLLM](https://github.com/vllm-project/vllm), avec support GPU, batching, et mise à l’échelle Kubernetes.

## 🚀 Fonctionnalités

- API REST via FastAPI
- Modèle LLM servi via vLLM
- Sticky session via header pour optimisation KV cache
- Configuration dynamique via Helm
- Logs formattés JSON sur stdout prêts pour collecte
- Monitoring Prometheus (/metrics exposés)
- Test de charge via `wrk` 

---

## 📦 Déploiement

### 1. Prérequis

- Kubernetes (testé avec `minikube`)
- Helm ≥ 3.x
- GPU (ou `useGPU: false` pour CPU-only). Attention, vLLM très instable sur CPU, nombreuses erreurs relevées et non support de WSL2 + CPU 
- NGINX ingress controller ou Traefik configurable (non déployé)

### 2. Build local des images

```bash
docker build -t <nom_de_repo>/fastapi:<tag>-f Dockerfile.fastapi .
docker build -t <nom_de_repo>/vllm-tinyllama:<tag> -f Dockerfile.vllm . # Nécessite de placer un modèle supporté vLLM dans /models
```

### 3. Déploiement avec Helm

```bash
helm upgrade --install llm-app ./helm-chart \
  --namespace llm-app --create-namespace
  ```

  Exemple de values par défaut:

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
  useGPU: true # si True, GPU utilisé (nécessite support de Nvidia device plugin)
  resources:
    requests:
      cpu: "1"
      memory: "4Gi"
    limits:
      cpu: "2"
      memory: "8Gi"

ingress:
  enabled: true  
  type: standard  # "traefik" or "standard"
  className: nginx  # ingress class name (e.g., nginx, traefik)
  host: fastapi.localhost

```
### 4. Nettoyage

```bash
helm uninstall llm-app -n <namespace_name>
kubectl delete namespace <namespace_name>
```


## Endpoints exposés 

/api/chat	Endpoint principal pour interroger le modèle
/metrics	Export Prometheus
/ready	Readiness probe
/healthz	Liveness probe


## Test de charge

```bash
./tests/run_load_test.sh
```
Valeurs paramétrables:

URL="http://fastapi.localhost/api/chat"
DURATION="30s"
THREADS=10
CONNECTIONS=100
SCRIPT="./tests/post.lua"


