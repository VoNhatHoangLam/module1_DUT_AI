import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
} from 'lucide-react';
import { QuizSet, QuizAttempt } from '../../types';
import { ConfirmModal } from '../modals/ConfirmModal';

interface QuizRunnerViewProps {
  activeQuiz: QuizSet;
  onFinishAttempt: (attempt: QuizAttempt) => void;
  onExit: () => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const QuizRunnerView: React.FC<QuizRunnerViewProps> = ({
  activeQuiz,
  onFinishAttempt,
  onExit,
  notify,
}) => {
  const [questionIndex, setQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(activeQuiz.timeLimitMinutes * 60);
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);

  // Timer countdown
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (!isSubmitted && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isSubmitted, timeLeft]);

  // Auto-submit when time is up
  useEffect(() => {
    if (!isSubmitted && timeLeft === 0) {
      handleSubmitQuiz();
      notify('Hết thời gian làm bài! Hệ thống đã tự động nộp bài.', 'info');
    }
  }, [timeLeft, isSubmitted]);

  const handleSubmitQuiz = () => {
    let correct = 0;
    activeQuiz.questions.forEach((q) => {
      if (userAnswers[q.id] === q.correctAnswer) {
        correct++;
      }
    });

    const scorePct = Math.round((correct / activeQuiz.questions.length) * 100);
    const newAttempt: QuizAttempt = {
      id: `h_${Date.now()}`,
      quizTitle: activeQuiz.title,
      takenDate: new Date().toLocaleString('vi-VN'),
      score: scorePct,
      correctCount: correct,
      totalCount: activeQuiz.questions.length,
      accuracy: `${scorePct}%`,
      status: 'Hoàn thành',
      userAnswers: userAnswers,
    };

    onFinishAttempt(newAttempt);
    setIsSubmitted(true);
    setShowSubmitConfirm(false);
    confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } });
    notify(`Hoàn thành bài thi! Điểm số của bạn: ${scorePct}%`, 'success');
  };

  const handleRestart = () => {
    setQuestionIndex(0);
    setUserAnswers({});
    setIsSubmitted(false);
    setTimeLeft(activeQuiz.timeLimitMinutes * 60);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header info (chỉ hiển thị khi đang làm bài) */}
      {!isSubmitted && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <h2 className="font-bold text-slate-900 text-base">{activeQuiz.title}</h2>
            <div className="text-xs text-slate-500 mt-0.5">
              Câu hỏi {questionIndex + 1} / {activeQuiz.questions.length}
            </div>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm font-bold">
            <Clock className="w-4 h-4 text-amber-600" />
            {Math.floor(timeLeft / 60)
              .toString()
              .padStart(2, '0')}
            :
            {(timeLeft % 60).toString().padStart(2, '0')}
          </div>
        </div>
      )}

      {/* Questions Answered Status Bar (chỉ hiển thị khi đang làm bài) */}
      {!isSubmitted && (
        <div className="flex items-center gap-1.5 overflow-x-auto py-2">
          {activeQuiz.questions.map((q, idx) => {
            const isAnswered = !!userAnswers[q.id];
            const isCurrent = idx === questionIndex;
            return (
              <button
                key={q.id}
                onClick={() => setQuestionIndex(idx)}
                className={`w-9 h-9 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  isCurrent
                    ? 'bg-blue-600 text-white ring-2 ring-blue-400'
                    : isAnswered
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      )}

      {/* QUIZ SUBMITTED RESULTS REVIEW */}
      {isSubmitted ? (
        <div className="space-y-6">
          {/* Result Hero */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 text-center shadow-lg space-y-4">
            <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mx-auto text-2xl font-black">
              🏆
            </div>
            <h2 className="text-2xl font-black text-slate-900">Kết quả bài thi</h2>
            {(() => {
              const totalQ = activeQuiz?.questions?.length || 1;
              const correctQ = (activeQuiz?.questions || []).filter(
                (q) => q && userAnswers[q.id] === q.correctAnswer
              ).length;
              const scorePct = Math.round((correctQ / totalQ) * 100);
              return (
                <>
                  <div className="text-5xl font-black text-blue-600">{scorePct}%</div>
                  <p className="text-slate-600 text-sm">
                    Bạn đã trả lời đúng <b>{correctQ} / {totalQ}</b> câu hỏi.
                  </p>
                </>
              );
            })()}
            <div className="flex justify-center gap-3 pt-2">
              <button
                onClick={handleRestart}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-sm transition-colors cursor-pointer"
              >
                Làm lại bài thi này
              </button>
              <button
                onClick={onExit}
                className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-colors cursor-pointer"
              >
                Danh sách bài thi
              </button>
            </div>
          </div>

          {/* Detailed Question Review */}
          <div className="space-y-4">
            <h3 className="font-extrabold text-lg text-slate-900">Xem lại đáp án và lời giải chi tiết:</h3>
            {activeQuiz.questions.map((q, idx) => {
              const userPick = userAnswers[q.id];
              const isCorrect = userPick === q.correctAnswer;
              return (
                <div
                  key={q.id}
                  className={`p-6 rounded-2xl border bg-white shadow-xs ${
                    isCorrect ? 'border-emerald-200' : 'border-rose-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <h4 className="font-bold text-slate-900 text-base">
                      Câu {idx + 1}: {q.question}
                    </h4>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider shrink-0 ${
                        isCorrect
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {isCorrect ? 'Chính xác' : 'Chưa đúng'}
                    </span>
                  </div>

                  <div className="space-y-2 mt-4 text-sm">
                    {(['A', 'B', 'C', 'D'] as const).map((opt) => {
                      const optText =
                        opt === 'A'
                          ? q.optionA
                          : opt === 'B'
                          ? q.optionB
                          : opt === 'C'
                          ? q.optionC
                          : q.optionD;
                      const isCorrectOpt = opt === q.correctAnswer;
                      const isUserPicked = userPick === opt;

                      return (
                        <div
                          key={opt}
                          className={`p-3 rounded-xl flex items-center justify-between border ${
                            isCorrectOpt
                              ? 'bg-emerald-50/70 border-emerald-300 text-emerald-900 font-semibold'
                              : isUserPicked
                              ? 'bg-rose-50 border-rose-300 text-rose-900'
                              : 'bg-slate-50 border-slate-200 text-slate-600'
                          }`}
                        >
                          <span>
                            <b>{opt}.</b> {optText}
                          </span>
                          {isCorrectOpt && (
                            <span className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                              <Check className="w-4 h-4" /> Đáp án đúng
                            </span>
                          )}
                          {isUserPicked && !isCorrectOpt && (
                            <span className="text-xs font-bold text-rose-700 flex items-center gap-1">
                              <X className="w-4 h-4" /> Bạn đã chọn
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="mt-4 p-3.5 rounded-xl bg-blue-50/80 border border-blue-200 text-xs text-blue-900">
                    <b>💡 Giải thích:</b> {q.explanation}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* ACTIVE QUESTION FORM */
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
              Câu hỏi {questionIndex + 1}
            </span>
            <h3 className="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
              {activeQuiz.questions[questionIndex].question}
            </h3>
          </div>

          <div className="space-y-3">
            {(['A', 'B', 'C', 'D'] as const).map((opt) => {
              const currentQ = activeQuiz.questions[questionIndex];
              const optText =
                opt === 'A'
                  ? currentQ.optionA
                  : opt === 'B'
                  ? currentQ.optionB
                  : opt === 'C'
                  ? currentQ.optionC
                  : currentQ.optionD;
              const isSelected = userAnswers[currentQ.id] === opt;

              return (
                <button
                  key={opt}
                  onClick={() =>
                    setUserAnswers((prev) => ({
                      ...prev,
                      [currentQ.id]: opt,
                    }))
                  }
                  className={`w-full text-left p-4 rounded-2xl border transition-all flex items-center gap-3.5 cursor-pointer ${
                    isSelected
                      ? 'bg-blue-50/90 border-blue-500 text-blue-900 shadow-xs ring-1 ring-blue-500'
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100 hover:border-slate-300'
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-xl font-bold text-xs flex items-center justify-center shrink-0 transition-colors ${
                      isSelected
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-slate-300 text-slate-700'
                    }`}
                  >
                    {opt}
                  </div>
                  <span className="text-sm font-semibold">{optText}</span>
                </button>
              );
            })}
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
            <button
              disabled={questionIndex === 0}
              onClick={() => setQuestionIndex((prev) => prev - 1)}
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer shrink-0"
            >
              <ChevronLeft className="w-4 h-4" /> Câu trước
            </button>

            {/* Nút nộp bài ở giữa thanh */}
            <button
              onClick={() => setShowSubmitConfirm(true)}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-emerald-600/20 cursor-pointer"
            >
              <Check className="w-4 h-4" /> Nộp bài
            </button>

            <div className="flex items-center gap-2 shrink-0 min-w-24 justify-end">
              <button
                disabled={questionIndex >= activeQuiz.questions.length - 1}
                onClick={() => setQuestionIndex((prev) => prev + 1)}
                className={`px-4 py-2.5 rounded-xl text-xs flex items-center justify-center gap-1 transition-colors min-w-24 ${
                  questionIndex < activeQuiz.questions.length - 1
                    ? 'bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-xs cursor-pointer'
                    : 'border border-slate-200 text-slate-400 opacity-40 cursor-not-allowed font-semibold'
                }`}
              >
                Câu tiếp <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CONFIRM QUIZ SUBMIT MODAL */}
      <ConfirmModal
        isOpen={showSubmitConfirm}
        title="Nộp bài thi ngay bây giờ?"
        description={`Bạn đã trả lời ${Object.keys(userAnswers).length} / ${activeQuiz.questions.length} câu hỏi. Hệ thống sẽ tự động chấm điểm và hiển thị lời giải chi tiết.`}
        confirmText="Nộp bài & Chấm điểm"
        cancelText="Xem lại câu hỏi"
        type="success"
        onConfirm={handleSubmitQuiz}
        onCancel={() => setShowSubmitConfirm(false)}
      />
    </div>
  );
};
