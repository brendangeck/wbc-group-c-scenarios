"""Debug script to verify tiebreaker calculations."""

# Known results between the three tied teams (if KOR beats AUS):
# Game 1: TPE 0 – AUS 3  (9 inn, AUS home, AUS won)
# Game 2: TPE 5 – KOR 4  (10 inn, KOR home, TPE won)
# Game 3: KOR X – AUS Y  (9 inn, AUS home, KOR wins so X > Y)

# Defensive outs recorded BY each team's defense:
# Game 1 (AUS home, won 3-0, 9 innings):
#   AUS defense: TPE batted 9 full innings = 27 outs recorded by AUS
#   TPE defense: AUS batted 8 innings (home team won, didn't bat bot 9) = 24 outs recorded by TPE
#   AUS allowed 0 runs, TPE allowed 3 runs

# Game 2 (KOR home, lost 4-5, 10 innings):
#   KOR defense: TPE batted 10 innings. TPE scored in top 10, then KOR failed in bot 10.
#     TPE batted full 10 innings = 30 outs recorded by KOR
#   TPE defense: KOR batted 10 innings (home team batted bot 10 but failed) = 30 outs recorded by TPE
#   KOR allowed 5 runs, TPE allowed 4 runs

# Game 3 (AUS home, KOR wins X-Y, 9 innings):
#   KOR defense: AUS batted 9 full innings (home team lost) = 27 outs recorded by KOR
#   AUS defense: KOR batted 9 full innings = 27 outs recorded by AUS
#   KOR allowed Y runs, AUS allowed X runs

# TPE ratio is FIXED (played games 1 and 2 only):
#   TPE total RA = 3 (vs AUS) + 4 (vs KOR) = 7
#   TPE total DO = 24 (vs AUS) + 30 (vs KOR) = 54
#   TPE ratio = 7/54 = 0.12963...

tpe_ra = 3 + 4
tpe_do = 24 + 30
tpe_ratio = tpe_ra / tpe_do
print(f"TPE fixed: RA={tpe_ra}, DO={tpe_do}, ratio={tpe_ratio:.5f}")

print()
print("Testing specific scenarios:")
print("=" * 70)

test_cases = [
    (1, 0, "Korea wins 1-0"),
    (3, 2, "Korea wins 3-2"),
    (5, 0, "Korea wins 5-0"),
    (5, 4, "Korea wins 5-4"),
    (7, 3, "Korea wins 7-3"),
    (8, 7, "Korea wins 8-7"),
    (10, 2, "Korea wins 10-2"),
]

for kor_runs, aus_runs, label in test_cases:
    # Korea: games vs TPE (game 2) + vs AUS (game 3)
    kor_ra = 5 + aus_runs          # allowed 5 vs TPE + Y vs AUS
    kor_do = 30 + 27               # 30 (game 2) + 27 (game 3) = 57
    kor_ratio = kor_ra / kor_do

    # Australia: games vs TPE (game 1) + vs KOR (game 3)
    aus_ra = 0 + kor_runs          # allowed 0 vs TPE + X vs KOR
    aus_do = 27 + 27               # 27 (game 1) + 27 (game 3) = 54
    aus_ratio = aus_ra / aus_do

    results = {"KOR": kor_ratio, "AUS": aus_ratio, "TPE": tpe_ratio}
    ranked = sorted(results.items(), key=lambda x: x[1])

    print(f"\n{label}:")
    print(f"  KOR: RA={kor_ra}, DO={kor_do}, ratio={kor_ratio:.5f}")
    print(f"  AUS: RA={aus_ra}, DO={aus_do}, ratio={aus_ratio:.5f}")
    print(f"  TPE: RA={tpe_ra}, DO={tpe_do}, ratio={tpe_ratio:.5f}")
    print(f"  Ranking: {ranked[0][0]} ({ranked[0][1]:.5f}) > {ranked[1][0]} ({ranked[1][1]:.5f}) > {ranked[2][0]} ({ranked[2][1]:.5f})")
    print(f"  #2 seed advances: {ranked[0][0]}")

print()
print("=" * 70)
print("Boundary analysis:")
print(f"  TPE ratio = {tpe_ratio:.5f}")
print(f"  AUS advances when AUS ratio < TPE ratio AND AUS ratio < KOR ratio")
print(f"    AUS ratio = kor_runs / 54 < {tpe_ratio:.5f}")
print(f"    kor_runs < {tpe_ratio * 54:.2f} => kor_runs <= {int(tpe_ratio * 54)}")
print(f"  KOR advances when KOR ratio < TPE ratio AND KOR ratio < AUS ratio")
print(f"    KOR ratio = (5 + aus_runs) / 57 < {tpe_ratio:.5f}")
print(f"    5 + aus_runs < {tpe_ratio * 57:.2f} => aus_runs < {tpe_ratio * 57 - 5:.2f} => aus_runs <= {int(tpe_ratio * 57 - 5)}")
