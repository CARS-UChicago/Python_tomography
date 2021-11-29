import logging
import sys
import dxchange
import tomopy
import numpy as np
import argparse

def preprocess_13bm(fname, dark_value=None, zinger_threshold=0.2, zinger_filter_size=3):
  logging.basicConfig(
    #filename=fname + '_preprocess.log',
    #filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

  logging.info('Reading data')
  proj, flat, dark, theta = dxchange.read_aps_13bm(fname + '.h5', 'hdf5')
  logging.info('proj.shape: %s', proj.shape)
  logging.info('flat.shape: %s', flat.shape)
  logging.info('dark.shape: %s', dark.shape)
  if (dark_value != None):
    dark = dark*0 + dark_value
  logging.info('dark[0]: %s', dark.item(0))
  logging.info('last theta: %s', theta[-1])

  logging.info('Normalizing')
  proj = tomopy.normalize(proj, flat, dark)
  logging.info("After normalizing, min=%f, max=%f", proj.min(), proj.max())

  logging.info('Removing zingers. threshold=%f, size=%d', zinger_threshold, zinger_filter_size)
  proj = tomopy.misc.corr.remove_outlier(proj, zinger_threshold, size=zinger_filter_size)
  logging.info("After remove_outlier, min=%f, max=%f", proj.min(), proj.max())

  logging.info('Converting to integer')
  proj = (10000.*proj).astype(np.int16)

  logging.info('Writing volume file')
  dxchange.write_netcdf4(proj, fname=fname + '.volume')
  logging.info('Volume file written')

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("filename",
                    help="name of hdf5 file")
  parser.add_argument("-d", "--dark_value", type=float,
                    help="dark field value")
  parser.add_argument("-t", "--zinger_threshold", type=float, default=0.2,
                    help="zinger threshold")
  parser.add_argument("-s", "--zinger_filter_size", type=int, default=3,
                    help="zinger filter_size")
  args = parser.parse_args()
  preprocess_13bm(args.filename, args.dark_value,
      zinger_threshold=args.zinger_threshold, zinger_filter_size=args.zinger_filter_size)
 