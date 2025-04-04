
#version 330 core

in vec2 vPos;
in vec4 vColor;

out vec4 fragColor;

void main() {
    float A = -dot(vPos, vPos); // -r^2 = -(Pos.x^2 + Pos.y^2)
    if(A < -0.25)
        discard;
    float B = exp(A) * vColor.a; // exp(-r^2) -> gaussian
    fragColor = vec4(B * vColor.rgb, B);
}
