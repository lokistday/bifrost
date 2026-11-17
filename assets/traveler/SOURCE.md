## Active light-form entrance

`raven.png` is reused unchanged from the existing Yggdrasil raven. The renderer
reuses its feather deformation, spectral material, glints and short afterimages,
with a fixed forward pitch so its head points away from the viewer into the nebula.
The entrance still owns the single animation clock and reduced-motion handling.

## Retained human experiments

`glass-back-v3.png` was edited with the built-in image generation
tool from `lightform-v2.png`. It faces directly away from the viewer. The edit
prompt is in `GLASS-PROMPT.txt`; the earlier source prompt is in
`LIGHTFORM-PROMPT.txt`. The renderer uses contrasting glass slivers, edge-weighted
particles, the raven's pink/purple/cyan spectrum, and synchronized 2.5D shoulder,
elbow, hip and knee movements. Figure scale is 74% of the preceding version.
It does not load the retained anatomical mesh or any remote rendering libraries.

## Retained anatomical mesh assets

The anatomical base mesh, joint locations and skinning weights are MakeHuman
core graphical assets, released under **CC0 1.0 Universal**.

- [Base mesh](https://github.com/makehumancommunity/makehuman/blob/master/makehuman/data/3dobjs/base.obj)
- [Rig and vertex weights](https://github.com/makehumancommunity/makehuman/tree/master/makehuman/data/rigs)
- [Graphical asset license](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md#c-the-license-for-the-bundled-assets)

The floating pose, material, light ribbons, shaders and renderer are BIFROST's
implementation. No MakeHuman application source code is included.

`scripts/build_traveler_mesh.py` converts the source OBJ and rig data to the
compact, local `js/traveler-mesh.js` asset. Browser playback needs no network
requests or external rendering libraries.
