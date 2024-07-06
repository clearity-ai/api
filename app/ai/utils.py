import numpy as np
import torch
from torchvision import transforms

from app.ai.constants import INPUT_HEIGHT, INPUT_WIDTH, SEG_LABELS_LIST

import pdb


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

### Transformations ###

to_tensor = transforms.ToTensor()
resizer = transforms.Resize(
    size=(INPUT_HEIGHT, INPUT_WIDTH), interpolation=transforms.InterpolationMode.NEAREST
)
# center_crop = transforms.CenterCrop(512)


def transform_image(img):
    """Apply transformations to image after opening with PIL."""

    # img = center_crop(img)
    img = resizer(img)
    img = to_tensor(img)

    return img


def transform_target(target):
    # target = center_crop(target)
    target = resizer(target)
    target = np.array(target, dtype=np.int64)


def label_img_to_rgb(label_img):
    label_img = np.squeeze(label_img)
    labels = np.unique(label_img)
    label_infos = [label for label in SEG_LABELS_LIST if label["id"] in labels]

    label_img_rgb = np.array([label_img, label_img, label_img]).transpose(1, 2, 0)
    for label in label_infos:
        mask = label_img == label["id"]
        label_img_rgb[mask] = label["rgb_values"]

    return label_img_rgb.astype(np.uint8)


def rgb_img_to_label(rgb_img):
    pass
    # TODO


### Segmentation ###


def segment_image(input_image, seg_model):
    inputs = input_image.unsqueeze(0)
    inputs = inputs.to(device)

    pdb.set_trace()

    # TODO: server crashes when trying to segment image. device is cpu. Memory error? No docker 287.9MB / 7.58GB
    with torch.no_grad():
        seg_probabilities = seg_model.forward(inputs)

    _, seg_mask = torch.max(seg_probabilities, 1)
    seg_mask = seg_mask[0].data.cpu()
    # undo -1 target operation while training
    # artifact of annotation tool forcing category ids to start at 1
    seg_mask = seg_mask + 1
    seg_mask = np.array(seg_mask)

    return seg_mask
