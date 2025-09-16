# ========================================================================
# Creator: Kat Mwenesongole 
# Notice: (C) Copyright 2025 by Kat Mwenesongole. All Rights Reserved. 
# ========================================================================

bl_info = {
    "name": "Kat Animation [binary] (.kanim)",
    "description": "Export animation data in Kat Animation format [binary] (.kanim)",
    "author": "Kat Mwenesongole",
    "version": (1, 0),
    "blender": (4, 5, 2),
    "location": "File > Export",
    "category": "Import-Export",
}

import bpy
import struct
import concurrent.futures

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# write .kanim data to disk
def write_kanim_data(context, filepath):
    f = open(filepath, "wb")
    
    selected = bpy.context.selected_objects[0]
    curves = selected.animation_data.action.fcurves
 
    frame_count = len(curves[0].keyframe_points)
    frames_per_sec =  bpy.context.scene.render.fps
    f.write(frame_count.to_bytes(4, byteorder = 'little'))
    f.write(frames_per_sec.to_bytes(4, byteorder = 'little'))
              
    frame = 0
    while frame < frame_count:
        frame_time = curves[0].keyframe_points[frame].co.x
        f.write(struct.pack('f', frame_time))

        # position
        f.write(struct.pack('f',  curves[1].keyframe_points[frame].co.y))
        f.write(struct.pack('f',  curves[2].keyframe_points[frame].co.y))
        f.write(struct.pack('f', -curves[0].keyframe_points[frame].co.y))

        # rotation
        rotation_x = curves[3].keyframe_points[frame].co.y
        rotation_y = curves[3+1].keyframe_points[frame].co.y
        rotation_z = curves[3+2].keyframe_points[frame].co.y
        
        if(rotation_x < 0): rotation_x = -rotation_x
        else:          rotation_x = (2*3.14159) - rotation_x    
        if(rotation_y < 0): rotation_y = -rotation_y
        else:          rotation_y = (2*3.14159) - rotation_y
        if(rotation_z < 0): rotation_z = -rotation_z
        else:          rotation_z = (2*3.14159) - rotation_z
        
        f.write(struct.pack('f', rotation_y))
        f.write(struct.pack('f', rotation_z))
        f.write(struct.pack('f', rotation_x))

        # scale
        f.write(struct.pack('f', curves[6+1].keyframe_points[frame].co.y))
        f.write(struct.pack('f', curves[6+2].keyframe_points[frame].co.y))
        f.write(struct.pack('f', curves[6].keyframe_points[frame].co.y))
                                       
        frame = frame + 1
    
    f.close()
    return {'FINISHED'}


class ExportAnimData(Operator, ExportHelper):
    """Export animation data in Kat Animation format [binary] (.kanim)"""
    bl_idname = "export_kanim.anim_data_binary"  # Important since its how bpy.ops.import_test.some_data is constructed.
    bl_label = "Save .kanim"

    filename_ext = ".kanim" #extension

    filter_glob: StringProperty(
        default="*.kanim",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
        )
    
    def execute(self, context):
        return write_kanim_data(context, self.filepath)

# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportAnimData.bl_idname, text="Kat Animation [binary] (.kanim)")

# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportAnimData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportAnimData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
