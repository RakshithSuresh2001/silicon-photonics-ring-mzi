# Step 4: GDS layout of both devices with gdsfactory's generic PDK (strip waveguide on layer WG = 1/0).
import gdsfactory as gf
gf.gpdk.PDK.activate()
ring = gf.components.ring_single(gap=0.325, radius=10, length_x=4, cross_section="strip")
mzi = gf.components.mzi(delta_length=100, cross_section="strip")
top = gf.Component("rem_photonics_top")
r = top << ring; z = top << mzi
z.dmovey(-60)
top.add_ports(r.ports, prefix="ring_"); top.add_ports(z.ports, prefix="mzi_")
top.write_gds("rem_photonics.gds")
ring.write_gds("ring.gds"); mzi.write_gds("mzi.gds")
print("layers:", sorted({str(l) for l in top.layers}))
print("bbox um:", top.dbbox())
