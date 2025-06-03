# -*- coding: utf-8 -*-

# app.py  ── minimal Shiny dashboard for the Pokémon optimiser
from shiny import App, reactive, render, ui
import pandas as pd
from optimizer import load_data   # ← uses your CSV
import ast
import httpx
from html import escape

API_URL = "https://stat418-final-project-696925248391.europe-west1.run.app/build-team"

df = load_data()          # one-time load (cached in optimizer.py)

# ---------- helper to prettify weaknesses column -------------------
def _pretty(tbl: pd.DataFrame) -> pd.DataFrame:
    out = tbl.copy()

    def clean(x):
        if isinstance(x, set):
            return ", ".join(sorted(x))
        try:
            return ", ".join(sorted(ast.literal_eval(x)))
        except Exception:
            return x

    out["weaknesses"] = out["weaknesses"].apply(clean)
    return out.drop(columns="weak_len", errors="ignore")

# ---------- UI ------------------------------------------------------
app_ui = ui.page_fluid(
    ui.h2("Pokémon Team Optimiser"),
    ui.markdown(
        "Pick up to **three starters**, set minimum base stats, and let the "
        "app fill the remaining slots while _minimising shared weaknesses_ "
        "and _covering all four roles_ (Tank / Physical Sweeper / "
        "Special Sweeper / Support)."
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.help_text("Starters are kept even if they violate the filters below."),
            ui.input_selectize(
                "starter",
                "Choose up to 3 starter Pokémon",
                choices=sorted(df["name"]),
                multiple=True,
                #max_items=3,
            ),
            ui.hr(),
            ui.markdown("Minimum base-stat thresholds"),
            
            ui.input_slider("hp_floor", "HP", 1, 170, 60),
            ui.input_slider("atk_floor",   "Attack",  1, 120, 60),
            ui.input_slider("def_floor",   "Defense", 1, 120, 60),
            ui.input_slider("spatk_floor", "Special Attack",  1, 120, 60),
            ui.input_slider("spdef_floor", "Special Defense", 1, 120, 60),
            ui.input_slider("spd_floor",   "Speed",           1, 120, 60),
            ui.input_action_button("go", "Generate team"),
        ),
        ui.output_data_frame("team_tbl"),
        ui.markdown("### Why this team?"),
        ui.output_text("explain_txt"),
    ),
)

# ---------- server --------------------------------------------------
def server(input, output, session):
    @reactive.event(input.go)          # runs only when button is clicked
    def _team():
        payload = {
            "starters": (input.starter() or [])[:3],
            "hp_floor":   input.hp_floor(),
            "atk_floor":  input.atk_floor(),
            "def_floor":  input.def_floor(),
            "spatk_floor":input.spatk_floor(),
            "spdef_floor":input.spdef_floor(),
            "spd_floor":  input.spd_floor(),
        }
            
        # POST to Cloud-Run Flask API
        r = httpx.post(API_URL, json=payload, timeout=30)
        r.raise_for_status()                # 4xx/5xx → exception in Shiny log
        return pd.DataFrame(r.json())       # API returns JSON list of dicts

    @output
    @render.data_frame
    def team_tbl():
        df = _team().copy()                     # 1 get fresh team
        df = _pretty(df)            # 2 prettify weaknesses
        df["role"] = df["role"]

        display_cols = [
        "name", "role", "hp", "attack", "defense",
        "special-attack", "special-defense", "speed",
        "total_stat", "types", "weaknesses"]
        display_cols = [c for c in display_cols if c in df.columns]
        df = df[display_cols]

        return df             # DataFrame appears in UI
    

    @output
    @render.text
    def explain_txt():
        df = _team().copy()
        if df.empty:
            return "No team generated yet."

        starters = (input.starter() or [])[:3]
        starters_msg = (
            f"Your starter{'s were' if len(starters)>1 else ' was'} "
            + ", ".join(starters) + ". "
            if starters else ""
        )

        roles = df["role"].value_counts().to_dict()
        role_msg = ", ".join(f"{k} × {v}" for k, v in roles.items())

        # total unique weaknesses vs. overlaps
        def _as_set(val):
            if isinstance(val, str):
                return {w.strip() for w in val.split(",") if w.strip()}
            return val
        
        all_w   = sum(df["weaknesses"].apply(lambda s: len(_as_set(s))), 0)
        uniq_w  = len(set().union(*df["weaknesses"].apply(_as_set)))
        weak_msg = (
            f"The squad has *{uniq_w}* distinct weaknesses "
            f"across *{all_w}* total type-matchups, meaning "
            f"only {all_w-uniq_w} overlap."
        )

        return (
            f"{starters_msg}"
            f"The optimiser first ensured every required role was covered "
            f"({role_msg}), then iteratively added Pokémon that introduced "
            f"the fewest *new* weaknesses. {weak_msg}"
        )

# ---------- run app -------------------------------------------------
app = App(app_ui, server)
