# utils.py

import os
from kubernetes import client, config
import jump
import structlog
import hashlib

logger = structlog.get_logger()

def resolve_vllm_backends() -> list[str]:
    """Resolve vLLM backends"""
    try:
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        namespace = os.getenv("POD_NAMESPACE", "llm-app")
        label_selector = os.getenv("VLLM_LABEL_SELECTOR", "app=llm-app-vllm")

        pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

        backends = []
        for pod in pods.items:
            if pod.status.phase == "Running" and pod.status.pod_ip:
                ip = pod.status.pod_ip
                backends.append(f"http://{ip}:8000")
        return backends

    except Exception as e:
        logger.error("Failed to resolve vLLM backends", error=str(e), exc_info=True)
        return []

def pick_backend(session_id: str, backends: list[str]) -> str:
    """Pick a backend for the session"""
    if not backends:
        raise ValueError("No available backends")

    key = int(hashlib.sha256(session_id.encode()).hexdigest(), 16)
    index = jump.hash(key, len(backends))
    return backends[index]
