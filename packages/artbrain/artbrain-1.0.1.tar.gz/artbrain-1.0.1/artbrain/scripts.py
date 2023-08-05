#!/usr/bin/python

'''
script.py: 
Runtime executable

'''

from artbrain.art import generate
from glob import glob
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
    description="draw png images onto brain maps")
    parser.add_argument("--input", dest='image', help="full path to png image", type=str, default=None,required=True)
    parser.add_argument('--nopreview', dest='nopreview', help="don't view output in browser", default=False, action='store_true')
    parser.add_argument("--output-folder", dest='output', help="output folder for html file", type=str, default=None)
    parser.add_argument("--port", dest='port', help="port for preview, if view is True", type=int, default=None)
    parser.add_argument("--rotate", dest='rotations', help="counter-clockwise rotations (default is 3 for upright)", type=int, default=3)

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    
    if args.image == None:
        print "Please specify input png image with --input argument."

    if args.nopreview == True:
        preview = False
    else:
        preview = True

    generate(template=args.image,
             output_folder=args.output,
             view=preview,
             port=args.port,
             rotations=args.rotations)
