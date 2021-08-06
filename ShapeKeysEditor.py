bl_info = {
    "name": "Shape Keys Editor",
    "description": "Sort ShapeKeys and rename with Regex",
    "author": "HahnZhu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Object Data > Shape Keys Editor",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

import re
import bpy


from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    PointerProperty,
    FloatVectorProperty,
)

from bpy.types import (
    Menu,
    Panel,
    Operator,
    PropertyGroup,
)

# fmt: off
WARNING_TIPS = [
    "No shape keys of your active object!",
    "Shape keys' names are not match!",
    "Arkit preset apply sucessfully!",
    "Something wrong happen!",
    "Shapekeys amounts are not match!",
    "Rename operation is done!",
    "Delete operation is done!",
    "Sort operation is done!"
]

# fmt: off
TEXTBLOCK_NAME = [
    "RENAME SHAPEKEYS HERE",
    "DELETE SHAPEKEYS HERE",
    "SORT SHAPEKEYS HERE",
]


# ------------------------------------------------------------------------
#    Def
# ------------------------------------------------------------------------

def update_enum(self, context):
    context.scene.skeditor.str_result = ""

def sort_sk(sklist):
    mysklist = sklist.copy()
    remove_count = 0
    for idx, sk in enumerate(sklist):
        current_sk = []
        for key in bpy.context.object.data.shape_keys.key_blocks:
            current_sk.append(key.name)

        try:
            index_of_current_sk = current_sk.index(sk)
            bpy.context.object.active_shape_key_index = index_of_current_sk
            bpy.ops.object.shape_key_move(type="TOP")

            if index_of_current_sk > 1:
                bpy.ops.object.shape_key_move(type="UP")

            step = 0
            while step < idx - remove_count:
                bpy.ops.object.shape_key_move(type="DOWN")
                step += 1
        except:
            remove_count += 1
            mysklist.remove(sk)

    if len(mysklist) == 0:
        return 1

    bpy.context.object.active_shape_key_index = 0
    return 7

def rename_sk(sklist):
    if not len(sklist) == len(bpy.context.object.data.shape_keys.key_blocks):
        return 4

    current_sk = []
    for key in bpy.context.object.data.shape_keys.key_blocks:
        current_sk.append(key.name)

    for idx, sk in enumerate(sklist):
        try:
            bpy.context.object.active_shape_key_index = idx
            bpy.context.object.data.shape_keys.key_blocks[current_sk[idx]].name = sk
        except:
            return 3

    bpy.context.object.active_shape_key_index = 0
    return 5

def delete_sk(sklist):
    for sk in sklist:
        current_sk = []
        for key in bpy.context.object.data.shape_keys.key_blocks:
            current_sk.append(key.name)

        try:
            index_of_current_sk = current_sk.index(sk)
            bpy.context.object.active_shape_key_index = index_of_current_sk
            bpy.ops.object.shape_key_remove(all=False)
        except:
            pass

    bpy.context.object.active_shape_key_index = 0
    return 6


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class SKEDITOR_Properties(PropertyGroup):

    bool_show_regex: BoolProperty(name="", description="", default=False)

    str_regex: StringProperty(
        name="Regex String",
        description="regex string with python standard, eg: foo[1-9]*bar",
        default="",
        maxlen=1024,
    )

    str_replace: StringProperty(
        name="Replace String",
        description="the replace string for regex",
        default="",
        maxlen=1024,
    )

    str_result: StringProperty(
        name="Replace String",
        description="result of preset apply",
        default="",
        maxlen=1024,
    )

    enum_tab: EnumProperty(
        name="tab",
        description="operations of shape keys",
        items=[
            ("rename", "Rename", ""),
            ("delete", "Delete", ""),
            ("sort", "Sort", ""),
        ],
        update=update_enum
    )


# ------------------------------------------------------------------------
#    Operator - Rename
# ------------------------------------------------------------------------

class SKEDITOR_OT_RenameSK(Operator):
    bl_idname = "skeditor.rename_shapekeys"
    bl_label = "Rename shapekeys in editor manually"
    bl_description = "Rename shapekeys in editor manually"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        textblock = bpy.data.texts.get(TEXTBLOCK_NAME[0])
        if textblock is None:
            textblock = bpy.data.texts.new(TEXTBLOCK_NAME[0])
        else:
            bpy.data.texts.get(TEXTBLOCK_NAME[0]).clear()

        skstr = ""
        for key in context.object.data.shape_keys.key_blocks:
            skstr += key.name + "\n"

        context.scene.skeditor.str_result = ""
        bpy.data.texts[TEXTBLOCK_NAME[0]].write(skstr)
        return {"FINISHED"}

class SKEDITOR_OT_ApplyRenameSK(Operator):
    bl_idname = "skeditor.apply_rename_shapekeys"
    bl_label = "Apply manual rename to shapekeys"
    bl_description = "Apply manual rename to shapekeys"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        skeditor = context.scene.skeditor

        final_sk = []
        textblock = bpy.data.texts.get(TEXTBLOCK_NAME[0])
        for line in textblock.lines:
            if line.body:
                final_sk.append(line.body)

        try:
            status = rename_sk(sklist=final_sk)
            skeditor.str_result = WARNING_TIPS[status]
        except:
            skeditor.str_result = WARNING_TIPS[3]

        return {"FINISHED"}

class SKEDITOR_OT_ApplyRenameWithRegex(Operator):
    bl_label = "Apply rename with regex"
    bl_idname = "skeditor.apply_rename_regex"
    bl_description = "Apply rename with regex"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        scene = context.scene
        skeditor = scene.skeditor
        object = context.object

        if skeditor.str_regex and object.data.shape_keys:
            pattern = re.compile(skeditor.str_regex)

            for idx, key in enumerate(object.data.shape_keys.key_blocks):
                replace_str = pattern.sub(skeditor.str_replace if skeditor.str_replace else "", key.name)
                replace_str = replace_str.replace("{i}", str(idx))
                object.data.shape_keys.key_blocks[key.name].name = replace_str

        return {"FINISHED"}


# ------------------------------------------------------------------------
#    Operator - Delete
# ------------------------------------------------------------------------

class SKEDITOR_OT_DeleteSK(Operator):
    bl_idname = "skeditor.delete_shapekeys"
    bl_label = "Delete shapekeys in editor manually"
    bl_description = "Delete shapekeys in editor manually"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        textblock = bpy.data.texts.get(TEXTBLOCK_NAME[1])
        if textblock is None:
            textblock = bpy.data.texts.new(TEXTBLOCK_NAME[1])
        else:
            bpy.data.texts.get(TEXTBLOCK_NAME[1]).clear()

        skstr = ""
        for key in context.object.data.shape_keys.key_blocks:
            skstr += key.name + "\n"

        context.scene.skeditor.str_result = ""
        bpy.data.texts[TEXTBLOCK_NAME[1]].write(skstr)
        return {"FINISHED"}

class SKEDITOR_OT_ApplyDeleteSK(Operator):
    bl_idname = "skeditor.apply_delete_shapekeys"
    bl_label = "Apply manual deletion to shapekeys"
    bl_description = "Apply manual deletion to shapekeys"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        skeditor = context.scene.skeditor

        final_sk = []
        textblock = bpy.data.texts.get(TEXTBLOCK_NAME[1])
        for line in textblock.lines:
            if line.body:
                final_sk.append(line.body)

        try:
            status = delete_sk(sklist=final_sk)
            skeditor.str_result = WARNING_TIPS[status]
        except:
            skeditor.str_result = WARNING_TIPS[3]

        return {"FINISHED"}


# ------------------------------------------------------------------------
#    Operator - Sort
# ------------------------------------------------------------------------

class SKEDITOR_OT_SortSK(Operator):
    bl_idname = "skeditor.sort_shapekeys"
    bl_label = "Sort shapekeys in editor manually"
    bl_description = "Sort shapekeys in editor manually"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        textblock = bpy.data.texts.get(TEXTBLOCK_NAME[2])
        if textblock is None:
            textblock = bpy.data.texts.new(TEXTBLOCK_NAME[2])
        else:
            bpy.data.texts.get(TEXTBLOCK_NAME[2]).clear()

        skstr = ""
        for key in context.object.data.shape_keys.key_blocks:
            skstr += key.name + "\n"

        context.scene.skeditor.str_result = ""
        bpy.data.texts[TEXTBLOCK_NAME[2]].write(skstr)
        return {"FINISHED"}

class SKEDITOR_OT_ApplySortSK(Operator):
    bl_idname = "skeditor.apply_sort_shapekeys"
    bl_label = "Apply manual sort to shapekeys"
    bl_description = "Apply manual sort to shapekeys"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        skeditor = context.scene.skeditor

        final_sk = []
        textblock = bpy.data.texts.get(TEXTBLOCK_NAME[2])
        for line in textblock.lines:
            if line.body:
                final_sk.append(line.body)

        try:
            status = sort_sk(sklist=final_sk)
            skeditor.str_result = WARNING_TIPS[status]
        except:
            skeditor.str_result = WARNING_TIPS[3]

        return {"FINISHED"}



# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class SKEDITOR_PT_MainPanel(Panel):
    bl_label = "Shape Keys Editor"
    bl_idname = "SKEDITOR_PT_MainPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        skeditor = scene.skeditor

        row = layout.row()
        row.prop(skeditor, "enum_tab", expand=True)

        if skeditor.enum_tab == "rename":
            row = layout.row()
            row.operator("skeditor.rename_shapekeys", text="Rename Edit")
            row.operator("skeditor.apply_rename_shapekeys", text="Apply")

            if skeditor.str_result:
                row = layout.row()
                row.alignment = "CENTER"
                if not skeditor.str_result == WARNING_TIPS[5]:
                    row.alert = True
                row.label(text=skeditor.str_result)

            layout.separator()
            layout.prop(skeditor, "bool_show_regex", text="Rename by regex")
            if skeditor.bool_show_regex:
                box = layout.box()
                box.prop(skeditor, "str_regex", text="Regex")
                box.prop(skeditor, "str_replace", text="Replace")
                box.operator("skeditor.apply_rename_regex", text="Apply")

        elif skeditor.enum_tab == "delete":
            row = layout.row()
            row.operator("skeditor.delete_shapekeys", text="Delete Edit")
            row.operator("skeditor.apply_delete_shapekeys", text="Apply")

            if skeditor.str_result:
                row = layout.row()
                row.alignment = "CENTER"
                if not skeditor.str_result == WARNING_TIPS[6]:
                    row.alert = True
                row.label(text=skeditor.str_result)

        elif skeditor.enum_tab == "sort":
            row = layout.row()
            row.operator("skeditor.sort_shapekeys", text="Sort Edit")
            row.operator("skeditor.apply_sort_shapekeys", text="Apply")

            if skeditor.str_result:
                row = layout.row()
                row.alignment = "CENTER"
                if not skeditor.str_result == WARNING_TIPS[7]:
                    row.alert = True
                row.label(text=skeditor.str_result)





# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    SKEDITOR_Properties,
    SKEDITOR_PT_MainPanel,
    SKEDITOR_OT_RenameSK,
    SKEDITOR_OT_ApplyRenameSK,
    SKEDITOR_OT_ApplyRenameWithRegex,
    SKEDITOR_OT_DeleteSK,
    SKEDITOR_OT_ApplyDeleteSK,
    SKEDITOR_OT_SortSK,
    SKEDITOR_OT_ApplySortSK
)

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.skeditor = PointerProperty(type=SKEDITOR_Properties)

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.skeditor
