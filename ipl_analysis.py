"""
IPL Data Analysis (2008-2023)
Run this script to perform quick analysis without Jupyter.
Full analysis available in IPL_Analysis.ipynb
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Config ────────────────────────────────────
DATA_DIR    = "data"
CHARTS_DIR  = "charts"
MATCHES     = os.path.join(DATA_DIR, "matches.csv")
DELIVERIES  = os.path.join(DATA_DIR, "deliveries.csv")

os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Load Data ─────────────────────────────────
def load_data():
    matches    = pd.read_csv(MATCHES)
    deliveries = pd.read_csv(DELIVERIES)
    print(f"Matches loaded    : {len(matches)}")
    print(f"Deliveries loaded : {len(deliveries)}")
    return matches, deliveries

# ── Team Win Count ────────────────────────────
def team_wins(matches):
    wins = matches['winner'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=wins.values, y=wins.index, palette='viridis', ax=ax)
    ax.set_title('Top 10 Teams by Wins (2008-2023)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Wins')
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'team_wins.png')
    plt.savefig(path, dpi=150)
    plt.show()
    print(f"Chart saved → {path}")
    return wins

# ── Toss Impact ───────────────────────────────
def toss_impact(matches):
    toss_win = matches[matches['toss_winner'] == matches['winner']]
    pct = round(len(toss_win) / len(matches) * 100, 2)
    print(f"\nToss winner also won match: {pct}% of the time")
    return pct

# ── Top Run Scorers ───────────────────────────
def top_batsmen(deliveries, top_n=10):
    runs = (
        deliveries.groupby('batter')['batsman_runs']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=runs.values, y=runs.index, palette='magma', ax=ax)
    ax.set_title(f'Top {top_n} Run Scorers — IPL', fontsize=14, fontweight='bold')
    ax.set_xlabel('Total Runs')
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'top_batsmen.png')
    plt.savefig(path, dpi=150)
    plt.show()
    print(f"Chart saved → {path}")
    return runs

# ── Top Wicket Takers ─────────────────────────
def top_bowlers(deliveries, top_n=10):
    wickets = (
        deliveries[deliveries['dismissal_kind'].notna() &
                   ~deliveries['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field'])]
        .groupby('bowler')['dismissal_kind']
        .count()
        .sort_values(ascending=False)
        .head(top_n)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=wickets.values, y=wickets.index, palette='rocket', ax=ax)
    ax.set_title(f'Top {top_n} Wicket Takers — IPL', fontsize=14, fontweight='bold')
    ax.set_xlabel('Total Wickets')
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'top_bowlers.png')
    plt.savefig(path, dpi=150)
    plt.show()
    print(f"Chart saved → {path}")
    return wickets

# ── Season-wise Totals ────────────────────────
def season_stats(matches):
    season_counts = matches['season'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(season_counts.index.astype(str), season_counts.values, color='steelblue')
    ax.set_title('Matches per Season', fontsize=14, fontweight='bold')
    ax.set_xlabel('Season')
    ax.set_ylabel('Matches')
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, 'season_stats.png')
    plt.savefig(path, dpi=150)
    plt.show()
    print(f"Chart saved → {path}")

# ── Main ──────────────────────────────────────
def main():
    print("=" * 45)
    print("  IPL Data Analysis — Quick Run")
    print("=" * 45)

    matches, deliveries = load_data()

    print("\n[1/4] Team win analysis...")
    team_wins(matches)

    print("\n[2/4] Toss impact...")
    toss_impact(matches)

    print("\n[3/4] Top batsmen...")
    top_batsmen(deliveries)

    print("\n[4/4] Top bowlers...")
    top_bowlers(deliveries)

    season_stats(matches)

    print("\n" + "=" * 45)
    print("  Analysis complete! Charts saved in /charts")
    print("=" * 45)

if __name__ == "__main__":
    main()