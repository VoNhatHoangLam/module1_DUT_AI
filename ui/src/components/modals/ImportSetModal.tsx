import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';

interface ImportSetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmImport: (cards: { term: string; definition: string }[]) => void;
  onForwardToManualCreate?: (cards: { term: string; definition: string }[]) => void;
  onNotify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const ImportSetModal: React.FC<ImportSetModalProps> = ({
  isOpen,
  onClose,
  onConfirmImport,
  onForwardToManualCreate,
  onNotify,
}) => {
  const [previewData, setPreviewData] = useState<{ term: string; definition: string }[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        if (!content) return;

        // Try JSON format first
        if (file.name.endsWith('.json')) {
          const parsed = JSON.parse(content);
          if (Array.isArray(parsed)) {
            const cards = parsed
              .filter((item) => item && (item.term || item.front) && (item.definition || item.back))
              .map((item) => ({
                term: String(item.term || item.front).trim(),
                definition: String(item.definition || item.back).trim(),
              }));
            if (cards.length > 0) {
              setPreviewData(cards);
              onNotify(`Đã tải thành công ${cards.length} thẻ từ tệp JSON!`, 'success');
              return;
            }
          }
        }

        // Parse CSV/TXT
        const lines = content.split(/\r?\n/).filter((l) => l.trim().length > 0);
        const parsedCards: { term: string; definition: string }[] = [];

        for (const line of lines) {
          // Check delimiter: comma, tab, or semicolon
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
            if (term && def && term.toLowerCase() !== 'term') {
              parsedCards.push({ term, definition: def });
            }
          }
        }

        if (parsedCards.length > 0) {
          setPreviewData(parsedCards);
          onNotify(`Đã tải thành công ${parsedCards.length} thẻ từ tệp!`, 'success');
        } else {
          onNotify('Không tìm thấy dữ liệu flashcard hợp lệ trong tệp (cần định dạng: term,definition)', 'error');
        }
      } catch (err) {
        onNotify('Lỗi đọc tệp! Vui lòng kiểm tra lại định dạng.', 'error');
      }
    };
    reader.readAsText(file);
  };

  const handleLoadSampleCSV = () => {
    const sample = [
      { term: 'Algorithm', definition: 'Tập hợp các bước hữu hạn giải quyết một vấn đề cụ thể.' },
      { term: 'Machine Learning', definition: 'Nhánh AI xây dựng hệ thống học hỏi trực tiếp từ dữ liệu.' },
      { term: 'API', definition: 'Giao diện lập trình ứng dụng cho phép các phần mềm trao đổi dữ liệu.' },
      { term: 'Database Index', definition: 'Cấu trúc dữ liệu tăng tốc độ truy xuất các bản ghi trong CSDL.' },
      { term: 'Asynchronous', definition: 'Mô hình lập trình không đồng bộ chạy nền không chặn luồng chính.' },
    ];
    setPreviewData(sample);
    onNotify('Đã nạp bản xem trước dữ liệu mẫu CSV!', 'info');
  };

  const handleConfirm = () => {
    if (!previewData.length) {
      onNotify('Chưa có dữ liệu để nhập!', 'error');
      return;
    }
    if (onForwardToManualCreate) {
      onForwardToManualCreate(previewData);
    } else {
      onConfirmImport(previewData);
    }
    setPreviewData([]);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-extrabold text-slate-900">Nhập bộ thẻ từ file</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-2xl border-2 border-dashed border-slate-200 text-center space-y-2 bg-slate-50">
            <Upload className="w-8 h-8 text-blue-500 mx-auto" />
            <div className="text-sm font-bold text-slate-800">Tải lên tệp CSV/JSON Flashcards</div>
            <p className="text-xs text-slate-500">
              Định dạng CSV mẫu: <code>term,definition</code> hoặc tệp JSON <code>[{`{"term": "...", "definition": "..."}`}]</code>
            </p>
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv,.txt,.json"
              onChange={handleFileUpload}
              className="hidden"
            />
            <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-3.5 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition-colors inline-block cursor-pointer shadow-xs"
              >
                Chọn tệp từ máy tính
              </button>
              <button
                type="button"
                onClick={handleLoadSampleCSV}
                className="px-3.5 py-1.5 rounded-lg bg-blue-100 text-blue-700 text-xs font-bold hover:bg-blue-200 transition-colors inline-block cursor-pointer"
              >
                Nạp dữ liệu mẫu CSV
              </button>
            </div>
          </div>

          {/* Preview list */}
          {previewData.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-600 uppercase">
                Xem trước ({previewData.length} thẻ):
              </div>
              <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-xl divide-y divide-slate-100">
                {previewData.map((d, i) => (
                  <div key={i} className="p-2.5 text-xs flex justify-between gap-4">
                    <span className="font-bold text-slate-800">{d.term}</span>
                    <span className="text-slate-500 text-right">{d.definition}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
            <button
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Đóng
            </button>
            <button
              disabled={previewData.length === 0}
              onClick={handleConfirm}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer shadow-xs"
            >
              Chuyển đến tạo bộ thẻ ({previewData.length} thẻ)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
