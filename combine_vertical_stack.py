import logging
import dxchange
import netCDF4
import numpy as np
import argparse
from numpy.lib.stride_tricks import as_strided

# This code is taken from the https://github.com/sbrisard/rebin/blob/master/rebin.py code.
# I just changed the last line to be able to specify that the dtype should be preserved.
# It was returning float64.

def rebin(a, factor, func=None):
  a = np.asarray(a)
  dim = a.ndim
  if np.isscalar(factor):
      factor = dim*(factor,)
  elif len(factor) != dim:
    raise ValueError('length of factor must be {} (was {})'
                       .format(dim, len(factor)))
  if func is None:
    func = np.mean
  for f in factor:
    if f != int(f):
      raise ValueError('factor must be an int or a tuple of ints '
                       '(got {})'.format(f))

  new_shape = [n//f for n, f in zip(a.shape, factor)]+list(factor)
  new_strides = [s*f for s, f in zip(a.strides, factor)]+list(a.strides)
  logging.info('a.dtype=%s, a.shape=%s, a.min()=%d, a.max()=%d', a.dtype, a.shape, a.min(), a.max())
  aa = as_strided(a, shape=new_shape, strides=new_strides)
  logging.info('aa.dtype=%s, aa.shape=%s, aa.min()=%d, aa.max()=%d', aa.dtype, aa.shape, aa.min(), aa.max())
  out = func(aa, axis=tuple(range(-dim, 0))).astype(a.dtype)
  logging.info('out.dtype=%s, out.shape=%s, out.min()=%d, out.max()=%d', out.dtype, out.shape, out.min(), out.max())
  return out

def read_tomo_volume(file):
  if file.endswith('h5'):
    data = dxchange.read_hdf5(file, '/exchange/data')
  else:
    # We cannot use dxchange.read_netcdf4(file, 'VOLUME') because the data will be scaled to float64
    # because of the scale_factor attribute in the netCDF files written by tomo_display.
    # Use the native netCDF4 functions and disable autoscaling
    f = netCDF4.Dataset(file, 'r')
    arr = f.variables['VOLUME']
    arr.set_auto_scale(False)
    data = arr[()]
    f.close()
  return data

def write_tomo_volume(file, data):
  if file.endswith('h5'):
    dxchange.write_hdf5(data, fname=file, gname='exchange', dname='data', overwrite=True)
  else:
    dxchange.write_netcdf4(data, fname=file, dname='VOLUME', overwrite=True)

def combine_vertical_stack(base_file, num_files, pixel_overlap, 
                           zstart=0, extension='.h5', binning=1,
                           suffix='A B C D E F G H I'):
  logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
  file = base_file + '_' + suffix[0] + 'recon' + extension
  suffix = suffix.split()
  logging.info('Suffixes = %s', suffix)
  logging.info('Reading file %s', file)
  v = read_tomo_volume(file)
  if (binning != 1):
    logging.info('Rebinning')
    v = rebin(v, binning)
    zstart = int(zstart/binning)
    pixel_overlap = int(pixel_overlap/binning)
  nx = v.shape[2]
  ny = v.shape[1]
  nz = v.shape[0]
     
  logging.info('Read file %s, dimensions=%d %d %d, datatype=%s', file, v.shape[0], v.shape[1], v.shape[2], v.dtype)
  nz_total = nz + (num_files-1) * (nz - pixel_overlap)
  logging.info('Creating empty array, dimensions = %d %d %d', nz_total, ny, nx)
  vol = np.empty((nz_total, ny, nx),dtype=v.dtype)
  logging.info('Inserting into volume array from slice %d to %d', 0, nz)
  vol[0:nz,:,:] = v
  for i in np.arange(1, num_files):
    file = base_file + '_' + suffix[i] + 'recon' + extension
    logging.info('Reading file %s', file)
    v = read_tomo_volume(file)
    if (binning != 1):
      logging.info('Rebinning')
      v = rebin(v, binning)
    first_slice = (nz - pixel_overlap)*i
    last_slice = first_slice + nz
    if (zstart != 0):
      first_slice += zstart
      last_slice += zstart
      v = v[zstart:, :, :]
    logging.info('Inserting in volume array from slice %d to %d', first_slice, last_slice)
    vol[first_slice:last_slice, :, :] = v
  file = base_file + 'combined_recon' + extension
  logging.info('Writing combined volume %s', file)
  write_tomo_volume(file, vol)
  logging.info('Done')

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("base_file",
                    help="base file name")
  parser.add_argument("num_files", type=int,
                    help="number of files")
  parser.add_argument("pixel_overlap", type=int,
                    help="number of overlappped pixels")
  parser.add_argument("-z", "--zstart", type=int, default=0,
                    help="first z value in second and subsequent files (default=0)")
  parser.add_argument("-b", "--binning", type=int, default=1,
                    help="binning for output (default=1, no binning)")
  parser.add_argument("-e", "--extension", default='.h5',
                    help="file extension (default='.h5')")
  parser.add_argument("-s", "--suffix", default='A B C D E F G H I',
                    help="file suffix (default='A B C D E F G H I')")
  args = parser.parse_args()
  combine_vertical_stack(args.base_file, args.num_files, 
      args.pixel_overlap, zstart=args.zstart, binning=args.binning,
      suffix=args.suffix, extension=args.extension) 
 