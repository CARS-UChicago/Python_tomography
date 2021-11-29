# Python_tomography
GSECARS Python code

This is the help output for the preprocessing code:

(tomopy) D:\Data\tomo_user\Gardner\TC07>python -m preprocess_13bm --help
usage: preprocess_13bm.py [-h] [-d DARK_VALUE] [-t ZINGER_THRESHOLD]
                          [-s ZINGER_FILTER_SIZE]
                          filename

positional arguments:
  filename              name of hdf5 file

optional arguments:
  -h, --help            show this help message and exit
  -d DARK_VALUE, --dark_value DARK_VALUE
                        dark field value
  -t ZINGER_THRESHOLD, --zinger_threshold ZINGER_THRESHOLD
                        zinger threshold
  -s ZINGER_FILTER_SIZE, --zinger_filter_size ZINGER_FILTER_SIZE
                        zinger filter_size

