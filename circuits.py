# Step 2: ring resonator and MZI spectra from the solved n_eff(lambda), checked against theory.
import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
m = json.load(open("modes.json"))
p = np.array(m["neff_fit"]); ng = m["ng_1550"]
neff = lambda wl: np.polyval(p, wl)
wl = np.linspace(1.50, 1.60, 400001)            # um
LOSS_DB_CM = 2.0                                  # assumed propagation loss
alpha = LOSS_DB_CM / 4.343 * 1e-4                 # power attenuation per um

# ---- racetrack ring, all-pass: R = 10 um, straight coupler Lc = 4 um, gap 325 nm (near critical coupling) ----
from geometry import ring_length, R, LX as Lc
L = ring_length()   # from the GDS: 4 Euler bends + straights
dn = m["supermodes_gap325_1550"][0] - m["supermodes_gap325_1550"][1]
kappa = np.sin(np.pi*abs(dn)*Lc/1.55)                  # field coupling of the straight section only
r = np.sqrt(1 - kappa**2); a = np.exp(-alpha*L/2)
phi = 2*np.pi*neff(wl)*L/wl
T_ring = (a**2 - 2*r*a*np.cos(phi) + r**2) / (1 - 2*a*r*np.cos(phi) + (r*a)**2)

def dips(T):
    i = np.where((T[1:-1] < T[:-2]) & (T[1:-1] < T[2:]))[0] + 1
    return wl[i], T[i]
rw, rT = dips(T_ring)
k = np.argmin(abs(rw - 1.55)); fsr_ring_sim = (rw[k+1] - rw[k-1])/2*1e3
ng_at = lambda w: np.polyval(p, w) - w*np.polyval(np.polyder(p), w)   # group index at wavelength w
# loaded Q from the FWHM of the dip nearest 1550 nm
lam0 = rw[k]; fsr_ring_th = lam0**2/(ng_at(lam0)*L)*1e3
win = (wl > lam0-0.5e-3*fsr_ring_sim) & (wl < lam0+0.5e-3*fsr_ring_sim)
half = (1 + rT[k])/2; below = wl[win][T_ring[win] < half]
fwhm = (below.max() - below.min())*1e3; Q = lam0*1e3/fwhm
er_db = -10*np.log10(rT[k])

# ---- MZI: ideal 50/50 splitters, delta L = 100 um ----
dL = 100.0
T_mzi = np.cos(np.pi*neff(wl)*dL/wl)**2 * np.exp(-alpha*dL/2)
mw, _ = dips(T_mzi)
j = np.argmin(abs(mw - 1.55)); fsr_mzi_sim = (mw[j+1] - mw[j-1])/2*1e3
fsr_mzi_th = mw[j]**2/(ng_at(mw[j])*dL)*1e3

res = dict(neff_1550=m["neff_1550"], ng_1550=ng, ring=dict(R_um=R, Lc_um=Lc, L_um=L, kappa_power=kappa**2,
      resonance_nm=lam0*1e3, fsr_sim_nm=fsr_ring_sim, fsr_theory_nm=fsr_ring_th, fwhm_pm=fwhm*1e3,
      Q_loaded=Q, extinction_dB=er_db), mzi=dict(dL_um=dL, fsr_sim_nm=fsr_mzi_sim, fsr_theory_nm=fsr_mzi_th),
      loss_dB_cm=LOSS_DB_CM)
json.dump(res, open("results.json", "w"), indent=1)
print(f"ring: L={L:.2f} um  kappa^2={kappa**2:.4f}  resonance {lam0*1e3:.3f} nm")
print(f"ring FSR sim {fsr_ring_sim:.4f} nm  theory {fsr_ring_th:.4f} nm  diff {100*(fsr_ring_sim/fsr_ring_th-1):+.2f}%")
print(f"ring FWHM {fwhm*1e3:.1f} pm  loaded Q {Q:,.0f}  extinction {er_db:.1f} dB")
print(f"MZI  FSR sim {fsr_mzi_sim:.4f} nm  theory {fsr_mzi_th:.4f} nm  diff {100*(fsr_mzi_sim/fsr_mzi_th-1):+.2f}%")

plt.rcParams.update({"font.family": "serif", "font.size": 10})
fig, ax = plt.subplots(2, 1, figsize=(7, 5.2), sharex=True)
ax[0].plot(wl*1e3, 10*np.log10(T_ring), "k", lw=0.8); ax[0].set_ylabel("Through port (dB)")
ax[0].set_title(f"Racetrack ring, R = 10 um, gap 325 nm: FSR {fsr_ring_sim:.2f} nm, loaded Q about {round(Q,-3):,.0f}")
ax[1].plot(wl*1e3, 10*np.log10(np.maximum(T_mzi, 1e-6)), "k", lw=0.8); ax[1].set_ylabel("Output (dB)")
ax[1].set_title(f"MZI, delta L = 100 um: FSR {fsr_mzi_sim:.2f} nm"); ax[1].set_ylim(-40, 1)
ax[1].set_xlabel("Wavelength (nm)"); ax[0].set_xlim(1530, 1570)
for a_ in ax: a_.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("spectra.png", dpi=200)
