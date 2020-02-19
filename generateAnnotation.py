import os
import re
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from unitConversion import *


def read_pom(fpath):
    bbox_by_pos_cam = {}
    cam_pos_pattern = re.compile(r'(\d+) (\d+)')
    cam_pos_bbox_pattern = re.compile(r'(\d+) (\d+) ([-\d]+) ([-\d]+) (\d+) (\d+)')
    with open(fpath, 'r') as fp:
        for line in fp:
            if 'RECTANGLE' in line:
                cam, pos = map(int, cam_pos_pattern.search(line).groups())
                if pos not in bbox_by_pos_cam:
                    bbox_by_pos_cam[pos] = {}
                if 'notvisible' in line:
                    bbox_by_pos_cam[pos][cam] = [-1, -1, -1, -1]
                else:
                    cam, pos, left, top, right, bottom = map(int, cam_pos_bbox_pattern.search(line).groups())
                    bbox_by_pos_cam[pos][cam] = [left, top, right, bottom]
    return bbox_by_pos_cam


def read_gt(cam):
    gt_3d = np.loadtxt(f'matchings/Camera{cam + 1}_3d.txt')
    gt_3d = gt_3d[np.where(np.logical_and(gt_3d[:, -3] >= 0, gt_3d[:, -3] <= 25))[0], :]
    gt_3d = gt_3d[np.where(np.logical_and(gt_3d[:, -2] >= 0, gt_3d[:, -2] <= 15))[0], :]
    frame, pid = gt_3d[:, 0], gt_3d[:, 1]
    foot_3d_coord = gt_3d[:, -3:-1].transpose()
    pos = get_pos_from_worldcoord(foot_3d_coord)
    return np.stack([frame, pid, pos], axis=1).astype(int)


def create_pid_annotation(pid, pos, bbox_by_pos_cam):
    person_annotation = {'personID': int(pid), 'positionID': int(pos), 'views': []}
    for cam in range(len(bbox_by_pos_cam[pos])):
        bbox = bbox_by_pos_cam[pos][cam]
        view_annotation = {'viewNum': cam, 'xmin': int(bbox[0]), 'ymin': int(bbox[1]),
                           'xmax': int(bbox[2]), 'ymax': int(bbox[3])}
        person_annotation['views'].append(view_annotation)
    return person_annotation


def annotate():
    bbox_by_pos_cam = read_pom('rectangles.pom')
    gts = []
    for cam in range(NUM_CAM):
        gt = read_gt(cam)
        gts.append(gt)
    gts = np.concatenate(gts, axis=0)
    gts = np.unique(gts, axis=0)
    print(f'average persons per frame: {gts.shape[0] / len(np.unique(gts[:, 0]))}')
    pids_dict = {}
    os.makedirs('annotations_positions', exist_ok=True)
    for frame in np.unique(gts[:, 0]):
        gts_frame = gts[gts[:, 0] == frame, :]
        annotations = []
        for i in range(gts_frame.shape[0]):
            pid, pos = gts_frame[i, 1:]
            if pid not in pids_dict:
                pids_dict[pid] = len(pids_dict)
            annotations.append(create_pid_annotation(pids_dict[pid], pos, bbox_by_pos_cam))
        with open('annotations_positions/{:05d}.json'.format(frame), 'w') as fp:
            json.dump(annotations, fp, indent=4)
        if frame == 1:
            for cam in range(NUM_CAM):
                img = Image.open(f'Image_subsets/C{cam + 1}/0000.jpg')

                # Create figure and axes
                fig, ax = plt.subplots(1)
                # Display the image
                ax.imshow(img)
                for anno in annotations:
                    anno = anno['views'][cam]
                    bbox = np.array([anno['xmin'], anno['ymin'], anno['xmax'], anno['ymax']])
                    if bbox[0] == -1 and bbox[1] == -1:
                        continue
                    bbox[2:] = bbox[2:] - bbox[:2]  # xywh

                    # Create a Rectangle patch
                    rect = patches.Rectangle(bbox[:2], bbox[2], bbox[3], linewidth=1, edgecolor='g', facecolor='none')
                    # Add the patch to the Axes
                    ax.add_patch(rect)
                plt.show()
                pass

    pass


if __name__ == '__main__':
    annotate()
