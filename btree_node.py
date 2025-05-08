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

    def insert_and_sort(self, key, value):
        if self.num_keys >= MAX_KEYS:
            raise Exception("Node is full.")
        self.keys[self.num_keys] = key
        self.values[self.num_keys] = value
        self.num_keys += 1
        kv_pairs = [(self.keys[i], self.values[i]) for i in range(self.num_keys)]
        kv_pairs.sort(key=lambda x: x[0])
        for i in range(self.num_keys):
            self.keys[i], self.values[i] = kv_pairs[i]

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
