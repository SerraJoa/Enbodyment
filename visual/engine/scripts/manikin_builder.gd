extends Node
class_name ManikinBuilder
## Construeix l'Skeleton3D + meshes primitius del maniquí a partir de
## data/manikin_skeleton.json (generat per tools/urdf_to_scene_data.py a partir
## de manikin/humanoid.urdf, que és la font de veritat de l'estructura).
##
## No es duplica l'URDF a mà: si canvia l'esquelet, es regenera el JSON i
## aquest script el reflecteix sense tocar cap escena.

const SKELETON_JSON_PATH := "res://data/manikin_skeleton.json"


static func build(parent: Node3D) -> Skeleton3D:
	var data := _load_json(SKELETON_JSON_PATH)
	var links: Dictionary = data["links"]
	var joints: Array = data["joints"]
	var root_link: String = data["root_link"]

	var children_by_parent := {}
	var joint_by_child := {}
	for j in joints:
		var joint: Dictionary = j
		children_by_parent.get_or_add(joint["parent"], []).append(joint["child"])
		joint_by_child[joint["child"]] = joint

	var skeleton := Skeleton3D.new()
	skeleton.name = "ManikinSkeleton"
	parent.add_child(skeleton)

	# Ordre topologic (BFS) des de l'arrel perque cada os es creï despres del seu pare.
	var order: Array[String] = [root_link]
	var queue: Array[String] = [root_link]
	while not queue.is_empty():
		var current: String = queue.pop_front()
		for child_name in children_by_parent.get(current, []):
			order.append(child_name)
			queue.append(child_name)

	var bone_index_by_name := {}
	for link_name in order:
		var bone_idx := skeleton.add_bone(link_name)
		bone_index_by_name[link_name] = bone_idx

		if link_name == root_link:
			skeleton.set_bone_parent(bone_idx, -1)
			skeleton.set_bone_rest(bone_idx, Transform3D(Basis.IDENTITY, Vector3.ZERO))
		else:
			var joint: Dictionary = joint_by_child[link_name]
			var parent_idx: int = bone_index_by_name[joint["parent"]]
			skeleton.set_bone_parent(bone_idx, parent_idx)
			var origin: Array = joint["origin_godot"]
			var pos := Vector3(origin[0], origin[1], origin[2])
			skeleton.set_bone_rest(bone_idx, Transform3D(Basis.IDENTITY, pos))

		var attachment := BoneAttachment3D.new()
		attachment.name = link_name + "_attachment"
		attachment.bone_name = link_name
		skeleton.add_child(attachment)

		var mesh_instance := _build_mesh_instance(links[link_name])
		attachment.add_child(mesh_instance)

	return skeleton


static func _build_mesh_instance(link_data: Dictionary) -> MeshInstance3D:
	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = link_data["name"] + "_mesh"

	var geometry: Dictionary = link_data["geometry"]
	var mesh: Mesh
	match geometry["type"]:
		"box":
			var box := BoxMesh.new()
			var size: Array = geometry["size"]
			box.size = Vector3(size[0], size[1], size[2])
			mesh = box
		"cylinder":
			var cyl := CylinderMesh.new()
			cyl.top_radius = geometry["radius"]
			cyl.bottom_radius = geometry["radius"]
			cyl.height = geometry["height"]
			mesh = cyl
		"sphere":
			var sph := SphereMesh.new()
			sph.radius = geometry["radius"]
			sph.height = geometry["radius"] * 2.0
			mesh = sph
		_:
			mesh = BoxMesh.new()

	mesh_instance.mesh = mesh

	var origin: Array = link_data["visual_origin_godot"]
	mesh_instance.position = Vector3(origin[0], origin[1], origin[2])

	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.6, 0.6, 0.6)
	mesh_instance.set_surface_override_material(0, material)

	return mesh_instance


static func _load_json(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("No s'ha pogut obrir %s — executa tools/urdf_to_scene_data.py primer." % path)
		return {}
	var text := file.get_as_text()
	var parsed = JSON.parse_string(text)
	if parsed == null:
		push_error("JSON invalid a %s" % path)
		return {}
	return parsed
