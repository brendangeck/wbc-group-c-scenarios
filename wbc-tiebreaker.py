import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="WBC Pool C Tiebreaker", layout="wide")
st.title("WBC 2026 Pool C — Who advances?")

st.markdown("If Korea beats Australia, all three finish 2-2. The tiebreaker is **fewest runs allowed per defensive out** in head-to-head games.")

# ── Fixed data from completed games ─────────────────────────────────────
# Game 1: AUS 3, TPE 0 — AUS home, 9 innings
#   AUS allowed 0, recorded 27 def outs | TPE allowed 3, recorded 24 def outs
# Game 2: TPE 5, KOR 4 — KOR home, 10 innings
#   KOR allowed 5, recorded 30 def outs | TPE allowed 4, recorded 30 def outs

GAME1 = {"AUS_ra": 0, "AUS_do": 27, "TPE_ra": 3, "TPE_do": 24}
GAME2 = {"KOR_ra": 5, "KOR_do": 30, "TPE_ra": 4, "TPE_do": 30}

# ── Mercy rule selector ────────────────────────────────────────────────
# KOR is road, AUS is home. Korea wins.
# Mercy: 15+ after 5 inn, 10+ after 7 inn. Game can also go full 9.
# If mercy after N innings (road team winning):
#   Road team (KOR) batted N full innings → AUS records N*3 def outs
#   Home team (AUS) batted N full innings (they bat bottom of Nth, still losing) → KOR records N*3 def outs
# If full 9 innings (road team winning):
#   KOR batted 9 innings → AUS records 27 def outs
#   AUS batted 9 innings (home team loses, bats bottom 9) → KOR records 27 def outs

GAME_END_OPTIONS = {
    "Full 9 innings":                       (9, 1),   # (innings, min margin to win)
    "Mercy after 5 innings (15+ run lead)": (5, 15),
    "Mercy after 6 innings (15+ run lead)": (6, 15),
    "Mercy after 7 innings (10+ run lead)": (7, 10),
    "Mercy after 8 innings (10+ run lead)": (8, 10),
}

game_end = st.selectbox("How does the Korea–Australia game end?", list(GAME_END_OPTIONS.keys()))
innings, min_margin = GAME_END_OPTIONS[game_end]

# Both teams bat the full mercy inning (road team is winning, home team bats bottom but fails)
game3_do = innings * 3


def compute_tiebreaker(kor_runs: int, aus_runs: int):
    """Compute RA/DO ratio for each team; return the team with the lowest (= advances)."""
    kor_total_ra = GAME2["KOR_ra"] + aus_runs       # 5 + Y
    kor_total_do = GAME2["KOR_do"] + game3_do        # 30 + game3_do

    aus_total_ra = GAME1["AUS_ra"] + kor_runs        # 0 + X
    aus_total_do = GAME1["AUS_do"] + game3_do         # 27 + game3_do

    tpe_total_ra = GAME1["TPE_ra"] + GAME2["TPE_ra"]  # 3 + 4 = 7 (fixed)
    tpe_total_do = GAME1["TPE_do"] + GAME2["TPE_do"]  # 24 + 30 = 54 (fixed)

    kor_ratio = kor_total_ra / kor_total_do
    aus_ratio = aus_total_ra / aus_total_do
    tpe_ratio = tpe_total_ra / tpe_total_do

    results = {"🇰🇷 KOR": kor_ratio, "🇦🇺 AUS": aus_ratio, "🇹🇼 TPE": tpe_ratio}
    sorted_teams = sorted(results.items(), key=lambda x: x[1])
    return sorted_teams[0][0], results


# ── Build the simulation data ────────────────────────────────────────────
max_runs = 20

records = []
for kor_r in range(1, max_runs + 1):
    for aus_r in range(0, max_runs):
        margin = kor_r - aus_r
        if margin < min_margin:
            if kor_r <= aus_r:
                label = "Australia"
            else:
                label = "N/A"
        else:
            winner, _ = compute_tiebreaker(kor_r, aus_r)
            if "KOR" in winner:
                label = "Korea"
            elif "AUS" in winner:
                label = "Australia"
            else:
                label = "Chinese Taipei"
        records.append({"Korea runs": kor_r, "Australia runs": aus_r, "Advances": label})

chart_df = pd.DataFrame(records)

color_scale = alt.Scale(
    domain=["Korea", "Australia", "Chinese Taipei", "N/A"],
    range=["#1a3a5c", "#1b5e20", "#b71c1c", "#222222"],
)

chart = (
    alt.Chart(chart_df)
    .mark_rect()
    .encode(
        x=alt.X("Australia runs:O", title="🇦🇺 Australia runs", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Korea runs:O", title="🇰🇷 Korea runs", sort="descending"),
        color=alt.Color("Advances:N", scale=color_scale, legend=alt.Legend(title="Who advances")),
        tooltip=["Korea runs", "Australia runs", "Advances"],
    )
    .properties(width=700, height=600)
)

text = (
    alt.Chart(chart_df[chart_df["Advances"] != "N/A"])
    .mark_text(fontSize=9, color="white")
    .encode(
        x=alt.X("Australia runs:O"),
        y=alt.Y("Korea runs:O", sort="descending"),
        text=alt.Text("Advances:N"),
    )
)

st.subheader("Who gets the #2 seed?")
st.markdown("Gray cells = impossible margin for this game length.")
st.altair_chart(chart + text, use_container_width=True)

# ── Explanation panel ───────────────────────────────────────────────────
with st.expander("Show the math"):
    tpe_ratio = 7 / 54
    st.markdown(f"""
    Game 3 ends after **{innings} innings** → **{game3_do} outs** per team.

    | Team | Runs allowed | Def outs | Ratio |
    |------|-------------|----------|-------|
    | 🇹🇼 TPE | 3 + 4 = 7 (fixed) | 24 + 30 = 54 (fixed) | {tpe_ratio:.4f} |
    | 🇰🇷 KOR | 5 + Y | 30 + {game3_do} = {30 + game3_do} | (5+Y)/{30 + game3_do} |
    | 🇦🇺 AUS | 0 + X | 27 + {game3_do} = {27 + game3_do} | X/{27 + game3_do} |

    Lowest ratio advances.
    """)

st.caption("Source: 2026 WBC official tiebreaker rules. Mercy rule: 15+ after 5 inn, 10+ after 7 inn.")
