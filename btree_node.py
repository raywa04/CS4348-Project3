# Constants for B-Tree structure
BLOCK_SIZE = 512          # Fixed block size per node (in bytes)
DEGREE = 10               # Minimum degree (t); controls branching factor
MAX_KEYS = 2 * DEGREE - 1 # Maximum keys per node (t-1 keys for leaves/internal)
MAX_CHILDREN = 2 * DEGREE # Maximum children per node

class BTreeNode:
    def __init__(self, block_id, parent_id=0, num_keys=0):
        self.block_id = block_id       # Disk block ID where this node is stored
        self.parent_id = parent_id     # Block ID of the parent node
        self.num_keys = num_keys       # Number of valid key-value pairs
        self.keys = [0] * MAX_KEYS     # Keys (sorted)
        self.values = [0] * MAX_KEYS   # Corresponding values
        self.children = [0] * MAX_CHILDREN # Children block pointers (0 = null)

    # Inserts a key-value pair at the end (used only when node has space)
    def insert_kv(self, key, value):
        if self.num_keys >= MAX_KEYS:
            raise Exception("Node is full. Splitting not yet implemented.")
        self.keys[self.num_keys] = key
        self.values[self.num_keys] = value
        self.num_keys += 1

    # Inserts and sorts key-value pair by key order
    def insert_and_sort(self, key, value):
        if self.num_keys >= MAX_KEYS:
            raise Exception("Node is full.")
        self.keys[self.num_keys] = key
        self.values[self.num_keys] = value
        self.num_keys += 1

        # Zip, sort, and unpack keys/values for consistent order
        kv_pairs = [(self.keys[i], self.values[i]) for i in range(self.num_keys)]
        kv_pairs.sort(key=lambda x: x[0])
        for i in range(self.num_keys):
            self.keys[i], self.values[i] = kv_pairs[i]

    # Serializes the node into a 512-byte block
    def to_bytes(self):
        b = bytearray(BLOCK_SIZE)
        b[0:8] = self.block_id.to_bytes(8, 'big')
        b[8:16] = self.parent_id.to_bytes(8, 'big')
        b[16:24] = self.num_keys.to_bytes(8, 'big')
        offset = 24

        # Write all keys
        for i in range(MAX_KEYS):
            b[offset:offset+8] = self.keys[i].to_bytes(8, 'big')
            offset += 8
        # Write all values
        for i in range(MAX_KEYS):
            b[offset:offset+8] = self.values[i].to_bytes(8, 'big')
            offset += 8
        # Write all children pointers
        for i in range(MAX_CHILDREN):
            b[offset:offset+8] = self.children[i].to_bytes(8, 'big')
            offset += 8
        return b

    # Deserializes a 512-byte block into a BTreeNode
    @staticmethod
    def from_bytes(block_bytes):
        node = BTreeNode(
            block_id=int.from_bytes(block_bytes[0:8], 'big'),
            parent_id=int.from_bytes(block_bytes[8:16], 'big'),
            num_keys=int.from_bytes(block_bytes[16:24], 'big')
        )
        offset = 24
        for i in range(MAX_KEYS):
            node.keys[i] = int.from_bytes(block_bytes[offset:offset+8], 'big')
            offset += 8
        for i in range(MAX_KEYS):
            node.values[i] = int.from_bytes(block_bytes[offset:offset+8], 'big')
            offset += 8
        for i in range(MAX_CHILDREN):
            node.children[i] = int.from_bytes(block_bytes[offset:offset+8], 'big')
            offset += 8
        return node

    # Creates a shallow copy (slice) of a subset of key-value pairs
    def clone_slice(self, new_block_id, start, end):
        new_node = BTreeNode(block_id=new_block_id, parent_id=0)
        new_node.num_keys = end - start
        for i in range(start, end):
            new_node.keys[i - start] = self.keys[i]
            new_node.values[i - start] = self.values[i]
        return new_node

    # Returns index of the child pointer where a key would go
    def find_child_index(self, key):
        for i in range(self.num_keys):
            if key < self.keys[i]:
                return i
        return self.num_keys

    # Checks if this node is a leaf (all child pointers are null/0)
    def is_leaf(self):
        return all(ptr == 0 for ptr in self.children[:self.num_keys + 1])
