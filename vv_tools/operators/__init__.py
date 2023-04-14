# operators/__init__.py

from . import camerasops
from . import generalops
from . import materialsops
from . import meshoperatorsops
from . import riggingops
from . import vrcanalysisops

classes = (
    camerasops.classes
    + generalops.classes
    + materialsops.classes
    + meshoperatorsops.classes
    + riggingops.classes
    + vrcanalysisops.classes
)
