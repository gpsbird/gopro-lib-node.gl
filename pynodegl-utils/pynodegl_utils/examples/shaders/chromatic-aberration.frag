#version 100

uniform sampler2D tex0_sampler;
uniform highp vec2 tex0_dimensions;
varying highp vec2 var_tex0_coord;

void main(void)
{
    highp vec2 step = 1.0 / tex0_dimensions;
    highp float b = texture2D(tex0_sampler, var_tex0_coord - step).b;
    highp float g = texture2D(tex0_sampler, var_tex0_coord).g;
    highp float r = texture2D(tex0_sampler, var_tex0_coord + step).r;
    gl_FragColor = vec4(r, g, b, 1.0);
}
