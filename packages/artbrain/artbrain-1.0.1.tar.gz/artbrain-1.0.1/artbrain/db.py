#!/usr/bin/python

from artbrain.utils import get_packagedir
import nibabel
import os

base = get_packagedir()

def get_standard_brain_mask():
    return nibabel.load(os.path.abspath(os.path.join("%s" %base,"data/MNI152_T1_2mm_brain_mask.nii.gz")))
    
def get_standard_brain():
    return nibabel.load(os.path.abspath(os.path.join("%s" %base,"data/MNI152_T1_2mm_brain.nii.gz")))
