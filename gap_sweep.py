# Step 3: design for critical coupling. Sweep the bus-ring gap, solve coupled supermodes,
# and find the gap where the field coupling r equals the round-trip loss a (deepest dip).
import json, numpy as np
from modes import neff
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from geometry import ring_length, LX as Lc
LOSS = 2.0
L = ring_length(); a = np.exp(-LOSS/4.343*1e-4*L/2)
rows = []
for g in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
    e, o = neff(1.55, gap=g)[:2]
    k = np.sin(np.pi*abs(e-o)*Lc/1.55); r = np.sqrt(1-k**2)
    tmin = (a-r)**2/(1-a*r)**2                    # through-port minimum at resonance
    rows.append(dict(gap_um=g, dn=abs(e-o), kappa2=k**2, r=r, extinction_dB=-10*np.log10(max(tmin,1e-12))))
    print(f"gap {g*1e3:3.0f} nm  dn {abs(e-o):.5f}  kappa^2 {k**2:.5f}  extinction {rows[-1]['extinction_dB']:5.1f} dB")
print(f"critical coupling needs kappa^2 = 1 - a^2 = {1-a**2:.5f}")
json.dump(dict(a=a, critical_kappa2=1-a**2, sweep=rows), open("gap_sweep.json","w"), indent=1)
plt.rcParams.update({"font.family": "serif", "font.size": 10})
g = [x["gap_um"]*1e3 for x in rows]
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.semilogy(g, [x["kappa2"] for x in rows], "ko-", label="power coupling, kappa^2")
ax.axhline(1-a**2, color="gray", ls="--", label="critical coupling (= round-trip loss)")
ax.set_xlabel("bus to ring gap (nm)"); ax.set_ylabel("kappa^2"); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)
ax2 = ax.twinx(); ax2.plot(g, [x["extinction_dB"] for x in rows], "s:", color="0.4"); ax2.set_ylabel("extinction (dB), squares")
fig.tight_layout(); fig.savefig("gap_sweep.png", dpi=200)
