import numpy as np
import cv2
import os

os.makedirs('intrinsic', exist_ok=True)
os.makedirs('extrinsic', exist_ok=True)
for cam in range(6):
    head_foot_image = np.loadtxt(f'matchings/Camera{cam + 1}.txt')
    head_foot_image = np.concatenate([head_foot_image[:, 2:4], head_foot_image[:, 4:]], axis=0). \
        reshape([1, -1, 2]).astype('float32')
    head_foot_3d = np.loadtxt(f'matchings/Camera{cam + 1}_3d.txt')
    head_foot_3d = np.concatenate([head_foot_3d[:, 2:5], head_foot_3d[:, 5:]], axis=0). \
        reshape([1, -1, 3]).astype('float32')
    cameraMatrix = cv2.initCameraMatrix2D(head_foot_3d, head_foot_image, (1080, 1920))
    retval, cameraMatrix, distCoeffs, rvecs, tvecs = \
        cv2.calibrateCamera(head_foot_3d, head_foot_image, (1080, 1920), cameraMatrix, None,
                            flags=cv2.CALIB_USE_INTRINSIC_GUESS)
    f = cv2.FileStorage(f'intrinsic/intr_Camera{cam + 1}.xml', flags=cv2.FILE_STORAGE_WRITE)
    f.write(name='camera_matrix', val=cameraMatrix)
    f.write(name='distortion_coefficients', val=distCoeffs)
    f.release()
    f = cv2.FileStorage(f'extrinsic/extr_Camera{cam + 1}.xml', flags=cv2.FileStorage_WRITE_BASE64)
    f.write(name='rvec', val=rvecs[0])
    f.write(name='tvec', val=tvecs[0])
    f.release()
pass
