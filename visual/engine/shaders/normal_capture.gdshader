shader_type spatial;
render_mode unshaded, cull_back;

// Normal en espai de vista codificada com a color (n*0.5+0.5), per ControlNet (normal map).
void fragment() {
	ALBEDO = NORMAL * 0.5 + 0.5;
}
