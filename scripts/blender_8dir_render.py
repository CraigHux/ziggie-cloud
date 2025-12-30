"""
Blender 8-Direction Sprite Renderer
====================================
Renders a 3D GLB model from 8 isometric directions for RTS game sprites.

Usage (CLI):
    blender --background --python blender_8dir_render.py -- --input model.glb --output ./sprites/

Directions (45 degree increments):
    0: South (S)      - Front view
    1: Southwest (SW)
    2: West (W)
    3: Northwest (NW)
    4: North (N)      - Back view
    5: Northeast (NE)
    6: East (E)
    7: Southeast (SE)

Output: 8 PNG files with transparency, named {basename}_dir{0-7}.png
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

    # Get imported objects (excluding camera and lights)
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


def setup_camera_isometric(distance: float = 10.0):
    """Create orthographic camera with isometric angle."""
    # Create camera
    bpy.ops.object.camera_add(location=(0, 0, 0))
    camera = bpy.context.object
    camera.name = "IsometricCamera"

    # Set to orthographic
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = distance * 1.5

    # Isometric angle: ~35.264 degrees from horizontal (arctan(1/sqrt(2)))
    # Standard isometric view
    iso_angle = math.radians(30)  # 30 degrees for RTS style

    camera.rotation_euler[0] = math.radians(90) - iso_angle  # Tilt down

    # Position camera
    camera.location = (0, -distance * math.cos(iso_angle), distance * math.sin(iso_angle))

    # Set as active camera
    bpy.context.scene.camera = camera

    return camera


def setup_lighting():
    """Create 3-point lighting setup."""
    # Key light (main)
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.object
    key_light.name = "KeyLight"
    key_light.data.energy = 3.0
    key_light.rotation_euler = (math.radians(45), math.radians(15), math.radians(45))

    # Fill light (softer, opposite side)
    bpy.ops.object.light_add(type='SUN', location=(-5, -5, 5))
    fill_light = bpy.context.object
    fill_light.name = "FillLight"
    fill_light.data.energy = 1.5
    fill_light.rotation_euler = (math.radians(60), math.radians(-15), math.radians(-45))

    # Rim light (back)
    bpy.ops.object.light_add(type='SUN', location=(0, 5, 8))
    rim_light = bpy.context.object
    rim_light.name = "RimLight"
    rim_light.data.energy = 2.0
    rim_light.rotation_euler = (math.radians(30), 0, math.radians(180))


def setup_render_settings(resolution: int = 512):
    """Configure render settings for sprite output."""
    scene = bpy.context.scene

    # Resolution
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100

    # PNG with transparency
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15

    # Transparent background
    scene.render.film_transparent = True

    # Use Eevee for fast rendering (or Cycles for higher quality)
    scene.render.engine = 'BLENDER_EEVEE'  # Blender 5.0 uses BLENDER_EEVEE

    # Eevee settings for quality (check for attribute existence for compatibility)
    if hasattr(scene, 'eevee'):
        if hasattr(scene.eevee, 'taa_render_samples'):
            scene.eevee.taa_render_samples = 64


def render_8_directions(camera, model_objects, output_dir: str, basename: str, resolution: int = 512):
    """Render model from 8 directions by rotating the model."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Direction labels for reference
    directions = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']

    # Find model center for rotation
    min_coords, max_coords = get_model_bounds(model_objects)
    center = [(min_coords[i] + max_coords[i]) / 2 for i in range(3)]

    # Create empty at center to parent objects for rotation
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
    pivot = bpy.context.object
    pivot.name = "RotationPivot"

    # Parent all model objects to pivot
    for obj in model_objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = pivot
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    rendered_files = []

    for i, direction in enumerate(directions):
        # Rotate pivot (45 degrees per direction)
        pivot.rotation_euler[2] = math.radians(i * 45)

        # Update scene
        bpy.context.view_layer.update()

        # Set output path
        output_file = output_path / f"{basename}_dir{i}_{direction}.png"
        bpy.context.scene.render.filepath = str(output_file)

        # Render
        print(f"Rendering direction {i} ({direction})...")
        bpy.ops.render.render(write_still=True)

        rendered_files.append(str(output_file))
        print(f"  Saved: {output_file}")

    return rendered_files


def auto_frame_camera(camera, objects):
    """Adjust camera to frame all objects properly."""
    # Calculate bounds
    min_coords, max_coords = get_model_bounds(objects)

    # Calculate size
    size = max(
        max_coords[0] - min_coords[0],
        max_coords[1] - min_coords[1],
        max_coords[2] - min_coords[2]
    )

    # Adjust orthographic scale with padding
    camera.data.ortho_scale = size * 2.0

    # Calculate center
    center = [(min_coords[i] + max_coords[i]) / 2 for i in range(3)]

    # Move camera target to center
    iso_angle = math.radians(30)
    distance = size * 3

    camera.location = (
        center[0],
        center[1] - distance * math.cos(iso_angle),
        center[2] + distance * math.sin(iso_angle)
    )

    # Point camera at center
    direction = Vector(center) - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()


def main():
    """Main function - parse args and run renderer."""
    # Get arguments after "--"
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="Render 3D model from 8 isometric directions")
    parser.add_argument("--input", "-i", required=True, help="Input GLB/GLTF file")
    parser.add_argument("--output", "-o", default="./sprites", help="Output directory")
    parser.add_argument("--resolution", "-r", type=int, default=512, help="Output resolution (default: 512)")
    parser.add_argument("--name", "-n", help="Base name for output files (default: input filename)")

    args = parser.parse_args(argv)

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    # Base name for outputs
    basename = args.name or input_path.stem

    print(f"=" * 60)
    print(f"Blender 8-Direction Sprite Renderer")
    print(f"=" * 60)
    print(f"Input:      {args.input}")
    print(f"Output:     {args.output}")
    print(f"Resolution: {args.resolution}x{args.resolution}")
    print(f"Base name:  {basename}")
    print(f"=" * 60)

    # Clear existing scene
    print("\nClearing scene...")
    clear_scene()

    # Import model
    print(f"Importing model: {args.input}")
    model_objects = import_glb(str(input_path.absolute()))
    print(f"  Imported {len(model_objects)} objects")

    # Setup camera
    print("Setting up isometric camera...")
    camera = setup_camera_isometric()

    # Auto-frame the model
    print("Framing model...")
    mesh_objects = [obj for obj in model_objects if obj.type == 'MESH']
    if mesh_objects:
        auto_frame_camera(camera, mesh_objects)

    # Setup lighting
    print("Setting up lighting...")
    setup_lighting()

    # Configure render settings
    print(f"Configuring render ({args.resolution}x{args.resolution})...")
    setup_render_settings(args.resolution)

    # Render all 8 directions
    print("\nRendering 8 directions...")
    rendered_files = render_8_directions(
        camera,
        mesh_objects,
        args.output,
        basename,
        args.resolution
    )

    print(f"\n{'=' * 60}")
    print(f"COMPLETE: Rendered {len(rendered_files)} sprites")
    for f in rendered_files:
        print(f"  - {f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
