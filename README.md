### Note:<br>
Sample `.blend`, `.kmesh` and `.kanim` provided.<br>
Rotation is given in positive radians.<br>
Y-up, Left hand coordinate system.<br><br>

# Kat Mesh Exporter (.kmesh)<br>
### Header
<pre>[32] name
[ 4] size 
[ 4] num of vertices 
[ 4] num of vertex lists 
[ 4] mesh transform offset 
[ 4] vertices'      offset 
[ 4] normals'       offset 
[ 4] binormals'     offset 
[ 4] tangents'      offset 
[ 4] uvs'           offset
[ 4] vertices' list information offset</pre>
#### note: total header size is 72 bytes and offsets are from the beginning of the file<br>
  
### Vertex List Information Header
<pre>[32]    list name
[4]     first vertex offset
[4]     number of vertices 
[float] colour red
[float] colour green
[float] colour blue
[float] colour alpha</pre>
#### note: total vertex list header size is 56 bytes and offset are from the beginning of the vertex array<br>
      
### Mesh Transform Header
<pre>[32]     list name
[float3] position (x,y,z)
[float3] euler rotation (x,y,z)
[float3] scale (x,y,z) </pre>
#### note: total transform size is 36 bytes<br>

# Kat Animation Exporter (.kanim)<br>
### Header
<pre>[4] number of keyframes
[4] frames per second
[4] keyframes' offset</pre>
#### note: total header size is 12 bytes<br>

### Keyframe Header
<pre>[float]  frame time
[float3] position (x,y,z)
[float3] euler rotation (x,y,z)
[float3] scale (x,y,z)</pre>
#### note: total keyframe header size is 40 bytes
