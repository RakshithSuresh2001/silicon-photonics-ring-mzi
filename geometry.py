# Ring path length taken from the gdsfactory layout itself, so simulation and GDS agree.
import gdsfactory as gf
gf.gpdk.PDK.activate()
R, LX, LY = 10.0, 4.0, 0.6
def ring_length(radius=R, length_x=LX, length_y=LY):
    bend = gf.components.bend_euler(radius=radius, cross_section="strip").info["length"]
    return 4*bend + 2*length_x + 2*length_y
