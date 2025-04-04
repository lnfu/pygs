#version 330 core

layout(location = 0) in vec2 aPos; // 頂點位置 (四邊形)

layout(location = 1) in vec3 aInstancePos;
layout(location = 2) in vec3 aInstanceScale;
layout(location = 3) in vec4 aInstanceRot;   // (x, y, z, w)
layout(location = 4) in vec4 aInstanceColor; // RGBA

uniform mat4 uView;
uniform mat4 uProjection;

// 傳給 fragment shader
out vec2 vPos; // (x, y)
out vec4 vColor; // RGBA

// ref: https://gamedev.stackexchange.com/questions/28395/rotating-vector3-by-a-quaternion
vec3 rotateVectorByQuaternion(vec3 v, vec4 q) {
    // q = (x, y, z, w)
    vec3 u = q.xyz;
    float s = q.w;

    return 2.0 * dot(u, v) * u + (s * s - dot(u, u)) * v + 2.0 * s * cross(u, v);
}

void main() {
    // TODO 轉成相機座標系

    // TODO clipping

    // scaling
    vec3 localPos = vec3(aPos * aInstanceScale.xy, 0.0);

    // rotation
    vec3 rotatedPos = rotateVectorByQuaternion(localPos, aInstanceRot);

    // center (position)
    vec3 worldPos = aInstancePos + rotatedPos;

    gl_Position = uProjection * uView * vec4(worldPos, 1.0);

    vColor = aInstanceColor;
    vPos = aPos;
}
