#version 120

// Simple Fragment Shader
// Supports textures, fog, and basic lighting

varying vec2 vTexCoord;
varying vec3 vNormal;
varying vec3 vViewPos;
varying float vDist;

uniform sampler2D uTexture;
uniform bool uUseTexture;

void main() {
    vec4 color = gl_Color;
    
    if (uUseTexture) {
        color *= texture2D(uTexture, vTexCoord);
    }
    
    // Apply fog (Fixed function fog emulation if needed, or rely on gl_Fog)
    // In legacy GLSL 1.20, we can access gl_Fog parameters if established
    
    float fogDensity = gl_Fog.density;
    float fogFactor = exp(-fogDensity * fogDensity * vDist * vDist);
    fogFactor = clamp(fogFactor, 0.0, 1.0);
    
    gl_FragColor = mix(gl_Fog.color, color, fogFactor);
}
