"""Kiểm thử hàng đợi và chức năng học flashcard."""

import unittest

from models import Card
from services import FlashcardStudyQueue, NoCardToReviewError
from utils import EmptyQueueError, Queue


class QueueTestCase(unittest.TestCase):
    def test_queue_uses_fifo_order(self) -> None:
        queue = Queue[int]()
        queue.enqueue(1)
        queue.enqueue(2)
        queue.enqueue(3)

        self.assertEqual(queue.peek(), 1)
        self.assertEqual(queue.dequeue(), 1)
        self.assertEqual(queue.dequeue(), 2)
        self.assertEqual(queue.dequeue(), 3)
        self.assertTrue(queue.is_empty())

    def test_empty_queue_raises_clear_error(self) -> None:
        queue = Queue[str]()

        with self.assertRaises(EmptyQueueError):
            queue.dequeue()
        with self.assertRaises(EmptyQueueError):
            queue.peek()


class FlashcardStudyQueueTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.card_one = Card(
            card_id=100,
            deck_id=10,
            front_text="Apple",
            back_text="Quả táo",
            position=1,
        )
        self.card_two = Card(
            card_id=101,
            deck_id=10,
            front_text="Banana",
            back_text="Quả chuối",
            position=2,
        )
        self.card_three = Card(
            card_id=102,
            deck_id=10,
            front_text="Cat",
            back_text="Con mèo",
            position=3,
        )

    def test_unknown_card_moves_to_end_of_queue(self) -> None:
        study_queue = FlashcardStudyQueue(
            [self.card_three, self.card_one, self.card_two]
        )

        study_queue.mark_unknown()

        self.assertEqual(study_queue.current_card, self.card_two)
        self.assertEqual(study_queue.remaining_count, 3)

        study_queue.mark_known()
        study_queue.mark_known()

        self.assertEqual(study_queue.current_card, self.card_one)

    def test_known_cards_are_removed_until_session_is_complete(self) -> None:
        study_queue = FlashcardStudyQueue([self.card_one, self.card_two])

        study_queue.review_current_card(is_known=True)
        study_queue.review_current_card(is_known=True)

        self.assertTrue(study_queue.is_completed)
        self.assertEqual(study_queue.remaining_count, 0)
        self.assertIsNone(study_queue.current_card)

    def test_reviewing_completed_session_raises_clear_error(self) -> None:
        study_queue = FlashcardStudyQueue([])

        with self.assertRaises(NoCardToReviewError):
            study_queue.mark_known()


if __name__ == "__main__":
    unittest.main()
