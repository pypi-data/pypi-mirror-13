#!/usr/bin/python

from artbrain.template import get_template, sub_template, save_template
from artbrain.db import get_standard_brain, get_standard_brain_mask
from artbrain.utils import read_png, map_to_brain, get_packagedir
from numpy.random import choice
import SimpleHTTPServer
from glob import glob
import SocketServer
import webbrowser
import tempfile
import nibabel
import pandas
import shutil
import json
import sys
import os

base = get_packagedir() 

def generate(template,output_folder=None,orthoview="axial",view=True,port=None,rotations=3):
    '''generate
    create an artbrain image

    :param template: the template image to generate brainart for! Only png has been tested. This image will be placed on all slices.
    :param output_folder: output folder for the final file, including a nifti image and web view. If not specified, will use TMP. To disable the web page, set view=False
    :param view: show in browser. Default is True.
    :param orthoview: one of sagittal, coronal, or axial. Currently only supported is axial.
    '''
    if output_folder == None:
        output_folder = tempfile.mkdtemp()

    # Read in nifti standard mask
    brain_mask = get_standard_brain_mask()

    # Extract 3d data
    image_3d = read_png(template)

    # Map onto brain!
    nii = map_to_brain(image_3d,brain_mask,axis=orthoview,rotations=rotations)

    # Save output to file
    if isinstance(nii,nibabel.Nifti1Image):
        new_image_name = os.path.splitext(os.path.split(template)[-1])[0]
        new_image = "%s/%s.nii.gz" %(output_folder,new_image_name)
        nibabel.save(nii,new_image)

        print "Nifti image saved to %s" %(new_image)

        # Open to show in browser
        if view==True:
            html_template = get_template("index")
            html_template = sub_template(html_template,"DATA","%s.nii.gz" %new_image_name)
            output_html = "%s/index.html" %output_folder
            save_template(output_html,html_template)

            # Copy brain image template
            shutil.copyfile(os.path.abspath(os.path.join("%s" %base,"data/MNI152_T1_2mm_brain.nii.gz")),"%s/MNI152_T1_2mm_brain.nii.gz" %output_folder)
        
            try:
                os.chdir(output_folder)
                if port == None:
                    port = choice(range(8000,9999),1)[0]
                Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
                httpd = SocketServer.TCPServer(("", port), Handler)
                print "Art brain viewer at localhost:%s" %port
                webbrowser.open("http://localhost:%s" %(port))
                httpd.serve_forever()
            except:
                print "Stopping web server..."
                httpd.server_close()
