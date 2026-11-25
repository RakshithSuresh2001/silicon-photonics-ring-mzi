# Step 5: KLayout DRC on the waveguide layer (1/0). Small rule deck modeled on typical
# silicon-photonics foundry minimums. A seeded-bad layout (gap 150 nm) proves the deck catches errors.
import sys, klayout.db as db
RULES = {"WG.W.1 min width (um)": 0.40, "WG.S.1 min space (um)": 0.20}
def run(gds):
    ly = db.Layout(); ly.read(gds)
    top = ly.top_cell(); li = ly.layer(1, 0)
    reg = db.Region(top.begin_shapes_rec(li)).merged()
    dbu = ly.dbu
    w = reg.width_check(int(RULES["WG.W.1 min width (um)"]/dbu))
    s = reg.space_check(int(RULES["WG.S.1 min space (um)"]/dbu))
    return {"WG.W.1": w.count(), "WG.S.1": s.count()}, w, s
if __name__ == "__main__":
    for g in sys.argv[1:]:
        res, w, s = run(g)
        print(f"{g:28s} width violations {res['WG.W.1']:3d}   space violations {res['WG.S.1']:3d}")
        for e in list(w.each())[:3]: print("   width:", e)
        for e in list(s.each())[:3]: print("   space:", e)
