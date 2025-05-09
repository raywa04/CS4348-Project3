import sys
import os
from btree_node import BTreeNode

BLOCK_SIZE = 512
MAGIC = b"4348PRJ3"
ROOT_ID_OFFSET = 8
NEXT_BLOCK_ID_OFFSET = 16

def write_header(file_path):
    with open(file_path, "wb") as f:
        block = bytearray(BLOCK_SIZE)
        block[0:8] = MAGIC
        block[8:16] = (0).to_bytes(8, 'big')
        block[16:24] = (1).to_bytes(8, 'big')
        f.write(block)

def read_header(file_path):
    with open(file_path, "rb") as f:
        block = f.read(BLOCK_SIZE)
        root_id = int.from_bytes(block[8:16], 'big')
        next_id = int.from_bytes(block[16:24], 'big')
        return root_id, next_id

def write_header_update(file_path, root_id, next_id):
    with open(file_path, "r+b") as f:
        block = bytearray(BLOCK_SIZE)
        block[0:8] = MAGIC
        block[8:16] = root_id.to_bytes(8, 'big')
        block[16:24] = next_id.to_bytes(8, 'big')
        f.seek(0)
        f.write(block)

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

def handle_search(file_path, key):
    root_id, _ = read_header(file_path)
    with open(file_path, "rb") as f:
        result = search_btree(f, root_id, int(key))
        if result is None:
            print("NOT FOUND")
        else:
            print(result)

def handle_print(file_path):
    root_id, _ = read_header(file_path)
    results = []
    with open(file_path, "rb") as f:
        inorder_traversal(f, root_id, results)
    for k, v in results:
        print(f"{k},{v}")

def handle_extract(file_path, out_path):
    root_id, _ = read_header(file_path)
    results = []
    with open(file_path, "rb") as f:
        inorder_traversal(f, root_id, results)
    with open(out_path, "w") as out:
        for k, v in results:
            out.write(f"{k},{v}\n")
    print(f"Extracted to {out_path}")

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
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
