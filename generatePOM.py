import os
import cv2
from unit_conversion import *

intrinsic_camera_matrix_filenames = ['intr_Camera1.xml', 'intr_Camera2.xml', 'intr_Camera3.xml', 'intr_Camera4.xml',
                                     'intr_Camera5.xml', 'intr_Camera6.xml']
extrinsic_camera_matrix_filenames = ['extr_Camera1.xml', 'extr_Camera2.xml', 'extr_Camera3.xml', 'extr_Camera4.xml',
                                     'extr_Camera5.xml', 'extr_Camera6.xml']


def generate_cam_pom(rvec, tvec, cameraMatrix, distCoeffs, cfg):
    image_width, image_height = cfg['image_width'], cfg['image_height']
    map_width, map_height, grid_ratio = cfg['map_width'], cfg['map_height'], cfg['grid_ratio']
    man_radius, man_height = cfg['man_radius'], cfg['man_height']
    # WILDTRACK has irregular denotion: H*W=480*1440, normally x would be \in [0,1440), not [0,480)
    # In our data annotation, we follow the regular x \in [0,W), and one can calculate x = pos % W, y = pos // W
    coord_x, coord_y = get_worldcoord_from_pos(np.arange(map_width * map_height * grid_ratio * grid_ratio))
    centers3d = np.stack([coord_x, coord_y, np.zeros_like(coord_y)], axis=1)
    points3d8s = []
    points3d8s.append(centers3d + np.array([man_radius, man_radius, 0]))
    points3d8s.append(centers3d + np.array([-man_radius, man_radius, 0]))
    points3d8s.append(centers3d + np.array([man_radius, -man_radius, 0]))
    points3d8s.append(centers3d + np.array([-man_radius, -man_radius, 0]))
    points3d8s.append(centers3d + np.array([man_radius, man_radius, man_height]))
    points3d8s.append(centers3d + np.array([-man_radius, man_radius, man_height]))
    points3d8s.append(centers3d + np.array([man_radius, -man_radius, man_height]))
    points3d8s.append(centers3d + np.array([-man_radius, -man_radius, man_height]))
    bbox = np.ones([centers3d.shape[0], 4]) * np.array([image_width, image_height, 0, 0])  # xmin,ymin,xmax,ymax
    for i in range(8):  # for all 8 points
        points_img, _ = cv2.projectPoints(points3d8s[i], rvec, tvec, cameraMatrix, distCoeffs)
        points_img = points_img.squeeze()
        bbox[:, 0] = np.min([bbox[:, 0], points_img[:, 0]], axis=0)  # xmin
        bbox[:, 1] = np.min([bbox[:, 1], points_img[:, 1]], axis=0)  # ymin
        bbox[:, 2] = np.max([bbox[:, 2], points_img[:, 0]], axis=0)  # xmax
        bbox[:, 3] = np.max([bbox[:, 3], points_img[:, 1]], axis=0)  # xmax
        pass
    points_img, _ = cv2.projectPoints(centers3d, rvec, tvec, cameraMatrix, distCoeffs)
    points_img = points_img.squeeze()
    bbox[:, 3] = points_img[:, 1]
    # offset = points_img[:, 0] - (bbox[:, 0] + bbox[:, 2]) / 2
    # bbox[:, 0] += offset
    # bbox[:, 2] += offset
    notvisible = np.zeros([centers3d.shape[0]])
    notvisible += (bbox[:, 0] >= image_width) + (bbox[:, 1] >= image_height) + (bbox[:, 2] <= 0) + (bbox[:, 3] <= 0)
    notvisible += bbox[:, 2] - bbox[:, 0] > bbox[:, 3] - bbox[:, 1]  # w > h
    notvisible += bbox[:, 2] - bbox[:, 0] > image_width / 3
    return bbox.astype(int), notvisible.astype(bool)


def test():
    cam_num = 6
    cfg = {'image_width': 1920,
           'image_height': 1080,
           'map_width': 25,
           'map_height': 15,
           'grid_ratio': 40,
           'man_radius': 0.16,
           'man_height': 1.8, }
    fpath = 'rectangles.pom'
    if os.path.exists(fpath):
        os.remove(fpath)
    fp = open(fpath, 'w')
    errors = []
    for cam in range(cam_num):
        fp_calibration = cv2.FileStorage(f'calibrations/intrinsic/{intrinsic_camera_matrix_filenames[cam]}',
                                         flags=cv2.FILE_STORAGE_READ)
        cameraMatrix, distCoeffs = fp_calibration.getNode('camera_matrix').mat(), fp_calibration.getNode(
            'distortion_coefficients').mat()
        fp_calibration.release()
        fp_calibration = cv2.FileStorage(f'calibrations/extrinsic/{extrinsic_camera_matrix_filenames[cam]}',
                                         flags=cv2.FILE_STORAGE_READ)
        rvec, tvec = fp_calibration.getNode('rvec').mat().squeeze(), fp_calibration.getNode('tvec').mat().squeeze()
        fp_calibration.release()

        bbox, notvisible = generate_cam_pom(rvec, tvec, cameraMatrix, distCoeffs, cfg)  # xmin,ymin,xmax,ymax

        for pos in range(len(notvisible)):
            if notvisible[pos]:
                fp.write(f'RECTANGLE {cam} {pos} notvisible\n')
            else:
                fp.write(f'RECTANGLE {cam} {pos} '
                         f'{bbox[pos, 0]} {bbox[pos, 1]} {bbox[pos, 2]} {bbox[pos, 3]}\n')

        foot_3d = get_worldcoord_from_pos(np.arange(len(notvisible)))
        foot_3d = np.concatenate([foot_3d, np.zeros([1, len(notvisible)])], axis=0).transpose()[
                  (1 - notvisible).astype(bool), :].reshape([1, -1, 3])
        projected_foot_2d, _ = cv2.projectPoints(foot_3d, rvec, tvec, cameraMatrix, distCoeffs)
        projected_foot_2d = projected_foot_2d.squeeze()
        foot_2d = np.array([(bbox[:, 0] + bbox[:, 2]) / 2, bbox[:, 3]]).transpose()[(1 - notvisible).astype(bool), :]
        projected_foot_2d = np.maximum(projected_foot_2d, 0)
        projected_foot_2d = np.minimum(projected_foot_2d, [1920, 1080])
        foot_2d = np.maximum(foot_2d, 0)
        foot_2d = np.minimum(foot_2d, [1920, 1080])
        errors.append(np.linalg.norm(projected_foot_2d - foot_2d, axis=1))
    errors = np.concatenate(errors)
    print(f'average error in image pixels: {np.average(errors)}')
    fp.close()
    pass


if __name__ == '__main__':
    test()
