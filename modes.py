# Step 1: TE0 mode of a 500 x 220 nm silicon strip waveguide in oxide (femwell FEM mode solver).
# Material dispersion: Si (Li 1980 fit) and SiO2 (Malitson 1965) Sellmeier models.
import numpy as np, json
from collections import OrderedDict
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.mesh import mesh_from_OrderedDict
from femwell.maxwell.waveguide import compute_modes

def n_si(wl):    # wl in um, Sellmeier (Li 1980, 293 K)
    l2 = wl**2
    return np.sqrt(11.6858 + 0.939816/l2 + 0.00810461*l2/(l2 - 1.1071**2))
def n_sio2(wl):  # Malitson 1965
    l2 = wl**2
    return np.sqrt(1 + 0.6961663*l2/(l2-0.0684043**2) + 0.4079426*l2/(l2-0.1162414**2) + 0.8974794*l2/(l2-9.896161**2))

def neff(wl, w=0.5, h=0.22, gap=None):
    if gap is None:
        cores = OrderedDict(core=box(-w/2, 0, w/2, h))
    else:   # two coupled waveguides for the directional coupler
        cores = OrderedDict(core=box(-gap/2-w, 0, -gap/2, h).union(box(gap/2, 0, gap/2+w, h)))
    polys = OrderedDict(**cores, box=box(-3, -2, 3, 0), clad=box(-3, 0, 3, 2))
    mesh = from_meshio(mesh_from_OrderedDict(polys, {"core": {"resolution": 0.02, "distance": 0.6}},
                                             default_resolution_max=0.25))
    b0 = Basis(mesh, ElementTriP0()); eps = b0.zeros()
    for sub, n in {"core": n_si(wl), "box": n_sio2(wl), "clad": n_sio2(wl)}.items():
        eps[b0.get_dofs(elements=sub)] = n**2
    modes = compute_modes(b0, eps, wavelength=wl, num_modes=4, order=1)
    te = [m for m in modes if m.te_fraction > 0.5]
    return [float(np.real(m.n_eff)) for m in te]

if __name__ == "__main__":
    wls = np.linspace(1.50, 1.60, 6)
    ne = np.array([neff(w)[0] for w in wls])
    p = np.polyfit(wls, ne, 2)
    wl0 = 1.55; n0 = np.polyval(p, wl0); dn = np.polyval(np.polyder(p), wl0)
    ng = n0 - wl0*dn
    # coupled pair, gap 200 nm: even/odd TE supermodes
    sup = neff(1.55, gap=0.2)[:2]
    out = dict(wavelengths_um=wls.tolist(), neff=ne.tolist(), neff_fit=p.tolist(),
               neff_1550=n0, ng_1550=ng, supermodes_gap200_1550=sup)
    json.dump(out, open("modes.json", "w"), indent=1)
    print(f"n_eff(1550) = {n0:.4f}   n_g(1550) = {ng:.4f}")
    print(f"gap 200 nm supermodes: even {sup[0]:.4f}  odd {sup[1]:.4f}  dn = {sup[0]-sup[1]:.4f}")
