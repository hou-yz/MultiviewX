import os
import numpy as np
import cv2


def cam_pom(intrinsic_fpath, extrinsic_fpath, cfg):
    fp = cv2.FileStorage(intrinsic_fpath, flags=cv2.FILE_STORAGE_READ)
    cameraMatrix, distCoeffs = fp.getNode('camera_matrix').mat(), fp.getNode('distortion_coefficients').mat()
    fp.release()
    fp = cv2.FileStorage(extrinsic_fpath, flags=cv2.FILE_STORAGE_READ)
    rvec, tvec = fp.getNode('rvec').mat(), fp.getNode('tvec').mat()
    fp.release()
    image_width, image_height = cfg['image_width'], cfg['image_height']
    map_width, map_height, grid_ratio = cfg['map_width'], cfg['map_height'], cfg['grid_ratio']
    man_radius, man_height = cfg['man_radius'], cfg['man_height']
    # WILDTRACK has irregular denotion: H*W=480*1440, normally x would be \in [0,1440), not [0,480)
    # In our data annotation, we follow the regular x \in [0,W), and one can calculate x = posID % W, y = posID // W
    grid_x, grid_y = np.meshgrid(np.arange(map_width * grid_ratio), np.arange(map_height * grid_ratio))
    grid_x, grid_y = (grid_x + 0.5) / grid_ratio, (grid_y + 0.5) / grid_ratio
    centers3d = np.stack([grid_x, grid_y, np.zeros_like(grid_x)], axis=2).reshape([-1, 3])
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
    notvisible = np.zeros([centers3d.shape[0]])
    notvisible += (bbox[:, 0] >= image_width) + (bbox[:, 1] >= image_height) + (bbox[:, 2] <= 0) + (bbox[:, 3] <= 0)
    notvisible += bbox[:, 2] - bbox[:, 0] > bbox[:, 3] - bbox[:, 1]  # w > h
    notvisible += bbox[:, 2] - bbox[:, 0] > image_width / 3
    return bbox.astype(int), notvisible


if __name__ == '__main__':
    cam_num = 6
    cfg = {'image_width': 1920,
           'image_height': 1080,
           'map_width': 25,
           'map_height': 15,
           'grid_ratio': 10,
           'man_radius': 0.16,
           'man_height': 1.8, }
    fpath = 'multiviewX/rectangles.pom'
    if os.path.exists(fpath):
        os.remove(fpath)
    fp = open(fpath, 'w')
    for cam in range(cam_num):
        bbox, notvisible = cam_pom(f'intrinsic/intr_Camera{cam + 1}.xml',
                                   f'extrinsic/extr_Camera{cam + 1}.xml', cfg)
        for posID in range(len(notvisible)):
            if notvisible[posID]:
                fp.write(f'RECTANGLE {cam} {posID} notvisible\n')
            else:
                fp.write(f'RECTANGLE {cam} {posID} '
                         f'{bbox[posID, 0]} {bbox[posID, 1]} {bbox[posID, 2]} {bbox[posID, 3]}\n')
        pass
    fp.close()
    pass
