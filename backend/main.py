from fastapi import FastAPI, HTTPException

from models.schemas import CompareRequest, CompareResponse
from services.comparator import compare_prices

app = FastAPI(
    title="Hotel Price Comparator",
    version="0.1.0",
    description="Compare normalized hotel prices across Qunar, Zhixing and Amap.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    try:
        return compare_prices(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
