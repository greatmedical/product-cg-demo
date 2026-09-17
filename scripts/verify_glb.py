# SPDX-License-Identifier: GPL-3.0-or-later
"""Read back one original GLB in a fresh Blender scene; do not remove data."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
source, destination = map(Path, args)
if destination.exists():
    raise SystemExit('Use a new report path; existing files are preserved.')
scene = bpy.data.scenes.new('GLB_Verification')
bpy.context.window.scene = scene
bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
meshes = [obj for obj in scene.objects if obj.type == 'MESH']
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
assert meshes and points, 'GLB contains no mesh'
assert not any(obj.type in {'LIGHT', 'CAMERA'} for obj in scene.objects), 'Product includes studio objects'
assert all(len(obj.data.materials) > 0 for obj in meshes), 'Missing product material'
materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
report = {
    'blender_version': bpy.app.version_string,
    'source_file': source.name,
    'mesh_count': len(meshes),
    'mesh_names': sorted(obj.name for obj in meshes),
    'materials': materials,
    'triangles': sum(sum(len(poly.vertices) - 2 for poly in obj.data.polygons) for obj in meshes),
    'bounds_min': [min(point[axis] for point in points) for axis in range(3)],
    'bounds_max': [max(point[axis] for point in points) for axis in range(3)],
    'cameras': 0,
    'lights': 0,
    'checks_passed': ['imports_in_blender_4_4', 'mesh_present', 'materials_present', 'no_studio_camera_or_light'],
    'not_tested': ['Unreal Engine import', 'manufacturing accuracy', 'customer reference fidelity'],
}
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
