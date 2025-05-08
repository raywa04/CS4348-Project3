import sys
import os

BLOCK_SIZE = 512
MAGIC = b"4348PRJ3"
HEADER_SIZE = BLOCK_SIZE
ROOT_ID_OFFSET = 8
NEXT_BLOCK_ID_OFFSET = 16

def write_header(file_path):
    with open(file_path, "wb") as f:
        # Block 0: Header
        block = bytearray(BLOCK_SIZE)
        block[0:8] = MAGIC
        block[ROOT_ID_OFFSET:ROOT_ID_OFFSET+8] = (0).to_bytes(8, 'big')  # Root ID
        block[NEXT_BLOCK_ID_OFFSET:NEXT_BLOCK_ID_OFFSET+8] = (1).to_bytes(8, 'big')  # Next block ID
        f.write(block)

def create_index(file_path):
    if os.path.exists(file_path):
        print("Error: File already exists.")
        sys.exit(1)
    write_header(file_path)
    print(f"Index file '{file_path}' created.")

def main():
    if len(sys.argv) < 3:
        print("Usage: project3 <command> <arguments>")
        return

    command = sys.argv[1]
    file_path = sys.argv[2]

    if command == "create":
        create_index(file_path)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
