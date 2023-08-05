#!/usr/bin/python

from numpy.random import choice
import artbrain.hello as hello
import scipy.ndimage
import itertools
import pandas
import nibabel
import numpy
import png
import os

def get_packagedir():
    return os.path.dirname(hello.__file__)

def read_png(png_image):
    pngReader=png.Reader(filename=png_image)
    row_count, column_count, pngdata, meta = pngReader.asDirect()
    bitdepth=meta['bitdepth']
    plane_count=meta['planes']
    image_2d = numpy.vstack(itertools.imap(numpy.uint16, pngdata))
    # If "image_plane" == 4, this means an alpha layer
    for row_index, one_boxed_row_flat_pixels in enumerate(pngdata):
        image_2d[row_index,:]=one_boxed_row_flat_pixels
    image_3d = numpy.reshape(image_2d,(row_count,column_count,plane_count))
    return image_3d

def map_to_brain(image_3d,brain_mask,axis="axial",rotations=3):
    '''map_to_brain
    map 3d data matrix onto a brain_mask, specified by axis. If axis is not valid, will return False. If valid, will return nibabel.Nifti1Image
    :param image_3d: numpy array read in from read_png. Usually of shape (512, 512, N), where N is 3 for 3D image, and 4 for png with alpha. If an alpha channel is found, pixels with 0 alpha will be rendered as transparent (0).
    '''
    R = image_3d[:,:,0]
    G = image_3d[:,:,1]
    B = image_3d[:,:,2]

    axis = axis.lower()

    # Convert to integer value
    rgb = R;
    rgb = (rgb << 8) + G
    rgb = (rgb << 8) + B

    # Normalize
    rgb = (rgb - rgb.mean()) / rgb.std()
    rgb = numpy.rot90(rgb, k=rotations)

    # Houston, we have alpha!
    alpha_channel = False
    if image_3d.shape[2] == 4:
        alpha_channel = True

    if axis == "axial":
        width = brain_mask.shape[0]
        height = brain_mask.shape[1]
    else:
        print "Invalid specification of atlas, %s. Currently only supported is axial." %axis
        return False

    # Only square images, sorry
    if rgb.shape[0] != rgb.shape[1]:
        print "Sorry, only square images are currently supported."
        return False

    # We will interpolate down the largest dimension of the image
    if rgb.shape[0] >= rgb.shape[1]: 
        scale =  float(width)/rgb.shape[0]
    else:
        scale = float(height)/rgb.shape[1]

    # order 0 means nearest interpolation
    scaled = scipy.ndimage.zoom(rgb, scale, order=0)
    if alpha_channel:
        scaled_alpha = scipy.ndimage.zoom(image_3d[:,:,3], scale, order=0)
        scaled[scaled_alpha==0] = 0

    # Calculate left and right padding, keep as ints to take floor
    padding_width = (width - scaled.shape[0]) /2
    padding_height = (height - scaled.shape[1]) /2
    padded = numpy.pad(scaled, ((padding_width,padding_width), # Default value is 0
                               (padding_height,padding_height)),mode="constant")

    # Create array of same size as brainmap, just in case we are off a bit
    array = numpy.zeros((width,height))

    # This is slow and stupid, but it will work
    for x in range(width):
        for y in range(height):
            try:
                array[x,y] = padded[x,y]
            except:
                pass

    # Let's write the image to all slices
    empty_brain = numpy.zeros(brain_mask.shape)
    mask = brain_mask.get_data()

    # Add support for other axis?
    if axis == "axial":

        for z in range(brain_mask.shape[2]):
            zslice = mask[:,:,z] 
            empty_brain[zslice!=0,z] = array[zslice!=0]

    nii = nibabel.Nifti1Image(empty_brain,affine=brain_mask.get_affine())
    return nii
