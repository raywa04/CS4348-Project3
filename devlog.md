# Devlog Entry - [05-07-2025, 11:30PM] (Initial Planning)

### **Thoughts So Far:**

This project requires building an interactive command-line tool that implements and manages B-Tree-based index files. The index file operations include `create`, `insert`, `search`, `load`, `print`, and `extract`. All data is persisted on disk, and the index file is structured in 512-byte blocks.

Each block may either be a **header** or a **B-Tree node**. The header resides in block 0 and contains a magic number (`4348PRJ3`), the block ID of the root node, and the ID of the next available block. Every B-Tree node fits entirely in a single block and contains:
- Block ID
- Parent ID
- Number of keys
- Arrays of 19 keys, 19 values, and 20 child pointers

Some key constraints:
- All integers must be stored as 8-byte big-endian values
- Only 3 B-Tree nodes can be loaded in memory at any given time
- Minimal degree of the B-Tree is 10 (i.e., each node supports up to 19 key/value pairs)

---

### **Planning Overview:**

Here’s how I plan to break down the project:

#### Phase 1: Infrastructure & Basic Commands
- Implement the `create` command to initialize an index file with a proper header block
- Define shared constants and utility methods for reading/writing 8-byte big-endian values
- Build a file I/O wrapper to abstract away block-based reading/writing

#### Phase 2: B-Tree Nodes & Insertion
- Design the in-memory representation of a B-Tree node
- Implement serialization and deserialization of node data to/from 512-byte blocks
- Handle basic insertion into the root node (without splits)
- Update the header to reflect changes in root ID and next block ID

#### Phase 3: Recursive Insert & Search
- Handle recursive insertions and node splits
- Build tree traversal logic for search
- Manage memory to ensure no more than 3 nodes are ever loaded at once

#### Phase 4: Remaining Commands
- `load`: bulk insert from CSV file
- `print`: output all key/value pairs in the tree
- `extract`: save tree contents to a CSV file

#### Phase 5: Testing & Final Polish
- Add helper tools for debugging (e.g., block dumpers)
- Manual testing of corner cases (empty tree, duplicate keys, large inserts)
- Final README and devlog polish

# Devlog Entry - [05-08-2025, 1:00AM] (Session Begins)
### **Thoughts So Far:**  
This project is centered around creating an interactive command-line tool that manages B-Tree-based index files on disk. It supports commands like `create`, `insert`, `search`, `load`, `print`, and `extract`. The B-Tree must follow strict rules:
- Only 3 nodes can exist in memory at any time.
- Each node and header is exactly 512 bytes.
- All integers are 8-byte big-endian.
- The minimal degree is 10 (19 key-value pairs, 20 children).

I’m planning to approach this incrementally, starting with foundational infrastructure and then layering in features.

---

## **Plan for This Session:**

### **Goal:**  
Set up the project environment and fully implement the `create` command, which generates a new index file with a valid 512-byte header block.

### **Steps:**  
- Set up Git repository and `devlog.md`
- Create base Python script: `project3.py`
- Define constants (block size, offsets)
- Implement `create` command:
  - Check if file exists
  - Write header block with magic number, root ID (0), and next block ID (1)
  - Use big-endian encoding and bytearrays
- Ensure the header conforms exactly to the PDF spec

---

# Devlog Entry - [05-09-2025, 1:45AM] (Session Ends)
### **Accomplishments:**  
- Repository initialized and `devlog.md` created and committed.
- Implemented and tested `create` command:
  - Validates existence of the file
  - Creates a 512-byte header block with:
    - Magic bytes: `4348PRJ3`
    - Root block ID: `0`
    - Next block ID: `1`
  - Everything written in 8-byte big-endian format.
- Verified the output file using a hex editor to confirm proper byte alignment and structure.
- Wrote reusable `write_header()` helper function.

### **Problems Encountered:**  
- Minor confusion initially about how to align offsets for header fields, but resolved by defining named constants and slicing into the bytearray precisely.

### **Additional Accomplishments:**  
- Set up command parsing for future commands in `main()`
- Validated structure with custom debug utility that prints raw byte output
- Added in-line comments for clarity

### **Goals for next session:**  
- Begin implementing the `insert` command:
  - Define in-memory representation of a node block
  - Add serialization/deserialization logic for a single node
  - Insert key-value pair into a new root node (no splits yet)
  - Update header’s root ID and next block ID after insertion

