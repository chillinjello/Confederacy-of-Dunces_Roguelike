from typing import Tuple

import numpy as np

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype( # dtype creates data that numpy can use (like a struct)
    [
        ("ch", np.int32), # character: Unicode codepoint.
        ("fg", "3B"), # foreground color: 3 unsigned bytes, for RGB colors.
        ("bg", "3B"), # background color
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool), # True if this tile can be walked over.
        ("transparent", np.bool), # True if this tile doesn't block FOV.
        ("dark", graphic_dt), # Graphics for when this tile is not in FOV.
        ("light", graphic_dt), # Graphics for whwen the tile is in FOV.
    ]
)

def new_tile(
    *, # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = lambda color: new_tile(
    walkable=True, 
    transparent=True, 
    dark=(ord("."), (max(0, color[0] - 100), max(0, color[1] - 100), max(0, color[2] - 100)), (0, 0, 0)),
    light=(ord("."), (color[0], color[1], color[2]), (0, 0, 0)),
)
wall = lambda color: new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (max(0, color[0] - 100), max(0, color[1] - 100), max(0, color[2] - 100)), (0, 0, 0)),
    light=(ord("#"), (color[0], color[1], color[2]), (0, 0, 0)),
)
down_stairs = lambda color: new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (max(0, color[0] - 100), max(0, color[1] - 100), max(0, color[2] - 100)), (0, 0, 0)),
    light=(ord(">"), (color[0], color[1], color[2]), (0, 0, 0)),
)