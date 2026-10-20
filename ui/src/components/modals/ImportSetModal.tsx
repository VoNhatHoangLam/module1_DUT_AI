import React, { useState } from 'react';
import { X, Upload, Loader2, Sparkles } from 'lucide-react';
import { deckService } from '../../services/deckService';

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
  const [isParsing, setIsParsing] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const content = event.target?.result as string;
        if (!content) return;

        // 1. Nếu là file JSON
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

        // 2. Nếu là file CSV/TXT: Gửi lên Backend để CsvImporter thẩm định và chuẩn hóa
        setIsParsing(true);
        try {
          const cards = await deckService.importCardsFromCsv(content);
          if (cards.length > 0) {
            setPreviewData(cards);
            onNotify(`Đã phân tích và thẩm định thành công ${cards.length} thẻ qua Backend CsvImporter!`, 'success');
          } else {
            onNotify('Không tìm thấy dữ liệu flashcard hợp lệ trong tệp CSV.', 'error');
          }
        } catch (apiErr: any) {
          onNotify(`Lỗi thẩm định CSV từ Backend: ${apiErr.message}`, 'error');
        } finally {
          setIsParsing(false);
        }
      } catch (err: any) {
        onNotify(`Lỗi đọc tệp: ${err.message}`, 'error');
      }
    };
    reader.readAsText(file);
  };

  const handleLoadSampleCSV = async () => {
    const sampleCsv = `front_text,back_text
Algorithm,Tập hợp các bước hữu hạn giải quyết một vấn đề cụ thể.
Machine Learning,Nhánh AI xây dựng hệ thống học hỏi trực tiếp từ dữ liệu.
API,Giao diện lập trình ứng dụng cho phép các phần mềm trao đổi dữ liệu.
Database Index,Cấu trúc dữ liệu tăng tốc độ truy xuất các bản ghi trong CSDL.
Asynchronous,Mô hình lập trình không đồng bộ chạy nền không chặn luồng chính.`;

    setIsParsing(true);
    try {
      const cards = await deckService.importCardsFromCsv(sampleCsv);
      setPreviewData(cards);
      onNotify(`Đã nạp và thẩm định thành công ${cards.length} thẻ mẫu qua Backend CsvImporter!`, 'success');
    } catch (err: any) {
      onNotify(`Lỗi nạp dữ liệu mẫu: ${err.message}`, 'error');
    } finally {
      setIsParsing(false);
    }
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
            <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
              <button
                type="button"
                disabled={isParsing}
                onClick={() => fileInputRef.current?.click()}
                className="px-3.5 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition-colors inline-flex items-center gap-1.5 cursor-pointer shadow-xs disabled:opacity-50"
              >
                {isParsing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                {isParsing ? 'Đang thẩm định CSV...' : 'Chọn tệp từ máy tính'}
              </button>
              <button
                type="button"
                disabled={isParsing}
                onClick={handleLoadSampleCSV}
                className="px-3.5 py-1.5 rounded-lg bg-blue-100 text-blue-700 text-xs font-bold hover:bg-blue-200 transition-colors inline-flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {isParsing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
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
