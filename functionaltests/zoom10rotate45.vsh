
void main():
{
    gl_Position.x = gl_Vertex.y * 10;
    gl_Position.y = gl_Vertex.x * 10;
    gl_Position.z = gl_Vertex.z;
    gl_Position.w = gl_Vertex.w;
}

