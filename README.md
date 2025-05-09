# CS4348 Project 3 – B-Tree Index File Manager

## Author
Rayyan Waris

## Description
This project implements a disk-based B-Tree index manager that stores key-value pairs in fixed-size 512-byte blocks. The system supports essential file operations, including insertion, lookup, traversal, and extraction, while enforcing a strict memory limit of 3 in-memory nodes at any time.

---

## Files

| File            | Description                                           |
|-----------------|-------------------------------------------------------|
| `project3.py`   | Main driver program. Implements command handling logic. |
| `btree_node.py` | BTreeNode class. Handles byte encoding/decoding and insert logic. |
| `devlog.md`     | Development log with session-based entries.           |
| `input.csv`     | File to test load command                             |
| `README.md`     | This file.                                            |

---

Please note: the input.csv file has been included in submission to be used to load, but the test.idx file and output.csv must be generated through the commands.

## Commands

```bash
# Create a new index file
python3 project3.py create test.idx

# Insert a single key-value pair
python3 project3.py insert test.idx 15 100

# Search for a key
python3 project3.py search test.idx 15

# Load key-value pairs from a CSV file (format: key,value)
python3 project3.py load test.idx input.csv

# Print all key-value pairs in order
python3 project3.py print test.idx

# Extract key-value pairs to a CSV file
python3 project3.py extract test.idx output.csv
