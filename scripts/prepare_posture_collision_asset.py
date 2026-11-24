#!/usr/bin/env python3
"""Create an isolated mesh-collision diagnostic asset; never replace locomotion."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from csdog_motion.calibration import ASSET


def clip_surface(mesh, normal, origin):
    """Keep a triangle surface in the positive half-space, without adding caps.

    Uses only existing numpy/trimesh; does not install a polygon dependency.
    """
    import numpy as np
    import trimesh
    triangles = []
    for triangle in mesh.triangles:
        polygon = []
        for a, b in zip(triangle, np.roll(triangle, -1, axis=0)):
            da, db = np.dot(a-origin, normal), np.dot(b-origin, normal)
            if da >= 0:
                polygon.append(a)
            if (da >= 0) != (db >= 0):
                polygon.append(a+(b-a)*(da/(da-db)))
        for i in range(1, len(polygon)-1):
            triangles.append([polygon[0], polygon[i], polygon[i+1]])
    vertices = np.asarray(triangles).reshape(-1, 3)
    faces = np.arange(len(vertices)).reshape(-1, 3)
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split-toe", action="store_true", help="Assign the distal 20mm of source knee mesh to its fixed sole child")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = ASSET/"robot_sim.urdf"
    tree = ET.parse(source)
    replaced = []
    for link in tree.getroot().findall("link"):
        if link.get("name").endswith("_sole"):
            continue
        visual = link.find("visual")
        if visual is None or visual.find("geometry/mesh") is None:
            raise ValueError("Expected a source mesh for each non-sole link")
        for collision in list(link.findall("collision")):
            link.remove(collision)
        collision = ET.SubElement(link, "collision")
        for name in ("origin", "geometry"):
            node = visual.find(name)
            if node is not None:
                collision.append(ET.fromstring(ET.tostring(node)))
        replaced.append(link.get("name"))
    toe_partitions = []
    if args.split_toe:
        import numpy as np
        import trimesh
        for leg in ("lr", "lf", "rf", "rr"):
            knee = tree.getroot().find(f"link[@name='link_{leg}_knee']")
            sole = tree.getroot().find(f"link[@name='link_{leg}_sole']")
            joint = tree.getroot().find(f"joint[@name='joint_link_{leg}_sole_fixed']")
            center = np.array([float(v) for v in joint.find("origin").get("xyz").split()])
            node = knee.find("collision/geometry/mesh")
            mesh_path = (ASSET/node.get("filename")).resolve()
            mesh = trimesh.load(mesh_path, process=False)
            # Current source knee visual origins are identity. Refuse an implicit frame change.
            origin = knee.find("collision/origin")
            if origin is not None and any(float(v) != 0 for key in ("xyz", "rpy") for v in origin.get(key, "0 0 0").split()):
                raise ValueError("Toe split requires identity source mesh origin")
            axis = center/np.linalg.norm(center)
            plane = center-.020*axis
            proximal = clip_surface(mesh, -axis, plane)
            distal = clip_surface(mesh, axis, plane)
            if proximal is None or distal is None or not len(proximal.faces) or not len(distal.faces):
                raise ValueError("Empty toe partition")
            # The union is the original surface, split at a plane; no sole center/radius moves.
            if not np.isclose(proximal.area+distal.area, mesh.area, rtol=1e-7, atol=1e-10):
                raise ValueError("Toe partition changed source surface area")
            distal.vertices -= center
            near = args.output/f"{leg}_knee_proximal.stl"
            tip = args.output/f"{leg}_toe_in_sole.stl"
            proximal.export(near)
            distal.export(tip)
            node.set("filename", str(near.resolve()))
            collision = ET.SubElement(sole, "collision")
            ET.SubElement(collision, "origin", xyz="0 0 0", rpy="0 0 0")
            ET.SubElement(ET.SubElement(collision, "geometry"), "mesh", filename=str(tip.resolve()))
            toe_partitions.append({"leg": leg, "distal_band_m": .020,
                "plane_in_knee_m": plane.tolist(), "normal_in_knee": axis.tolist(),
                "source_mesh_sha256": hashlib.sha256(mesh_path.read_bytes()).hexdigest(),
                "source_surface_area_m2": float(mesh.area),
                "partition_surface_area_m2": float(proximal.area+distal.area),
                "scope": "Surface partition only; convex decomposition may approximate both parts"})
    meshes = {}
    for node in tree.getroot().findall(".//mesh"):
        path = (ASSET/node.get("filename")).resolve()
        node.set("filename", str(path))
        meshes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    output = args.output/"robot_posture_mesh_diagnostic.urdf"
    tree.write(output, encoding="utf-8", xml_declaration=True)
    report = {"schema": "csdog_mesh_collision_diagnostic_v1",
        "scope": "Independent source-mesh convex-decomposition test; not approved for locomotion/posture execution or hardware",
        "urdf": str(output.resolve()), "source_urdf_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "diagnostic_urdf_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "mesh_sha256": meshes, "replaced_collision_links": replaced,
        "toe_partitions": toe_partitions,
        "unchanged": ["joint axes/origins/limits", "masses/inertias", "calibrated sole spheres", "visuals"],
        "required_import_settings": {"collider_type": "convex_decomposition", "self_collision": True,
            "enabled_self_collisions": True, "replace_cylinders_with_capsules": False},
        "training_enabled": False, "policy_loading_enabled": False}
    (args.output/"provenance.json").write_text(json.dumps(report, indent=2)+"\n")
    print(args.output/"provenance.json")


if __name__ == "__main__":
    main()
