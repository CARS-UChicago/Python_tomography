import logging
import dxchange
import netCDF4
import numpy as np
import argparse

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
                           zstart=0, suffix='.h5',  
                           extensions='A B C D E F G H I'):
  logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
  file = base_file + '_' + extensions[0] + 'recon' + suffix
  extensions = extensions.split()
  logging.info('Extensions = %s', extensions)
  logging.info('Reading file %s', file)
  v = read_tomo_volume(file)
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
    file = base_file + '_' + extensions[i] + 'recon' + suffix
    logging.info('Reading file %s', file)
    v = read_tomo_volume(file)
    first_slice = (nz - pixel_overlap)*i
    last_slice = first_slice + nz
    if (zstart != 0):
      first_slice += zstart
      last_slice += zstart
      v = v[zstart:, :, :]
    logging.info('Inserting in volume array from slice %d to %d', first_slice, last_slice)
    vol[first_slice:last_slice, :, :] = v
    #if (zstart ne 0) then begin
    #    zrange = [zstart, nz-1]
    #    vol[0, 0, (((nz-pixel_overlap)*i) + zstart)] = read_tomo_volume(base_file + '_' + extensions[i] + 'recon' + suffix, zrange=zrange)
  file = base_file + 'combined_recon' + suffix
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
  parser.add_argument("-s", "--suffix", default='.h5',
                    help="file suffix (default='.h5')")
  parser.add_argument("-e", "--extensions", default='A B C D E F G H I',
                    help="file extensions (default='A B C D E F G H I')")
  args = parser.parse_args()
  combine_vertical_stack(args.base_file, args.num_files, 
      args.pixel_overlap, zstart=args.zstart, 
      suffix=args.suffix, extensions=args.extensions) 
 