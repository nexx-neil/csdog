"""Raw model identity and paths only; no inferred physics or control parameters."""
import xml.etree.ElementTree as ET
from dogfight.common.paths import MODEL, ASSETS
MODEL_ID = "csdog_12dof"
URDF = MODEL / "robot.urdf"
USD_DIRECTORY = ASSETS / MODEL_ID

def declared_joint_names():
    """URDF declaration order, explicitly not an Isaac runtime action order."""
    return tuple(joint.attrib["name"] for joint in ET.parse(URDF).getroot().findall("joint")
                 if joint.attrib["type"] != "fixed")
