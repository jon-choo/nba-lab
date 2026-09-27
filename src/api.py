from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from nba_api.stats.static import players as players_static
from pydantic import BaseModel

from formula_parser import STAT_DEFINITIONS, evaluate_formula
from stats_engine import get_player_shots

app = FastAPI(title="NBA Lab API")

# Dev-only: lets a frontend running on a different port call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/players/search")
def search_players(q: str):
    q = q.strip().lower()
    if len(q) < 2:
        return []

    matches = [
        {"id": p["id"], "full_name": p["full_name"], "is_active": p["is_active"]}
        for p in players_static.get_players()
        if q in p["full_name"].lower()
    ]
    matches.sort(key=lambda p: (not p["is_active"], p["full_name"]))
    return matches[:15]


@app.get("/api/stats/definitions")
def stat_definitions():
    return sorted(STAT_DEFINITIONS.keys())


@app.get("/api/shots")
def shots(player: str, season: str):
    try:
        df = get_player_shots(player, season)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch shot data: {exc}")

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No shot data for {player} in {season}")

    return df.to_dict(orient="records")


class FormulaRequest(BaseModel):
    player: str
    season: str
    formula: str


@app.post("/api/formula/evaluate")
def formula_evaluate(req: FormulaRequest):
    try:
        result, breakdown, errors = evaluate_formula(req.player, req.season, req.formula)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to evaluate formula: {exc}")

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    return {"result": result, "breakdown": breakdown}
