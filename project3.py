import sys
import os
from btree_node import BTreeNode  # Custom BTreeNode class from external file

# Constants
BLOCK_SIZE = 512  # fixed block size for each node
MAGIC = b"4348PRJ3"  # file header signature
ROOT_ID_OFFSET = 8
NEXT_BLOCK_ID_OFFSET = 16

# Writes an initial header block with root_id = 0 and next_id = 1
def write_header(file_path):
    with open(file_path, "wb") as f:
        block = bytearray(BLOCK_SIZE)
        block[0:8] = MAGIC
        block[8:16] = (0).to_bytes(8, 'big')
        block[16:24] = (1).to_bytes(8, 'big')
        f.write(block)

# Reads the root_id and next available block_id from the header
def read_header(file_path):
    with open(file_path, "rb") as f:
        block = f.read(BLOCK_SIZE)
        root_id = int.from_bytes(block[8:16], 'big')
        next_id = int.from_bytes(block[16:24], 'big')
        return root_id, next_id

# Updates the header block with the current root_id and next available block
def write_header_update(file_path, root_id, next_id):
    with open(file_path, "r+b") as f:
        block = bytearray(BLOCK_SIZE)
        block[0:8] = MAGIC
        block[8:16] = root_id.to_bytes(8, 'big')
        block[16:24] = next_id.to_bytes(8, 'big')
        f.seek(0)
        f.write(block)

# Recursively searches the B-Tree for a key and returns its value or None
def search_btree(file, block_id, key):
    file.seek(block_id * BLOCK_SIZE)
    block_bytes = file.read(BLOCK_SIZE)
    node = BTreeNode.from_bytes(block_bytes)

    for i in range(node.num_keys):
        if key == node.keys[i]:
            return node.values[i]
        elif key < node.keys[i]:
            if node.children[i] == 0:
                return None
            return search_btree(file, node.children[i], key)
    if node.children[node.num_keys] != 0:
        return search_btree(file, node.children[node.num_keys], key)
    return None

# Recursively traverses the tree in-order and stores key-value pairs in 'results'
def inorder_traversal(file, block_id, results):
    file.seek(block_id * BLOCK_SIZE)
    block_bytes = file.read(BLOCK_SIZE)
    node = BTreeNode.from_bytes(block_bytes)

    for i in range(node.num_keys):
        if node.children[i] != 0:
            inorder_traversal(file, node.children[i], results)
        results.append((node.keys[i], node.values[i]))
    if node.children[node.num_keys] != 0:
        inorder_traversal(file, node.children[node.num_keys], results)

# Command: search <file> <key>
def handle_search(file_path, key):
    root_id, _ = read_header(file_path)
    with open(file_path, "rb") as f:
        result = search_btree(f, root_id, int(key))
        if result is None:
            print("NOT FOUND")
        else:
            print(result)

# Command: print <file>
def handle_print(file_path):
    root_id, _ = read_header(file_path)
    results = []
    with open(file_path, "rb") as f:
        inorder_traversal(f, root_id, results)
    for k, v in results:
        print(f"{k},{v}")

# Command: extract <file> <outfile>
def handle_extract(file_path, out_path):
    root_id, _ = read_header(file_path)
    results = []
    with open(file_path, "rb") as f:
        inorder_traversal(f, root_id, results)
    with open(out_path, "w") as out:
        for k, v in results:
            out.write(f"{k},{v}\n")
    print(f"Extracted to {out_path}")

# Command: insert <file> <key> <value>
def insert(file_path, key, value):
    key, value = int(key), int(value)
    root_id, next_id = read_header(file_path)

    with open(file_path, "r+b") as f:
        if root_id == 0:
            # Tree is empty, create new root
            node = BTreeNode(block_id=next_id)
            node.insert_kv(key, value)
            f.seek(next_id * BLOCK_SIZE)
            f.write(node.to_bytes())
            write_header_update(file_path, root_id=next_id, next_id=next_id + 1)
            print(f"Inserted {key}:{value} into new root at block {next_id}")
        else:
            # Insert into existing root
            f.seek(root_id * BLOCK_SIZE)
            block_bytes = f.read(BLOCK_SIZE)
            node = BTreeNode.from_bytes(block_bytes)
            if node.num_keys >= 19:
                print("Root node full. Splitting not implemented in this version.")
                return
            node.insert_and_sort(key, value)
            f.seek(root_id * BLOCK_SIZE)
            f.write(node.to_bytes())
            print(f"Inserted {key}:{value} into existing root at block {root_id}")

# Command: load <file> <csvfile>
def handle_load(file_path, csv_path):
    if not os.path.exists(csv_path):
        print(f"CSV file '{csv_path}' not found.")
        return
    with open(csv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue
            key_str, value_str = line.split(",", 1)
            try:
                insert(file_path, int(key_str), int(value_str))
            except ValueError:
                print(f"Invalid line skipped: {line}")

# Entry point — parses and runs the appropriate command
def main():
    if len(sys.argv) < 3:
        print("Usage: project3 <command> <arguments>")
        return

    command = sys.argv[1]
    file_path = sys.argv[2]

    if command == "create":
        write_header(file_path)
        print(f"Index file '{file_path}' created.")
    elif command == "search":
        if len(sys.argv) < 4:
            print("Usage: project3 search <file> <key>")
            return
        handle_search(file_path, sys.argv[3])
    elif command == "print":
        handle_print(file_path)
    elif command == "extract":
        if len(sys.argv) < 4:
            print("Usage: project3 extract <file> <outfile>")
            return
        handle_extract(file_path, sys.argv[3])
    elif command == "insert":
        if len(sys.argv) < 5:
            print("Usage: project3 insert <file> <key> <value>")
            return
        insert(file_path, sys.argv[3], sys.argv[4])
    elif command == "load":
        if len(sys.argv) < 4:
            print("Usage: project3 load <indexfile> <csvfile>")
            return
        handle_load(file_path, sys.argv[3])
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
