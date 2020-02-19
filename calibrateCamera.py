import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from datasetParameters import *


def calibrate():
    os.makedirs('calibrations/intrinsic', exist_ok=True)
    os.makedirs('calibrations/extrinsic', exist_ok=True)
    for cam in range(NUM_CAM):
        points_2d = np.loadtxt(f'matchings/Camera{cam + 1}.txt')
        points_3d = np.loadtxt(f'matchings/Camera{cam + 1}_3d.txt')
        visualize_foot_image = points_2d[points_2d[:, 0] == 1, -2:]
        image = cv2.imread(f'Image_subsets/C{cam + 1}/0000.jpg')
        for point in visualize_foot_image:
            cv2.circle(image, tuple(point.astype(int)), 20, (0, 255, 0), -1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()
        points_2d_list, points_3d_list = [], []
        for view in range(9):
            points_2d_list.append(points_2d[:, 2 * view + 2:2 * (view + 1) + 2])
            points_3d_list.append(points_3d[:, 3 * view + 2:3 * (view + 1) + 2])
        points_2d = np.concatenate(points_2d_list, axis=0).reshape([1, -1, 2]).astype('float32')
        points_3d = np.concatenate(points_3d_list, axis=0).reshape([1, -1, 3]).astype('float32')
        cameraMatrix = cv2.initCameraMatrix2D(points_3d, points_2d, (IMAGE_HEIGHT, IMAGE_WIDTH))
        retval, cameraMatrix, distCoeffs, rvecs, tvecs = \
            cv2.calibrateCamera(points_3d, points_2d, (IMAGE_HEIGHT, IMAGE_WIDTH), cameraMatrix, None,
                                flags=cv2.CALIB_USE_INTRINSIC_GUESS)
        f = cv2.FileStorage(f'calibrations/intrinsic/intr_Camera{cam + 1}.xml', flags=cv2.FILE_STORAGE_WRITE)
        f.write(name='camera_matrix', val=cameraMatrix)
        f.write(name='distortion_coefficients', val=distCoeffs)
        f.release()
        f = cv2.FileStorage(f'calibrations/extrinsic/extr_Camera{cam + 1}.xml', flags=cv2.FileStorage_WRITE_BASE64)
        f.write(name='rvec', val=rvecs[0])
        f.write(name='tvec', val=tvecs[0])
        f.release()
    pass


if __name__ == '__main__':
    calibrate()
