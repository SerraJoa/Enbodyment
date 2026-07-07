# engine — branca visual (Godot)

Escena Godot 4 que construeix el maniquí a partir de `manikin/humanoid.urdf` i
exporta els render passes (color, depth, normal, motion) que la branca de
difusió fa servir com a conditioning (ControlNet) i com a warp.

## Estat: verificat vs pendent

Provat amb Godot **4.7** (2026-07-06): el maniquí es construeix correctament
(19 bones) i l'exportació de color/depth/normal funciona.

- [x] `tools/urdf_to_scene_data.py` — **provat**: llegeix `humanoid.urdf` +
  `metadata.yaml` i escriu `data/manikin_skeleton.json` (19 links, 18 joints,
  geometria i eixos convertits a coordenades Godot). Es pot re-executar sempre
  que l'URDF canviï.
- [x] `scripts/manikin_builder.gd` — **provat**: construeix l'Skeleton3D +
  meshes primitius a runtime llegint el JSON. L'esquelet surt dret i amb
  proporcions correctes.
- [x] `scripts/gbuffer_export.gd` (color/depth/normal) + `shaders/*.gdshader`
  — **provat**: prement `P` durant l'execució, captura color/depth/normal a
  `user://gbuffer_test/` substituint `material_override` i llegint
  `viewport.get_texture()`.
- [ ] **Motion vectors: implementats, pendents de provar.** `shaders/motion_capture.gdshader`
  compara el clip-space actual amb el del frame anterior (via l'instance
  uniform `prev_model_matrix`, que `gbuffer_export.gd` fixa a partir del
  `global_transform` guardat a la crida anterior) i el codifica com a color
  (bias+scale, com un normal map). `main.gd` gira l'esquelet 5° entre
  captures perquè hi hagi moviment real per provar-ho. **No s'ha pogut
  verificar sense Godot obert** — pendent que ho provis tu (vegeu més avall).
  Simplificació coneguda: assumeix que la càmera no es mou entre les dues
  captures comparades.

## Requisits

- Godot **4.7** (verificat). Hauria de funcionar amb qualsevol 4.3+.
- Renderer **Forward+** (per defecte a Godot 4, ja configurat a `project.godot`).

## Flux de treball

1. Si canvia `manikin/humanoid.urdf` o `metadata.yaml`:
   ```
   python tools/urdf_to_scene_data.py
   ```
2. Obre `project.godot` amb Godot i executa `scenes/main.tscn`.
3. Comprova visualment que l'esquelet surt dret i amb les proporcions
   correctes (peu de dos segments, braços amb massa visible).
4. Prem `P` — captura el frame 0 (motion hauria de sortir gris pla, sense
   moviment previ). Prem `P` una altra vegada — gira l'esquelet 5° i captura
   el frame 1; ara `motion_0001.png` hauria de mostrar color no-neutre (no
   gris pla) allà on el cos s'ha desplaçat a la imatge. Revisa les imatges a
   `user://gbuffer_test/` (Godot mostra la ruta absoluta a la consola).

## Següent pas

Validar visualment `motion_0001.png` (pas 4 de dalt). Si surt tot gris pla
malgrat el gir, el més probable és que `set_instance_shader_parameter` no
estigui rebent la `Projection` correctament — revisar-ho junts. Un cop
validat, connectar `diffusion/src/embodiment_visual/warp.py` amb frames
reals enlloc de dades sintètiques de test.
