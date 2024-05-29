import json
import sys
import argparse
import os
from enum import IntEnum

# State of the upload, as saved in the output file.
# select.py Populates the "queued" list with subdirectories of the selection.
upload_state = {
    "completed": [],
    "queued": [],
    "failed": [],
}

class Entry_type(IntEnum):
    UNKNOWN = -1
    DIRECTORY = 0
    FILE = 1

### ENTRY SELECTION

# Recursively traverses the file tree.
def traverse(entry_path, entry):

    # Readout an entry based on its schema
    [ entry_name, entry_type, entry_size, *entry_children ] = entry

    # Batchable (i.e. considered a single, separate upload job) 
    # if within the size limit or is a file
    batchable = (entry_size <= args.max_batch_size) or (entry_type == int(Entry_type.FILE))

    # Determine relationship between this entry and the selected subdirectory
    common_path = os.path.commonpath([ entry_path, subdir_path ]) 
    contains_subdir = common_path == entry_path
    inside_subdir = common_path == subdir_path
    
    # If this entry is contained within the selected subdirectory, 
    # and is batchable, then add its path to the queue
    if (inside_subdir and batchable):
        upload_state["queued"].append(entry_path)

    # Otherwise, if this entry is contained within the selected subdirectory but is not batchable,
    # of if it contains the selected subdirectory, then we recurse further.
    elif (inside_subdir and not batchable) or contains_subdir:
        for child in entry_children:
            child_name = child[0]
            child_path = os.path.join(entry_path, child_name)
            traverse(child_path, child)

    # Otherwise do nothing

### WRITE

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='batch.py',
        description=
        """
    Based on the file tree generated by find.py,
    we batch upload directories with maximum total bytesize --max-batch-size,
    and individually upload files inside directories larger than --max-batch-size.
    This program creates these batches and add them to a queue (batch.json). 
        """
    )
    parser.add_argument('root', help='path to the root directory')
    parser.add_argument('--file-tree', help='path to the JSON file tree')
    parser.add_argument('--subdir', help='path to the top subdirectory to upload; defaults to the root')
    parser.add_argument('--max-batch-size', type=int, help='largest size (in bytes) for a batch')
    parser.add_argument('-o', '--out', help='output file')
    args = parser.parse_args()

    root_path = os.path.abspath(args.root)
    subdir_path = os.path.abspath(args.subdir)

    # Loads in the file tree (i.e. the top level entry)
    with open(args.file_tree) as f:
        root_entry = json.load(f)

    traverse(root_path, root_entry)
    if args.out:
        with open(args.out, "w") as f:
            json.dump(upload_state, f)
            f.write("\n")
    else:
        print(json.dumps(upload_state))

