#!/usr/bin/env python3
"""Static, simulator-free URDF gate for CSDog assets.

The report deliberately separates XML/asset correctness from hardware-model
readiness.  A structurally valid URDF can still fail the physics gate when its
limits are placeholders or its collision geometry is unsuitable for training.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def floats(text: str | None, count: int) -> list[float]:
    values = [float(value) for value in (text or "").split()]
    if len(values) != count:
        raise ValueError(f"expected {count} values, got {values}")
    return values


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def transform(xyz: list[float], rpy: list[float]) -> list[list[float]]:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rotation = [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ]
    return [
        [rotation[0][0], rotation[0][1], rotation[0][2], xyz[0]],
        [rotation[1][0], rotation[1][1], rotation[1][2], xyz[1]],
        [rotation[2][0], rotation[2][1], rotation[2][2], xyz[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def apply_tf(tf: list[list[float]], xyz: list[float]) -> list[float]:
    value = xyz + [1.0]
    return [sum(tf[row][column] * value[column] for column in range(4)) for row in range(3)]


def stl_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if len(data) >= 84:
        triangles = struct.unpack_from("<I", data, 80)[0]
        if 84 + triangles * 50 == len(data):
            lower = [float("inf")] * 3
            upper = [float("-inf")] * 3
            offset = 84
            for _ in range(triangles):
                for vertex in range(3):
                    xyz = struct.unpack_from("<fff", data, offset + 12 + vertex * 12)
                    lower = [min(lower[i], xyz[i]) for i in range(3)]
                    upper = [max(upper[i], xyz[i]) for i in range(3)]
                offset += 50
            return {
                "format": "binary",
                "bytes": len(data),
                "triangles": triangles,
                "bounds_m": {"min": lower, "max": upper, "extent": [upper[i] - lower[i] for i in range(3)]},
                "sha256": digest,
            }
    return {"format": "unknown_or_ascii", "bytes": len(data), "triangles": None, "sha256": digest}


def git_commit(repo: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def issue(code: str, severity: str, message: str, evidence: Any = None) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code, "severity": severity, "message": message}
    if evidence is not None:
        value["evidence"] = evidence
    return value


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# CSDog URDF 静态审计",
        "",
        f"- 总门禁：**{report['gate']['status']}**",
        f"- 结构门禁：**{report['gate']['structure_status']}**",
        f"- 仿真就绪门禁：**{report['gate']['simulation_readiness_status']}**",
        f"- 实机部署门禁：**{report['gate']['hardware_deployment_status']}**",
        f"- Git commit：`{report['git_commit']}`",
        f"- URDF：`{report['urdf']}`",
        f"- link / revolute joint：{summary['link_count']} / {summary['revolute_joint_count']}",
        f"- 总质量：{summary['total_mass_kg']:.8f} kg",
        f"- 零位形整机质心：`{summary['zero_pose_center_of_mass_m']}` m",
        f"- 零位形足底球心高度差：{summary['zero_pose_foot_height_spread_m']:.8f} m",
        f"- mesh：{summary['mesh_file_count']} 个，collision 三角形合计 {summary['collision_triangle_count']}",
        "",
        "## 已证实问题",
        "",
    ]
    confirmed = [item for item in report["issues"] if item["severity"] in {"error", "review_required"}]
    if not confirmed:
        lines.append("- 无。")
    for item in confirmed:
        lines.append(f"- `{item['code']}` [{item['severity']}] {item['message']}")
    hardware_blocks = [item for item in report["issues"] if item["severity"] == "hardware_blocker"]
    lines += ["", "## 实机部署阻断项", ""]
    if not hardware_blocks:
        lines.append("- 无。")
    for item in hardware_blocks:
        lines.append(f"- `{item['code']}` [{item['severity']}] {item['message']}")
    lines += ["", "## 警告与待测试假设", ""]
    warnings = [item for item in report["issues"] if item["severity"] in {"warning", "hypothesis"}]
    if not warnings:
        lines.append("- 无。")
    for item in warnings:
        lines.append(f"- `{item['code']}` [{item['severity']}] {item['message']}")
    lines += ["", "## 关节顺序与限位", "", "| # | 名称 | parent → child | axis | lower | upper | effort | velocity |", "|---:|---|---|---|---:|---:|---:|---:|"]
    for index, joint in enumerate(report["joints"]):
        limit = joint["limit"]
        lines.append(
            f"| {index} | `{joint['name']}` | `{joint['parent']}` → `{joint['child']}` | "
            f"`{joint['axis']}` | {limit['lower']} | {limit['upper']} | {limit['effort']} | {limit['velocity']} |"
        )
    lines += ["", "## 门禁结论", "", report["gate"]["reason"], ""]
    return "\n".join(lines)


def audit(args: argparse.Namespace) -> dict[str, Any]:
    urdf = args.urdf.resolve()
    root = ET.parse(urdf).getroot()
    links = root.findall("link")
    joints_xml = root.findall("joint")
    link_names = [node.attrib["name"] for node in links]
    issues: list[dict[str, Any]] = []
    joints: list[dict[str, Any]] = []
    child_to_joint: dict[str, dict[str, Any]] = {}

    for node in joints_xml:
        origin = node.find("origin")
        limit_node = node.find("limit")
        axis = floats(node.find("axis").attrib.get("xyz"), 3) if node.find("axis") is not None else [1.0, 0.0, 0.0]
        limit = {
            key: float(limit_node.attrib[key]) if limit_node is not None and key in limit_node.attrib else None
            for key in ("lower", "upper", "effort", "velocity")
        }
        value = {
            "name": node.attrib["name"],
            "type": node.attrib.get("type"),
            "parent": node.find("parent").attrib["link"],
            "child": node.find("child").attrib["link"],
            "origin_xyz": floats(origin.attrib.get("xyz", "0 0 0"), 3) if origin is not None else [0.0] * 3,
            "origin_rpy": floats(origin.attrib.get("rpy", "0 0 0"), 3) if origin is not None else [0.0] * 3,
            "axis": axis,
            "axis_norm": math.sqrt(sum(component * component for component in axis)),
            "limit": limit,
        }
        joints.append(value)
        child_to_joint[value["child"]] = value

    children = {joint["child"] for joint in joints}
    roots = sorted(set(link_names) - children)
    if len(roots) != 1:
        issues.append(issue("URDF_ROOT_COUNT", "error", f"expected one root link, found {roots}"))
    if len(link_names) != len(set(link_names)):
        issues.append(issue("DUPLICATE_LINK_NAMES", "error", "link names are not unique"))
    joint_names = [joint["name"] for joint in joints]
    if len(joint_names) != len(set(joint_names)):
        issues.append(issue("DUPLICATE_JOINT_NAMES", "error", "joint names are not unique"))

    expected = json.loads(args.expectations.read_text(encoding="utf-8")) if args.expectations else {}
    expected_joints = expected.get("actuated_joint_names")
    revolute = [joint for joint in joints if joint["type"] == "revolute"]
    if expected_joints and [joint["name"] for joint in revolute] != expected_joints:
        issues.append(issue("JOINT_ORDER_MISMATCH", "error", "revolute joint names/order differ from manifest", {"expected": expected_joints, "actual": [joint["name"] for joint in revolute]}))
    if expected.get("link_names") and link_names != expected["link_names"]:
        issues.append(issue("LINK_ORDER_MISMATCH", "error", "link names/order differ from manifest", {"expected": expected["link_names"], "actual": link_names}))
    expected_feet = expected.get("foot_link_names", [])
    for foot_name in expected_feet:
        foot = next((node for node in links if node.attrib["name"] == foot_name), None)
        if foot is None:
            issues.append(issue("MISSING_FOOT_LINK", "error", f"expected foot link does not exist: {foot_name}"))
        elif not foot.findall("collision"):
            issues.append(issue("FOOT_WITHOUT_COLLISION", "error", f"expected foot link has no collision geometry: {foot_name}"))
    for joint in revolute:
        if abs(joint["axis_norm"] - 1.0) > 1.0e-4:
            issues.append(issue("JOINT_AXIS_NOT_UNIT", "error", f"{joint['name']} axis norm is {joint['axis_norm']}"))
        limit = joint["limit"]
        if any(limit[key] is None for key in ("lower", "upper", "effort", "velocity")):
            issues.append(issue("JOINT_LIMIT_INCOMPLETE", "error", f"{joint['name']} has incomplete limits"))
        elif limit["lower"] >= limit["upper"] or limit["effort"] <= 0 or limit["velocity"] <= 0:
            issues.append(issue("JOINT_LIMIT_INVALID", "error", f"{joint['name']} has invalid limits", limit))

    limit_tuples = {(joint["limit"]["lower"], joint["limit"]["upper"], joint["limit"]["effort"], joint["limit"]["velocity"]) for joint in revolute}
    if len(limit_tuples) == 1 and revolute:
        issues.append(issue("UNIFORM_TEMPLATE_LIMITS", "review_required", "all 12 joints use one identical limit tuple; mechanical/electrical provenance is not recorded", next(iter(limit_tuples))))
    if any(abs(joint["limit"]["lower"] + math.pi) < 0.01 and abs(joint["limit"]["upper"] - math.pi) < 0.01 for joint in revolute):
        issues.append(issue("FULL_ROTATION_POSITION_LIMITS", "review_required", "revolute joints use approximately ±pi; self-collision is disabled and real hard stops are unverified"))
    if not expected.get("simulation_parameters_verified", False):
        issues.append(issue("SIMULATION_PARAMETERS_UNVERIFIED", "review_required", "simulation joint limits and actuator bounds lack an approved, traceable profile"))
    simulation_profile = expected.get("simulation_profile")
    if simulation_profile and not (args.repo.resolve() / simulation_profile).is_file():
        issues.append(issue("SIMULATION_PROFILE_MISSING", "error", f"simulation profile does not exist: {simulation_profile}"))
    if not expected.get("hardware_parameters_verified", False):
        issues.append(issue("HARDWARE_LIMITS_UNVERIFIED", "hardware_blocker", "continuous torque and assembled mechanical hard stops are unverified; simulation results must not be deployed to hardware"))

    mesh_records: dict[str, dict[str, Any]] = {}
    visual_meshes: list[str] = []
    collision_meshes: list[str] = []
    masses: dict[str, float] = {}
    inertial_com: dict[str, list[float]] = {}
    for link in links:
        name = link.attrib["name"]
        inertial = link.find("inertial")
        if inertial is None or inertial.find("mass") is None or inertial.find("inertia") is None:
            issues.append(issue("MISSING_INERTIAL", "error", f"{name} has no complete inertial block"))
            continue
        mass = float(inertial.find("mass").attrib["value"])
        masses[name] = mass
        inertial_origin = inertial.find("origin")
        inertial_com[name] = floats(inertial_origin.attrib.get("xyz", "0 0 0"), 3) if inertial_origin is not None else [0.0] * 3
        inertia = inertial.find("inertia").attrib
        ixx, iyy, izz = (float(inertia[key]) for key in ("ixx", "iyy", "izz"))
        ixy, ixz, iyz = (float(inertia.get(key, 0.0)) for key in ("ixy", "ixz", "iyz"))
        determinant = ixx * iyy * izz + 2 * ixy * ixz * iyz - ixx * iyz**2 - iyy * ixz**2 - izz * ixy**2
        if mass <= 0 or ixx <= 0 or ixx * iyy - ixy**2 <= 0 or determinant <= 0:
            issues.append(issue("INERTIA_NOT_POSITIVE_DEFINITE", "error", f"{name} mass/inertia is not positive definite"))
        if ixx + iyy < izz or ixx + izz < iyy or iyy + izz < ixx:
            issues.append(issue("INERTIA_TRIANGLE_VIOLATION", "warning", f"{name} diagonal inertia violates rigid-body triangle inequality"))
        for role in ("visual", "collision"):
            for geometry in link.findall(f"{role}/geometry"):
                mesh = geometry.find("mesh")
                if mesh is None:
                    continue
                filename = mesh.attrib["filename"]
                (visual_meshes if role == "visual" else collision_meshes).append(filename)
                path = (urdf.parent / filename).resolve()
                if not path.is_file():
                    issues.append(issue("MISSING_MESH", "error", f"{role} mesh does not exist: {filename}"))
                elif filename not in mesh_records:
                    mesh_records[filename] = stl_info(path)

    shared = sorted(set(visual_meshes) & set(collision_meshes))
    if shared:
        issues.append(issue("VISUAL_COLLISION_MESH_REUSE", "warning", f"all {len(shared)} collision meshes are also used as visuals; independent low-poly collision provenance is absent", shared))
    high_poly = {name: data["triangles"] for name, data in mesh_records.items() if data.get("triangles") and data["triangles"] > args.max_collision_triangles and name in collision_meshes}
    if high_poly:
        issues.append(issue("HIGH_POLY_COLLISION", "review_required", f"{len(high_poly)} collision meshes exceed {args.max_collision_triangles} triangles", high_poly))

    link_tf: dict[str, list[list[float]]] = {}
    if len(roots) == 1:
        link_tf[roots[0]] = transform([0.0] * 3, [0.0] * 3)
        unresolved = joints.copy()
        while unresolved:
            progress = False
            for joint in unresolved[:]:
                if joint["parent"] in link_tf:
                    link_tf[joint["child"]] = matmul(link_tf[joint["parent"]], transform(joint["origin_xyz"], joint["origin_rpy"]))
                    unresolved.remove(joint)
                    progress = True
            if not progress:
                issues.append(issue("KINEMATIC_TREE_DISCONNECTED", "error", "joint graph contains a cycle or disconnected component"))
                break
    total_mass = sum(masses.values())
    weighted_com = [0.0] * 3
    if total_mass > 0 and all(name in link_tf for name in masses):
        for name, mass in masses.items():
            world_com = apply_tf(link_tf[name], inertial_com[name])
            weighted_com = [weighted_com[i] + mass * world_com[i] for i in range(3)]
        weighted_com = [value / total_mass for value in weighted_com]

    zero_pose_foot_positions = {
        name: apply_tf(link_tf[name], [0.0, 0.0, 0.0])
        for name in expected_feet
        if name in link_tf
    }
    foot_heights = [position[2] for position in zero_pose_foot_positions.values()]
    foot_height_spread = max(foot_heights) - min(foot_heights) if foot_heights else 0.0
    max_foot_height_spread = expected.get("max_zero_pose_foot_height_spread_m")
    if max_foot_height_spread is not None and foot_height_spread > max_foot_height_spread:
        issues.append(
            issue(
                "ZERO_POSE_FOOT_HEIGHT_MISMATCH",
                "error",
                "zero-pose sole centers are not coplanar",
                {
                    "maximum_spread_m": max_foot_height_spread,
                    "actual_spread_m": foot_height_spread,
                    "positions_m": zero_pose_foot_positions,
                },
            )
        )

    if expected.get("total_mass_kg") is not None and abs(total_mass - expected["total_mass_kg"]) > expected.get("total_mass_tolerance_kg", 1.0e-6):
        issues.append(issue("TOTAL_MASS_MISMATCH", "error", "total mass differs from manifest", {"expected": expected["total_mass_kg"], "actual": total_mass}))
    issues.append(issue("COM_REQUIRES_DYNAMIC_VALIDATION", "hypothesis", "zero-pose COM is computed from URDF, but support polygon margin and loaded hardware COM still require simulation/CAD validation", weighted_com))
    issues.append(issue("CONTACT_PATCH_UNVERIFIED", "hypothesis", "mesh existence does not prove watertight foot collision, stable contact patches, or correct friction behavior"))

    structural_errors = [item for item in issues if item["severity"] == "error"]
    readiness_blocks = [item for item in issues if item["severity"] in {"error", "review_required"}]
    structure_status = "PASS" if not structural_errors else "FAIL"
    readiness_status = "PASS" if not readiness_blocks else "FAIL"
    hardware_status = "PASS" if expected.get("hardware_parameters_verified", False) and not structural_errors else "FAIL"
    status = "PASS" if structure_status == readiness_status == "PASS" else "FAIL"
    reason = "Static simulation gate passed; hardware deployment remains separately gated." if status == "PASS" else ("Static structure is valid, but simulation is blocked until every review_required item has traceable provenance." if structure_status == "PASS" else "Static structure is invalid; do not start simulation.")
    return {
        "schema_version": 1,
        "git_commit": git_commit(args.repo.resolve()),
        "urdf": str(urdf),
        "expectations": str(args.expectations.resolve()) if args.expectations else None,
        "gate": {
            "status": status,
            "structure_status": structure_status,
            "physics_readiness_status": readiness_status,
            "simulation_readiness_status": readiness_status,
            "hardware_deployment_status": hardware_status,
            "reason": reason,
        },
        "summary": {
            "root_links": roots,
            "link_count": len(links),
            "joint_count": len(joints),
            "revolute_joint_count": len(revolute),
            "total_mass_kg": total_mass,
            "zero_pose_center_of_mass_m": weighted_com,
            "zero_pose_foot_positions_m": zero_pose_foot_positions,
            "zero_pose_foot_height_spread_m": foot_height_spread,
            "mesh_file_count": len(mesh_records),
            "collision_triangle_count": sum(mesh_records[name].get("triangles") or 0 for name in set(collision_meshes) if name in mesh_records),
        },
        "links": link_names,
        "joints": joints,
        "meshes": mesh_records,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urdf", type=Path)
    parser.add_argument("--expectations", type=Path)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-collision-triangles", type=int, default=1000)
    args = parser.parse_args()
    report = audit(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report["gate"], ensure_ascii=False))
    return 0 if report["gate"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
