# ========================================================================
# Creator: Kat Mwenesongole 
# Notice: (C) Copyright 2025 by Kat Mwenesongole. All Rights Reserved. 
# ========================================================================

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# write .kanim data to disk
def write_kanim_data(context, filepath):
    f = open(filepath, "w", encoding='utf-8')
    
    selected = bpy.context.selected_objects[0]
    curves = selected.animation_data.action.fcurves
 
    frame_count = len(curves[0].keyframe_points)
    f.write('keyframes [%i]\n' % frame_count)
    f.write('frames per sec [%i]\n\n' % bpy.context.scene.render.fps)
    
    frame = 0
    while frame < frame_count:
        frame_index = curves[0].keyframe_points[frame].co.x
        f.write('frame [%i]\n' % frame_index)
        
        # position
        f.write('[%s] %f, %f, %f\n' % (curves[0].data_path, 
                                       curves[0].keyframe_points[frame].co.y,
                                       curves[1].keyframe_points[frame].co.y,
                                       curves[2].keyframe_points[frame].co.y))                         
        # rotation
        rot_x = curves[3].keyframe_points[frame].co.y
        rot_y = curves[3+1].keyframe_points[frame].co.y
        rot_z = curves[3+2].keyframe_points[frame].co.y
        
        if(rot_x < 0): rot_x = -rot_x
        else:          rot_x = (2*3.14159) - rot_x    
        if(rot_y < 0): rot_y = -rot_y
        else:          rot_y = (2*3.14159) - rot_y
        if(rot_z < 0): rot_z = -rot_z
        else:          rot_z = (2*3.14159) - rot_z
        f.write('[%s] %f, %f, %f\n' % (curves[3].data_path, rot_x, rot_y, rot_z))                      
        
        # scale
        f.write('[%s] %f, %f, %f\n' % (curves[6].data_path, 
                                       curves[6].keyframe_points[frame].co.y,
                                       curves[6+1].keyframe_points[frame].co.y,
                                       curves[6+2].keyframe_points[frame].co.y)) 
        frame = frame + 1
    
    f.close()
    return {'FINISHED'}


class ExportAnimData(Operator, ExportHelper):
    """Export animation data in Kat Animation format (.kanim)"""
    bl_idname = "export_test.some_data"  # Important since its how bpy.ops.import_test.some_data is constructed.
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
    self.layout.operator(ExportAnimData.bl_idname, text="Kat Animation (.kanim)")

# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportAnimData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportAnimData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()