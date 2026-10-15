import React, { useState, useRef, useEffect } from 'react';
import { X, Plus, Trash2, Upload, PenTool, CheckCircle2, AlertCircle } from 'lucide-react';

interface CreateSetModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialCards?: { term: string; definition: string }[];
  initialTitle?: string;
  initialDescription?: string;
  initialCategory?: string;
  initialTab?: 'manual' | 'file';
  onNotify?: (msg: string, type?: 'success' | 'error' | 'info') => void;
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
  initialTab = 'manual',
  onNotify,
  onSubmit,
}) => {
  const [activeTab, setActiveTab] = useState<'manual' | 'file'>('manual');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [cardsList, setCardsList] = useState<{ term: string; definition: string }[]>([
    { term: '', definition: '' },
    { term: '', definition: '' },
  ]);
  const [fileNotice, setFileNotice] = useState<{ type: 'success' | 'error' | 'info'; msg: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab || 'manual');
      setFileNotice(null);
      if (initialCards && initialCards.length > 0) {
        setCardsList(initialCards);
        setTitle(initialTitle || `Bộ thẻ nhập từ file (${new Date().toLocaleDateString('vi-VN')})`);
        setDescription(initialDescription || 'Bộ thẻ được tạo từ nội dung file đã tải lên.');
      } else {
        setTitle('');
        setDescription('');
        setCardsList([
          { term: '', definition: '' },
          { term: '', definition: '' },
        ]);
      }
    }
  }, [isOpen, initialCards, initialTitle, initialDescription, initialTab]);

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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        if (!content) return;

        // 1. Parse JSON
        if (file.name.endsWith('.json')) {
          const parsed = JSON.parse(content);
          if (Array.isArray(parsed)) {
            const cards = parsed
              .filter(
                (item) =>
                  item &&
                  (item.term || item.front || item.front_text) &&
                  (item.definition || item.back || item.back_text)
              )
              .map((item) => ({
                term: String(item.front_text || item.term || item.front).trim(),
                definition: String(item.back_text || item.definition || item.back).trim(),
              }));
            if (cards.length > 0) {
              setCardsList(cards);
              const successMsg = `Đã tải thành công ${cards.length} thẻ từ tệp JSON!`;
              setFileNotice({ type: 'success', msg: successMsg });
              onNotify?.(successMsg, 'success');
              if (!title.trim()) {
                setTitle(file.name.replace(/\.[^/.]+$/, ''));
              }
              return;
            }
          }
        }

        // 2. Parse CSV / TXT
        const lines = content.split(/\r?\n/).filter((l) => l.trim().length > 0);
        const parsedCards: { term: string; definition: string }[] = [];

        for (const line of lines) {
          let parts: string[] = [];
          if (line.includes('\t')) {
            parts = line.split('\t');
          } else if (line.includes(';')) {
            parts = line.split(';');
          } else if (line.includes(',')) {
            parts = line.split(',');
          }

          if (parts.length >= 2) {
            const term = parts[0].trim().replace(/^["']|["']$/g, '');
            const def = parts.slice(1).join(',').trim().replace(/^["']|["']$/g, '');
            const lowerTerm = term.toLowerCase();
            if (term && def && lowerTerm !== 'term' && lowerTerm !== 'front_text' && lowerTerm !== 'front') {
              parsedCards.push({ term, definition: def });
            }
          }
        }

        if (parsedCards.length > 0) {
          setCardsList(parsedCards);
          const successMsg = `Đã tải thành công ${parsedCards.length} thẻ từ tệp!`;
          setFileNotice({ type: 'success', msg: successMsg });
          onNotify?.(successMsg, 'success');
          if (!title.trim()) {
            setTitle(file.name.replace(/\.[^/.]+$/, ''));
          }
        } else {
          const errMsg = 'Không tìm thấy dữ liệu flashcard hợp lệ trong tệp (cần định dạng: front_text,back_text)';
          setFileNotice({ type: 'error', msg: errMsg });
          onNotify?.(errMsg, 'error');
        }
      } catch (err) {
        const errMsg = 'Lỗi đọc tệp! Vui lòng kiểm tra lại định dạng.';
        setFileNotice({ type: 'error', msg: errMsg });
        onNotify?.(errMsg, 'error');
      }
    };
    reader.readAsText(file);
    // Reset file input so user can re-upload same file if desired
    e.target.value = '';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validCards = cardsList.filter((c) => c.term.trim() && c.definition.trim());

    if (validCards.length === 0) {
      const errMsg =
        activeTab === 'file'
          ? 'Vui lòng chọn và tải lên tệp CSV/JSON hợp lệ trước khi tạo!'
          : 'Bộ thẻ cần ít nhất 1 flashcard hợp lệ (điền đủ thuật ngữ và định nghĩa)!';
      setFileNotice({ type: 'error', msg: errMsg });
      onNotify?.(errMsg, 'error');
      return;
    }

    onSubmit({
      title,
      description,
      category: initialCategory || 'Chung',
      privacy: 'public',
      cards: validCards,
    });

    // Reset state
    setTitle('');
    setDescription('');
    setCardsList([
      { term: '', definition: '' },
      { term: '', definition: '' },
    ]);
    setFileNotice(null);
    setActiveTab('manual');
  };

  const filledCardsCount = cardsList.filter((c) => c.term.trim() && c.definition.trim()).length;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        {/* Modal Top Header (always maintained) */}
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-extrabold text-slate-900">Tạo bộ Flashcard mới</h3>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Top persistent inputs: Tên bộ thẻ & Mô tả ngắn */}
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

          {/* Sub-tabs right below "Mô tả ngắn": Tạo thủ công / Tạo từ file */}
          <div className="pt-1">
            <div className="flex p-1 bg-slate-100 rounded-xl gap-1">
              <button
                type="button"
                onClick={() => setActiveTab('manual')}
                className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                  activeTab === 'manual'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <PenTool className="w-3.5 h-3.5" />
                Tạo thủ công
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('file')}
                className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                  activeTab === 'file'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Upload className="w-3.5 h-3.5" />
                Tạo từ file
              </button>
            </div>
          </div>

          {/* Dynamic Bottom Area based on Tab */}
          {activeTab === 'manual' ? (
            /* Tab 1: Tạo thủ công */
            <div className="space-y-3 pt-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Danh sách các thẻ ({cardsList.length})
                </label>
                <button
                  type="button"
                  onClick={handleAddNewRow}
                  className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 cursor-pointer"
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
                      required={idx === 0 && activeTab === 'manual'}
                      placeholder="Thuật ngữ / Mặt trước..."
                      value={card.term}
                      onChange={(e) => handleCardChange(idx, 'term', e.target.value)}
                      className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      required={idx === 0 && activeTab === 'manual'}
                      placeholder="Định nghĩa / Mặt sau..."
                      value={card.definition}
                      onChange={(e) => handleCardChange(idx, 'definition', e.target.value)}
                      className="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    {cardsList.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveRow(idx)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
                        title="Xóa thẻ này"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* Tab 2: Tạo từ file (sao chép đầy đủ từ giao diện nhập file) */
            <div className="space-y-4 pt-1">
              <div className="p-5 rounded-2xl border-2 border-dashed border-slate-200 text-center space-y-2 bg-slate-50">
                <Upload className="w-8 h-8 text-blue-500 mx-auto" />
                <div className="text-sm font-bold text-slate-800">Tải lên tệp CSV Flashcards</div>
                <p className="text-xs text-slate-500">
                  Định dạng CSV mẫu: <code className="bg-slate-200/70 px-1.5 py-0.5 rounded text-slate-700 font-mono">front_text,back_text</code>
                </p>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".csv,.txt,.json"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition-colors inline-block cursor-pointer shadow-xs"
                  >
                    Chọn tệp từ máy tính
                  </button>
                </div>
              </div>

              {/* Status Notice */}
              {fileNotice && (
                <div
                  className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 ${
                    fileNotice.type === 'error'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : fileNotice.type === 'success'
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-blue-50 text-blue-800 border border-blue-200'
                  }`}
                >
                  {fileNotice.type === 'error' ? (
                    <AlertCircle className="w-4 h-4 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                  )}
                  <span>{fileNotice.msg}</span>
                </div>
              )}

              {/* Preview list */}
              {filledCardsCount > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold text-slate-600 uppercase">
                      Xem trước ({filledCardsCount} thẻ đã nạp):
                    </div>
                    <button
                      type="button"
                      onClick={() => setActiveTab('manual')}
                      className="text-xs text-blue-600 hover:text-blue-700 font-bold cursor-pointer"
                    >
                      Mở trong tab Tạo thủ công &rarr;
                    </button>
                  </div>
                  <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-xl divide-y divide-slate-100 bg-white">
                    {cardsList
                      .filter((d) => d.term.trim() || d.definition.trim())
                      .map((d, i) => (
                        <div key={i} className="p-2.5 text-xs flex justify-between gap-4">
                          <span className="font-bold text-slate-800 line-clamp-1">{d.term || '(Trống)'}</span>
                          <span className="text-slate-500 text-right line-clamp-1">{d.definition || '(Trống)'}</span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Modal Actions Footer */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Hủy bỏ
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs transition-colors shadow-xs cursor-pointer"
            >
              {filledCardsCount > 0 ? `Tạo bộ thẻ (${filledCardsCount} thẻ)` : 'Tạo bộ thẻ'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
