bl_info = {
    "name": "ShapeKeys Editor",
    "description": "Easily Edit ShapeKeys in Blender",
    "author": "HahnZhu",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Object Data > ShapeKeys Editor",
    "warning": "",
    "wiki_url": "https://blenderartists.org/t/addon-shapekeys-editor/1320941",
    "tracker_url": "https://github.com/hahnzhu/ShapeKeysEditor/issues",
    "category": "Object",
}

import os
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
    "No ShapeKeys of your active object!",
    "ShapeKeys' names are not match!",
    "Arkit preset apply sucessfully!",
    "Something wrong happen!",
    "Shapekeys amounts are not match!",
    "Rename operation is done!",
    "Delete operation is done!",
    "Sort operation is done!",
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
    context.scene.skeditor.str_result_from_file = ""

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

def isTxtFile(context, filepath):
    skeditor = context.scene.skeditor

    if (os.path.isdir(filepath)):
        skeditor.str_result_from_file = 'choose file instead of folder'
        return False
    elif (os.path.splitext(filepath)[1] != '.txt'):
        skeditor.str_result_from_file = 'choose file with txt format'
        return False
    return True

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class SKEDITOR_Properties(PropertyGroup):

    bool_show_regex: BoolProperty(name="", description="", default=False)
    bool_show_external_rename: BoolProperty(name="", description="", default=False)
    bool_show_external_delete: BoolProperty(name="", description="", default=False)
    bool_show_external_sort: BoolProperty(name="", description="", default=False)

    str_regex: StringProperty(
        name="Regex String",
        description="regex string with python standard, eg: foo[1-9]*bar",
        default="",
        maxlen=1024,
        update=update_enum
    )

    str_replace: StringProperty(
        name="Replace String",
        description="the replace string for regex",
        default="",
        maxlen=1024,
        update=update_enum
    )

    str_result: StringProperty(
        name="Replace String",
        description="result of preset apply",
        default="",
        maxlen=1024,
    )

    str_result_from_file: StringProperty(
        name="Replace String",
        description="result of external file apply",
        default="",
        maxlen=1024,
    )

    str_filepath_rename: StringProperty(
        name="",
        description="external file path with .txt format",
        default="",
        maxlen=1024,
        subtype="FILE_PATH",
        update=update_enum
    )

    str_filepath_delete: StringProperty(
        name="",
        description="external file path with .txt format",
        default="",
        maxlen=1024,
        subtype="FILE_PATH",
        update=update_enum
    )

    str_filepath_sort: StringProperty(
        name="",
        description="external file path with .txt format",
        default="",
        maxlen=1024,
        subtype="FILE_PATH",
        update=update_enum
    )

    enum_tab: EnumProperty(
        name="",
        description="operations of shapekeys",
        items=[
            ("rename", "Rename", "Rename in TextEditor"),
            ("delete", "Delete", "Delete in TextEditor"),
            ("sort", "Sort", "Sort in TextEditor"),
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
            if line.body.strip():
                final_sk.append(line.body.strip())
        try:
            status = rename_sk(sklist=final_sk)
            skeditor.str_result = WARNING_TIPS[status]
        except:
            skeditor.str_result = WARNING_TIPS[3]

        return {"FINISHED"}

class SKEDITOR_OT_ApplyRenameSKWithFile(Operator):
    bl_idname = "skeditor.apply_rename_shapekeys_with_file"
    bl_label = "Apply manual rename to shapekeys with file"
    bl_description = "Apply manual rename to shapekeys with file"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        skeditor = context.scene.skeditor
        filepath = skeditor.str_filepath_rename

        if isTxtFile(context, filepath):
            final_sk = []
            textblock = open(filepath, 'r')

            for line in textblock.readlines():
                if line.strip():
                    final_sk.append(line.strip())
            try:
                status = rename_sk(sklist=final_sk)
                skeditor.str_result_from_file = WARNING_TIPS[status]
            except:
                skeditor.str_result_from_file = WARNING_TIPS[3]

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
            if line.body.strip():
                final_sk.append(line.body.strip())

        try:
            status = delete_sk(sklist=final_sk)
            skeditor.str_result = WARNING_TIPS[status]
        except:
            skeditor.str_result = WARNING_TIPS[3]

        return {"FINISHED"}

class SKEDITOR_OT_ApplyDeleteSKWithFile(Operator):
    bl_idname = "skeditor.apply_delete_shapekeys_with_file"
    bl_label = "Apply manual deletion to shapekeys with file"
    bl_description = "Apply manual deletion to shapekeys with file"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        skeditor = context.scene.skeditor
        filepath = skeditor.str_filepath_delete

        if isTxtFile(context, filepath):
            final_sk = []
            textblock = open(filepath, 'r')
            for line in textblock.readlines():
                if line.strip():
                    final_sk.append(line.strip())
            try:
                status = delete_sk(sklist=final_sk)
                skeditor.str_result_from_file = WARNING_TIPS[status]
            except:
                skeditor.str_result_from_file = WARNING_TIPS[3]

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
            if line.body.strip():
                final_sk.append(line.body.strip())

        try:
            status = sort_sk(sklist=final_sk)
            skeditor.str_result = WARNING_TIPS[status]
        except:
            skeditor.str_result = WARNING_TIPS[3]

        return {"FINISHED"}

class SKEDITOR_OT_ApplySortSKWithFile(Operator):
    bl_idname = "skeditor.apply_sort_shapekeys_with_file"
    bl_label = "Apply manual sort to shapekeys with file"
    bl_description = "Apply manual sort to shapekeys with file"

    @classmethod
    def poll(self, context):
        return context.object and context.object.data.shape_keys

    def execute(self, context):
        skeditor = context.scene.skeditor
        filepath = skeditor.str_filepath_sort

        if isTxtFile(context, filepath):
            final_sk = []
            textblock = open(filepath, 'r')
            for line in textblock.readlines():
                if line.strip():
                    final_sk.append(line.strip())
            try:
                status = sort_sk(sklist=final_sk)
                skeditor.str_result_from_file = WARNING_TIPS[status]
            except:
                skeditor.str_result_from_file = WARNING_TIPS[3]

        return {"FINISHED"}



# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class SKEDITOR_PT_MainPanel(Panel):
    bl_label = "ShapeKeys Editor"
    bl_idname = "SKEDITOR_PT_MainPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        skeditor = scene.skeditor

        row = layout.row()
        row.prop(skeditor, "enum_tab", expand=False)

        # Tab - rename
        if skeditor.enum_tab == "rename":
            row = layout.row()
            row.operator("skeditor.rename_shapekeys", text="Edit In TextEditor")
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

            layout.prop(skeditor, "bool_show_external_rename", text="Rename by external file")
            if skeditor.bool_show_external_rename:
                box = layout.box()
                box.prop(skeditor, "str_filepath_rename")

                if skeditor.str_result_from_file:
                    row = box.row()
                    row.alignment = "CENTER"
                    if not skeditor.str_result_from_file == WARNING_TIPS[5]:
                        row.alert = True
                    row.label(text=skeditor.str_result_from_file)

                box.operator("skeditor.apply_rename_shapekeys_with_file", text="Apply")


        # Tab - delete
        elif skeditor.enum_tab == "delete":
            row = layout.row()
            row.operator("skeditor.delete_shapekeys", text="Edit In TextEditor")
            row.operator("skeditor.apply_delete_shapekeys", text="Apply")

            if skeditor.str_result:
                row = layout.row()
                row.alignment = "CENTER"
                if not skeditor.str_result == WARNING_TIPS[6]:
                    row.alert = True
                row.label(text=skeditor.str_result)

            layout.prop(skeditor, "bool_show_external_delete", text="Delete by external file")
            if skeditor.bool_show_external_delete:
                box = layout.box()
                box.prop(skeditor, "str_filepath_delete")

                if skeditor.str_result_from_file:
                    row = box.row()
                    row.alignment = "CENTER"
                    if not skeditor.str_result_from_file == WARNING_TIPS[6]:
                        row.alert = True
                    row.label(text=skeditor.str_result_from_file)

                box.operator("skeditor.apply_delete_shapekeys_with_file", text="Apply")

        # Tab - sort
        elif skeditor.enum_tab == "sort":
            row = layout.row()
            row.operator("skeditor.sort_shapekeys", text="Edit In TextEditor")
            row.operator("skeditor.apply_sort_shapekeys", text="Apply")

            if skeditor.str_result:
                row = layout.row()
                row.alignment = "CENTER"
                if not skeditor.str_result == WARNING_TIPS[7]:
                    row.alert = True
                row.label(text=skeditor.str_result)

            layout.prop(skeditor, "bool_show_external_sort", text="Sort by external file")
            if skeditor.bool_show_external_sort:
                box = layout.box()
                box.prop(skeditor, "str_filepath_sort")

                if skeditor.str_result_from_file:
                    row = box.row()
                    row.alignment = "CENTER"
                    if not skeditor.str_result_from_file == WARNING_TIPS[7]:
                        row.alert = True
                    row.label(text=skeditor.str_result_from_file)

                box.operator("skeditor.apply_sort_shapekeys_with_file", text="Apply")



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
    SKEDITOR_OT_ApplySortSK,
    SKEDITOR_OT_ApplyRenameSKWithFile,
    SKEDITOR_OT_ApplyDeleteSKWithFile,
    SKEDITOR_OT_ApplySortSKWithFile
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
