# ShapeKeysEditor
ShapeKeysEditor is a addon aims to edit shape keys easily in Blender.

## Documentation
See [Blenderartists threads](https://blenderartists.org/t/addon-shapekeys-editor/1320941).


## How to build develop environment?

* Install VSCode [Here](https://code.visualstudio.com/download).
* Install plugin call [Blender Development](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development)
* Add Conifg: `Ctrl+Shift+P` → `Preferences: Open Setting (JSON)`

    ```json
    "blender.addon.reloadOnSave": true,
    "blender.allowModifyExternalPython": true,
    ```
* Install [fake-bpy-module](https://github.com/nutti/fake-bpy-module): Blender Python API modules for the code completion in IDE.
* Add the plugin folder into VSCode Editor and rename `ShapeKeysEditor.py` to `__init__.py`
* Open Blender and load the plugin: `Ctrl+Shift+P` → `Blender: Build and Start` → `Choose your Blender Executable File`
* It will reload everytime you edit `__init__.py` file or you can manually reload by `Ctrl+Shift+P` → `Blender: Reload Addons`.
* Enable `Editor - Preferences - Interface - Display - Developer Extras / Python tooltips` in Blender for more information.


## Changelog

* 1.0.0 (Aug 6, 2021): First version with rename/sort/delete feature.
* 1.1.0 (Jan 4, 2022): Add feature for sorting the ShapeKeys with external txt file.
