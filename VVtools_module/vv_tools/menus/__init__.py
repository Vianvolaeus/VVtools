#menus/init (top bar)

from . import topbar
from . import camerasmenu
from . import generalmenu
from . import materialsmenu
from . import meshoperatorsmenu
from . import riggingmenu
from . import vrcmenu

classes = topbar.classes


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)