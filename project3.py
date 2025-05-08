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
        block[ROOT_ID_OFFSET:ROOT_ID_OFFSET+8] = (0).to_bytes(8, 'big')
        block[NEXT_BLOCK_ID_OFFSET:NEXT_BLOCK_ID_OFFSET+8] = (1).to_bytes(8, 'big')
        f.write(block)

def read_header(file_path):
    with open(file_path, "rb") as f:
        block = f.read(BLOCK_SIZE)
        if block[0:8] != MAGIC:
            raise Exception("Invalid file format.")
        root_id = int.from_bytes(block[ROOT_ID_OFFSET:ROOT_ID_OFFSET+8], 'big')
        next_id = int.from_bytes(block[NEXT_BLOCK_ID_OFFSET:NEXT_BLOCK_ID_OFFSET+8], 'big')
        return root_id, next_id

def write_header_update(file_path, root_id, next_id):
    with open(file_path, "r+b") as f:
        block = bytearray(BLOCK_SIZE)
        block[0:8] = MAGIC
        block[ROOT_ID_OFFSET:ROOT_ID_OFFSET+8] = root_id.to_bytes(8, 'big')
        block[NEXT_BLOCK_ID_OFFSET:NEXT_BLOCK_ID_OFFSET+8] = next_id.to_bytes(8, 'big')
        f.seek(0)
        f.write(block)

def create_index(file_path):
    if os.path.exists(file_path):
        print("Error: File already exists.")
        sys.exit(1)
    write_header(file_path)
    print(f"Index file '{file_path}' created.")

def split_root(file_path, root_node, key, value, root_id, next_id):
    root_node.insert_and_sort(key, value)
    mid = root_node.num_keys // 2
    promoted_key = root_node.keys[mid]
    promoted_value = root_node.values[mid]

    left_node = root_node.clone_slice(new_block_id=root_id, start=0, end=mid)
    right_node = root_node.clone_slice(new_block_id=next_id, start=mid + 1, end=root_node.num_keys)

    new_root = BTreeNode(block_id=next_id + 1)
    new_root.keys[0] = promoted_key
    new_root.values[0] = promoted_value
    new_root.children[0] = root_id
    new_root.children[1] = next_id
    new_root.num_keys = 1

    with open(file_path, "r+b") as f:
        f.seek(root_id * BLOCK_SIZE)
        f.write(left_node.to_bytes())
        f.seek(next_id * BLOCK_SIZE)
        f.write(right_node.to_bytes())
        f.seek((next_id + 1) * BLOCK_SIZE)
        f.write(new_root.to_bytes())

    write_header_update(file_path, root_id=next_id + 1, next_id=next_id + 2)
    print(f"Root split. New root at block {next_id + 1}")

def insert(file_path, key, value):
    key, value = int(key), int(value)
    root_id, next_id = read_header(file_path)

    with open(file_path, "r+b") as f:
        if root_id == 0:
            node = BTreeNode(block_id=next_id)
            node.insert_kv(key, value)
            f.seek(next_id * BLOCK_SIZE)
            f.write(node.to_bytes())
            write_header_update(file_path, root_id=next_id, next_id=next_id + 1)
            print(f"Inserted {key}:{value} into new root at block {next_id}")
        else:
            f.seek(root_id * BLOCK_SIZE)
            block_bytes = f.read(BLOCK_SIZE)
            node = BTreeNode.from_bytes(block_bytes)
            if node.num_keys >= 19:
                split_root(file_path, node, key, value, root_id, next_id)
            else:
                node.insert_and_sort(key, value)
                f.seek(root_id * BLOCK_SIZE)
                f.write(node.to_bytes())
                print(f"Inserted {key}:{value} into existing root at block {root_id}")

def main():
    if len(sys.argv) < 3:
        print("Usage: project3 <command> <arguments>")
        return

    command = sys.argv[1]
    file_path = sys.argv[2]

    if command == "create":
        create_index(file_path)
    elif command == "insert":
        if len(sys.argv) < 5:
            print("Usage: project3 insert <file> <key> <value>")
            return
        insert(file_path, sys.argv[3], sys.argv[4])
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
