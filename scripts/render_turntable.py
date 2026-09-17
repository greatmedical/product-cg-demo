# SPDX-License-Identifier: GPL-3.0-or-later
"""Render a saved original animated scene to a new directory of PNGs."""
import bpy
import json
import sys
import time
from pathlib import Path

args = sys.argv[sys.argv.index('--') + 1:]
output = Path(args[0]).resolve()
if output.exists():
    raise SystemExit('Use a new output directory; existing files are preserved.')
output.mkdir(parents=True)
scene = bpy.context.scene
assert scene.camera, 'No camera in the saved active scene'
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 720
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 144
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = str(output / 'frame-')
scene.render.use_file_extension = True
scene.render.use_overwrite = False
started = time.monotonic()
bpy.ops.render.render(animation=True)
frames = sorted(output.glob('frame-*.png'))
assert len(frames) == 144, f'Expected 144 frames, got {len(frames)}'
(output / 'render-report.json').write_text(json.dumps({
    'blender_version': bpy.app.version_string,
    'resolution': [720, 720],
    'fps': 24,
    'frames': len(frames),
    'duration_seconds': 6,
    'render_elapsed_seconds': round(time.monotonic() - started, 2),
    'measurement_scope': 'Animation render only; not modeling, review, labor or total cost.'
}, indent=2) + '\n')
