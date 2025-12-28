"""
Blender 8-Direction Sprite Renderer for MeowPing RTS
Renders 3D models as isometric sprites from 8 cardinal/ordinal directions

Usage:
    blender model.blend --background --python render_8_directions.py -- --output sprites/ [--resolution 128]

Directions:
    N(0), NE(45), E(90), SE(135), S(180), SW(225), W(270), NW(315)

Author: VULCAN (Elite Art Team - VFX Artist)
Project: Ziggie AI Game Dev System / MeowPing RTS
"""

import bpy
import math
import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional


# 8 Standard RTS Directions (clockwise from North)
DIRECTIONS = [
    ("N", 0),      # North - facing away from camera
    ("NE", 45),    # Northeast
    ("E", 90),     # East - facing right
    ("SE", 135),   # Southeast
    ("S", 180),    # South - facing toward camera
    ("SW", 225),   # Southwest
    ("W", 270),    # West - facing left
    ("NW", 315),   # Northwest
]

# Faction color presets (HSV hue shifts)
FACTION_COLORS = {
    "neutral": 0.0,     # No shift (original colors)
    "red": 0.0,         # Red faction (base)
    "blue": 0.55,       # Blue faction (180 degree hue shift)
    "green": 0.33,      # Green faction (120 degree hue shift)
    "gold": 0.12,       # Gold/Yellow faction
    "purple": 0.75,     # Purple faction
    "cyan": 0.50,       # Cyan faction
    "orange": 0.08,     # Orange faction
}


def setup_render_settings(resolution: int = 128, transparent: bool = True) -> None:
    """Configure render settings for sprite output with transparency"""
    scene = bpy.context.scene

    # Resolution settings
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100

    # Transparent background for sprite extraction
    scene.render.film_transparent = transparent

    # PNG output with RGBA
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.image_settings.compression = 15

    # Use EEVEE for fast, consistent rendering
    scene.render.engine = 'BLENDER_EEVEE'

    # Anti-aliasing samples
    if hasattr(scene, 'eevee'):
        scene.eevee.taa_render_samples = 64

    # Color management for consistent output
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    print(f"[VULCAN] Render settings: {resolution}x{resolution}, transparent={transparent}, engine=EEVEE")


def setup_isometric_camera(
    distance: float = 10.0,
    elevation_angle: float = 30.0,
    ortho_scale: float = 6.0
) -> bpy.types.Object:
    """
    Set up orthographic camera for isometric view

    Args:
        distance: Camera distance from origin
        elevation_angle: Angle above horizontal (30 for isometric, 45 for dimetric)
        ortho_scale: Orthographic scale (zoom level)

    Returns:
        Camera object
    """
    # Create or get camera
    if 'SpriteCamera' in bpy.data.objects:
        camera = bpy.data.objects['SpriteCamera']
    else:
        camera_data = bpy.data.cameras.new('SpriteCamera')
        camera = bpy.data.objects.new('SpriteCamera', camera_data)
        bpy.context.scene.collection.objects.link(camera)

    # Set as active camera
    bpy.context.scene.camera = camera

    # Configure orthographic projection
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = ortho_scale

    # Position camera for isometric view
    # Standard RTS isometric: 30-degree elevation, 45-degree rotation
    elev_rad = math.radians(elevation_angle)

    camera.location.x = distance * math.cos(elev_rad) * 0.707  # cos(45)
    camera.location.y = -distance * math.cos(elev_rad) * 0.707
    camera.location.z = distance * math.sin(elev_rad)

    # Point camera at origin
    # Rotation: 60 degrees X (look down), 0 Y, 45 degrees Z (isometric angle)
    camera.rotation_euler = (
        math.radians(90 - elevation_angle),  # X rotation
        0,                                    # Y rotation
        math.radians(45)                      # Z rotation
    )

    print(f"[VULCAN] Camera: ortho_scale={ortho_scale}, elevation={elevation_angle}deg, distance={distance}")
    return camera


def setup_lighting() -> None:
    """Set up three-point lighting for consistent sprite rendering"""
    # Remove existing lights
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Key light (main light, warm)
    key_light_data = bpy.data.lights.new('KeyLight', 'SUN')
    key_light_data.energy = 1.5
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new('KeyLight', key_light_data)
    bpy.context.scene.collection.objects.link(key_light)
    key_light.location = (5, -5, 10)
    key_light.rotation_euler = (math.radians(45), 0, math.radians(45))

    # Fill light (softer, cool)
    fill_light_data = bpy.data.lights.new('FillLight', 'SUN')
    fill_light_data.energy = 0.5
    fill_light_data.color = (0.95, 0.95, 1.0)
    fill_light = bpy.data.objects.new('FillLight', fill_light_data)
    bpy.context.scene.collection.objects.link(fill_light)
    fill_light.location = (-5, 5, 8)
    fill_light.rotation_euler = (math.radians(45), 0, math.radians(-135))

    # Back light (rim light for separation)
    back_light_data = bpy.data.lights.new('BackLight', 'SUN')
    back_light_data.energy = 0.8
    back_light_data.color = (1.0, 1.0, 1.0)
    back_light = bpy.data.objects.new('BackLight', back_light_data)
    bpy.context.scene.collection.objects.link(back_light)
    back_light.location = (0, 5, 5)
    back_light.rotation_euler = (math.radians(30), 0, math.radians(180))

    print("[VULCAN] Three-point lighting configured")


def find_model_object(model_name: Optional[str] = None) -> Optional[bpy.types.Object]:
    """
    Find the target model object to render

    Args:
        model_name: Optional name to search for (partial match)

    Returns:
        Model object or None
    """
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    if not mesh_objects:
        print("[VULCAN] ERROR: No mesh objects found in scene")
        return None

    if model_name:
        # Search for matching name
        for obj in mesh_objects:
            if model_name.lower() in obj.name.lower():
                print(f"[VULCAN] Found model: {obj.name}")
                return obj
        print(f"[VULCAN] WARNING: Model '{model_name}' not found, using first mesh")

    # Use first mesh object
    model = mesh_objects[0]
    print(f"[VULCAN] Using model: {model.name}")
    return model


def center_model(model: bpy.types.Object) -> None:
    """Center model at origin and set origin to center of mass"""
    bpy.ops.object.select_all(action='DESELECT')
    model.select_set(True)
    bpy.context.view_layer.objects.active = model

    # Set origin to geometry center
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    # Move to origin
    model.location = (0, 0, 0)

    print(f"[VULCAN] Model '{model.name}' centered at origin")


def render_8_directions(
    model: bpy.types.Object,
    output_dir: Path,
    model_name: str,
    resolution: int = 128
) -> List[Path]:
    """
    Render model from 8 directions

    Args:
        model: Blender object to render
        output_dir: Output directory path
        model_name: Base name for output files
        resolution: Render resolution

    Returns:
        List of rendered file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered_files = []

    # Store original rotation
    original_rotation = model.rotation_euler.z

    print(f"[VULCAN] Rendering 8 directions for '{model_name}'...")
    print("-" * 50)

    for direction_name, angle in DIRECTIONS:
        # Rotate model to face direction
        model.rotation_euler.z = math.radians(angle)

        # Set output path with direction name
        output_file = output_dir / f"{model_name}_{direction_name}.png"
        bpy.context.scene.render.filepath = str(output_file)

        # Render
        bpy.ops.render.render(write_still=True)
        rendered_files.append(output_file)

        print(f"  [{direction_name:2s}] {angle:3d}deg -> {output_file.name}")

    # Restore original rotation
    model.rotation_euler.z = original_rotation

    print("-" * 50)
    print(f"[VULCAN] Rendered {len(rendered_files)} direction sprites")

    return rendered_files


def render_animation_directions(
    model: bpy.types.Object,
    output_dir: Path,
    model_name: str,
    animation_name: str = "idle",
    frame_start: int = 1,
    frame_end: int = 4,
    resolution: int = 128
) -> List[Path]:
    """
    Render animation from 8 directions (for animated sprites)

    Args:
        model: Blender object to render
        output_dir: Output directory path
        model_name: Base name for output files
        animation_name: Animation name (idle, walk, attack, death)
        frame_start: First animation frame
        frame_end: Last animation frame
        resolution: Render resolution

    Returns:
        List of rendered file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered_files = []

    scene = bpy.context.scene
    original_rotation = model.rotation_euler.z

    print(f"[VULCAN] Rendering {animation_name} animation ({frame_end - frame_start + 1} frames) x 8 directions...")
    print("-" * 50)

    for direction_name, angle in DIRECTIONS:
        # Rotate model to face direction
        model.rotation_euler.z = math.radians(angle)

        # Render each frame
        for frame in range(frame_start, frame_end + 1):
            scene.frame_set(frame)
            frame_idx = frame - frame_start

            # Set output path: modelname_animation_direction_frame.png
            output_file = output_dir / f"{model_name}_{animation_name}_{direction_name}_{frame_idx:02d}.png"
            scene.render.filepath = str(output_file)

            # Render
            bpy.ops.render.render(write_still=True)
            rendered_files.append(output_file)

        print(f"  [{direction_name:2s}] {angle:3d}deg -> {frame_end - frame_start + 1} frames")

    # Restore original rotation
    model.rotation_euler.z = original_rotation

    print("-" * 50)
    print(f"[VULCAN] Rendered {len(rendered_files)} animation frames")

    return rendered_files


def parse_arguments() -> dict:
    """Parse command line arguments (after --)"""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    args = {
        "model": None,
        "output": "C:/Ziggie/assets/sprites/rendered",
        "resolution": 128,
        "animation": None,
        "frame_start": 1,
        "frame_end": 4,
    }

    i = 0
    while i < len(argv):
        if argv[i] == "--model" and i + 1 < len(argv):
            args["model"] = argv[i + 1]
            i += 2
        elif argv[i] == "--output" and i + 1 < len(argv):
            args["output"] = argv[i + 1]
            i += 2
        elif argv[i] == "--resolution" and i + 1 < len(argv):
            args["resolution"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--animation" and i + 1 < len(argv):
            args["animation"] = argv[i + 1]
            i += 2
        elif argv[i] == "--frame-start" and i + 1 < len(argv):
            args["frame_start"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--frame-end" and i + 1 < len(argv):
            args["frame_end"] = int(argv[i + 1])
            i += 2
        else:
            i += 1

    return args


def main():
    """Main rendering pipeline"""
    print("\n" + "=" * 60)
    print("VULCAN - 8-Direction Sprite Renderer")
    print("Elite Art Team - Ziggie AI Game Dev System")
    print("=" * 60 + "\n")

    # Parse arguments
    args = parse_arguments()

    print(f"Configuration:")
    print(f"  Model:      {args['model'] or 'auto-detect'}")
    print(f"  Output:     {args['output']}")
    print(f"  Resolution: {args['resolution']}x{args['resolution']}")
    if args['animation']:
        print(f"  Animation:  {args['animation']} (frames {args['frame_start']}-{args['frame_end']})")
    print()

    # Setup scene
    setup_render_settings(resolution=args["resolution"])
    setup_isometric_camera()
    setup_lighting()

    # Find model
    model = find_model_object(args["model"])
    if not model:
        print("[VULCAN] ERROR: No model found to render")
        return

    # Center model
    center_model(model)

    # Determine model name for output files
    model_name = args["model"] if args["model"] else model.name.lower().replace(" ", "_")
    output_dir = Path(args["output"])

    # Render
    if args["animation"]:
        rendered_files = render_animation_directions(
            model=model,
            output_dir=output_dir,
            model_name=model_name,
            animation_name=args["animation"],
            frame_start=args["frame_start"],
            frame_end=args["frame_end"],
            resolution=args["resolution"]
        )
    else:
        rendered_files = render_8_directions(
            model=model,
            output_dir=output_dir,
            model_name=model_name,
            resolution=args["resolution"]
        )

    print("\n" + "=" * 60)
    print(f"Rendering complete! {len(rendered_files)} files created")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
