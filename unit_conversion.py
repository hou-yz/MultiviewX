import numpy as np


def get_worldgrid_from_pos(pos):
    grid_x = pos % (25 * 40)
    grid_y = pos // (25 * 40)
    return np.array([grid_x, grid_y], dtype=int)


def get_pos_from_worldgrid(worldgrid):
    grid_x, grid_y = worldgrid
    return grid_x + grid_y * 25 * 40


def get_worldgrid_from_worldcoord(world_coord):
    coord_x, coord_y = world_coord
    grid_x = coord_x * 40
    grid_y = coord_y * 40
    return np.array([grid_x, grid_y]).round()


def get_worldcoord_from_worldgrid(worldgrid):
    grid_x, grid_y = worldgrid
    coord_x = grid_x / 40
    coord_y = grid_y / 40
    return np.array([coord_x, coord_y])


def get_worldcoord_from_pos(pos):
    grid = get_worldgrid_from_pos(pos)
    return get_worldcoord_from_worldgrid(grid)


def get_pos_from_worldcoord(world_coord):
    grid = get_worldgrid_from_worldcoord(world_coord)
    return get_pos_from_worldgrid(grid)
