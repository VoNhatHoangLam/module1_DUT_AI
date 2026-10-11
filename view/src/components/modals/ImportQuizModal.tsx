import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';

interface QuizQuestionImport {
  question: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
}

interface ImportQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmImport: (questions: QuizQuestionImport[]) => void;
  onNotify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const ImportQuizModal: React.FC<ImportQuizModalProps> = ({
  isOpen,
  onClose,
  onConfirmImport,
  onNotify,
}) => {
  const [previewData, setPreviewData] = useState<QuizQuestionImport[]>([]);

  if (!isOpen) return null;

  const handleLoadSampleQuizCSV = () => {
    const sampleQuiz: QuizQuestionImport[] = [
      {
        question: 'Độ phức tạp thời gian trung bình của tìm kiếm nhị phân (Binary Search) là?',
        optionA: 'O(1)',
        optionB: 'O(n)',
        optionC: 'O(log n)',
        optionD: 'O(n^2)',
        correctAnswer: 'C',
        explanation: 'Binary Search chia đôi không gian tìm kiếm sau mỗi bước.',
      },
      {
        question: 'Giao thức nào hoạt động tại tầng Transport cung cấp kết nối tin cậy?',
        optionA: 'UDP',
        optionB: 'TCP',
        optionC: 'IP',
        optionD: 'HTTP',
        correctAnswer: 'B',
        explanation: 'TCP cung cấp kết nối đảm bảo tin cậy và truyền đúng thứ tự gói tin.',
      },
      {
        question: 'Trong cơ sở dữ liệu quan hệ, khóa chính (Primary Key) có đặc điểm gì?',
        optionA: 'Có thể chứa giá trị NULL',
        optionB: 'Không duy nhất',
        optionC: 'Duy nhất và không được NULL',
        optionD: 'Chỉ áp dụng cho trường số nguyên',
        correctAnswer: 'C',
        explanation: 'Primary key định danh duy nhất cho từng bản ghi và không được phép null.',
      },
    ];
    setPreviewData(sampleQuiz);
    onNotify('Đã nạp bản xem trước dữ liệu mẫu Quiz CSV!', 'info');
  };

  const handleConfirm = () => {
    if (!previewData.length) {
      onNotify('Chưa có dữ liệu quiz để nhập!', 'error');
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
          <h3 className="text-xl font-extrabold text-slate-900">Nhập đề thi Quiz từ file</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-2xl border-2 border-dashed border-slate-200 text-center space-y-2 bg-slate-50">
            <Upload className="w-8 h-8 text-indigo-500 mx-auto" />
            <div className="text-sm font-bold text-slate-800">Tải lên tệp CSV câu hỏi trắc nghiệm</div>
            <p className="text-xs text-slate-500">
              Cấu trúc cột: question, option_a, option_b, option_c, option_d, correct_answer, explanation
            </p>
            <button
              onClick={handleLoadSampleQuizCSV}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-100 text-indigo-700 text-xs font-bold hover:bg-indigo-200 transition-colors inline-block mt-1"
            >
              Nạp nhanh dữ liệu mẫu Quiz CSV
            </button>
          </div>

          {/* Preview table */}
          {previewData.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-600 uppercase">
                Xem trước ({previewData.length} câu hỏi hợp lệ):
              </div>
              <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-xl">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-100 font-bold">
                    <tr>
                      <th className="p-2">Câu hỏi</th>
                      <th className="p-2">Đáp án đúng</th>
                      <th className="p-2">Giải thích</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {previewData.map((d, i) => (
                      <tr key={i}>
                        <td className="p-2 font-semibold text-slate-900">{d.question}</td>
                        <td className="p-2 font-bold text-emerald-600">{d.correctAnswer}</td>
                        <td className="p-2 text-slate-500">{d.explanation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Xác nhận nhập đề thi Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
