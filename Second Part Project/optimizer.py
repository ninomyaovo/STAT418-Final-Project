# -*- coding: utf-8 -*-

from __future__ import annotations

import functools
import pathlib
from typing import List, Set

import pandas as pd
import re, ast

# ---------------------------------------------------------------------
# 1.  Paths
# ---------------------------------------------------------------------
PKG_DIR   = pathlib.Path(__file__).parent          # …/second_part
DATA_PATH = "pokemon_clean.csv"

# ---------------------------------------------------------------------
# 2.  Data loader (cached per worker)
# ---------------------------------------------------------------------
@functools.lru_cache
def load_data() -> pd.DataFrame:
    """Return the cached Pokémon DataFrame (no external calls)."""
    df = pd.read_csv(DATA_PATH)

    # Ensure weaknesses column is a Python set for fast checks
    df["weaknesses"] = df["weaknesses"].fillna("").apply(
        lambda s: set(w.strip() for w in s.split(",") if w)
    )

    # Add total_stat if missing
    stat_cols = {
        "hp", "attack", "defense", "special-attack", "special-defense", "speed"
    }
    if "total_stat" not in df.columns and stat_cols.issubset(df.columns):
        df["total_stat"] = df[list(stat_cols)].sum(axis=1)
     
    #reassign roles
    df["role"] = df.apply(_assign_role, axis=1)

    return df

# ---------------------------------------------------------------------
# 3.  Role classifier (same thresholds you used before)
# ---------------------------------------------------------------------
def _assign_role(p) -> str:
    stat_block = {
        "hp": p["hp"],
        "attack": p["attack"],
        "defense": p["defense"],
        "special-attack": p["special-attack"],
        "special-defense": p["special-defense"],
        "speed": p["speed"]
    }

    max_stat = max(stat_block, key=stat_block.get)

    # Physical Sweeper: attack is highest & speed >= 75
    if max_stat == "attack" and p["speed"] >= 75:
        return "Physical Sweeper"

    # Special Sweeper: sp. atk is highest & speed >= 75
    if max_stat == "special-attack" and p["speed"] >= 75:
        return "Special Sweeper"

    # Tank: hp/def/spdef is highest and at least one of them is high
    if max_stat in ["hp", "defense", "special-defense"]:
        return "Tank"

    # Fallback if no criteria are met
    return "Support"



# ---------------------------------------------------------------------
# 4.  Greedy optimiser
# ---------------------------------------------------------------------
def optimise_team(
    starters: List[str] | None = None,
    hp_floor:   int = 0,
    atk_floor:  int = 0,
    def_floor:  int = 0,
    spatk_floor:int = 0,
    spdef_floor:int = 0,
    spd_floor:  int = 0,
    team_size:  int = 6,
    required_roles: Set[str] | None = None,
) -> pd.DataFrame:
    """
    Build a balanced team that

    • Includes every user-selected starter Pokémon.
    • Attempts to cover each role in `required_roles`.
    • Minimises overlapping weaknesses greedily.

    Parameters
    ----------
    starters        : list[str] – Pokémon names (Title-case) pre-selected in UI.
    hp_floor        : int       – HP threshold for **non-starters**.
    team_size       : int       – Final team length (default 6).
    required_roles  : set[str]  – Roles that should appear at least once.
                                  Default = {'Tank','Physical Sweeper',
                                             'Special Sweeper','Support'}

    Returns
    -------
    pd.DataFrame    – Final squad (len ≤ team_size).
    """

    df = load_data()

    # 0 ▸ sanity & defaults
    starters = [s.title() for s in (starters or [])]
    if required_roles is None:
        required_roles = {"Tank", "Physical Sweeper",
                          "Special Sweeper", "Support"}
    # 1 ▸ filter pool
    team   = df[df["name"].isin(starters)].copy()
    used_w = set().union(*team["weaknesses"])
    added_roles = set(team["role"])

    # 2 ▸  build the pool for the remaining slots
    pool = (
        df[~df["name"].isin(starters) & (df["hp"] >= hp_floor)]
            .assign(weak_len=lambda d: d["weaknesses"].apply(len))
            .sort_values(["weak_len", "total_stat"])
            .drop(columns="weak_len")
    )

    floors = {
        "hp": hp_floor,
        "attack": atk_floor,
        "defense": def_floor,
        "special-attack": spatk_floor,
        "special-defense": spdef_floor,
        "speed": spd_floor,
    }

    for col, floor in floors.items():
        pool = pool[pool[col] >= floor]

    # 3 ▸ first pass – cover missing roles with no new overlap
    for role in required_roles - added_roles:
        for _, p in pool.iterrows():
            if p["role"] == role and p["weaknesses"].isdisjoint(used_w):
                team = pd.concat([team, p.to_frame().T])
                used_w.update(p["weaknesses"])
                added_roles.add(role)
                pool = pool.drop(p.name)
                break

    # 4 ▸ second pass – fill remaining slots with zero-overlap picks
    for _, p in pool.iterrows():
        if len(team) >= team_size:
            break
        if p["weaknesses"].isdisjoint(used_w):
            team = pd.concat([team, p.to_frame().T])
            used_w.update(p["weaknesses"])
            pool = pool.drop(p.name)

    # 5 ▸ final pass – allow overlap if we still need bodies
    if len(team) < team_size:
        extra = pool.head(team_size - len(team))
        team = pd.concat([team, extra])

    # ---------- prettify weaknesses column ---------------------------
    team["weaknesses"] = team["weaknesses"].apply(_to_csv)
    return team.reset_index(drop=True)



def _to_csv(val):
    # brute-force cleanup: strip braces/quotes, split on commas
    stripped = re.sub(r"[{}\'\"]", "", str(val))          # drop { } and '
    words = [w.strip() for w in stripped.split(",") if w.strip()]
    return str(words) if len(words) == 1 else ", ".join(words)
# Quick smoke test (run in terminal)
"""
from optimizer import optimise_team
squad = optimise_team(starters=["Pikachu"], hp_floor=120)
print(squad[["name", "role", "hp", "weaknesses"]])
"""
