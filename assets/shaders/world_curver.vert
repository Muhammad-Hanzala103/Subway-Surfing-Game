#version 120

// World Bending Vertex Shader
// compatible with legacy OpenGL (version 120)

varying vec2 vTexCoord;
varying vec3 vNormal;
varying vec3 vViewPos;
varying float vDist;

uniform float uTime;
uniform float uCurveStrength; 

void main() {
    vTexCoord = gl_MultiTexCoord0.xy;
    vNormal = gl_NormalMatrix * gl_Normal;
    
    // Get view space position
    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
    vViewPos = viewPos.xyz;
    vDist = -viewPos.z; // Distance from camera
    
    // Calculate world bending
    // Curve downwards based on distance squared
    float curve = uCurveStrength * vDist * vDist;
    viewPos.y -= curve;
    
    gl_Position = gl_ProjectionMatrix * viewPos;
    
    // Pass color
    gl_FrontColor = gl_Color;
}
