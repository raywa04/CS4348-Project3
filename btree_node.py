BLOCK_SIZE = 512
DEGREE = 10
MAX_KEYS = 2 * DEGREE - 1  # 19
MAX_CHILDREN = 2 * DEGREE  # 20

class BTreeNode:
    def __init__(self, block_id, parent_id=0, num_keys=0):
        self.block_id = block_id
        self.parent_id = parent_id
        self.num_keys = num_keys
        self.keys = [0] * MAX_KEYS
        self.values = [0] * MAX_KEYS
        self.children = [0] * MAX_CHILDREN

    def insert_kv(self, key, value):
        if self.num_keys >= MAX_KEYS:
            raise Exception("Node is full. Splitting not yet implemented.")
        self.keys[self.num_keys] = key
        self.values[self.num_keys] = value
        self.num_keys += 1

    def to_bytes(self):
        b = bytearray(BLOCK_SIZE)
        b[0:8] = self.block_id.to_bytes(8, 'big')
        b[8:16] = self.parent_id.to_bytes(8, 'big')
        b[16:24] = self.num_keys.to_bytes(8, 'big')
        offset = 24
        for i in range(MAX_KEYS):
            b[offset:offset+8] = self.keys[i].to_bytes(8, 'big')
            offset += 8
        for i in range(MAX_KEYS):
            b[offset:offset+8] = self.values[i].to_bytes(8, 'big')
            offset += 8
        for i in range(MAX_CHILDREN):
            b[offset:offset+8] = self.children[i].to_bytes(8, 'big')
            offset += 8
        return b
