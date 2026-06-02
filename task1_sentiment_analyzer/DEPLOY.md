# Task 1 — Sentiment Analyzer Local Deployment

A FastAPI service wrapping the HuggingFace `distilbert-base-uncased-finetuned-sst-2-english` model, deployed on a local k3d Kubernetes cluster.

---

## Prerequisites

- Docker Desktop running
- k3d cluster running (`k3d-gooperator` in this case)
- `kubectl` configured and pointing to your cluster

Verify your cluster is up:

```bash
kubectl get nodes
```

You should see your server node in `Ready` state.

---

## Step 1 — Build the Docker Image

From the repo root:

```bash
docker build -t sentiment-analyzer:v1.0 task1_sentiment_analyzer/
```

This will:
- Install all Python dependencies (FastAPI, PyTorch, Transformers)
- Download and bake the HuggingFace model into the image at build time

> Takes ~3-5 minutes on first build. Subsequent builds use layer cache.

---

## Step 2 — Import Image into k3d

k3d clusters don't pull from your local Docker daemon by default. You must import the image directly:

```bash
k3d image import sentiment-analyzer:v1.0 -c gooperator
```

Replace `gooperator` with your cluster name if different. Check your cluster name with:

```bash
k3d cluster list
```

---

## Step 3 — Deploy to Kubernetes

Apply the deployment and service manifests:

```bash
kubectl apply -f task1_sentiment_analyzer/k8s/
```

This creates:
- A `Deployment` managing 1 replica pod
- A `ClusterIP` Service exposing port 80 → 8000

---

## Step 4 — Wait for Pod to be Ready

The pod takes ~30 seconds to start (model loads into memory):

```bash
kubectl wait --for=condition=ready pod -l app=sentiment-analyzer --timeout=120s
```

Confirm everything is running:

```bash
kubectl get pods
kubectl get svc sentiment-analyzer
```

---

## Step 5 — Test the API

Port-forward the service to your local machine:

```bash
kubectl port-forward svc/sentiment-analyzer 8080:80
```

In a separate terminal, send a prediction request:

```bash
# Single prediction
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love learning MLOps!"}'

# Batch prediction
curl -X POST http://localhost:8080/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["This is great!", "This is terrible."]}'

# Health check
curl http://localhost:8080/health
```

Expected response:

```json
{
  "text": "I love learning MLOps!",
  "label": "POSITIVE",
  "score": 0.9987
}
```

---

## Teardown

```bash
kubectl delete -f task1_sentiment_analyzer/k8s/
```

---

## Notes

- `imagePullPolicy: Never` is set in the deployment — required when using locally imported images in k3d
- The model is baked into the Docker image at build time, so no internet access is needed at runtime
- If your agent node is `NotReady`, replicas is set to 1 so the pod schedules only on the server node
- The service type is `ClusterIP` (internal only) — use `port-forward` for local access, or change to `LoadBalancer`/`NodePort` for external access
