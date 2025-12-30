"""
Blender GLB Thumbnail Generator
===============================
Renders a quick preview thumbnail of a 3D GLB model for Discord notifications.

Usage (CLI):
    blender --background --python blender_thumbnail.py -- --input model.glb --output preview.png

Output: Single PNG thumbnail (512x512 by default) with transparency.
"""

import bpy
import math
import sys
import os
from pathlib import Path
from mathutils import Vector


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def import_glb(filepath: str):
    """Import GLB/GLTF model."""
    bpy.ops.import_scene.gltf(filepath=filepath)
    imported = [obj for obj in bpy.context.selected_objects]
    if not imported:
        raise ValueError(f"No objects imported from {filepath}")
    return imported


def get_model_bounds(objects):
    """Calculate bounding box of all objects."""
    min_coords = [float('inf')] * 3
    max_coords = [float('-inf')] * 3

    for obj in objects:
        if obj.type == 'MESH':
            for corner in obj.bound_box:
                world_corner = obj.matrix_world @ Vector(corner)
                for i in range(3):
                    min_coords[i] = min(min_coords[i], world_corner[i])
                    max_coords[i] = max(max_coords[i], world_corner[i])

    return min_coords, max_coords


def setup_camera_for_thumbnail(objects):
    """Create orthographic camera with good viewing angle for thumbnail."""
    # Get model bounds
    min_coords, max_coords = get_model_bounds(objects)
    center = [(min_coords[i] + max_coords[i]) / 2 for i in range(3)]
    size = max(max_coords[i] - min_coords[i] for i in range(3))

    # Create camera
    bpy.ops.object.camera_add(location=(0, 0, 0))
    camera = bpy.context.object
    camera.name = "ThumbnailCamera"

    # Set to orthographic
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = size * 1.5

    # Position: front-top-right angle (good for thumbnails)
    distance = size * 2
    angle_h = math.radians(45)  # Horizontal rotation
    angle_v = math.radians(30)  # Vertical tilt

    camera.location = (
        center[0] + distance * math.sin(angle_h) * math.cos(angle_v),
        center[1] - distance * math.cos(angle_h) * math.cos(angle_v),
        center[2] + distance * math.sin(angle_v)
    )

    # Point at center
    direction = Vector(center) - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    bpy.context.scene.camera = camera
    return camera


def setup_lighting():
    """Create simple 3-point lighting."""
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.object
    key_light.data.energy = 3.0
    key_light.rotation_euler = (math.radians(45), 0, math.radians(45))

    # Fill light
    bpy.ops.object.light_add(type='SUN', location=(-5, -5, 5))
    fill_light = bpy.context.object
    fill_light.data.energy = 1.5
    fill_light.rotation_euler = (math.radians(60), 0, math.radians(-45))

    # Rim light
    bpy.ops.object.light_add(type='SUN', location=(0, 5, 8))
    rim_light = bpy.context.object
    rim_light.data.energy = 2.0
    rim_light.rotation_euler = (math.radians(-30), 0, math.radians(180))


def setup_render_settings(output_path: str, resolution: int = 512):
    """Configure render settings for thumbnail."""
    scene = bpy.context.scene

    # Resolution
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100

    # Output format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Transparent background
    scene.render.film_transparent = True

    # Use EEVEE for speed and compatibility (no OIDN dependency)
    # Note: Cycles with denoising fails on VPS builds without OpenImageDenoiser
    scene.render.engine = 'BLENDER_EEVEE'

    # EEVEE settings for quick, clean thumbnails
    if hasattr(scene, 'eevee'):
        scene.eevee.taa_render_samples = 32
        scene.eevee.use_soft_shadows = True

    scene.render.filepath = output_path


def render_thumbnail(input_path: str, output_path: str, resolution: int = 512):
    """Main function to render a thumbnail of a GLB model."""
    print(f"[Thumbnail] Rendering: {input_path}")
    print(f"[Thumbnail] Output: {output_path}")

    # Clear and import
    clear_scene()
    objects = import_glb(input_path)

    # Setup scene
    setup_camera_for_thumbnail(objects)
    setup_lighting()
    setup_render_settings(output_path, resolution)

    # Render
    bpy.ops.render.render(write_still=True)
    print(f"[Thumbnail] Complete: {output_path}")

    return output_path


def parse_args():
    """Parse command line arguments after '--'."""
    argv = sys.argv
    if "--" not in argv:
        return None, None, 512

    args = argv[argv.index("--") + 1:]

    input_path = None
    output_path = None
    resolution = 512

    i = 0
    while i < len(args):
        if args[i] in ['--input', '-i'] and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        elif args[i] in ['--output', '-o'] and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] in ['--resolution', '-r'] and i + 1 < len(args):
            resolution = int(args[i + 1])
            i += 2
        else:
            i += 1

    return input_path, output_path, resolution


if __name__ == "__main__":
    input_path, output_path, resolution = parse_args()

    if not input_path:
        print("Error: --input required")
        print("Usage: blender --background --python blender_thumbnail.py -- --input model.glb --output preview.png")
        sys.exit(1)

    if not output_path:
        # Default output: same name with _thumbnail.png
        output_path = str(Path(input_path).with_suffix('')) + "_thumbnail.png"

    render_thumbnail(input_path, output_path, resolution)
