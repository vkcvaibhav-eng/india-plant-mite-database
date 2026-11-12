"""Figures for Paper 2, drawn from the tables in data/analysis/ (run analyse.py first).

Writes 300 dpi PNG files to figures/. Colours: categorical slots 1-6 of the validated reference palette
in fixed order, one per mite group; the host-breadth classes use one blue ramp, light to dark.
"""
import csv, pathlib, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
A, F = ROOT / "data/analysis", ROOT / "figures"
F.mkdir(exist_ok=True)

GROUPS = ["Tetranychidae", "Tenuipalpidae", "Eriophyoidea", "Tarsonemidae", "Tuckerellidae", "Phytoseiidae"]
COLOR = dict(zip(GROUPS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]))
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})


def read(name):
    with open(A / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, linewidth=0.6); ax.set_axisbelow(True)


def italic_legend(ax, groups, **kw):
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOR[g]) for g in groups]
    leg = ax.legend(handles, groups, frameon=False, **kw)
    for t in leg.get_texts():
        t.set_color(INK)
    return leg


# ---------------------------------------------------------------- Fig. 1 species per state
rows = read("where_species_by_state.csv")[::-1]
fig, ax = plt.subplots(figsize=(6.3, 7.2))
left = [0] * len(rows)
for g in GROUPS:
    vals = [int(r[g]) for r in rows]
    ax.barh([r["state"] for r in rows], vals, left=left, height=0.68, color=COLOR[g], edgecolor="white", linewidth=0.6, label=g)
    left = [a + b for a, b in zip(left, vals)]
for i, r in enumerate(rows):
    ax.text(left[i] + 6, i, r["species"], va="center", fontsize=7.5, color=INK2)
ax.set_xlabel("Species recorded")
grid(ax); ax.tick_params(axis="y", length=0, labelsize=8)
italic_legend(ax, GROUPS, loc="lower right", fontsize=8)
ax.set_xlim(0, max(left) * 1.08)
fig.tight_layout(); fig.savefig(F / "fig1_species_by_state.png", dpi=300); plt.close(fig)

# ---------------------------------------------------------------- Fig. 2 descriptions per decade
rows = read("when_described_per_decade.csv")
early = {g: sum(int(r[g]) for r in rows if int(r["decade"][:4]) < 1900) for g in GROUPS}
keep = [r for r in rows if int(r["decade"][:4]) >= 1900]
labels = ["before 1900"] + [r["decade"] for r in keep]
fig, ax = plt.subplots(figsize=(6.3, 3.6))
bottom = [0] * len(labels)
for g in GROUPS:
    vals = [early[g]] + [int(r[g]) for r in keep]
    ax.bar(labels, vals, bottom=bottom, width=0.7, color=COLOR[g], edgecolor="white", linewidth=0.6, label=g)
    bottom = [a + b for a, b in zip(bottom, vals)]
for i, b in enumerate(bottom):
    ax.text(i, b + 4, str(b), ha="center", fontsize=7, color=INK2)
ax.set_ylabel("Species described"); grid(ax, "y")
ax.tick_params(axis="x", labelsize=7.5, length=0)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
italic_legend(ax, GROUPS, loc="upper left", fontsize=7.5, ncol=2)
fig.tight_layout(); fig.savefig(F / "fig2_described_per_decade.png", dpi=300); plt.close(fig)

# ---------------------------------------------------------------- Fig. 3 host breadth
rows = [r for r in read("hosts_breadth_by_group.csv") if r["group"] != "Phytoseiidae"]
classes = [("one_host_genus", "1 host genus"), ("2_5", "2–5"), ("6_20", "6–20"), ("over_20", "more than 20")]
fig, ax = plt.subplots(figsize=(6.3, 2.8))
names = [f"{r['group']} (n = {int(r['species']) - int(r['no_host_genus'])})" for r in rows][::-1]
left = [0.0] * len(rows)
for (col, lab), colr in zip(classes, RAMP):
    vals = []
    for r in rows[::-1]:
        n = int(r["species"]) - int(r["no_host_genus"])
        vals.append(100 * int(r[col]) / n if n else 0)
    ax.barh(names, vals, left=left, height=0.6, color=colr, edgecolor="white", linewidth=0.8, label=lab)
    for i, v in enumerate(vals):
        if v >= 9:
            ax.text(left[i] + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=7,
                    color=INK if colr == RAMP[0] else "white")
    left = [a + b for a, b in zip(left, vals)]
ax.set_xlim(0, 100); ax.set_xlabel("Share of species with a recorded host (%)")
ax.tick_params(axis="y", length=0); grid(ax)
leg = ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.45, 1.22), fontsize=8)
fig.tight_layout(); fig.savefig(F / "fig3_host_breadth.png", dpi=300); plt.close(fig)

# ---------------------------------------------------------------- Fig. 4 host genera with most phytophagous species
# genus level: the sources name many hosts only to genus ("Citrus sp."), so species-level ranks are not comparable
rows = read("hosts_top_genera.csv")[:20][::-1]
PHY = [g for g in GROUPS if g != "Phytoseiidae"]
fig, ax = plt.subplots(figsize=(6.3, 5.0))
lab = []
for r in rows:
    # one common name, that of the most-recorded species of the genus
    name = re.split(r" / | \(", r["common_names"].split("; ")[0])[0].strip().lower()
    lab.append(f"$\\it{{{r['host_genus']}}}$" + (f" ({name})" if name and name != r["host_genus"].lower() else ""))
left = [0] * len(rows)
for g in PHY:
    vals = [int(r[g]) for r in rows]
    ax.barh(lab, vals, left=left, height=0.66, color=COLOR[g], edgecolor="white", linewidth=0.6, label=g)
    left = [a + b for a, b in zip(left, vals)]
for i, v in enumerate(left):
    ax.text(v + 0.5, i, str(v), va="center", fontsize=7.5, color=INK2)
ax.set_xlabel("Phytophagous mite species recorded on the genus"); grid(ax)
ax.tick_params(axis="y", length=0, labelsize=7.5)
italic_legend(ax, [g for g in PHY if g != "Tuckerellidae"], loc="lower right", fontsize=8)
fig.tight_layout(); fig.savefig(F / "fig4_top_host_genera.png", dpi=300); plt.close(fig)

# ---------------------------------------------------------------- Fig. 5 barcoded share by states recorded
rows = read("link_barcoded_by_states.csv")
rows = [r for r in rows if r["states_recorded"] != "0"]
fig, ax = plt.subplots(figsize=(4.6, 3.0))
x = [r["states_recorded"].replace("-", "–") for r in rows]
y = [100 * float(r["share_barcoded"]) for r in rows]
ax.bar(x, y, width=0.6, color=COLOR["Tetranychidae"])
for i, r in enumerate(rows):
    ax.text(i, y[i] + 1.5, f"{r['barcoded']}/{r['species']}", ha="center", fontsize=8, color=INK2)
ax.set_xlabel("Indian states with a record"); ax.set_ylabel("Species with a COI barcode (%)")
ax.set_ylim(0, 80); grid(ax, "y"); ax.tick_params(axis="x", length=0)
fig.tight_layout(); fig.savefig(F / "fig5_barcoded_by_states.png", dpi=300); plt.close(fig)
print("figures written:", sorted(p.name for p in F.glob("*.png")))
