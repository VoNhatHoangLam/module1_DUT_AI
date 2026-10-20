import { FlashcardSet } from '../types';
import { request } from './apiClient';

export interface GetDecksResponse {
  items: FlashcardSet[];
  total_pages: number;
  page: number;
  page_size: number;
}

export interface CreateDeckPayload {
  title: string;
  description?: string;
  category?: string;
  privacy?: 'public' | 'private';
  cards: { term: string; definition: string; position?: number }[];
}

export const deckService = {
  /**
   * Lấy danh sách bộ thẻ kèm phân trang và tìm kiếm theo tiêu đề.
   */
  async getDecks(keyword?: string, page: number = 1, pageSize: number = 20): Promise<GetDecksResponse> {
    const params = new URLSearchParams();
    if (keyword && keyword.trim()) params.set('keyword', keyword.trim());
    params.set('page', String(page));
    params.set('page_size', String(pageSize));

    return request<GetDecksResponse>(`/decks?${params.toString()}`);
  },

  /**
   * Lấy chi tiết bộ thẻ và danh sách thẻ con O(log N).
   */
  async getDeckById(deckId: number | string): Promise<FlashcardSet> {
    return request<FlashcardSet>(`/decks/${deckId}`);
  },

  /**
   * Tạo mới bộ thẻ và lưu vào decks.csv & cards.csv qua Cây AVL.
   */
  async createDeck(payload: CreateDeckPayload): Promise<FlashcardSet> {
    return request<FlashcardSet>('/decks', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Xóa vĩnh viễn bộ thẻ và các thẻ con liên quan (Cascade Delete).
   */
  async deleteDeck(deckId: number | string): Promise<{ success: boolean; message: string }> {
    return request<{ success: boolean; message: string }>(`/decks/${deckId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Phân tích và kiểm tra cú pháp thẻ từ CSV để chuẩn hóa trước khi tạo bộ thẻ.
   */
  async importCardsFromCsv(csvContent: string): Promise<{ term: string; definition: string }[]> {
    const rawList = await request<any[]>('/decks/import', {
      method: 'POST',
      body: JSON.stringify({ csv_content: csvContent }),
    });

    return rawList.map((item) => ({
      term: item.term || item.front_text || '',
      definition: item.definition || item.back_text || '',
    }));
  },
};
