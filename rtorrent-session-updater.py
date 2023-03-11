from argparse import ArgumentParser
import glob
import re

# Read new .rtorrent parent directory from command-line argument.
parser = ArgumentParser(description='Change tied_to_file path in Rtorrent '
                                    'session files.')
parser.add_argument('--new-parent-dir', required = False)
args = parser.parse_args()

# Get list of files.
files = glob.glob('[0-9A-F]' * 40 + '.torrent.rtorrent')

# Read file contents into Python.
contents = []
for file in files:
    with open(file, "r") as f:
        contents.append(f.read())

parent_dir_lambda = lambda x: re.sub(r'.*tied_to_file\d+:(.*)\.rtorrent.*',
                                     r'\1', x)
parent_dirs = list(set(list(map(parent_dir_lambda, contents))))
number_of_parent_dirs = len(parent_dirs)

# Quit if more than one .rtorrent/ parent directory was found.
if number_of_parent_dirs != 1:
    print('More than one parent directory found. This is not supported by the '
          'current implementation. Quiting.')
    quit()
else:
    parent_dir = parent_dirs[0]

# Display current path of .rtorrent/ parent directory.
print('Current .rtorrent/ parent directory in all session files: {}'\
        .format('\n'.join(parent_dirs)) + '\n')

# Quit if no command-line argument was given. 
if args.new_parent_dir == None:
    print('No new .rtorrent parent directory specified. Use the '
          '--new-parent-dir command-line argument to do so.')

# Replace tied_to_file parent directory with new parent directory.
for file in zip(files, contents):
    # Extract the character length of the current torrent file path. This is
    # used as checksum of the value of tied_to_file. Therefore, it has to be
    # adjusted to the character length of its new value.
    char_len = int(re.sub(r'.*tied_to_file(\d+):.*', r'\1', file[1]))

    # Increment this with (character length of the new parent directory minus
    # the character length of the current parent directory) to get the new
    # checksum value.
    new_char_len = char_len + (len(args.new_parent_dir) - len(parent_dir))

    # Write the new content to file
    new_content = re.sub(r'tied_to_file\d+:.*.rtorrent/',
                         r'tied_to_file{}:{}.rtorrent/'.format(new_char_len, \
                           args.new_parent_dir),
                         file[1])
    with open(file[0], 'w') as f:
        f.write(new_content)
