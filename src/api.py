from pathlib import Path
from typing import List, Literal

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from nba_api.stats.static import players as players_static
from pydantic import BaseModel

from formula_parser import (
    SHOT_TYPES,
    STAT_DEFINITIONS,
    ZONES,
    build_custom_definitions,
    evaluate_formula,
)
from stats_engine import get_player_shots

app = FastAPI(title="NBA Lab API")


def data_error(exc):
    if isinstance(exc, requests.exceptions.RequestException):
        return HTTPException(
            status_code=503,
            detail="Can't reach the NBA stats server right now. Players already saved in the database still work.",
        )
    return HTTPException(status_code=502, detail=f"Failed to load data: {exc}")

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


@app.get("/api/stats/options")
def stat_options():
    return {"zones": ZONES, "shot_types": list(SHOT_TYPES.keys())}


@app.get("/api/shots")
def shots(player: str, season: str):
    try:
        df = get_player_shots(player, season)
    except Exception as exc:
        raise data_error(exc)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No shot data for {player} in {season}")

    return df.to_dict(orient="records")


class CustomStat(BaseModel):
    name: str
    zones: List[str] = []
    shot_types: List[str] = []
    shot_match: Literal["any", "all"] = "any"


class FormulaRequest(BaseModel):
    player: str
    season: str
    formula: str
    custom_stats: List[CustomStat] = []


@app.post("/api/formula/evaluate")
def formula_evaluate(req: FormulaRequest):
    custom_definitions, custom_errors = build_custom_definitions(
        [stat.model_dump() for stat in req.custom_stats]
    )
    if custom_errors:
        raise HTTPException(status_code=400, detail=custom_errors)

    try:
        result, breakdown, errors = evaluate_formula(
            req.player, req.season, req.formula, custom_definitions
        )
    except Exception as exc:
        raise data_error(exc)

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    return {"result": result, "breakdown": breakdown}


# Serve the built React app (run `npm run build` in frontend/ first)
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
