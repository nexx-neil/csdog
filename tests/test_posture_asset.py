import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
sys.path.insert(0, str(ROOT/"source/stackforce_simready_generated_robot_lab"))
from prepare_posture_collision_asset import clip_surface
from csdog_motion.calibration import ASSET


class PostureAssetTests(unittest.TestCase):
    def test_triangle_clipping_preserves_surface_and_half_spaces(self):
        mesh = trimesh.creation.box(extents=(.2, .13, .1))
        axis = np.array([.3, -.4, .7])
        axis /= np.linalg.norm(axis)
        origin = np.array([.01, -.02, .005])
        positive = clip_surface(mesh, axis, origin)
        negative = clip_surface(mesh, -axis, origin)
        self.assertAlmostEqual(positive.area+negative.area, mesh.area, places=13)
        self.assertGreaterEqual(((positive.vertices-origin)@axis).min(), -1e-15)
        self.assertLessEqual(((negative.vertices-origin)@axis).max(), 1e-15)
        # No artificial closure/cap is added at the cut.
        for piece in (positive, negative):
            self.assertTrue(all(np.isfinite(piece.vertices).flat))

    def test_asset_generation_preserves_axes_inertia_and_sole_spheres(self):
        with tempfile.TemporaryDirectory(prefix="csdog-posture-test-") as folder:
            output = Path(folder)/"asset"
            subprocess.run([sys.executable, str(ROOT/"scripts/prepare_posture_collision_asset.py"),
                "--output", str(output), "--split-toe"], check=True, capture_output=True)
            provenance = json.loads((output/"provenance.json").read_text())
            old = ET.parse(ASSET/"robot_sim.urdf").getroot()
            new = ET.parse(provenance["urdf"]).getroot()
            self.assertEqual([ET.tostring(j) for j in old.findall("joint")],
                             [ET.tostring(j) for j in new.findall("joint")])
            for a, b in zip(old.findall("link"), new.findall("link")):
                self.assertEqual(a.get("name"), b.get("name"))
                self.assertEqual(ET.tostring(a.find("inertial")), ET.tostring(b.find("inertial")))
                if a.get("name").endswith("_sole"):
                    self.assertEqual(ET.tostring(a.find("collision")), ET.tostring(b.find("collision")))
                    self.assertEqual(len(b.findall("collision")), 2)
            for part in provenance["toe_partitions"]:
                self.assertAlmostEqual(part["source_surface_area_m2"], part["partition_surface_area_m2"], places=12)
                leg = part["leg"]
                center = np.array([float(v) for v in new.find(f"joint[@name='joint_link_{leg}_sole_fixed']/origin").get("xyz").split()])
                plane, axis = np.array(part["plane_in_knee_m"]), np.array(part["normal_in_knee"])
                distal = trimesh.load(output/f"{leg}_toe_in_sole.stl", process=False)
                proximal = trimesh.load(output/f"{leg}_knee_proximal.stl", process=False)
                self.assertGreaterEqual(((distal.vertices+center-plane)@axis).min(), -2e-8)
                self.assertLessEqual(((proximal.vertices-plane)@axis).max(), 2e-8)
            for path, sha in provenance["mesh_sha256"].items():
                self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), sha)
            self.assertFalse(provenance["training_enabled"])


if __name__ == "__main__":
    unittest.main()
