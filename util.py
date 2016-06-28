import cv2
import numpy as np

def get_motion_mask(frames, threshold):
    diff_frames = [cv2.absdiff(frames[i],frames[i-1]) for i in range(1, len(frames))]
    diff = sum(diff_frames)/len(diff_frames)

    diff = diff[:,:,0] + diff[:,:,1] + diff[:,:,2]
    mask = diff < threshold
    diff[mask] = 0
    diff[~mask] = 255

    return diff

def cleanup_mask(mask, erode_val, dilate_val):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode_val,erode_val))
    mask = cv2.erode(mask, kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_val,dilate_val))
    mask = cv2.dilate(mask, kernel)

    return mask

def get_bounding_rect(diff):
    indices = np.nonzero(diff)
    if len(indices[0]) > 0 and len(indices[1]) > 0:
        return ((min(indices[1]), min(indices[0])),
                (max(indices[1]), max(indices[0])))
    else:
        return None
