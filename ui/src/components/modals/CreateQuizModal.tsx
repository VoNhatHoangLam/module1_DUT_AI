import React, { useState, useEffect, useRef } from 'react';
import { X, Plus, Trash2, Upload, PenTool, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { FlashcardSet } from '../../types';

export interface QuizQuestionInput {
  question: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  points?: number;
}

interface CreateQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetDeck?: FlashcardSet | null;
  availableSets?: FlashcardSet[];
  initialQuestions?: QuizQuestionInput[];
  initialTitle?: string;
  initialDescription?: string;
  initialCategory?: string;
  initialPrivacy?: 'public' | 'private';
  initialTab?: 'manual' | 'file';
  onNotify?: (msg: string, type?: 'success' | 'error' | 'info') => void;
  onSubmit: (data: {
    title: string;
    description: string;
    category: string;
    privacy: 'public' | 'private';
    timeLimitMinutes: number;
    questions: QuizQuestionInput[];
  }) => void;
}

export const CreateQuizModal: React.FC<CreateQuizModalProps> = ({
  isOpen,
  onClose,
  targetDeck,
  availableSets = [],
  initialQuestions,
  initialTitle,
  initialDescription,
  initialCategory,
  initialPrivacy,
  initialTab = 'manual',
  onNotify,
  onSubmit,
}) => {
  const [selectedDeckId, setSelectedDeckId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'manual' | 'file'>('manual');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [timeLimitMinutes, setTimeLimitMinutes] = useState(10);
  const [fileNotice, setFileNotice] = useState<{ type: 'success' | 'error'; msg: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [questions, setQuestions] = useState<QuizQuestionInput[]>([
    {
      question: '',
      optionA: '',
      optionB: '',
      optionC: '',
      optionD: '',
      correctAnswer: 'A',
      explanation: '',
      points: 1,
    },
  ]);

  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
      setFileNotice(null);
      if (initialQuestions && initialQuestions.length > 0) {
        setQuestions(
          initialQuestions.map((q) => ({
            ...q,
            points: typeof q.points === 'number' ? q.points : 1,
          }))
        );
        setTitle(
          initialTitle ||
            (targetDeck
              ? `Quiz: ${targetDeck.title}`
              : `Bộ đề Quiz nhập từ file (${new Date().toLocaleDateString('vi-VN')})`)
        );
        setDescription(
          initialDescription ||
            (targetDeck
              ? `Đề thi trắc nghiệm tạo từ bộ thẻ "${targetDeck.title}"`
              : 'Đề thi trắc nghiệm được tạo từ nội dung file tải lên.')
        );
      } else if (targetDeck) {
        setSelectedDeckId(targetDeck.id);
        setTitle(`Quiz: ${targetDeck.title}`);
        setDescription(`Đề thi trắc nghiệm tạo từ bộ thẻ "${targetDeck.title}"`);
        if (targetDeck.cards && targetDeck.cards.length > 0) {
          const cards = targetDeck.cards;
          const generated: QuizQuestionInput[] = cards.map((card, idx) => {
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
              points: 1,
            };
          });
          setQuestions(generated);
        } else {
          setQuestions([
            {
              question: '',
              optionA: '',
              optionB: '',
              optionC: '',
              optionD: '',
              correctAnswer: 'A',
              explanation: '',
              points: 1,
            },
          ]);
        }
      } else {
        setSelectedDeckId('');
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
            points: 1,
          },
        ]);
      }
    }
  }, [
    isOpen,
    targetDeck,
    initialQuestions,
    initialTitle,
    initialDescription,
    initialTab,
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
        points: 1,
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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        if (!content) return;

        // 1. Try JSON
        if (file.name.endsWith('.json')) {
          const parsed = JSON.parse(content);
          if (Array.isArray(parsed)) {
            const list: QuizQuestionInput[] = parsed
              .filter(
                (item) =>
                  item &&
                  item.question &&
                  (item.optionA || item.option_a || item.a) &&
                  (item.optionB || item.option_b || item.b)
              )
              .map((item) => ({
                question: String(item.question || item.question_text || '').trim(),
                optionA: String(item.optionA || item.option_a || item.a || '').trim(),
                optionB: String(item.optionB || item.option_b || item.b || '').trim(),
                optionC: String(item.optionC || item.option_c || item.c || '').trim(),
                optionD: String(item.optionD || item.option_d || item.d || '').trim(),
                correctAnswer: (['A', 'B', 'C', 'D'].includes(
                  String(item.correctAnswer || item.correct_answer || 'A').toUpperCase()
                )
                  ? String(item.correctAnswer || item.correct_answer || 'A').toUpperCase()
                  : 'A') as 'A' | 'B' | 'C' | 'D',
                explanation: String(item.explanation || '').trim(),
                points: typeof item.points === 'number' ? item.points : (!isNaN(Number(item.points)) && item.points !== '' ? Number(item.points) : 1),
              }));

            if (list.length > 0) {
              setQuestions(list);
              const successMsg = `Đã tải thành công ${list.length} câu hỏi quiz từ tệp JSON!`;
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
        // Expected structure: question_text,option_a,option_b,option_c,option_d,correct_answer,points
        const lines = content.split(/\r?\n/).filter((l) => l.trim().length > 0);
        const parsedList: QuizQuestionInput[] = [];

        for (const line of lines) {
          let parts: string[] = [];
          if (line.includes('\t')) parts = line.split('\t');
          else if (line.includes(';')) parts = line.split(';');
          else parts = line.split(',');

          if (parts.length >= 3) {
            const qText = parts[0]?.trim().replace(/^["']|["']$/g, '');
            const optionA = parts[1]?.trim().replace(/^["']|["']$/g, '');
            const optionB = parts[2]?.trim().replace(/^["']|["']$/g, '');
            const optionC = (parts[3] || '').trim().replace(/^["']|["']$/g, '');
            const optionD = (parts[4] || '').trim().replace(/^["']|["']$/g, '');
            let rawAns = (parts[5] || 'A').trim().toUpperCase().replace(/^["']|["']$/g, '');
            if (!['A', 'B', 'C', 'D'].includes(rawAns)) rawAns = 'A';

            // col 6 can be points or explanation
            const col6 = (parts[6] || '').trim().replace(/^["']|["']$/g, '');
            const col7 = (parts[7] || '').trim().replace(/^["']|["']$/g, '');
            let points = 1;
            let explanation = '';

            if (col6 && !isNaN(Number(col6))) {
              points = Number(col6);
              explanation = col7;
            } else {
              explanation = col6;
              if (col7 && !isNaN(Number(col7))) {
                points = Number(col7);
              }
            }

            const lowerQ = qText.toLowerCase();
            if (
              qText &&
              optionA &&
              optionB &&
              lowerQ !== 'question' &&
              lowerQ !== 'question_text' &&
              lowerQ !== 'question text' &&
              lowerQ !== 'câu hỏi' &&
              lowerQ !== 'cau_hoi'
            ) {
              parsedList.push({
                question: qText,
                optionA,
                optionB,
                optionC,
                optionD,
                correctAnswer: rawAns as 'A' | 'B' | 'C' | 'D',
                explanation,
                points,
              });
            }
          }
        }

        if (parsedList.length > 0) {
          setQuestions(parsedList);
          const successMsg = `Đã tải thành công ${parsedList.length} câu hỏi quiz từ tệp!`;
          setFileNotice({ type: 'success', msg: successMsg });
          onNotify?.(successMsg, 'success');
          if (!title.trim()) {
            setTitle(file.name.replace(/\.[^/.]+$/, ''));
          }
        } else {
          const errMsg =
            'Không tìm thấy dữ liệu quiz hợp lệ trong tệp (cần các cột: question, option_a, option_b, option_c, option_d, correct_answer, explanation)';
          setFileNotice({ type: 'error', msg: errMsg });
          onNotify?.(errMsg, 'error');
        }
      } catch (err) {
        const errMsg = 'Lỗi đọc tệp quiz! Vui lòng kiểm tra lại định dạng.';
        setFileNotice({ type: 'error', msg: errMsg });
        onNotify?.(errMsg, 'error');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  const handleLoadFromDeckCards = () => {
    if (!targetDeck || !targetDeck.cards || targetDeck.cards.length === 0) return;
    const cards = targetDeck.cards;
    const generated: QuizQuestionInput[] = cards.map((card, idx) => {
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
        points: 1,
      };
    });
    setQuestions(generated);
    const msg = `Đã tự động trích xuất ${generated.length} câu hỏi từ bộ thẻ "${targetDeck.title}"!`;
    setFileNotice({ type: 'success', msg });
    onNotify?.(msg, 'info');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validQuestions = questions.filter(
      (q) => q.question.trim() && q.optionA.trim() && q.optionB.trim()
    );

    if (validQuestions.length === 0) {
      const errMsg =
        activeTab === 'file'
          ? 'Chưa có câu hỏi nào được nạp từ tệp! Vui lòng tải lên tệp CSV/JSON trước khi tạo.'
          : 'Vui lòng nhập ít nhất 1 câu hỏi hợp lệ với tối thiểu 2 phương án (A và B)!';
      setFileNotice({ type: 'error', msg: errMsg });
      onNotify?.(errMsg, 'error');
      return;
    }

    if (!title.trim()) {
      onNotify?.('Vui lòng nhập tên bộ đề Quiz!', 'error');
      return;
    }

    onSubmit({
      title: title.trim(),
      description: description.trim() || 'Bộ đề thi trắc nghiệm ôn tập.',
      category: initialCategory || targetDeck?.category || 'Chung',
      privacy: 'public',
      timeLimitMinutes: Math.max(1, timeLimitMinutes || 10),
      questions: validQuestions,
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
        points: 1,
      },
    ]);
    setFileNotice(null);
    setActiveTab('manual');
  };

  const validQuestionsCount = questions.filter(
    (q) => q.question.trim() && q.optionA.trim() && q.optionB.trim()
  ).length;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        {/* Modal Top Header (always maintained) */}
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-extrabold text-slate-900">
            {targetDeck ? `Tạo quiz từ: ${targetDeck.title}` : 'Tạo bộ đề thi Quiz mới'}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Trường Bộ thẻ */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Bộ thẻ
              </label>
              <span className="text-[11px] font-semibold text-slate-400">
                {targetDeck ? '(Đã điền sẵn • Không cho sửa)' : '(Tùy chọn liên kết)'}
              </span>
            </div>
            {targetDeck ? (
              <input
                type="text"
                value={targetDeck.title}
                readOnly
                disabled
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-700 font-bold text-sm cursor-not-allowed select-none shadow-xs"
              />
            ) : availableSets && availableSets.length > 0 ? (
              <select
                value={selectedDeckId}
                onChange={(e) => {
                  const newId = e.target.value;
                  setSelectedDeckId(newId);
                  const found = availableSets.find((s) => s.id === newId);
                  if (found) {
                    if (!title.trim()) setTitle(`Quiz: ${found.title}`);
                    if (!description.trim()) setDescription(`Đề thi trắc nghiệm tạo từ bộ thẻ "${found.title}"`);
                  }
                }}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm bg-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs"
              >
                <option value="">-- Không chọn bộ thẻ (Tạo độc lập) --</option>
                {availableSets.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title} ({s.cards.length} thẻ)
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value="Không liên kết bộ thẻ"
                readOnly
                disabled
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 text-sm cursor-not-allowed select-none shadow-xs"
              />
            )}
          </div>

          {/* Top persistent inputs: Tiêu đề đề thi & Mô tả ngắn + Thời gian */}
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
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Mô tả ngắn đề thi
              </label>
              <input
                type="text"
                placeholder="Ghi chú về nội dung và mức độ khó..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Thời gian (phút)
              </label>
              <input
                type="number"
                min="1"
                max="180"
                value={timeLimitMinutes}
                onChange={(e) => setTimeLimitMinutes(Number(e.target.value))}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Sub-tabs right below "Mô tả ngắn": Tạo thủ công / Tạo từ file */}
          <div className="pt-1">
            <div className="flex p-1 bg-slate-100 rounded-xl gap-1">
              <button
                type="button"
                onClick={() => setActiveTab('manual')}
                className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                  activeTab === 'manual'
                    ? 'bg-white text-indigo-600 shadow-xs'
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
                    ? 'bg-white text-indigo-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Upload className="w-3.5 h-3.5" />
                Tạo từ file
              </button>
            </div>
          </div>

          {/* Notification banner inside modal */}
          {fileNotice && (
            <div
              className={`p-3 rounded-xl text-xs flex items-center gap-2 transition-all ${
                fileNotice.type === 'success'
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  : 'bg-rose-50 text-rose-800 border border-rose-200'
              }`}
            >
              {fileNotice.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              )}
              <span className="font-medium">{fileNotice.msg}</span>
            </div>
          )}

          {/* Tab Content */}
          {activeTab === 'manual' ? (
            /* Tab 1: Tạo thủ công */
            <div className="space-y-3 pt-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Danh sách câu hỏi ({questions.length})
                </label>
                <button
                  type="button"
                  onClick={handleAddQuestion}
                  className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
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
                        <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg px-2 py-1 shadow-2xs">
                          <span className="text-[11px] font-bold text-slate-500 whitespace-nowrap">Điểm:</span>
                          <input
                            type="number"
                            min="0"
                            step="any"
                            value={q.points !== undefined ? q.points : 1}
                            onChange={(e) =>
                              handleUpdateQuestion(idx, {
                                points: e.target.value === '' ? 0 : Number(e.target.value),
                              })
                            }
                            className="w-10 text-xs font-bold text-indigo-700 text-center outline-none bg-transparent"
                            placeholder="1"
                            title="Điểm cho câu hỏi này"
                          />
                        </div>
                        <select
                          value={q.correctAnswer}
                          onChange={(e) =>
                            handleUpdateQuestion(idx, {
                              correctAnswer: e.target.value as 'A' | 'B' | 'C' | 'D',
                            })
                          }
                          className="text-xs bg-white border border-slate-200 rounded-lg px-2 py-1 font-bold text-emerald-700 cursor-pointer shadow-2xs"
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
                            className="p-1 text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
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
          ) : (
            /* Tab 2: Tạo từ file (sao chép đầy đủ từ giao diện nhập file Quiz) */
            <div className="space-y-4 pt-1">
              <div className="p-5 rounded-2xl border-2 border-dashed border-slate-200 text-center space-y-2 bg-slate-50">
                <Upload className="w-8 h-8 text-indigo-500 mx-auto" />
                <div className="text-sm font-bold text-slate-800">Tải lên tệp CSV Quiz</div>
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
                <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition-colors inline-block cursor-pointer shadow-xs"
                  >
                    Chọn tệp từ máy tính
                  </button>
                  {targetDeck && targetDeck.cards && targetDeck.cards.length > 0 && (
                    <button
                      type="button"
                      onClick={handleLoadFromDeckCards}
                      className="px-4 py-2 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold hover:bg-emerald-200 transition-colors inline-flex items-center gap-1 cursor-pointer"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      Nạp từ {targetDeck.cards.length} thẻ của bộ này
                    </button>
                  )}
                </div>
              </div>

              {/* Preview table in file tab */}
              {validQuestionsCount > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-bold text-slate-700 uppercase">
                      Xem trước ({validQuestionsCount} câu hỏi đã nạp):
                    </div>
                    <button
                      type="button"
                      onClick={() => setActiveTab('manual')}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 underline cursor-pointer"
                    >
                      Chuyển sang tab thủ công để chỉnh sửa
                    </button>
                  </div>
                  <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-xs text-slate-700">
                      <thead className="bg-slate-100 font-bold sticky top-0">
                        <tr>
                          <th className="p-2">Câu hỏi</th>
                          <th className="p-2">Đáp án đúng</th>
                          <th className="p-2">Điểm</th>
                          <th className="p-2">Giải thích</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {questions
                          .filter((q) => q.question.trim() && q.optionA.trim())
                          .map((d, i) => (
                            <tr key={i}>
                              <td className="p-2 font-semibold text-slate-900">{d.question}</td>
                              <td className="p-2 font-bold text-emerald-600">{d.correctAnswer}</td>
                              <td className="p-2 font-bold text-indigo-600">{d.points ?? 1}</td>
                              <td className="p-2 text-slate-500">{d.explanation || '—'}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Action buttons (always maintained) */}
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
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-colors shadow-xs cursor-pointer flex items-center gap-1.5"
            >
              <span>Xác nhận tạo bộ đề Quiz</span>
              {validQuestionsCount > 0 && (
                <span className="bg-indigo-700/60 text-white text-[10px] px-1.5 py-0.5 rounded-full">
                  {validQuestionsCount} câu
                </span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
