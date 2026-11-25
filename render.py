# Layout images with KLayout
import klayout.lay as lay
for name, h in [("rem_photonics", 1100), ("ring", 900)]:
    v = lay.LayoutView(); v.load_layout(f"{name}.gds", True)
    v.set_config("background-color", "#ffffff"); v.set_config("grid-visible", "false")
    v.max_hier(); v.zoom_fit()
    it = v.begin_layers()
    while not it.at_end():
        p = it.current().dup(); p.fill_color = 0x2b5a8a; p.frame_color = 0x163a5e; p.dither_pattern = 0
        v.set_layer_properties(it, p); it.next()
    v.save_image(f"{name}_layout.png", 1400, h)
