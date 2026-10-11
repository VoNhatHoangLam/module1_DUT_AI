import React, { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';

interface QuizQuestionInput {
  question: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
}

interface CreateQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description: string;
    category: string;
    timeLimitMinutes: number;
    questions: QuizQuestionInput[];
  }) => void;
}

export const CreateQuizModal: React.FC<CreateQuizModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Công nghệ thông tin');
  const [timeLimitMinutes, setTimeLimitMinutes] = useState(10);
  const [questions, setQuestions] = useState<QuizQuestionInput[]>([
    {
      question: '',
      optionA: '',
      optionB: '',
      optionC: '',
      optionD: '',
      correctAnswer: 'A',
      explanation: '',
    },
  ]);

  if (!isOpen) return null;

  const handleAddQuestion = () => {
    setQuestions([
      ...questions,
      {
        question: '',
        optionA: '',
        optionB: '',
        optionC: '',
        optionD: '',
        correctAnswer: 'A',
        explanation: '',
      },
    ]);
  };

  const handleRemoveQuestion = (idx: number) => {
    if (questions.length <= 1) return;
    setQuestions(questions.filter((_, i) => i !== idx));
  };

  const handleUpdateQuestion = (idx: number, patch: Partial<QuizQuestionInput>) => {
    const updated = [...questions];
    updated[idx] = { ...updated[idx], ...patch };
    setQuestions(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      title,
      description,
      category,
      timeLimitMinutes,
      questions,
    });
    // Reset
    setTitle('');
    setDescription('');
    setQuestions([
      {
        question: '',
        optionA: '',
        optionB: '',
        optionC: '',
        optionD: '',
        correctAnswer: 'A',
        explanation: '',
      },
    ]);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-extrabold text-slate-900">Tạo bộ đề thi Quiz mới</h3>
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
              Tiêu đề bài thi Quiz *
            </label>
            <input
              type="text"
              required
              placeholder="Ví dụ: Ôn tập Kiểm thử Phần mềm & CI/CD"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Mô tả ngắn đề thi
            </label>
            <input
              type="text"
              placeholder="Ghi chú về nội dung và mức độ khó..."
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
                Thời gian làm bài (phút)
              </label>
              <input
                type="number"
                min="1"
                max="120"
                value={timeLimitMinutes}
                onChange={(e) => setTimeLimitMinutes(Number(e.target.value))}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Danh sách câu hỏi ({questions.length})
              </label>
              <button
                type="button"
                onClick={handleAddQuestion}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Thêm câu hỏi
              </button>
            </div>

            <div className="space-y-4 max-h-72 overflow-y-auto pr-1">
              {questions.map((q, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-600">
                      Câu hỏi {idx + 1}
                    </span>
                    <div className="flex items-center gap-2">
                      <select
                        value={q.correctAnswer}
                        onChange={(e) =>
                          handleUpdateQuestion(idx, {
                            correctAnswer: e.target.value as 'A' | 'B' | 'C' | 'D',
                          })
                        }
                        className="text-xs bg-white border border-slate-200 rounded-lg px-2 py-1 font-bold text-emerald-700"
                      >
                        <option value="A">Đáp án đúng: A</option>
                        <option value="B">Đáp án đúng: B</option>
                        <option value="C">Đáp án đúng: C</option>
                        <option value="D">Đáp án đúng: D</option>
                      </select>
                      {questions.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveQuestion(idx)}
                          className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  <input
                    type="text"
                    required
                    placeholder="Nội dung câu hỏi trắc nghiệm..."
                    value={q.question}
                    onChange={(e) => handleUpdateQuestion(idx, { question: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-white text-xs font-medium"
                  />

                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      required
                      placeholder="Phương án A..."
                      value={q.optionA}
                      onChange={(e) => handleUpdateQuestion(idx, { optionA: e.target.value })}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                    />
                    <input
                      type="text"
                      required
                      placeholder="Phương án B..."
                      value={q.optionB}
                      onChange={(e) => handleUpdateQuestion(idx, { optionB: e.target.value })}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                    />
                    <input
                      type="text"
                      placeholder="Phương án C..."
                      value={q.optionC}
                      onChange={(e) => handleUpdateQuestion(idx, { optionC: e.target.value })}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                    />
                    <input
                      type="text"
                      placeholder="Phương án D..."
                      value={q.optionD}
                      onChange={(e) => handleUpdateQuestion(idx, { optionD: e.target.value })}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                    />
                  </div>

                  <input
                    type="text"
                    placeholder="Lời giải thích chi tiết..."
                    value={q.explanation}
                    onChange={(e) => handleUpdateQuestion(idx, { explanation: e.target.value })}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs text-slate-600"
                  />
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
              Xác nhận tạo bộ đề Quiz
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
