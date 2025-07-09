import h5py

def replace_flat_fields(bad_file_name, good_file_name):
  bad_file = h5py.File(bad_file_name, 'r+')
  bad_flat = bad_file['/exchange/data_white']
  good_file = h5py.File(good_file_name, 'r')
  good_flat = good_file['/exchange/data_white']
  bad_flat[...] = good_flat
  bad_file.close()
  good_file.close()
