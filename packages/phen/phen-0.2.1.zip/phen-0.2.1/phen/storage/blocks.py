#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Manager for storage of incomplete files (i.e. during download).
"""


class BlocksManager:
    def __init__(self, blocks, path, restart):
        self.blocks = blocks
        self.path = path
        # ignore any previous incompletely downloaded blocks
        if restart:
            cur_alloc = blocks.read().replace(b'a', b'0')
            self.mark(blk_type=cur_alloc)

    def mark(self, blk_id=0, blk_type=b'a'):
        self.blocks.seek(blk_id)
        self.blocks.write(blk_type)
        self.blocks.flush()

    def adjust(self, size):
        self.blocks.seek(0)
        cur_alloc = self.blocks.read()
        if len(cur_alloc) != size:
            cur_alloc += b'0' * (size - len(cur_alloc))
            self.mark(blk_type=cur_alloc)
        self.size = size
        return size

    def remaining(self):
        self.blocks.seek(0)
        cur_alloc = self.blocks.read()
        if not hasattr(self, "size"):
            self.size = len(cur_alloc)
        return cur_alloc.count(b'0'), len(cur_alloc) - 1

    def get_next(self, blk_id=0, blk_type=b'1'):
        self.blocks.seek(blk_id)
        state = self.blocks.read()
        if not state or state[0] != b'1':
            next_available = state.find(blk_type)
            if next_available < 0:
                return -1
            return blk_id + next_available
        return blk_id

    def alloc(self, blk_id=0, check_first=False):
        if check_first:
            self.blocks.seek(blk_id)
            if self.blocks.read(1) != b'0':
                return None
        self.mark(blk_id)
        cur_alloc = self.blocks.read()
        p = cur_alloc.find(b'0')
        if p < 0:
            return self.size
        else:
            return blk_id + 1 + p

    def finished(self, remove):
        self.blocks.close()
        if remove:
            import os
            os.unlink(self.path)
