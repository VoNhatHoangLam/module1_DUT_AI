import { StudySessionState } from '../types';
import { request } from './apiClient';

export const studyService = {
  /**
   * Bắt đầu phiên học flashcard: khởi tạo FlashcardStudyQueue (hàng đợi 2 giai đoạn FIFO).
   */
  async startStudy(deckId: number | string): Promise<StudySessionState> {
    return request<StudySessionState>('/study/start', {
      method: 'POST',
      body: JSON.stringify({ deck_id: Number(deckId) }),
    });
  },

  /**
   * Đánh dấu thẻ hiện tại (Thuộc / Chưa thuộc).
   * - Nếu đánh dấu Chưa thuộc -> thẻ được enqueue vào cuối Queue FIFO để ôn lại.
   * - Nếu đánh dấu Đã thuộc -> ghi nhận thẻ thuộc thành công.
   */
  async markCard(sessionId: string, isKnown: boolean): Promise<StudySessionState> {
    return request<StudySessionState>(`/study/${sessionId}/mark`, {
      method: 'POST',
      body: JSON.stringify({ is_known: isKnown }),
    });
  },

  /**
   * Lấy trạng thái hiện tại của phiên ôn tập thẻ.
   */
  async getStudyState(sessionId: string): Promise<StudySessionState> {
    return request<StudySessionState>(`/study/${sessionId}/state`);
  },
};
