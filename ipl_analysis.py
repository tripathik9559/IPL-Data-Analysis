"""
IPL Data Analysis (2008-2023)
==============================
Comprehensive analysis of 988 matches and 2,17,000+ deliveries.
Covers team performance, toss impact, top players,
scoring patterns, venue stats, and head-to-head records.

Author  : Kartikey Kumar Tripathi
Dataset : Kaggle IPL Complete Dataset (2008-2023)
Run     : python ipl_analysis.py
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

warnings.filterwarnings('ignore')

# ── Global Style ──────────────────────────────────────────────────────────────
sns.set_theme(style='darkgrid', palette='viridis')
plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor':   '#161b22',
    'axes.edgecolor':   '#30363d',
    'axes.labelcolor':  '#c9d1d9',
    'text.color':       '#c9d1d9',
    'xtick.color':      '#8b949e',
    'ytick.color':      '#8b949e',
    'grid.color':       '#21262d',
    'figure.dpi':       130,
})

ACCENT_COLORS = ['#58a6ff', '#3fb950', '#f78166', '#d2a8ff',
                 '#ffa657', '#79c0ff', '#56d364', '#ff7b72']

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR   = 'data'
CHARTS_DIR = 'charts'
MATCHES_F  = os.path.join(DATA_DIR, 'matches.csv')
DELIVER_F  = os.path.join(DATA_DIR, 'deliveries.csv')

os.makedirs(CHARTS_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — DATA LOADING & CLEANING
# ══════════════════════════════════════════════════════════════════════════════

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load matches and deliveries CSVs with basic validation."""
    if not os.path.exists(MATCHES_F):
        raise FileNotFoundError(
            f"'{MATCHES_F}' not found.\n"
            "Download from: https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020"
        )

    matches    = pd.read_csv(MATCHES_F)
    deliveries = pd.read_csv(DELIVER_F)

    # Standardise column names
    matches.columns    = matches.columns.str.strip().str.lower()
    deliveries.columns = deliveries.columns.str.strip().str.lower()

    # Coerce date
    if 'date' in matches.columns:
        matches['date'] = pd.to_datetime(matches['date'], errors='coerce')

    print(f"  Matches loaded    : {len(matches):,} rows")
    print(f"  Deliveries loaded : {len(deliveries):,} rows")
    print(f"  Seasons covered   : {sorted(matches['season'].unique())}")
    return matches, deliveries


def data_summary(matches: pd.DataFrame, deliveries: pd.DataFrame):
    """Print a quick summary of the dataset."""
    print("\n" + "─" * 50)
    print("  DATASET SUMMARY")
    print("─" * 50)
    print(f"  Total matches      : {len(matches):,}")
    print(f"  Total deliveries   : {len(deliveries):,}")
    print(f"  Unique teams       : {matches['team1'].nunique()}")
    print(f"  Unique venues      : {matches['venue'].nunique()}")
    print(f"  Unique seasons     : {matches['season'].nunique()}")
    print(f"  Date range         : {matches['date'].min().date()} → {matches['date'].max().date()}")
    print("─" * 50)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — TEAM PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════

def team_wins(matches: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """Bar chart of top N teams by total wins."""
    wins = matches['winner'].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(wins.index[::-1], wins.values[::-1],
                   color=ACCENT_COLORS[:top_n][::-1], edgecolor='none')

    for bar, val in zip(bars, wins.values[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=10, fontweight='bold',
                color='#c9d1d9')

    ax.set_title(f'Top {top_n} Teams by Total Wins (IPL 2008–2023)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Number of Wins')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('team_wins.png')
    return wins


def win_by_margin(matches: pd.DataFrame):
    """Distribution of win margins (runs vs wickets)."""
    by_runs    = matches[matches['result'] == 'runs']['result_margin'].dropna()
    by_wickets = matches[matches['result'] == 'wickets']['result_margin'].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(by_runs, bins=25, color='#58a6ff', edgecolor='none', alpha=0.85)
    axes[0].set_title('Wins by Runs — Margin Distribution', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Margin (Runs)')
    axes[0].set_ylabel('Count')

    axes[1].hist(by_wickets, bins=10, color='#3fb950', edgecolor='none', alpha=0.85)
    axes[1].set_title('Wins by Wickets — Margin Distribution', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Margin (Wickets)')

    plt.suptitle('How Dominant Were the Victories?', fontsize=14,
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    _save('win_margins.png')


def season_wise_matches(matches: pd.DataFrame):
    """Matches played per IPL season."""
    counts = matches['season'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.bar(counts.index.astype(str), counts.values,
           color='#d2a8ff', edgecolor='none', width=0.6)
    ax.set_title('Matches Played Per IPL Season', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Season')
    ax.set_ylabel('Number of Matches')
    plt.xticks(rotation=45)
    for i, (x, v) in enumerate(zip(counts.index.astype(str), counts.values)):
        ax.text(i, v + 0.3, str(v), ha='center', fontsize=9, color='#c9d1d9')
    plt.tight_layout()
    _save('season_matches.png')


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — TOSS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def toss_impact(matches: pd.DataFrame) -> float:
    """How often does winning the toss lead to winning the match?"""
    toss_win_match = matches[matches['toss_winner'] == matches['winner']]
    pct = round(len(toss_win_match) / len(matches) * 100, 2)

    # Decision breakdown
    decisions = matches['toss_decision'].value_counts()
    decision_wins = (
        matches[matches['toss_winner'] == matches['winner']]
        ['toss_decision'].value_counts()
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Pie — toss win vs loss
    axes[0].pie(
        [len(toss_win_match), len(matches) - len(toss_win_match)],
        labels=['Toss winner\nalso won', 'Toss winner\nlost'],
        colors=['#3fb950', '#f78166'],
        autopct='%1.1f%%', startangle=90,
        textprops={'color': '#c9d1d9', 'fontsize': 11}
    )
    axes[0].set_title('Does Winning the Toss Help?', fontsize=12, fontweight='bold')

    # Bar — bat vs field decision
    decision_win_pct = (decision_wins / decisions * 100).fillna(0)
    axes[1].bar(decision_win_pct.index, decision_win_pct.values,
                color=['#58a6ff', '#ffa657'], edgecolor='none', width=0.4)
    axes[1].set_title('Win % by Toss Decision', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Win %')
    axes[1].set_ylim(0, 100)

    plt.suptitle('Toss Impact Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save('toss_analysis.png')

    print(f"\n  Toss winner also won the match: {pct}% of the time")
    return pct


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — BATTING ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def top_batsmen(deliveries: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """Top run scorers across all IPL seasons."""
    runs = (
        deliveries.groupby('batter')['batsman_runs']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(runs.index[::-1], runs.values[::-1],
                   color=ACCENT_COLORS[:top_n][::-1], edgecolor='none')
    for bar, val in zip(bars, runs.values[::-1]):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
                f'{val:,}', va='center', fontsize=10, color='#c9d1d9')

    ax.set_title(f'Top {top_n} Run Scorers — All IPL Seasons',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Total Runs')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('top_batsmen.png')
    return runs


def boundary_analysis(deliveries: pd.DataFrame, top_n: int = 10):
    """Who hits the most fours and sixes?"""
    fours  = deliveries[deliveries['batsman_runs'] == 4].groupby('batter').size()
    sixes  = deliveries[deliveries['batsman_runs'] == 6].groupby('batter').size()

    top_fours = fours.sort_values(ascending=False).head(top_n)
    top_sixes = sixes.sort_values(ascending=False).head(top_n)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    axes[0].barh(top_fours.index[::-1], top_fours.values[::-1],
                 color='#58a6ff', edgecolor='none')
    axes[0].set_title(f'Top {top_n} Four Hitters', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Number of Fours')

    axes[1].barh(top_sixes.index[::-1], top_sixes.values[::-1],
                 color='#ffa657', edgecolor='none')
    axes[1].set_title(f'Top {top_n} Six Hitters', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Number of Sixes')

    plt.suptitle('Boundary Kings of IPL', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save('boundary_kings.png')


def powerplay_scoring(deliveries: pd.DataFrame):
    """Average runs scored in powerplay (overs 1-6) vs death (17-20)."""
    pp    = deliveries[deliveries['over'].between(0, 5)]
    death = deliveries[deliveries['over'].between(16, 19)]

    pp_avg    = pp.groupby('match_id')['total_runs'].sum().mean()
    death_avg = death.groupby('match_id')['total_runs'].sum().mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    phases = ['Powerplay\n(Overs 1-6)', 'Middle Overs\n(7-16)', 'Death Overs\n(17-20)']
    mid    = deliveries[deliveries['over'].between(6, 15)]
    mid_avg = mid.groupby('match_id')['total_runs'].sum().mean()

    avgs   = [pp_avg, mid_avg, death_avg]
    colors = ['#58a6ff', '#3fb950', '#f78166']
    bars   = ax.bar(phases, avgs, color=colors, edgecolor='none', width=0.5)

    for bar, val in zip(bars, avgs):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', fontsize=11,
                fontweight='bold', color='#c9d1d9')

    ax.set_title('Avg Runs per Match Phase', fontsize=14, fontweight='bold', pad=12)
    ax.set_ylabel('Average Runs')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('phase_scoring.png')


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — BOWLING ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

NON_BOWLER_DISMISSALS = {'run out', 'retired hurt', 'obstructing the field'}

def top_bowlers(deliveries: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """Top wicket takers excluding run-outs."""
    wk = (
        deliveries[
            deliveries['dismissal_kind'].notna() &
            ~deliveries['dismissal_kind'].isin(NON_BOWLER_DISMISSALS)
        ]
        .groupby('bowler')['dismissal_kind']
        .count()
        .sort_values(ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(wk.index[::-1], wk.values[::-1],
            color='#f78166', edgecolor='none')
    for i, val in enumerate(wk.values[::-1]):
        ax.text(val + 0.5, i, str(val), va='center',
                fontsize=10, color='#c9d1d9')

    ax.set_title(f'Top {top_n} Wicket Takers — All IPL Seasons',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Total Wickets')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('top_bowlers.png')
    return wk


def economy_rate(deliveries: pd.DataFrame, min_overs: int = 30, top_n: int = 10):
    """Best economy rates (min N overs bowled)."""
    grp = deliveries.groupby('bowler').agg(
        total_runs=('total_runs', 'sum'),
        balls=('ball', 'count')
    )
    grp['overs']   = grp['balls'] / 6
    grp            = grp[grp['overs'] >= min_overs]
    grp['economy'] = (grp['total_runs'] / grp['overs']).round(2)
    best            = grp['economy'].sort_values().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(best.index[::-1], best.values[::-1],
            color='#56d364', edgecolor='none')
    for i, val in enumerate(best.values[::-1]):
        ax.text(val + 0.05, i, f'{val:.2f}', va='center',
                fontsize=10, color='#c9d1d9')

    ax.set_title(f'Best Economy Rates (min {min_overs} overs)',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Economy Rate')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('economy_rates.png')


def dismissal_types(deliveries: pd.DataFrame):
    """Pie chart of all dismissal kinds."""
    kinds = deliveries['dismissal_kind'].dropna().value_counts()

    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts, autotexts = ax.pie(
        kinds.values,
        labels=kinds.index,
        autopct='%1.1f%%',
        colors=sns.color_palette('viridis', len(kinds)),
        startangle=140,
        pctdistance=0.82,
        textprops={'color': '#c9d1d9', 'fontsize': 9}
    )
    ax.set_title('Dismissal Types — IPL 2008-2023',
                 fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    _save('dismissal_types.png')


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — VENUE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def venue_stats(matches: pd.DataFrame, top_n: int = 10):
    """Most used venues and their match counts."""
    venue_counts = matches['venue'].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(venue_counts.index[::-1], venue_counts.values[::-1],
            color='#79c0ff', edgecolor='none')
    for i, val in enumerate(venue_counts.values[::-1]):
        ax.text(val + 0.3, i, str(val), va='center',
                fontsize=10, color='#c9d1d9')

    ax.set_title(f'Top {top_n} Most Used Venues',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Matches Hosted')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('venue_stats.png')


def home_advantage(matches: pd.DataFrame):
    """
    Approximate home advantage — teams that play in their city venue.
    Simple heuristic: toss winner choosing to bat at home.
    """
    city_wins = matches.groupby('city').apply(
        lambda g: (g['toss_winner'] == g['winner']).mean()
    ).sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(city_wins.index, city_wins.values * 100,
           color='#d2a8ff', edgecolor='none', width=0.6)
    ax.axhline(50, color='#f78166', linestyle='--', linewidth=1.2,
               label='50% baseline')
    ax.set_title('Toss Win → Match Win % by City',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_ylabel('Win %')
    ax.set_ylim(0, 100)
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    _save('city_toss_win.png')


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — HEAD-TO-HEAD
# ══════════════════════════════════════════════════════════════════════════════

def head_to_head(matches: pd.DataFrame, team_a: str, team_b: str):
    """Win/loss breakdown between two specific teams."""
    h2h = matches[
        ((matches['team1'] == team_a) & (matches['team2'] == team_b)) |
        ((matches['team1'] == team_b) & (matches['team2'] == team_a))
    ]

    if h2h.empty:
        print(f"  No matches found between {team_a} and {team_b}")
        return

    a_wins = (h2h['winner'] == team_a).sum()
    b_wins = (h2h['winner'] == team_b).sum()
    no_res = len(h2h) - a_wins - b_wins

    fig, ax = plt.subplots(figsize=(7, 7))
    sizes  = [a_wins, b_wins, no_res] if no_res > 0 else [a_wins, b_wins]
    labels = [team_a, team_b, 'No Result'] if no_res > 0 else [team_a, team_b]
    colors = ['#58a6ff', '#f78166', '#8b949e']

    ax.pie(sizes, labels=labels, autopct='%1.1f%%',
           colors=colors[:len(sizes)], startangle=90,
           textprops={'color': '#c9d1d9', 'fontsize': 12})
    ax.set_title(f'Head-to-Head: {team_a} vs {team_b}\n({len(h2h)} matches)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    _save(f'h2h_{team_a[:3]}_{team_b[:3]}.png')

    print(f"\n  {team_a} vs {team_b} — {len(h2h)} matches")
    print(f"  {team_a} wins : {a_wins}")
    print(f"  {team_b} wins : {b_wins}")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — PLAYER OF THE MATCH
# ══════════════════════════════════════════════════════════════════════════════

def player_of_match_leaders(matches: pd.DataFrame, top_n: int = 10):
    """Who has won Player of the Match most often?"""
    potm = matches['player_of_match'].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(potm.index[::-1], potm.values[::-1],
                   color='#ffa657', edgecolor='none')
    for bar, val in zip(bars, potm.values[::-1]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=10, color='#c9d1d9')

    ax.set_title(f'Top {top_n} Player of the Match Awards',
                 fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Awards')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    _save('player_of_match.png')
    return potm


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════════════════════

def _save(filename: str):
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=plt.rcParams['figure.facecolor'])
    plt.show()
    print(f"    Saved → {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "=" * 55)
    print("   IPL DATA ANALYSIS PIPELINE (2008–2023)")
    print("=" * 55)

    matches, deliveries = load_data()
    data_summary(matches, deliveries)

    print("\n[1/12] Team wins...")
    team_wins(matches)

    print("[2/12] Win margins...")
    win_by_margin(matches)

    print("[3/12] Season-wise matches...")
    season_wise_matches(matches)

    print("[4/12] Toss impact...")
    toss_impact(matches)

    print("[5/12] Top batsmen...")
    top_batsmen(deliveries)

    print("[6/12] Boundary analysis...")
    boundary_analysis(deliveries)

    print("[7/12] Powerplay vs death scoring...")
    powerplay_scoring(deliveries)

    print("[8/12] Top bowlers...")
    top_bowlers(deliveries)

    print("[9/12] Economy rates...")
    economy_rate(deliveries)

    print("[10/12] Dismissal types...")
    dismissal_types(deliveries)

    print("[11/12] Venue stats...")
    venue_stats(matches)
    home_advantage(matches)

    print("[12/12] Player of the Match leaders...")
    player_of_match_leaders(matches)

    print("\n  Bonus — Head to Head: MI vs CSK")
    head_to_head(matches, 'Mumbai Indians', 'Chennai Super Kings')

    print("\n" + "=" * 55)
    print(f"  DONE! All charts saved in /{CHARTS_DIR}/")
    print("=" * 55)


if __name__ == '__main__':
    main()