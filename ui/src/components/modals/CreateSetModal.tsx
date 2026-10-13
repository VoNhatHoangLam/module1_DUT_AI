import React, { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';

interface CreateSetModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialCards?: { term: string; definition: string }[];
  initialTitle?: string;
  initialDescription?: string;
  initialCategory?: string;
  onSubmit: (data: {
    title: string;
    description: string;
    category: string;
    privacy: 'public' | 'private';
    cards: { term: string; definition: string }[];
  }) => void;
}

export const CreateSetModal: React.FC<CreateSetModalProps> = ({
  isOpen,
  onClose,
  initialCards,
  initialTitle,
  initialDescription,
  initialCategory,
  onSubmit,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Công nghệ thông tin');
  const [privacy, setPrivacy] = useState<'public' | 'private'>('public');
  const [cardsList, setCardsList] = useState<{ term: string; definition: string }[]>([
    { term: '', definition: '' },
    { term: '', definition: '' },
  ]);

  React.useEffect(() => {
    if (isOpen) {
      if (initialCards && initialCards.length > 0) {
        setCardsList(initialCards);
        setTitle(initialTitle || `Bộ thẻ nhập từ file (${new Date().toLocaleDateString('vi-VN')})`);
        setDescription(initialDescription || 'Bộ thẻ được tạo từ nội dung file đã tải lên.');
        if (initialCategory) setCategory(initialCategory);
      } else {
        setTitle('');
        setDescription('');
        setCategory('Công nghệ thông tin');
        setPrivacy('public');
        setCardsList([
          { term: '', definition: '' },
          { term: '', definition: '' },
        ]);
      }
    }
  }, [isOpen, initialCards, initialTitle, initialDescription, initialCategory]);

  if (!isOpen) return null;

  const handleAddNewRow = () => {
    setCardsList([...cardsList, { term: '', definition: '' }]);
  };

  const handleRemoveRow = (index: number) => {
    if (cardsList.length <= 1) return;
    setCardsList(cardsList.filter((_, i) => i !== index));
  };

  const handleCardChange = (index: number, field: 'term' | 'definition', val: string) => {
    const next = [...cardsList];
    next[index][field] = val;
    setCardsList(next);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      title,
      description,
      category,
      privacy,
      cards: cardsList,
    });
    // Reset form
    setTitle('');
    setDescription('');
    setCardsList([
      { term: '', definition: '' },
      { term: '', definition: '' },
    ]);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-extrabold text-slate-900">Tạo bộ Flashcard mới</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Tên bộ thẻ *
            </label>
            <input
              type="text"
              required
              placeholder="Ví dụ: 100 Từ vựng IELTS chủ đề Environment"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Mô tả ngắn
            </label>
            <input
              type="text"
              placeholder="Ghi chú về nội dung và mục tiêu học..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Chủ đề
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Công nghệ thông tin">Công nghệ thông tin</option>
                <option value="Ngoại ngữ">Ngoại ngữ</option>
                <option value="Thiết kế">Thiết kế</option>
                <option value="Khoa học">Khoa học</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Quyền riêng tư
              </label>
              <select
                value={privacy}
                onChange={(e) => setPrivacy(e.target.value as any)}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="public">🌐 Công khai (Đăng ngay lập tức)</option>
                <option value="private">🔒 Riêng tư (Chỉ mình tôi)</option>
              </select>
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Danh sách các thẻ ({cardsList.length})
              </label>
              <button
                type="button"
                onClick={handleAddNewRow}
                className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Thêm thẻ
              </button>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
              {cardsList.map((card, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 border border-slate-200 rounded-2xl flex items-center gap-2"
                >
                  <div className="w-6 text-center text-xs font-bold text-slate-400">
                    {idx + 1}
                  </div>
                  <input
                    type="text"
                    required
                    placeholder="Thuật ngữ / Mặt trước..."
                    value={card.term}
                    onChange={(e) => handleCardChange(idx, 'term', e.target.value)}
                    className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                  />
                  <input
                    type="text"
                    required
                    placeholder="Định nghĩa / Mặt sau..."
                    value={card.definition}
                    onChange={(e) => handleCardChange(idx, 'definition', e.target.value)}
                    className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                  />
                  {cardsList.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveRow(idx)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 transition-colors"
            >
              Hủy bỏ
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs transition-colors shadow-xs"
            >
              Tạo bộ thẻ
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
