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

# Devlog Entry - [05-08-2025, 1:50AM] (Session Begins)
### **Thoughts So Far:**  
Now that the `create` command is complete and working, it’s time to start building the `insert` command. The goal is to insert a key/value pair into the B-Tree. Since this is the first insert, it will also involve creating the root node (if it doesn’t exist). We'll keep it simple for now — no splits, just a flat insert into the root node if it's empty.

A key challenge is serializing and deserializing node structures using big-endian 8-byte values and ensuring the offsets match the node layout precisely. The node will be written to the block specified by `next_block_id`, and the header must then be updated to reflect the root node’s block ID and increment the next block ID.

---

## **Plan for This Session:**

### **Goal:**  
Implement a basic version of the `insert` command that:
- Loads the header block
- Creates a root node if none exists
- Adds a single key/value pair to the root node
- Writes the root node and updates the header accordingly

### **Steps:**
- Define BTreeNode class for node serialization and deserialization
- Implement insert logic:
  - Load header
  - Check if root node exists
  - If not, create a root node block, insert key/value, and update header
- Use only 1 node in memory for this step (root)
- Write helper functions for reading/writing blocks and big-endian conversions

---

# Devlog Entry - [05-08-2025, 2:20AM] (Session Ends)
### **Accomplishments:**  
- Implemented a `BTreeNode` class that supports:
  - Node initialization with default arrays
  - Insertion of a single key/value
  - Serialization to 512-byte block using big-endian format
- Wrote the first stage of the `insert` command:
  - Detects if the tree is empty
  - Creates and writes a root node with the given key/value
  - Updates the header with root block ID and next available block
- Successfully tested multiple inserts into empty files
- Confirmed block structure with a hex viewer

### **Problems Encountered:**  
- Made an off-by-8-byte error when laying out the fields — fixed after defining offsets more precisely
- Had to debug why inserted integers were not appearing correctly — issue was forgetting to use `.to_bytes(8, 'big')` in a couple of places

### **Additional Accomplishments:**
- Refactored read/write header functions to support reusability across commands
- Validated that file offsets are properly aligned to block boundaries

### **Goals for next session:**  
- Implement reading and deserializing a BTreeNode from disk
- Begin handling insertions into an existing root node (no splits yet)
- Add search logic for finding correct insert position in a non-empty root

---

# Devlog Entry - [05-08-2025, 2:25AM] (Session Begins)
### **Thoughts So Far:**  
Now that insertion into an empty tree works, the next step is handling insertions into an **existing root node**, as long as it has space. This is still a simplified scenario — we will not handle node splits or traversing deeper levels of the tree yet.

The idea is:
- Load the root node from the file
- Insert the new key/value if the node is not full
- Sort the key/value pairs for in-node ordering
- Rewrite the root node to disk  
This will help validate the B-Tree format and prepare us for handling deeper insertions and splits later.

---

## **Plan for This Session:**

### **Goal:**  
Enable the `insert` command to work on an existing root node that is not full.

### **Steps:**
- Add method to `BTreeNode` to read from bytes (`from_bytes`)
- Modify `insert` logic to load root node and insert if there’s room
- Sort key/value pairs inside the node to maintain order
- Rewrite updated node back to disk

---

# Devlog Entry - [05-08-2025, 2:50AM] (Session Ends)
### **Accomplishments:**  
- Implemented `from_bytes()` method to deserialize a node from disk
- Built `insert_and_sort()` to keep key/value pairs sorted after insertion
- Updated `insert()` to work on an existing root (if not full)
- Verified the insertions remain sorted and persisted across multiple runs
- Inserted up to 19 keys in a single-node tree, ensuring in-memory and on-disk state matched

### **Problems Encountered:**  
- Needed to carefully manage slice offsets when deserializing from bytes
- Initially forgot to update the node’s `num_keys` after sort — fixed

### **Additional Accomplishments:**  
- Confirmed the full cycle of loading → mutating → saving a node works correctly
- Cleaned up debug prints and added validation for key/value conversion

### **Goals for next session:**  
- Implement node splitting when inserting into a full root
- Create two children and promote the median key
- Begin enforcing the “3 nodes in memory” rule during splits

---

# Devlog Entry - [05-08-2025, 3:00AM] (Session Begins)

### **Thoughts So Far:**  
So far, I’ve implemented inserting into an empty tree and inserting into a non-full root node. Now I’m tackling the case where the root node is full — which requires **splitting the root**.

In a B-Tree, when the root node is full and a new key is inserted:
- The root node must be split into two children.
- The median key is promoted to a new root node.
- The existing root becomes the left child, and a new right child is created for the upper half of keys.

This step involves writing 3 nodes to disk:
1. Left child (existing root node, sliced to lower half)
2. Right child (newly created with upper half)
3. New root node (containing the promoted key and two child pointers)

This will also test how well I manage memory (stay under 3 nodes in memory).

---

## **Plan for This Session:**

### **Goal:**  
Implement root node splitting logic. If the root is full:
- Split into two nodes
- Promote the median key into a new root
- Update the header to point to the new root block

### **Steps:**
- Write a `split_root()` helper that:
  - Reads the full root node
  - Partitions keys/values into left and right
  - Creates a new root with promoted median
  - Updates header block with new root ID and increments next block ID
- Ensure only 3 nodes in memory are used:
  - Original root → becomes left child
  - New right child
  - New root



