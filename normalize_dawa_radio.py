import logging

import sys
import h5py
import dxchange
import numpy as np
import tomopy
import argparse

def normalize_dawa_radio(flat_file, radio_file, 
    first_image=None, last_image=None, 
    xshift=0, yshift=0, 
    dark_value=None, 
    zinger_threshold=0, zinger_filter_size=3):
  logging.basicConfig(
    filename=radio_file + '_normalized.log',
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
  logging.info('Reading data')
  flat_file_name = flat_file + '.h5'
  radio_file_name = radio_file + '.h5'
  flat = dxchange.read_hdf5(flat_file_name, '/exchange/data_white')
  dark_field_value = dxchange.read_hdf5(flat_file_name, '/process/acquisition/dark_fields/dark_field_value')[0]
  dark = flat[0,:,:] * 0 + dark_field_value
  first = 0
  if (first_image != None):
    first = first_image
  with h5py.File(radio_file_name, "r") as f:
    data = f['/exchange/data_white']
    last = data.shape[0]
  if (last_image != None):
    last = last_image
  logging.info('first image: %d', first)
  logging.info('last image: %d', last)
  radio = dxchange.read_hdf5(radio_file_name, '/exchange/data_white', slc=((first, last, 1), None))
  if (xshift != 0):
    flat = np.roll(flat, xshift, axis=2)
  if (yshift != 0):
    flat = np.roll(flat, yshift, axis=1)
  logging.info('xshift: %d', xshift)
  logging.info('yshift: %d', yshift)
  logging.info('radio.shape: %s', radio.shape)
  logging.info('flat.shape: %s', flat.shape)
  logging.info('dark.shape: %s', dark.shape)
  if (dark_value != None):
    dark = dark*0 + dark_value
  logging.info('dark[0]: %s', dark.item(0))

  logging.info('Normalizing')
  radio = tomopy.normalize(radio, flat, dark)
  logging.info("After normalizing, min: %f, max: %f", radio.min(), radio.max())

  if (zinger_threshold != 0):
    logging.info('Removing zingers. threshold:%f, size:%d', zinger_threshold, zinger_filter_size)
    radio = tomopy.misc.corr.remove_outlier(radio, zinger_threshold, size=zinger_filter_size)
    logging.info("After remove_outlier, min: %f, max: %f", radio.min(), radio.max())

  logging.info('Converting to integer')
  radio = (10000.*radio).astype(np.int16)

  logging.info('Writing normalized file')
  dxchange.write_hdf5(radio, fname=radio_file + '_normalized.h5', overwrite=True)
  logging.info('Normalized file written')

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("flat_file",
                    help="file for flat fields")
  parser.add_argument("radiography_file",
                    help="file for radiographs")
  parser.add_argument("-f", "--first_image", type=int,
                    help="first  image to process")
  parser.add_argument("-l", "--last_image", type=int,
                    help="last image to process")
  parser.add_argument("-x", "--xshift", type=int, default=0,
                    help="number of pixels to shift flat field horizontally")
  parser.add_argument("-y", "--yshift", type=int, default=0,
                    help="number of pixels to shift flat field vertically")
  parser.add_argument("-d", "--dark_value", type=float,
                    help="dark field value")
  parser.add_argument("-t", "--zinger_threshold", type=float, default=0.2,
                    help="zinger threshold")
  parser.add_argument("-s", "--zinger_filter_size", type=int, default=3,
                    help="zinger filter_size")
  args = parser.parse_args()
  normalize_dawa_radio(args.flat_file, args.radiography_file, 
      first_image=args.first_image, last_image=args.last_image, 
      xshift=args.xshift, yshift=args.yshift, 
      dark_value=args.dark_value, 
      zinger_threshold=args.zinger_threshold, zinger_filter_size=args.zinger_filter_size)
 