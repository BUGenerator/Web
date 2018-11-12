from skimage.io import imread, imsave
import numpy as np
from keras import models
from skimage.morphology import binary_opening, disk
import os.environ

fullres_model = models.load_model("model_fullres_keras.h5")
if os.environ.get('SHIPDETECTION_BROKEN_MODEL'):
    from keras.optimizers import Adam
    import keras.backend as K
    def IoU(y_true, y_pred, eps=1e-6):
        if np.max(y_true) == 0.0:
            return IoU(1-y_true, 1-y_pred) ## empty image; calc IoU of zeros
        intersection = K.sum(y_true * y_pred, axis=[1,2,3])
        union = K.sum(y_true, axis=[1,2,3]) + K.sum(y_pred, axis=[1,2,3]) - intersection
        return -K.mean( (intersection + eps) / (union + eps), axis=0)
    fullres_model.compile(optimizer=Adam(1e-3, decay=1e-6), loss=IoU, metrics=['binary_accuracy'])

def _raw_prediction(img):
    img = np.expand_dims(img, 0)/255.0
    seg = fullres_model.predict(img)[0]
    return seg, img[0]

def smooth(seg):
    return binary_opening(seg>0.99, np.expand_dims(disk(2), -1))

def predict_by_path(img_path):
    img = imread(img_path)
    seg, img = _raw_prediction(img)
    # return smooth(cur_seg), c_img
    return seg, img

def save_by_path(img, path):
    return imsave(path, seg)

def extract_seg(seg):
    l = []
    return l

# seg, img = predict_by_path("")

# ax2.imshow(first_seg[:, :, 0], cmap=get_cmap('jet'))
# reencoded = masks_as_color(multi_rle_encode(smooth(first_seg)[:, :, 0]))
