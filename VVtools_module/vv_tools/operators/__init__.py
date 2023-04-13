# operators/__init__.py

from .rigging import (
    VVTools_OT_MergeToActiveBone,
    VVTools_OT_SmoothRigXfer,
)

# add other imports from operator .py files later

__all__ = [
    "VVTools_OT_MergeToActiveBone",
    "VVTools_OT_SmoothRigXfer",
    # Add the names of any additional operator classes you want to import
]

