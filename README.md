# ofc_fl_sim

An **Open Face Chinese (OFC) Poker Fantasyland solver**.

Given a Fantasyland hand of 13–16 cards, `ofc_fl_sim` finds the arrangement into
three rows that maximizes royalty points without fouling. It can also run Monte
Carlo simulations over many random deals to report expected scores, the
Fantasyland-retention rate, and the full score distribution.

## What problem it solves

In OFC, a player who reaches **Fantasyland** is dealt all of their cards at once
and must set them into three rows:

- **Top** — 3 cards
- **Middle** — 5 cards
- **Bottom** — 5 cards

The setting is legal only if it does **not foul**, i.e. hand strength must be
non-decreasing from top to bottom: `bottom ≥ middle ≥ top`. The solver searches
every valid arrangement and picks the best one, prioritizing (in order):

1. **Total royalty points**
2. **Staying in Fantasyland** (trips on top, or quads-or-better on bottom)
3. **Combined absolute hand strength** across all rows (expected rows won at
   showdown)
4. Per-row strength, as a final deterministic tie-break

## Requirements

- Python 3 (standard library only — no dependencies to install)

## Usage

The script is executable:

```sh
./ofc_fl_sim --hand "Ac2c5c9cAd3d4dTdQd5s8sTsKs"
```

Or invoke it with Python directly:

```sh
python3 ofc_fl_sim --hand "Ac2c5c9cAd3d4dTdQd5s8sTsKs"
```

### Card notation

Each card is two characters: a **rank** followed by a **suit**, concatenated
with no separators. Input is case-insensitive and tolerates stray whitespace.

- Ranks: `2 3 4 5 6 7 8 9 T J Q K A`
- Suits: `c` (clubs), `d` (diamonds), `h` (hearts), `s` (spades)

A hand must contain **13 to 16** unique cards.

### Solve a single hand

```sh
$ ./ofc_fl_sim --hand "Ac2c5c9cAd3d4dTdQd5s8sTsKs"

  Top   :  2c 8s Ts         High Card           0 pts
  Middle:  Ac 5c 9c 5s Ks   Pair                0 pts
  Bottom:  Ad 3d 4d Td Qd   Flush              +4 pts
  ----------------------------------------------
  Total                                         +4 pts

  Stays in Fantasyland: no
```

If more than 13 cards are given, the extra cards are set aside and shown as
`Discarded:`.

### Run simulations

Deal and solve `N` random hands, then report aggregate statistics:

```sh
$ ./ofc_fl_sim --sims 200 --seed 42

  Simulated 200 random 13-card Fantasyland hands

  Average score:          9.16 points
  Std deviation:          4.51
  Min / Median / Max:   0 / 9 / 23
  25th / 75th / 90th:   6 / 12 / 15
  Stays in Fantasyland: 10/200 (5.0%)

  Average royalties by row:
    Top:     3.11
    Middle:  1.88
    Bottom:  4.17

  Score distribution:
      0-4    ###############                             31 (15.5%)
      5-9    ########################################    85 (42.5%)
     10-14   ############################                60 (30.0%)
     15-19   ##########                                  21 (10.5%)
     20-24   #                                            3 ( 1.5%)
```

A live progress indicator with an ETA is shown on `stderr` for larger runs.

## Command-line options

| Option | Description |
| --- | --- |
| `--hand STRING` | Solve a single hand given as a 2-char-per-card string. |
| `--sims N` | Deal and solve `N` random hands and report statistics instead of solving one hand. |
| `--cards K` | Cards per dealt hand in simulation mode (13–16, default 13). |
| `--seed S` | Random seed for reproducible simulations. |

`--hand` and `--sims` are mutually exclusive; exactly one is required.

## Scoring reference

Royalties follow standard OFC scoring.

**Top (3 cards)**

| Hand | Points |
| --- | --- |
| Pair 66 … AA | 1 … 9 |
| Trips 222 … AAA | 10 … 22 |

**Middle (5 cards)**

| Hand | Points |
| --- | --- |
| Three of a Kind | 2 |
| Straight | 4 |
| Flush | 8 |
| Full House | 12 |
| Four of a Kind | 20 |
| Straight Flush | 30 |
| Royal Flush | 50 |

**Bottom (5 cards)**

| Hand | Points |
| --- | --- |
| Straight | 2 |
| Flush | 4 |
| Full House | 6 |
| Four of a Kind | 10 |
| Straight Flush | 15 |
| Royal Flush | 25 |

**Staying in Fantasyland:** trips on top, or four-of-a-kind-or-better on bottom.
