"""Explicit, auditable mesh collider setup for isolated posture diagnostics only.

No import side effects; Omniverse imports are local to simulator-only functions.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np


def normalize_mesh_colliders(stage, robot_path, quality="default"):
    from pxr import Usd, UsdGeom, UsdPhysics, PhysxSchema
    if quality not in ("default", "fine"):
        raise ValueError("Unknown cooking quality")
    root = stage.GetPrimAtPath(robot_path)
    rows = []
    paths = [str(p.GetPath()) for p in Usd.PrimRange(root, Usd.TraverseInstanceProxies())
             if p.HasAPI(UsdPhysics.CollisionAPI) and p.IsA(UsdGeom.Xform)]
    for path in paths:
        parent = stage.GetPrimAtPath(path)
        ancestors, current = [], parent
        while current and current.GetPath() != root.GetPath():
            if current.IsInstance():
                ancestors.append(str(current.GetPath()))
            current = current.GetParent()
        for instance_path in reversed(ancestors):
            stage.GetPrimAtPath(instance_path).SetInstanceable(False)
        parent = stage.GetPrimAtPath(path)
        meshes = [p for p in Usd.PrimRange(parent, Usd.TraverseInstanceProxies()) if p.IsA(UsdGeom.Mesh)]
        if not meshes:
            raise ValueError(f"Collision Xform has no mesh: {parent.GetPath()}")
        approximation = UsdPhysics.MeshCollisionAPI(parent).GetApproximationAttr().Get()
        if approximation != "convexDecomposition":
            raise ValueError(f"Unexpected source approximation: {approximation}")
        enabled = UsdPhysics.CollisionAPI(parent).GetCollisionEnabledAttr().Get()
        for mesh in meshes:
            UsdPhysics.CollisionAPI.Apply(mesh).CreateCollisionEnabledAttr(enabled)
            UsdPhysics.MeshCollisionAPI.Apply(mesh).CreateApproximationAttr(approximation)
            for attr in parent.GetAuthoredAttributes():
                if attr.GetName().startswith("physxCollision:"):
                    PhysxSchema.PhysxCollisionAPI.Apply(mesh)
                    mesh.CreateAttribute(attr.GetName(), attr.GetTypeName()).Set(attr.Get())
            api = PhysxSchema.PhysxConvexDecompositionCollisionAPI.Apply(mesh)
            settings = {} if quality == "default" else {
                "ErrorPercentage": .5, "VoxelResolution": 2000000, "MaxConvexHulls": 64,
                "HullVertexLimit": 64, "MinThickness": .00025, "ShrinkWrap": True}
            for key, value in settings.items():
                getattr(api, "Create"+key+"Attr")(value)
            rows.append({"old_parent": str(parent.GetPath()), "mesh": str(mesh.GetPath()),
                         "approximation": approximation, "quality": quality, "settings": settings})
        parent.RemoveAPI(UsdPhysics.CollisionAPI)
        parent.RemoveAPI(UsdPhysics.MeshCollisionAPI)
    if not rows:
        raise ValueError("No collider Xforms normalized; refuse to assume unchanged input format")
    return {"recipe": "explicit_mesh_"+quality+"_v1", "converted": rows,
            "scope": "Moves collision APIs to mesh geometry in a separate diagnostic scene; no source URDF changes"}


def extract_cooked_meshes(stage, robot_path, urdf, output):
    """Export PhysX requested hulls in original URDF coordinates before reset."""
    import trimesh
    from scipy.spatial import cKDTree
    from pxr import Usd, UsdGeom, UsdPhysics, UsdUtils, PhysicsSchemaTools
    from omni.physx import get_physx_cooking_interface
    from omni.physx.bindings._physx import PhysxCollisionRepresentationResult
    from .posture_preflight import PostureGeometry, origin_transform
    from .calibration import ASSET
    from .contracts import JOINT_NAMES
    from .training import file_hash
    xml = ET.parse(urdf).getroot()
    links = {n.get("name") for n in xml.findall("link")}
    frames = PostureGeometry(ASSET/"robot_sim.urdf", JOINT_NAMES).world_frames(np.zeros(12), 1.)
    for frame in frames.values():
        frame[2, 3] -= 1.
    prims = list(Usd.PrimRange(stage.GetPrimAtPath(robot_path), Usd.TraverseInstanceProxies()))
    base = next(p for p in prims if p.GetName() == "base" and p.HasAPI(UsdPhysics.RigidBodyAPI))
    def mat(prim):
        return np.array(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default())).T
    base_inv = np.linalg.inv(mat(base))
    stage_id = UsdUtils.StageCache.Get().Insert(stage).ToLongInt()
    cooking = get_physx_cooking_interface()
    records = []
    for prim in prims:
        if not prim.HasAPI(UsdPhysics.CollisionAPI):
            continue
        body = prim
        while body and body.GetName() not in links:
            body = body.GetParent()
        if not body:
            raise ValueError("Unresolved collision owner")
        link = body.GetName()
        local = np.linalg.inv(frames[link])@base_inv@mat(prim)
        if prim.IsA(UsdGeom.Mesh):
            points = np.array(UsdGeom.Mesh(prim).GetPointsAttr().Get())@local[:3, :3].T+local[:3, 3]
            errors = []
            for collision in xml.find(f"link[@name='{link}']").findall("collision"):
                node = collision.find("geometry/mesh")
                if node is None:
                    continue
                path = Path(node.get("filename"))
                if not path.is_absolute():
                    path = Path(urdf).parent/path
                vertices = np.asarray(trimesh.load(path, process=False).vertices)
                vertices *= np.array([float(v) for v in node.get("scale", "1 1 1").split()])
                t = origin_transform(collision.find("origin"))
                vertices = vertices@t[:3, :3].T+t[:3, 3]
                errors.append(max(cKDTree(vertices).query(points)[0].max(), cKDTree(points).query(vertices)[0].max()))
            error = float(min(errors))
            if error > 2e-6:
                raise ValueError(f"USD/URDF source-frame mismatch {link}: {error}")
            hulls, statuses = [], []
            def ready(result, convexes):
                statuses.append(str(result))
                if result != PhysxCollisionRepresentationResult.RESULT_VALID:
                    return
                for hull in convexes:
                    vertices = np.array([[v.x, v.y, v.z] for v in hull.vertices])
                    vertices = vertices@local[:3, :3].T+local[:3, 3]
                    faces = []
                    for polygon in hull.polygons:
                        indices = list(hull.indices[polygon.index_base:polygon.index_base+polygon.num_vertices])
                        faces += [[int(indices[0]), int(indices[i]), int(indices[i+1])] for i in range(1, len(indices)-1)]
                    hulls.append({"vertices": vertices.tolist(), "faces": faces})
            cooking.request_convex_collision_representation(stage_id=stage_id,
                collision_prim_id=PhysicsSchemaTools.sdfPathToInt(str(prim.GetPath())),
                run_asynchronously=False, on_result=ready)
            if not hulls:
                raise RuntimeError(f"Cooking failed for {prim.GetPath()}: {statuses}")
            records.append({"link": link, "usd_path": str(prim.GetPath()), "kind": "convex_meshes",
                "source_frame_error_m": error, "source_points_in_urdf_link_m": points.tolist(), "hulls": hulls})
            print("COOKED", link, len(hulls), "frame error", error, flush=True)
        elif prim.IsA(UsdGeom.Sphere):
            records.append({"link": link, "kind": "sphere", "radius_m": float(UsdGeom.Sphere(prim).GetRadiusAttr().Get()),
                            "transform_in_urdf_link": local.tolist()})
        else:
            raise ValueError("Unsupported explicit collider "+str(prim.GetPath()))
    if len(records) != 21:
        raise ValueError(f"Expected 17 source mesh colliders and 4 sole spheres, got {len(records)}")
    result = {"schema": "csdog_cooked_convex_audit_v1", "urdf_sha256": file_hash(urdf),
        "module_sha256": file_hash(__file__), "shapes": records,
        "scope": "PhysX cooked hull representation in original URDF frames, checked against input mesh vertices"}
    Path(output).write_text(json.dumps(result)+"\n")
    return {"mesh_count": 17, "sole_sphere_count": 4, "hull_count": sum(len(r.get("hulls", [])) for r in records),
            "max_source_frame_error_m": max(r.get("source_frame_error_m", 0.) for r in records)}
