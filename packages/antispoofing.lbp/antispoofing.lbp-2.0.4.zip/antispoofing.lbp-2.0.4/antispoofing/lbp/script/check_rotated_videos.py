#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed  8 Apr 11:34:56 CEST 2015

"""Calculates the normalized LBP histogram of the normalized faces in each of the frames of the videos in the REPLAY-ATTACK (or CASIA_FASD) database. The result are LBP histograms for each frame of the video. Different types of LBP operators are supported. The histograms can be computed for a subset of the videos in the database (using the protocols in the database). The output is a single .hdf5 file for each video. The procedure is described in the paper: "On the Effectiveness of Local Binary patterns in Face Anti-spoofing" - Chingovska, Anjos & Marcel; BIOSIG 2012
"""

import os, sys
import argparse
import bob.io.base
import bob.ip.color
import bob.io.video
import bob.io.image
import numpy
import math
import string

import antispoofing.utils.faceloc as faceloc
from antispoofing.utils.db import *

from pymediainfo import MediaInfo

def main():

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'database')
  OUTPUT_DIR = os.path.join(basedir, 'lbp_features')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str,
      dest='inputdir', default=INPUT_DIR, help='Base directory containing the videos to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-d', '--directory', dest="directory", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-e', '--enrollment', action='store_true', default=False, dest='enrollment', help='If True, will do the processing on the enrollment data of the database (defaults to "%(default)s")')
  parser.add_argument('-t', '--task', default='print_rotated', dest='task', help='If print_rotated, will detect the rotated videos, if save_rotated, will save frames from the rotated videos (defaults to "%(default)s")', choices=('print_rotated', 'save_rotated', 'save_faces', 'print_face_sizes'))
  #######
  # Database especific configuration
  #######
  #Database.create_parser(parser)
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()

  ########################
  #Querying the database
  ########################
  #database = new_database(databaseName,args=args)
  database = args.cls(args)
  
  if args.enrollment:  
    process = database.get_enroll_data()
  else:  
    realObjects, attackObjects = database.get_all_data()
    process = realObjects + attackObjects
  
  if args.task == 'print_rotated':
    for obj in process:
      media_info = MediaInfo.parse(obj.videofile(directory=args.inputdir))
      for track in media_info.tracks:
        if track.track_type == 'Video':
          if track.rotation != u'0.000':
            sys.stdout.write('%s\n' % obj.make_path())
            #print track.bit_rate, track.bit_rate_mode, track.codec
  
  if args.task == 'save_rotated':
    for obj in process:
      input = bob.io.video.reader(obj.videofile(directory=args.inputdir))
      vin = input.load()
      sys.stdout.write("Processing file %s (%d frames)\n" % (obj.make_path(),
        input.number_of_frames))

      locations_1 = obj.bbx(directory=args.inputdir)
      locations = {x[0]:faceloc.BoundingBox(x[1], x[2], x[3], x[4]) for x in locations_1}
      
      #locations = faceloc.read_face(obj.facefile(args.inputdir))
      #locations = faceloc.expand_detections(locations, input.number_of_frames)

      if obj.is_rotated():
        frame = bob.ip.color.rgb_to_gray(vin[0,:,:,:])
        frame = numpy.rot90(numpy.rot90(frame))
        bbx = locations[0]
        if bbx and bbx.is_valid(): #and bbx.height > bbxsize_filter:
          cutframe = frame[bbx.y:(bbx.y+bbx.height),bbx.x:(bbx.x+bbx.width)]  

        bob.io.base.save(cutframe.astype('uint8'), obj.make_path(directory=args.directory, extension='.jpg'))  
  
  if args.task == 'save_faces':
    for obj in process:
      input = bob.io.video.reader(obj.videofile(directory=args.inputdir))
      vin = input.load()
      sys.stdout.write("Processing file %s (%d frames)\n" % (obj.make_path(),
        input.number_of_frames))

      locations_1 = obj.bbx(directory=args.inputdir)
      locations = {x[0]:faceloc.BoundingBox(x[1], x[2], x[3], x[4]) for x in locations_1}
    
      frame = bob.ip.color.rgb_to_gray(vin[0,:,:,:])
      bbx = locations[0]
      if bbx and bbx.is_valid(): #and bbx.height > bbxsize_filter:
        cutframe = frame[bbx.y:(bbx.y+bbx.height),bbx.x:(bbx.x+bbx.width)]  

      bob.io.base.save(cutframe.astype('uint8'), obj.make_path(directory=args.directory, extension='.jpg'))  

  if args.task == 'print_face_sizes':
    smallest_face = (1000,1000)
    largest_face = (0,0)
    smallest_face_bbx = None
    largest_face_bbx=None
    smallest_face_name = (None, -1) # this tuple is file name and frame
    largest_face_name = (None, -1) # this tuple is file name and frame
    heights = []; widths=[]
    for obj in process:
      input = bob.io.video.reader(obj.videofile(directory=args.inputdir))
      vin = input.load()
      sys.stdout.write("Processing file %s (%d frames)\n" % (obj.make_path(),
        input.number_of_frames))

      locations_1 = obj.bbx(directory=args.inputdir)
      locations = {x[0]:faceloc.BoundingBox(x[1], x[2], x[3], x[4]) for x in locations_1}
      locations = faceloc.expand_detections(locations, input.number_of_frames)

      for k in range(0, vin.shape[0]):
        bbx = locations[k]

        #import ipdb; ipdb.set_trace()
        heights.append(bbx.height)
        widths.append(bbx.width)

        if bbx.height * bbx.width < smallest_face[0] * smallest_face[1]:
          smallest_face = (bbx.height, bbx.width)
          smallest_face_name = (obj, k)
          smallest_face_bbx = bbx
        if bbx.height * bbx.width > largest_face[0] * largest_face[1]:  
          largest_face = (bbx.height, bbx.width)
          largest_face_name = (obj, k)
          largest_face_bbx = bbx
      
    sys.stdout.write("Median height: %.2f, median width: %2f\n" % (numpy.median(heights), numpy.median(widths)))
    sys.stdout.write("Average height: %.2f, average width: %2f\n" % (numpy.mean(heights), numpy.mean(widths)))
    sys.stdout.write("Smallest face: %dx%d\n" % (smallest_face[0], smallest_face[1]))
    sys.stdout.write("Largest face: %dx%d\n" % (largest_face[0], largest_face[1]))
    
    # save the smallest frame
    smallest_input = bob.io.video.reader(smallest_face_name[0].videofile(directory=args.inputdir))
    smallest_vin = smallest_input.load()
    frame = bob.ip.color.rgb_to_gray(smallest_vin[smallest_face_name[1],:,:,:])
    if smallest_face_name[0].is_rotated():
      frame = numpy.rot90(numpy.rot90(frame))
    bbx = smallest_face_bbx  
    faceframe = frame[bbx.y:(bbx.y+bbx.height),bbx.x:(bbx.x+bbx.width)]  
    bob.io.base.save(faceframe.astype('uint8'), os.path.join(args.directory, 'smallest.jpg'))  

    # save the largest frame
    largest_input = bob.io.video.reader(largest_face_name[0].videofile(directory=args.inputdir))
    largest_vin = largest_input.load()
    frame = bob.ip.color.rgb_to_gray(largest_vin[largest_face_name[1],:,:,:])
    if largest_face_name[0].is_rotated():
      frame = numpy.rot90(numpy.rot90(frame))
    bbx = largest_face_bbx  
    faceframe = frame[bbx.y:(bbx.y+bbx.height),bbx.x:(bbx.x+bbx.width)]  
    bob.io.base.save(faceframe.astype('uint8'), os.path.join(args.directory, 'largest.jpg'))

      
  sys.stdout.flush()


  return 0

if __name__ == "__main__":
  main()
