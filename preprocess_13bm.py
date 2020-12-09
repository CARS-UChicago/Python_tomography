import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.info('Importing packages ...')

import sys
import dxchange
import tomopy
import numpy as np

def preprocess_13bm(fname, dark_value=0, zinger_threshold=0.2, zinger_filter_size=3):
  logging.info('Reading data')
  proj, flat, dark, theta = dxchange.read_aps_13bm(fname + '.h5', 'hdf5')
  logging.info('proj.shape: %s', proj.shape)
  logging.info('flat.shape: %s', flat.shape)
  logging.info('dark.shape: %s', dark.shape)
  if (dark_value != 0):
    dark = dark*0 + dark_value
  logging.info('dark[0]: %s', dark.item(0))
  logging.info('last theta: %s', theta[-1])

  logging.info('Normalizing')
  norm = tomopy.normalize(proj, flat, dark)
  print("After normalizing, min, max=", norm.min(), norm.max())

  #logging.info('Removing zingers. threshold, size=', zinger_threshold, zinger_filter_size)
  #tomopy.misc.corr.remove_outlier(norm, zinger_threshold, size=zinger_filter_size)
  #print("After remove_outlier, min, max=", norm.min(), norm.max())

  logging.info('Converting to integer')
  norm = (10000.*norm).astype(np.int16)

  logging.info('Writing volume file')
  dxchange.write_netcdf4(norm, fname=fname + '.volume')
  logging.info('Volume file written')

if __name__ == "__main__":
  num_args = len(sys.argv)
  if (num_args < 2) or (num_args > 3):
    print('Usage: preproccess_13bm base_file [dark_value]')
    exit
  fname = sys.argv[1]
  dark_value = 0
  if num_args == 3:
    dark_value = float(sys.argv[2])
  preprocess_13bm(fname, dark_value)
 