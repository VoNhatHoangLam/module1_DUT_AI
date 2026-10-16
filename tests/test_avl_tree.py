"""Kiểm thử Cấu trúc Dữ liệu Cây AVL (AVLTree & MultiAVLTree)."""

import math
import random
import unittest

from utils import AVLTree, MultiAVLTree


class AVLTreeTestCase(unittest.TestCase):
    def test_empty_tree(self) -> None:
        tree = AVLTree[int, str]()
        self.assertTrue(tree.is_empty())
        self.assertEqual(len(tree), 0)
        self.assertEqual(tree.height(), 0)
        self.assertIsNone(tree.search(1))
        self.assertFalse(tree.contains(1))
        self.assertIsNone(tree.min_key())
        self.assertIsNone(tree.max_key())
        self.assertEqual(tree.inorder(), [])

    def test_single_element(self) -> None:
        tree = AVLTree[int, str]()
        tree.insert(10, "ten")

        self.assertFalse(tree.is_empty())
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree.height(), 1)
        self.assertEqual(tree.search(10), "ten")
        self.assertTrue(tree.contains(10))
        self.assertEqual(tree.min_key(), 10)
        self.assertEqual(tree.max_key(), 10)
        self.assertEqual(tree.inorder(), ["ten"])
        self.assertTrue(tree.is_balanced())

    def test_duplicate_insert_behavior(self) -> None:
        tree = AVLTree[int, str]()
        tree.insert(5, "five")

        with self.assertRaises(KeyError):
            tree.insert(5, "five_again")

        tree.insert(5, "five_updated", replace=True)
        self.assertEqual(tree.search(5), "five_updated")
        self.assertEqual(len(tree), 1)

    def test_rotations_left_left(self) -> None:
        # Chèn giảm dần 30 -> 20 -> 10 gây lệch trái, kích hoạt quay phải (LL)
        tree = AVLTree[int, int]()
        tree.insert(30, 30)
        tree.insert(20, 20)
        tree.insert(10, 10)

        self.assertTrue(tree.is_balanced())
        self.assertEqual(tree.root.key, 20)
        self.assertEqual(tree.height(), 2)
        self.assertEqual(tree.inorder(), [10, 20, 30])

    def test_rotations_right_right(self) -> None:
        # Chèn tăng dần 10 -> 20 -> 30 gây lệch phải, kích hoạt quay trái (RR)
        tree = AVLTree[int, int]()
        tree.insert(10, 10)
        tree.insert(20, 20)
        tree.insert(30, 30)

        self.assertTrue(tree.is_balanced())
        self.assertEqual(tree.root.key, 20)
        self.assertEqual(tree.height(), 2)
        self.assertEqual(tree.inorder(), [10, 20, 30])

    def test_rotations_left_right(self) -> None:
        # Chèn 30 -> 10 -> 20 gây lệch Trái - Phải (LR)
        tree = AVLTree[int, int]()
        tree.insert(30, 30)
        tree.insert(10, 10)
        tree.insert(20, 20)

        self.assertTrue(tree.is_balanced())
        self.assertEqual(tree.root.key, 20)
        self.assertEqual(tree.height(), 2)
        self.assertEqual(tree.inorder(), [10, 20, 30])

    def test_rotations_right_left(self) -> None:
        # Chèn 10 -> 30 -> 20 gây lệch Phải - Trái (RL)
        tree = AVLTree[int, int]()
        tree.insert(10, 10)
        tree.insert(30, 30)
        tree.insert(20, 20)

        self.assertTrue(tree.is_balanced())
        self.assertEqual(tree.root.key, 20)
        self.assertEqual(tree.height(), 2)
        self.assertEqual(tree.inorder(), [10, 20, 30])

    def test_delete_leaf(self) -> None:
        tree = AVLTree[int, str]()
        tree.insert(20, "20")
        tree.insert(10, "10")
        tree.insert(30, "30")

        self.assertTrue(tree.delete(10))
        self.assertEqual(len(tree), 2)
        self.assertIsNone(tree.search(10))
        self.assertEqual(tree.inorder(), ["20", "30"])
        self.assertTrue(tree.is_balanced())

    def test_delete_node_with_one_child(self) -> None:
        tree = AVLTree[int, str]()
        tree.insert(20, "20")
        tree.insert(10, "10")
        tree.insert(30, "30")
        tree.insert(25, "25")

        self.assertTrue(tree.delete(30))
        self.assertEqual(len(tree), 3)
        self.assertIsNone(tree.search(30))
        self.assertEqual(tree.inorder(), ["10", "20", "25"])
        self.assertTrue(tree.is_balanced())

    def test_delete_node_with_two_children(self) -> None:
        tree = AVLTree[int, str]()
        tree.insert(20, "20")
        tree.insert(10, "10")
        tree.insert(30, "30")
        tree.insert(25, "25")
        tree.insert(35, "35")

        self.assertTrue(tree.delete(20))
        self.assertEqual(len(tree), 4)
        self.assertIsNone(tree.search(20))
        self.assertEqual(tree.inorder(), ["10", "25", "30", "35"])
        self.assertTrue(tree.is_balanced())

    def test_delete_non_existent(self) -> None:
        tree = AVLTree[int, str]()
        tree.insert(1, "one")
        self.assertFalse(tree.delete(99))
        self.assertEqual(len(tree), 1)

    def test_large_random_dataset_preserves_balance(self) -> None:
        random.seed(42)
        keys = list(range(1, 1001))
        random.shuffle(keys)

        tree = AVLTree[int, int]()
        for k in keys:
            tree.insert(k, k * 2)

        self.assertEqual(len(tree), 1000)
        self.assertTrue(tree.is_balanced())

        # Theo định lý AVL, chiều cao tối đa không vượt quá 1.44 * log2(N + 2)
        max_theoretical_height = 1.45 * math.log2(1000 + 2)
        self.assertLessEqual(tree.height(), max_theoretical_height)

        # Kiểm tra tính chính xác của tìm kiếm
        for k in keys:
            self.assertEqual(tree.search(k), k * 2)

        # Xóa 500 phần tử ngẫu nhiên và kiểm tra tính cân bằng
        for k in keys[:500]:
            self.assertTrue(tree.delete(k))

        self.assertEqual(len(tree), 500)
        self.assertTrue(tree.is_balanced())

        for k in keys[:500]:
            self.assertIsNone(tree.search(k))

        for k in keys[500:]:
            self.assertEqual(tree.search(k), k * 2)


class MultiAVLTreeTestCase(unittest.TestCase):
    def test_multi_tree_operations(self) -> None:
        mtree = MultiAVLTree[str, int]()
        mtree.insert("fruit", 1)
        mtree.insert("fruit", 2)
        mtree.insert("vegetable", 3)
        mtree.insert("fruit", 4)

        self.assertEqual(len(mtree), 4)
        self.assertEqual(mtree.search("fruit"), [1, 2, 4])
        self.assertEqual(mtree.search("vegetable"), [3])
        self.assertEqual(mtree.search("meat"), [])

        # Xóa phần tử
        self.assertTrue(mtree.remove("fruit", 2))
        self.assertEqual(mtree.search("fruit"), [1, 4])
        self.assertEqual(len(mtree), 3)

        # Cập nhật chuyển nhóm
        mtree.update_record(old_key="fruit", new_key="vegetable", value=4)
        self.assertEqual(mtree.search("fruit"), [1])
        self.assertEqual(mtree.search("vegetable"), [3, 4])


if __name__ == "__main__":
    unittest.main()
