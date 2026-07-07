shader_type spatial;
render_mode unshaded, cull_back;

// Profunditat lineal (espai de vista) normalitzada [0,1] entre near/far,
// exportada com a gris per servir de conditioning de ControlNet (depth).
uniform float near_plane : hint_range(0.01, 10.0) = 0.05;
uniform float far_plane : hint_range(1.0, 100.0) = 10.0;

varying float v_view_depth;

void vertex() {
	vec4 view_pos = MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	v_view_depth = -view_pos.z; // camera mira cap a -Z en espai de vista
}

void fragment() {
	float d = clamp((v_view_depth - near_plane) / (far_plane - near_plane), 0.0, 1.0);
	ALBEDO = vec3(d);
}
