from datasetParameters import *
import numpy as np


def get_worldgrid_from_pos(pos):
    grid_x = pos % (MAP_WIDTH * MAP_EXPAND)
    grid_y = pos // (MAP_WIDTH * MAP_EXPAND)
    return np.array([grid_x, grid_y], dtype=int)


def get_pos_from_worldgrid(worldgrid):
    grid_x, grid_y = worldgrid
    return grid_x + grid_y * MAP_WIDTH * MAP_EXPAND


def get_worldgrid_from_worldcoord(world_coord):
    coord_x, coord_y = world_coord
    grid_x = coord_x * MAP_EXPAND
    grid_y = coord_y * MAP_EXPAND
    return np.array([grid_x, grid_y], dtype=int)


def get_worldcoord_from_worldgrid(worldgrid):
    grid_x, grid_y = worldgrid
    coord_x = grid_x / MAP_EXPAND
    coord_y = grid_y / MAP_EXPAND
    return np.array([coord_x, coord_y])


def get_worldcoord_from_pos(pos):
    grid = get_worldgrid_from_pos(pos)
    return get_worldcoord_from_worldgrid(grid)


def get_pos_from_worldcoord(world_coord):
    grid = get_worldgrid_from_worldcoord(world_coord)
    return get_pos_from_worldgrid(grid)
