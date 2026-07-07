shader_type spatial;
render_mode unshaded, cull_back;

// Motion vectors en espai de pantalla (UV), codificats com a color per exportar a PNG
// (mateixa idea que un normal map: bias+scale perquè capi en [0,1]).
//
// Requereix que gbuffer_export.gd fixi `prev_model_matrix` amb el global_transform
// d'aquest mesh al frame anterior. Si no n'hi ha (primer frame), s'hi passa el
// transform actual -> motion zero -> surt gris pla (0.5, 0.5).
//
// IMPORTANT: ha de ser un `uniform` normal (amb un ShaderMaterial propi per mesh),
// NO un `instance uniform` — els instance uniforms de Godot només admeten tipus
// escalars/vectorials, no mat4. Amb `instance uniform` el valor no s'aplicava de
// veritat i sortia un offset gegant constant (detectat provant-ho: motion no-zero
// ja al primer frame, sense cap moviment previ).
//
// Decodificació a Python: veure gbuffer.py (MOTION_SCALE ha de coincidir exactament).
// Simplificació: assumeix que la càmera NO es mou entre els dos frames comparats
// (VIEW_MATRIX és el mateix als dos termes) — vàlid per aquesta escena estàtica de prova.

uniform mat4 prev_model_matrix;

const float MOTION_SCALE = 0.25; // marge maxim codificable: +/-0.25 de l'amplada/alcada de pantalla

varying vec4 v_current_clip;
varying vec4 v_prev_clip;

void vertex() {
	v_current_clip = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	v_prev_clip = PROJECTION_MATRIX * VIEW_MATRIX * prev_model_matrix * vec4(VERTEX, 1.0);
}

void fragment() {
	vec2 current_ndc = v_current_clip.xy / v_current_clip.w;
	vec2 prev_ndc = v_prev_clip.xy / v_prev_clip.w;
	vec2 motion_uv = (current_ndc - prev_ndc) * 0.5; // NDC ([-1,1]) -> UV ([0,1])

	vec2 encoded = clamp(motion_uv / MOTION_SCALE, -1.0, 1.0) * 0.5 + 0.5;
	ALBEDO = vec3(encoded, 0.5);
}
