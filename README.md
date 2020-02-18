# The MultiviewX dataset

The MultiviewX dataset dedicates to multiview synthetic pedestrian detection. It follows the [WILDTRACK dataset](https://www.epfl.ch/labs/cvlab/data/data-wildtrack/) for set-up, annotation, and structure. 

The MultiviewX dataset is generated on a 25 meter by 15 meter playground. It has 6 cameras that has overlapping field-of-view. The images in MultiviewX dataset are of high resolution, 1920x1080, and are synchronized. To fully exploit the complementary views, calibrations are also provided in MultiviewX dataset. 

## Downloads
to be announced.

## Utilities for multiviewX dataset.
 
How to's
- copy the 2d/3d simulation annotations into `/matchings`.
- run the followings.
```shell script
python calibrateCamrea.py
python generatePOM.py
python generateAnnotation.py
```
- done.
