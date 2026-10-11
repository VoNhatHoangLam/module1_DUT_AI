import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';

interface ImportSetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmImport: (cards: { term: string; definition: string }[]) => void;
  onNotify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const ImportSetModal: React.FC<ImportSetModalProps> = ({
  isOpen,
  onClose,
  onConfirmImport,
  onNotify,
}) => {
  const [previewData, setPreviewData] = useState<{ term: string; definition: string }[]>([]);

  if (!isOpen) return null;

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
    onConfirmImport(previewData);
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
              Định dạng CSV mẫu: <code>term,definition</code>
            </p>
            <button
              onClick={handleLoadSampleCSV}
              className="px-3.5 py-1.5 rounded-lg bg-blue-100 text-blue-700 text-xs font-bold hover:bg-blue-200 transition-colors inline-block mt-1"
            >
              Nạp nhanh dữ liệu mẫu CSV
            </button>
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
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 transition-colors"
            >
              Đóng
            </button>
            <button
              disabled={previewData.length === 0}
              onClick={handleConfirm}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Xác nhận nhập bộ thẻ
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
