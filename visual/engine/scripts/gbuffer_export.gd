extends Node
class_name GBufferExport
## Exporta els render passes (color, depth, normal, motion) que la branca de
## difusió necessita com a conditioning + warp. Substitueix temporalment el
## material de cada MeshInstance3D del maniquí per un shader de captura,
## renderitza un frame, i desa la imatge — després restaura el material
## original.
##
## Motion vectors: compara el `global_transform` de cada mesh en aquest frame
## amb el que tenia al frame anterior (guardat a `_previous_transforms`,
## static perquè persisteix entre crides). Simplificació: assumeix càmera
## estàtica entre captures (veure shaders/motion_capture.gdshader). Sense
## previous (primer frame), la motion surt zero.

const DEPTH_SHADER := preload("res://shaders/depth_capture.gdshader")
const NORMAL_SHADER := preload("res://shaders/normal_capture.gdshader")
const MOTION_SHADER := preload("res://shaders/motion_capture.gdshader")

# Ha de coincidir EXACTAMENT amb MOTION_SCALE al shader i amb MOTION_SCALE a
# diffusion/src/embodiment_visual/gbuffer.py (decode).
const MOTION_SCALE := 0.25

static var _previous_transforms: Dictionary = {}


static func _find_mesh_instances(node: Node) -> Array[MeshInstance3D]:
	var result: Array[MeshInstance3D] = []
	for child in node.get_children():
		if child is MeshInstance3D:
			result.append(child)
		result.append_array(_find_mesh_instances(child))
	return result


static func capture_frame(viewport: Viewport, skeleton_root: Node, out_dir: String, frame_index: int) -> void:
	DirAccess.make_dir_recursive_absolute(out_dir)
	var meshes := _find_mesh_instances(skeleton_root)
	var original_overrides: Array = []
	for m in meshes:
		original_overrides.append(m.material_override)

	# --- Color (materials originals, ja aplicats) ---
	await RenderingServer.frame_post_draw
	var color_img := viewport.get_texture().get_image()
	color_img.save_png("%s/color_%04d.png" % [out_dir, frame_index])

	# --- Depth ---
	var depth_mat := ShaderMaterial.new()
	depth_mat.shader = DEPTH_SHADER
	for m in meshes:
		m.material_override = depth_mat
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw  # marge per assegurar que el frame renderitzat és el nou
	var depth_img := viewport.get_texture().get_image()
	depth_img.save_png("%s/depth_%04d.png" % [out_dir, frame_index])

	# --- Normal ---
	var normal_mat := ShaderMaterial.new()
	normal_mat.shader = NORMAL_SHADER
	for m in meshes:
		m.material_override = normal_mat
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var normal_img := viewport.get_texture().get_image()
	normal_img.save_png("%s/normal_%04d.png" % [out_dir, frame_index])

	# --- Motion ---
	# Un ShaderMaterial PER mesh (no compartit) perquè cadascun necessita el seu propi
	# prev_model_matrix — i mat4 no es pot passar com a `instance uniform` (veure shader).
	for m in meshes:
		var mat := ShaderMaterial.new()
		mat.shader = MOTION_SHADER
		var prev_transform: Transform3D = _previous_transforms.get(m, m.global_transform)
		mat.set_shader_parameter("prev_model_matrix", Projection(prev_transform))
		m.material_override = mat
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var motion_img := viewport.get_texture().get_image()
	motion_img.save_png("%s/motion_%04d.png" % [out_dir, frame_index])

	# Desa les transforms d'aquest frame per a la propera crida.
	for m in meshes:
		_previous_transforms[m] = m.global_transform

	# --- Restaurar materials originals ---
	for i in meshes.size():
		meshes[i].material_override = original_overrides[i]
