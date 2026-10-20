from typing import Optional
from collections import deque
from models import Card
class DeckService:
    def __init__(self, card_repository=None):
        # ... (giữ nguyên phần khởi tạo của dự án) ...
        self.card_repository = card_repositor
        # Khai báo cấu trúc dữ liệu Queue (Hàng đợi hai đầu) để quản lý phiên học
        # Key là deck_id (int), Value là một deque chứa các đối tượng Card
        self.learning_queues: dict[int, deque[Card]] = {}
    #2 CHỨC NĂNG LIÊN QUAN ĐẾN QUEUE
    def view_deck_detail_queue(self, deck_id: int) -> Optional[Card]:
        """
        Tính năng 5: Xem chi tiết bộ thẻ (Dùng queue)
        Bắt đầu một phiên học mới, nạp tất cả các thẻ vào queue (mặc định chưa thuộc).
        [INPUT]
            - deck_id (int): ID của bộ thẻ mà người dùng muốn học.       
        [OUTPUT]
            - Card: Đối tượng thẻ nằm ở cuối queue để hiển thị.
            - None: Nếu bộ thẻ rỗng hoặc người dùng đã học thuộc hết tất cả.        
        [LOGIC]
            1. Kiểm tra xem bộ thẻ này đã có hàng đợi học hay chưa.
            2. Nếu chưa, lấy tất cả thẻ của bộ thẻ này từ DB và đẩy vào deque.
            3. Trả về thẻ ở vị trí cuối cùng của deque (queue[-1]).
        """
        # Nếu chưa có phiên học cho deck_id này, tiến hành khởi tạo
        if deck_id not in self.learning_queues:
            # Lấy toàn bộ thẻ của deck_id này từ database/file 
            all_cards = [
                card for card in self.card_repository.get_all() 
                if card.deck_id == deck_id
            ]
            # Nếu bộ thẻ không có thẻ nào, trả về None
            if not all_cards:
                return None    
            # Đưa tất cả flashcard vào queue. Ban đầu mặc định tất cả đều chưa thuộc.
            self.learning_queues[deck_id] = deque(all_cards)
        queue = self.learning_queues[deck_id]
        # Nếu queue rỗng (người dùng đã học xong phiên này)
        if not queue:
            return None    
        # Trả về thẻ ở CUỐI queue để hiển thị (không xóa khỏi queue)
        return queue[-1]
    def record_card_result_queue(self, deck_id: int, is_memorized: bool) -> Optional[Card]:
        """
        Tính năng 6: Ghi nhận kết quả lật thẻ (Dùng queue)
        Xử lý thẻ hiện tại và trả về thẻ tiếp theo.
        [INPUT]
            - deck_id (int): ID của bộ thẻ đang học.
            - is_memorized (bool): Kết quả đánh giá. 
                                   True -> Đã thuộc, False -> Chưa thuộc.                           
        [OUTPUT]
            - Card: Đối tượng thẻ tiếp theo (nằm ở cuối queue) để tiếp tục hiển thị.
            - None: Nếu hàng đợi rỗng (đã học xong toàn bộ thẻ trong phiên).     
        [LOGIC]
            1. Rút thẻ đang hiển thị ở cuối queue ra (dùng pop).
            2. Nếu người dùng chọn "Chưa thuộc" (False): nhét thẻ đó vào đầu queue (dùng appendleft) 
               để thẻ này tự động xuất hiện lại sau khi duyệt hết các thẻ còn lại.
            3. Nếu người dùng chọn "Đã thuộc" (True): thẻ đã bị pop() nên sẽ biến mất vĩnh viễn khỏi queue.
            4. Trả về thẻ tiếp theo ở cuối queue (nếu còn).
        """
        # Kiểm tra xem có tồn tại hàng đợi học cho bộ thẻ này không
        if deck_id not in self.learning_queues or not self.learning_queues[deck_id]:
            raise ValueError("Không có hàng đợi học cho bộ thẻ này.")  
        queue = self.learning_queues[deck_id]
        # BƯỚC 1: Lấy thẻ đang hiển thị ở CUỐI queue ra ngoài (thẻ này không còn trong queue nữa)
        current_card = queue.pop()
        # BƯỚC 2: Kiểm tra kết quả ghi nhận
        if not is_memorized:
            # Nếu CHƯA THUỘC -> Thêm lại thẻ vào ĐẦU queue (bên trái)
            queue.appendleft(current_card)
        # Nếu ĐÃ THUỘC -> Bỏ qua, không thêm lại vào queue
        # BƯỚC 3: Kiểm tra xem queue còn thẻ nào không để tiếp tục
        if not queue:
            # Xóa sạch phiên học vì đã hoàn thành
            del self.learning_queues[deck_id]
            return None
        # BƯỚC 4: Trả về thẻ tiếp theo ở CUỐI queue để giao diện hiển thị
        return queue[-1]