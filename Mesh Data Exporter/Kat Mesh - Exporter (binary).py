# ========================================================================
# Creator: Kat Mwenesongole 
# Notice: (C) Copyright 2023 by Kat Mwenesongole. All Rights Reserved. 
# ========================================================================

bl_info = {
    "name": "Kat Mesh [binary] (.kmesh)",
    "description": "Export mesh data in Kat Mesh format [binary] (.kmesh)",
    "author": "Kat Mwenesongole",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "category": "Import-Export",
}

import bpy
import bmesh
import struct
import concurrent.futures

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from math      import sqrt, pi
from mathutils import Matrix, Vector

def triangulate_object(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces = bm.faces[:])
    bm.to_mesh(me)
    bm.free()

def write(context, filepath): 
    
    # duplicate selected objects, then join them into one mesh.
    bpy.ops.object.duplicate() 
    bpy.ops.object.join()
    
    f = open(filepath, 'wb') 
    
    # there should be only one object in the array.
    for selected in bpy.context.selected_objects:
        mesh = selected.data
        obj  = selected
        
        triangulate_object(obj)
       
        # vertices orginised based on material.
        material_names   = [] # list of material names.
        material_counts  = [] # list of no. of vertices that make up a particular material in order of material names.
        material_offsets = [] # list of material offsets in order of material names.
        material_colours = [] # list of material colours in order of material names.
        
        vertices  = [] 
        uvs       = []
        normals   = []
        binormals = []
        tangents  = []
        
        #vertex, normal, bitangent, tangent & uv count
        vertex_count = 0
        
        for face in mesh.polygons:
            vertex_count = vertex_count + 3
            current_name = obj.material_slots[face.material_index].material.name
            current_colour = obj.material_slots[face.material_index].material.diffuse_color
            unique = True
            
            for material in material_names:
                if (material == current_name):
                    unique = False 
                    break
                
            if(unique == True):
                count = 0
                num   = 0

                for surface in mesh.polygons:          
                    mat_surface  = obj.material_slots[surface.material_index].material

                    if (mat_surface.name == current_name):
                        vertices.append(mesh.vertices[surface.vertices[0]].co)
                        vertices.append(mesh.vertices[surface.vertices[1]].co)
                        vertices.append(mesh.vertices[surface.vertices[2]].co)
                        
                        if (face.use_smooth == True):
                            normals.append(mesh.vertices[surface.vertices[0]].normal)
                            normals.append(mesh.vertices[surface.vertices[1]].normal)
                            normals.append(mesh.vertices[surface.vertices[2]].normal)
                        else:
                            normals.append(surface.normal)
                            normals.append(surface.normal)
                            normals.append(surface.normal)
                            
                        binormals.append(mesh.loops[num].bitangent)
                        binormals.append(mesh.loops[num + 1].bitangent)
                        binormals.append(mesh.loops[num + 2].bitangent)
                        
                        tangents.append(mesh.loops[num].tangent)
                        tangents.append(mesh.loops[num + 1].tangent)
                        tangents.append(mesh.loops[num + 2].tangent)     
                            
                        uvs.append(mesh.uv_layers.active.data[num].uv)
                        uvs.append(mesh.uv_layers.active.data[num + 1].uv)
                        uvs.append(mesh.uv_layers.active.data[num + 2].uv)
                        
                        num   = num   + 3;
                        count = count + 3;
                    else:
                        num   = num + 3
                                                     
                material_counts.append(count)
                material_names.append(current_name) 
                material_colours.append(current_colour)
        
        #calculate material offsets
        cumulative = 0
        count      = 0
        for mat in material_counts:
            material_offsets.append(cumulative)
            cumulative = cumulative + material_counts[count]
            count = count + 1
                           
        #calculate material count         
        material_count = 0
        for mat in material_names:
            material_count = material_count + 1
            
        #calculate rotation
        # (+) anti-clockwise (-) clockwise
        rotation_x =  obj.rotation_euler.y # must be positive radians
        rotation_y =  obj.rotation_euler.z # must be positive radians
        rotation_z =  obj.rotation_euler.x # must be positive radians
        if(rotation_x < 0): rotation_x = -rotation_x
        else:               rotation_x = (2*pi) - rotation_x
        if(rotation_y < 0): rotation_y = -rotation_y
        else:               rotation_y = (2*pi) - rotation_y
        if(rotation_z < 0): rotation_z = -rotation_z
        else:               rotation_z = (2*pi) - rotation_z
            
        #offsets
        orientation_offset = 32 + (10 * 4)
        material_offset    = orientation_offset + (3 * 3 * 4) 
        vert_offset        = material_offset    + (material_count * (32 + 24))
        norm_offset        = vert_offset        + (vertex_count   * 3  * 4)
        binorm_offset      = norm_offset        + (vertex_count   * 3  * 4)
        tangent_offset     = binorm_offset      + (vertex_count   * 3  * 4)
        uv_offset          = tangent_offset     + (vertex_count   * 3  * 4)
          
        size  = uv_offset + (vertex_count * 2 * 4)
        
        #writing
                 
        #count
        f.write((obj.name.split('.')[0]).ljust(32,"\0")[:32].encode('ascii'))
        
        f.write(          size.to_bytes(4, byteorder = 'little'))
        f.write(  vertex_count.to_bytes(4, byteorder = 'little'))
        f.write(material_count.to_bytes(4, byteorder = 'little'))    
        f.write(orientation_offset.to_bytes(4, byteorder = 'little'))      
        f.write(       vert_offset.to_bytes(4, byteorder = 'little'))
        f.write(       norm_offset.to_bytes(4, byteorder = 'little'))
        f.write(     binorm_offset.to_bytes(4, byteorder = 'little'))
        f.write(    tangent_offset.to_bytes(4, byteorder = 'little'))
        f.write(         uv_offset.to_bytes(4, byteorder = 'little'))
        f.write(   material_offset.to_bytes(4, byteorder = 'little'))
        
        #orientation
        f.write(struct.pack('f',  obj.location.y))
        f.write(struct.pack('f',  obj.location.z))
        f.write(struct.pack('f', -obj.location.x))  
        f.write(struct.pack('f',  rotation_x))
        f.write(struct.pack('f',  rotation_y))
        f.write(struct.pack('f',  rotation_z))
        f.write(struct.pack('f',  obj.scale.y))
        f.write(struct.pack('f',  obj.scale.z))
        f.write(struct.pack('f',  obj.scale.x))
               
        count = 0  
        for mat in material_names:
            f.write(material_names  [count].ljust(32, "\0")[:32].encode('ascii'))
            f.write(material_offsets[count].to_bytes(4, byteorder = 'little'))
            f.write(material_counts [count].to_bytes(4, byteorder = 'little'))
            f.write(struct.pack('f', material_colours[count][0]))
            f.write(struct.pack('f', material_colours[count][1]))
            f.write(struct.pack('f', material_colours[count][2]))
            f.write(struct.pack('f', material_colours[count][3]))
            count = count + 1
          
        for vertex in vertices:
            f.write(struct.pack('f',  vertex.y))
            f.write(struct.pack('f',  vertex.z))
            f.write(struct.pack('f', -vertex.x))   
            
        for normal in normals:
            f.write(struct.pack('f',  normal.y))
            f.write(struct.pack('f',  normal.z)) 
            f.write(struct.pack('f', -normal.x))        
        for binormal in binormals:
            f.write(struct.pack('f',  binormal.y))
            f.write(struct.pack('f',  binormal.z)) 
            f.write(struct.pack('f', -binormal.x)) 
        for tangent in tangents:
            f.write(struct.pack('f',  tangent.y))
            f.write(struct.pack('f',  tangent.z)) 
            f.write(struct.pack('f', -tangent.x)) 
            
        for uv in uvs:
            f.write(struct.pack('f', uv[0]))
            f.write(struct.pack('f', uv[1]))
        
    bpy.ops.object.delete()
                    
    f.close()
    return {'FINISHED'}


class ExportMeshData(Operator, ExportHelper):
    """Export mesh data in Kat Mesh format [binary] (.kmesh)""" 
    bl_idname = "export_kmesh.mesh_data_binary"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Save .kmesh"

    filename_ext = ".kmesh"
    filter_glob: StringProperty(default="*.km", options = {'HIDDEN'}, maxlen=255)

    def execute(self, context):
        return write(context, self.filepath)

# export menu
def menu_func_export(self, context):
    self.layout.operator(ExportMeshData.bl_idname, text = "Kat Mesh [binary] (.kmesh)")

def register():
    bpy.utils.register_class(ExportMeshData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportMeshData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
