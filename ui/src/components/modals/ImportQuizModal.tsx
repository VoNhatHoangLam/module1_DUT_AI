import React, { useState, useRef } from 'react';
import { X, Upload, Sparkles, Loader2 } from 'lucide-react';
import { FlashcardSet } from '../../types';
import { quizService } from '../../services/quizService';

interface QuizQuestionImport {
  question: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  points?: number;
}

interface ImportQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetDeck?: FlashcardSet | null;
  onConfirmImport: (questions: QuizQuestionImport[], privacy?: 'public' | 'private') => void;
  onForwardToManualCreate?: (
    questions: QuizQuestionImport[],
    privacy?: 'public' | 'private',
    deck?: FlashcardSet | null
  ) => void;
  onNotify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const ImportQuizModal: React.FC<ImportQuizModalProps> = ({
  isOpen,
  onClose,
  targetDeck,
  onConfirmImport,
  onForwardToManualCreate,
  onNotify,
}) => {
  const [previewData, setPreviewData] = useState<QuizQuestionImport[]>([]);
  const [privacy, setPrivacy] = useState<'public' | 'private'>('public');
  const [isParsing, setIsParsing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
            const list: QuizQuestionImport[] = parsed
              .filter((item) => item && item.question && item.optionA && item.optionB)
              .map((item) => ({
                question: String(item.question).trim(),
                optionA: String(item.optionA).trim(),
                optionB: String(item.optionB).trim(),
                optionC: String(item.optionC || '').trim(),
                optionD: String(item.optionD || '').trim(),
                correctAnswer: (['A', 'B', 'C', 'D'].includes(item.correctAnswer)
                  ? item.correctAnswer
                  : 'A') as 'A' | 'B' | 'C' | 'D',
                explanation: String(item.explanation || '').trim(),
              }));
            if (list.length > 0) {
              setPreviewData(list);
              onNotify(`Đã tải thành công ${list.length} câu hỏi quiz từ tệp JSON!`, 'success');
              return;
            }
          }
        }

        // 2. Nếu là file CSV/TXT: Gửi lên Backend để QuizService thẩm định và chuẩn hóa
        setIsParsing(true);
        try {
          const parsedList = await quizService.importQuestionsFromCsv(content);
          if (parsedList.length > 0) {
            setPreviewData(parsedList as QuizQuestionImport[]);
            onNotify(`Đã thẩm định và nạp thành công ${parsedList.length} câu hỏi qua Backend QuizService!`, 'success');
          } else {
            onNotify('Không tìm thấy dữ liệu câu hỏi hợp lệ trong tệp CSV.', 'error');
          }
        } catch (apiErr: any) {
          onNotify(`Lỗi thẩm định CSV từ Backend: ${apiErr.message}`, 'error');
        } finally {
          setIsParsing(false);
        }
      } catch (err: any) {
        onNotify(`Lỗi đọc tệp quiz: ${err.message}`, 'error');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  const handleLoadSampleQuizCSV = async () => {
    const sampleCsv = `question_text,option_a,option_b,option_c,option_d,correct_answer,points
Độ phức tạp thời gian trung bình của tìm kiếm nhị phân (Binary Search) là?,O(1),O(n),O(log n),O(n^2),C,1.0
Giao thức nào hoạt động tại tầng Transport cung cấp kết nối tin cậy?,UDP,TCP,IP,HTTP,B,1.0
Cấu trúc dữ liệu nào hoạt động theo nguyên tắc LIFO (Last In First Out)?,Queue,Stack,Array,Linked List,B,1.0
Cây AVL là cấu trúc dữ liệu nào?,Cây tìm kiếm nhị phân tự cân bằng,Cây B-Tree bậc 3,Đồ thị có hướng không chu trình,Bảng băm,A,1.0`;

    setIsParsing(true);
    try {
      const parsedList = await quizService.importQuestionsFromCsv(sampleCsv);
      setPreviewData(parsedList as QuizQuestionImport[]);
      onNotify(`Đã nạp và thẩm định thành công ${parsedList.length} câu hỏi mẫu qua Backend QuizService!`, 'success');
    } catch (err: any) {
      onNotify(`Lỗi nạp dữ liệu mẫu: ${err.message}`, 'error');
    } finally {
      setIsParsing(false);
    }
  };

  const handleLoadFromDeckCards = () => {
    if (!targetDeck || !targetDeck.cards || targetDeck.cards.length === 0) return;
    const cards = targetDeck.cards;
    const generated: QuizQuestionImport[] = cards.map((card, idx) => {
      const otherAnswers = cards
        .filter((_, i) => i !== idx)
        .map((c) => c.definition)
        .filter((b) => b && b !== card.definition);

      return {
        question: `Nội dung tương ứng với thuật ngữ: "${card.term}" là gì?`,
        optionA: card.definition,
        optionB: otherAnswers[0] || 'Lựa chọn bổ sung B',
        optionC: otherAnswers[1] || 'Lựa chọn bổ sung C',
        optionD: otherAnswers[2] || 'Không có đáp án phù hợp',
        correctAnswer: 'A',
        explanation: `Thuật ngữ: ${card.term} -> Định nghĩa: ${card.definition}`,
      };
    });
    setPreviewData(generated);
    onNotify(`Đã tự động trích xuất ${generated.length} câu hỏi từ bộ thẻ "${targetDeck.title}"!`, 'info');
  };

  const handleConfirm = () => {
    if (!previewData.length) {
      onNotify('Chưa có dữ liệu quiz để nhập!', 'error');
      return;
    }
    if (onForwardToManualCreate) {
      onForwardToManualCreate(previewData, privacy, targetDeck);
    } else {
      onConfirmImport(previewData, privacy);
    }
    setPreviewData([]);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-extrabold text-slate-900">
            {targetDeck ? 'Tạo quiz từ file' : 'Nhập đề thi Quiz từ file'}
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          {targetDeck && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Bộ thẻ
                </label>
                <span className="text-[11px] font-semibold text-slate-400">
                  (Cố định từ bộ thẻ đã chọn)
                </span>
              </div>
              <input
                type="text"
                value={targetDeck.title}
                readOnly
                disabled
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-700 font-bold text-sm cursor-not-allowed select-none shadow-xs"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Quyền riêng tư
            </label>
            <select
              value={privacy}
              onChange={(e) => setPrivacy(e.target.value as 'public' | 'private')}
              className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="public">🌐 Công khai</option>
              <option value="private">🔒 Riêng tư</option>
            </select>
          </div>

          <div className="p-4 rounded-2xl border-2 border-dashed border-slate-200 text-center space-y-2 bg-slate-50">
            <Upload className="w-8 h-8 text-indigo-500 mx-auto" />
            <p className="text-xs text-slate-500">
              Định dạng CSV mẫu: <code className="bg-slate-200/70 px-1.5 py-0.5 rounded text-slate-700 font-mono">question_text,option_a,option_b,option_c,option_d,correct_answer,points</code>
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
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition-colors inline-block cursor-pointer shadow-xs"
              >
                Chọn tệp từ máy tính
              </button>
              <button
                type="button"
                onClick={handleLoadSampleQuizCSV}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-100 text-indigo-700 text-xs font-bold hover:bg-indigo-200 transition-colors inline-block cursor-pointer"
              >
                Nạp dữ liệu mẫu Quiz CSV
              </button>
              {targetDeck && targetDeck.cards && targetDeck.cards.length > 0 && (
                <button
                  type="button"
                  onClick={handleLoadFromDeckCards}
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-100 text-emerald-800 text-xs font-bold hover:bg-emerald-200 transition-colors inline-flex items-center gap-1 cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Nạp từ {targetDeck.cards.length} thẻ của bộ này
                </button>
              )}
            </div>
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
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Đóng
            </button>
            <button
              disabled={previewData.length === 0}
              onClick={handleConfirm}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer shadow-xs"
            >
              Chuyển đến tạo đề Quiz ({previewData.length} câu)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
