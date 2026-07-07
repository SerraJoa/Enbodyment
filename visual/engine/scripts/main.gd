extends Node3D
## Escena d'entrada: construeix el maniquí i posa una càmera per validar
## visualment l'esquelet i l'exportació de G-buffer (color/depth/normal/motion).

var _skeleton: Skeleton3D
var _capture_frame_index := 0


func _ready() -> void:
	var env := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.15, 0.15, 0.15)
	env.environment = environment
	add_child(env)

	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -30, 0)
	add_child(light)

	_skeleton = ManikinBuilder.build(self)

	var camera := Camera3D.new()
	# Maniquí dret ~1.7m d'alçada (pelvis a ~0.9m de terra); càmera enrere i amunt.
	camera.position = Vector3(0.0, 1.0, 3.0)
	camera.look_at(Vector3(0.0, 0.9, 0.0), Vector3.UP)
	add_child(camera)
	camera.current = true

	print("Maniquí construït: %d bones." % _skeleton.get_bone_count())


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_P:
		# Gira NOMÉS l'esquelet (no `self`, que també conté la càmera) perquè hi hagi
		# moviment relatiu real entre captures — sense això la motion sempre sortiria
		# zero encara que el shader estigués perfecte.
		if _capture_frame_index > 0:
			_skeleton.rotate_y(deg_to_rad(5.0))

		var out_dir := "user://gbuffer_test"
		await GBufferExport.capture_frame(get_viewport(), self, out_dir, _capture_frame_index)
		print("G-buffer exportat a %s (frame %d)" % [ProjectSettings.globalize_path(out_dir), _capture_frame_index])
		_capture_frame_index += 1
