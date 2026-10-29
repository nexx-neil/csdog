#!/usr/bin/env python3
"""Generate the simulation-only CSDog v2 URDF without changing the source export.

The source mesh URDF is retained byte-for-byte for provenance.  This generator
replaces training collisions with deterministic URDF primitives, adds separate
sole links, and applies the explicitly provisional simulation joint envelope.
It never claims that the selected limits are physical hardware hard stops.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


def fmt(values: list[float] | tuple[float, ...]) -> str:
    return " ".join(f"{value:.8g}" for value in values)


def norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def cylinder_rpy(vector: list[float]) -> tuple[float, float, float]:
    """Return RPY rotating a cylinder's local +Z axis onto vector."""
    length = norm(vector)
    x, y, z = (value / length for value in vector)
    yaw = math.atan2(y, x)
    pitch = math.atan2(math.sqrt(x * x + y * y), z)
    return (0.0, pitch, yaw)


def add_collision(link: ET.Element, geometry_tag: str, geometry_attrs: dict[str, str], xyz: list[float], rpy: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> None:
    collision = ET.SubElement(link, "collision")
    ET.SubElement(collision, "origin", {"xyz": fmt(xyz), "rpy": fmt(rpy)})
    geometry = ET.SubElement(collision, "geometry")
    ET.SubElement(geometry, geometry_tag, geometry_attrs)


def add_segment(link: ET.Element, endpoint: list[float], radius: float) -> None:
    length = norm(endpoint)
    center = [value * 0.5 for value in endpoint]
    add_collision(
        link,
        "cylinder",
        {"radius": f"{radius:.8g}", "length": f"{length:.8g}"},
        center,
        cylinder_rpy(endpoint),
    )


def joint_class(name: str) -> str:
    suffix = name.rsplit("_", 1)[-1]
    return {"1": "hip_roll", "2": "hip_pitch", "3": "knee"}[suffix]


def generate(source: Path, output: Path, profile_path: Path) -> None:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    root = ET.parse(source).getroot()
    limits = profile["simulation_envelope"]["joint_limits_rad"]
    effort = profile["simulation_envelope"]["effort_limit_nm"]
    velocity = profile["simulation_envelope"]["velocity_limit_rad_s"]
    sole_cfg = profile["derived_collision"]

    joints = {node.attrib["name"]: node for node in root.findall("joint")}
    links = {node.attrib["name"]: node for node in root.findall("link")}
    child_joint_origins: dict[str, list[float]] = {}
    for joint in joints.values():
        parent = joint.find("parent").attrib["link"]
        origin = joint.find("origin")
        child_joint_origins[parent] = [float(value) for value in origin.attrib["xyz"].split()]
        lower, upper = limits[joint_class(joint.attrib["name"])]
        limit = joint.find("limit")
        limit.attrib.update(
            lower=f"{lower:.8g}", upper=f"{upper:.8g}", effort=f"{effort:.8g}", velocity=f"{velocity:.8g}"
        )

    for link in links.values():
        for collision in list(link.findall("collision")):
            link.remove(collision)
        name = link.attrib["name"]
        if name == "base":
            add_collision(link, "box", {"size": "0.22 0.20 0.10"}, [0.0, 0.0, -0.05])
        elif name.endswith("hip_roll"):
            add_collision(link, "sphere", {"radius": "0.048"}, [0.0, 0.0, 0.0])
            add_segment(link, child_joint_origins[name], 0.030)
        elif name.endswith("hip_pitch"):
            add_collision(link, "sphere", {"radius": "0.048"}, [0.0, 0.0, 0.0])
            add_segment(link, child_joint_origins[name], 0.026)
        elif name.endswith("knee"):
            add_collision(link, "sphere", {"radius": "0.040"}, [0.0, 0.0, 0.0])
            sole_center = sole_cfg["sole_centers_in_knee_link_m"][name]
            add_segment(link, sole_center, 0.018)

    sole_radius = float(sole_cfg["sole_radius_m"])
    sole_mass = float(sole_cfg["sole_mass_kg"])
    inertia = 0.4 * sole_mass * sole_radius * sole_radius
    for knee_name, center in sole_cfg["sole_centers_in_knee_link_m"].items():
        sole_name = knee_name.replace("_knee", "_sole")
        sole = ET.SubElement(root, "link", {"name": sole_name})
        inertial = ET.SubElement(sole, "inertial")
        ET.SubElement(inertial, "origin", {"xyz": "0 0 0", "rpy": "0 0 0"})
        ET.SubElement(inertial, "mass", {"value": f"{sole_mass:.8g}"})
        ET.SubElement(
            inertial,
            "inertia",
            {"ixx": f"{inertia:.8g}", "ixy": "0", "ixz": "0", "iyy": f"{inertia:.8g}", "iyz": "0", "izz": f"{inertia:.8g}"},
        )
        visual = ET.SubElement(sole, "visual")
        ET.SubElement(visual, "origin", {"xyz": "0 0 0", "rpy": "0 0 0"})
        visual_geometry = ET.SubElement(visual, "geometry")
        ET.SubElement(visual_geometry, "sphere", {"radius": f"{sole_radius:.8g}"})
        material = ET.SubElement(visual, "material", {"name": f"{sole_name}_color"})
        ET.SubElement(material, "color", {"rgba": "0.10 0.10 0.12 1"})
        add_collision(sole, "sphere", {"radius": f"{sole_radius:.8g}"}, [0.0, 0.0, 0.0])
        joint = ET.SubElement(root, "joint", {"name": f"joint_{sole_name}_fixed", "type": "fixed"})
        ET.SubElement(joint, "parent", {"link": knee_name})
        ET.SubElement(joint, "child", {"link": sole_name})
        ET.SubElement(joint, "origin", {"xyz": fmt(center), "rpy": "0 0 0"})

    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    root.insert(0, ET.Comment(f" generated from {source.name} sha256={source_sha} using {profile_path.name}; simulation only "))
    ET.indent(root, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(output, encoding="utf-8", xml_declaration=True)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    asset_dir = repo / "source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=asset_dir / "robot.urdf")
    parser.add_argument("--output", type=Path, default=asset_dir / "robot_sim.urdf")
    parser.add_argument("--profile", type=Path, default=repo / "config/csdog_v2_hardware_profile.json")
    args = parser.parse_args()
    generate(args.source.resolve(), args.output.resolve(), args.profile.resolve())
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
