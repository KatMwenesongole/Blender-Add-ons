# ========================================================================
# Creator: Kat Mwenesongole 
# Notice: (C) Copyright 2023 by Kat Mwenesongole. All Rights Reserved. 
# ========================================================================

bl_info = {
    "name": "Kat Mesh [text] (.kmesh)",
    "description": "Export mesh data in Kat Mesh format [text] (.kmesh)",
    "author": "Kat Mwenesongole",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "category": "Import-Export",
}

import bpy
import bmesh

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
    
    f = open(filepath, 'w', encoding='utf-8')
    
    # there should be only one object in the array.
    for selected in bpy.context.selected_objects:
    
        mesh = selected.data
        obj  = selected
     
        triangulate_object(obj)
        
        mesh.calc_tangents()
            
        # vertices orginised based on material
        material_names   = [] # list of material names
        material_counts  = [] # list of no. of vertices that make up a particular material in order of material names
        material_offsets = [] # list of material indentations in order of material names
        material_colours = [] # list of material colours in order of material names
        
        vertices   = []
        uvs        = []
        normals    = []
        bitangents = []
        tangents   = []
        
        #calculate vertex, normal & uv count
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
                    mat_surface = obj.material_slots[surface.material_index].material

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
                            
                            
                        bitangents.append(mesh.loops[num].bitangent)
                        bitangents.append(mesh.loops[num + 1].bitangent)
                        bitangents.append(mesh.loops[num + 2].bitangent)  
                        
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
        count = 0
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
        rotation_z = -obj.rotation_euler.x # must be positive radians
        
        if(rotation_x < 0): rotation_x = -rotation_x
        else:               rotation_x = (2*pi) - rotation_x    
        if(rotation_y < 0): rotation_y = -rotation_y
        else:               rotation_y = (2*pi) - rotation_y
        if(rotation_z < 0): rotation_z = -rotation_z
        else:               rotation_z = (2*pi) - rotation_z
            
        #writing    
        f.write("name: " + (obj.name).split('.')[0] + "\n")
        f.write('vertex   count: %i\n'   % (vertex_count)) 
        f.write('material count: %i\n\n' % (material_count))    
        
        count = 0  
        for mat in material_names:
            f.write('(%s offset:%i count:%i colour:%f %f %f %f)\n' % (material_names[count], material_offsets[count], material_counts[count], material_colours[count][0], material_colours[count][1], material_colours[count][2], material_colours[count][3]))
            count = count + 1

        f.write('\nposition: %f %f %f\n' % (obj.location.y      , obj.location.z      , -obj.location.x))
        f.write('rotation: %f %f %f\n'   % (rotation_x, rotation_y, rotation_z))
        f.write('scale:    %f %f %f\n\n' % (obj.scale.y         , obj.scale.z         ,  obj.scale.x))
                   
        f.write("vertex:\n")
        for vertex in vertices:
            f.write(('%f '  % ( vertex.y)).rjust(10, "\0"));
            f.write(('%f '  % ( vertex.z)).rjust(10, "\0"));
            f.write(('%f\n' % (-vertex.x)).rjust(10, "\0"));
        f.write("\n")  
        
        f.write("uv:\n")
        for uv in uvs:
            f.write('%f %f\n' % (uv[0], uv[1]))
        f.write("\n")  
        
        f.write("normal:\n")
        for normal in normals:
            f.write(('%f '  % ( normal.y)).rjust(10, "\0"));
            f.write(('%f '  % ( normal.z)).rjust(10, "\0"));
            f.write(('%f\n' % (-normal.x)).rjust(10,  "\0"));
        f.write("\n")  
        
        f.write("binormal:\n")
        for bitangent in bitangents:
            f.write(('%f '  % ( bitangent.y)).rjust(10, "\0"));
            f.write(('%f '  % ( bitangent.z)).rjust(10, "\0"));
            f.write(('%f\n' % (-bitangent.x)).rjust(10, "\0"));
        f.write("\n")
        
        f.write("tangent:\n")
        for tangent in tangents:
            f.write(('%f '  % ( tangent.y)).rjust(10, "\0"));
            f.write(('%f '  % ( tangent.z)).rjust(10, "\0"));
            f.write(('%f\n' % (-tangent.x)).rjust(10, "\0"));
        f.write("\n")

    bpy.ops.object.delete()
                    
    f.close()
    return {'FINISHED'}


class ExportMeshData(Operator, ExportHelper):
    """Export mesh data in Kat Mesh format [text] (.kmesh)""" 
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Save .kmesh"

    # file extension
    filename_ext = ".kmesh"
    filter_glob: StringProperty(default="*.kmesh", options = {'HIDDEN'}, maxlen=255)

    def execute(self, context):
        return write(context, self.filepath)


# export menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text = "Kat Mesh [text] (.kmesh)")


def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()