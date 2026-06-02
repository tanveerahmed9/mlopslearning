from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="Sentiment Analyzer", version="1.0")

# Load model once at startup
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


class TextInput(BaseModel):
    text: str


class BatchInput(BaseModel):
    texts: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(input: TextInput):
    result = sentiment_pipeline(input.text)[0]
    return {
        "text": input.text,
        "label": result["label"],
        "score": round(result["score"], 4),
    }


@app.post("/predict/batch")
def predict_batch(input: BatchInput):
    results = sentiment_pipeline(input.texts)
    return [
        {"text": t, "label": r["label"], "score": round(r["score"], 4)}
        for t, r in zip(input.texts, results)
    ]
