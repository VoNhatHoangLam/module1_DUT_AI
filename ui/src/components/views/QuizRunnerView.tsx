import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  RotateCcw,
  ListOrdered,
} from 'lucide-react';
import { QuizSet, QuizAttempt, QuizSessionState, QuizAttemptResult } from '../../types';
import { quizService } from '../../services/quizService';
import { ConfirmModal } from '../modals/ConfirmModal';

interface QuizRunnerViewProps {
  activeQuiz: QuizSet;
  initialSession?: QuizSessionState | null;
  onFinishAttempt: (attempt: QuizAttempt) => void;
  onExit: () => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const QuizRunnerView: React.FC<QuizRunnerViewProps> = ({
  activeQuiz,
  initialSession = null,
  onFinishAttempt,
  onExit,
  notify,
}) => {
  const [session, setSession] = useState<QuizSessionState | null>(initialSession);
  const [submittedResult, setSubmittedResult] = useState<QuizAttemptResult | null>(null);
  const [timeLeft, setTimeLeft] = useState((activeQuiz.timeLimitMinutes || 10) * 60);
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(!initialSession);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Khởi tạo phiên làm bài 2-Stack trên Backend nếu chưa có
  useEffect(() => {
    let isMounted = true;
    if (!session && !submittedResult) {
      setIsLoading(true);
      quizService
        .startQuiz(activeQuiz.id)
        .then((newSession) => {
          if (isMounted) {
            setSession(newSession);
            setIsLoading(false);
          }
        })
        .catch((err) => {
          if (isMounted) {
            notify(`Không thể bắt đầu bài thi: ${err.message}`, 'error');
            setIsLoading(false);
          }
        });
    }
    return () => {
      isMounted = false;
    };
  }, [activeQuiz.id]);

  // Bộ đếm thời gian thi
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (!submittedResult && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [submittedResult, timeLeft]);

  // Tự động nộp bài khi hết thời gian
  useEffect(() => {
    if (!submittedResult && timeLeft === 0 && session) {
      handleSubmitQuiz();
      notify('Hết thời gian làm bài! Hệ thống tự động nộp bài thi.', 'info');
    }
  }, [timeLeft, submittedResult, session]);

  const handleSelectAnswer = async (opt: 'A' | 'B' | 'C' | 'D') => {
    if (!session || !session.current_question) return;

    try {
      const updated = await quizService.answerQuestion(session.attempt_id, opt);
      // Bảo đảm khi trả lời câu cuối cùng, giao diện vẫn giữ nguyên câu đó
      if (!updated.current_question && session.current_question) {
        setSession({
          ...updated,
          current_question: session.current_question,
          current_answer: opt,
          can_forward: false,
        });
      } else {
        setSession(updated);
      }
    } catch (err: any) {
      notify(`Lỗi chọn đáp án: ${err.message}`, 'error');
    }
  };

  const handleBack = async () => {
    if (!session || !session.can_back) return;
    try {
      const updated = await quizService.navigateBack(session.attempt_id);
      setSession(updated);
    } catch (err: any) {
      notify(`Không thể quay lại câu trước: ${err.message}`, 'error');
    }
  };

  const handleForward = async () => {
    if (!session || !session.can_forward) return;
    try {
      const updated = await quizService.navigateForward(session.attempt_id);
      setSession(updated);
    } catch (err: any) {
      notify(`Không thể tiến tới câu kế tiếp: ${err.message}`, 'error');
    }
  };

  const handleSubmitQuiz = async () => {
    if (!session) return;
    setIsSubmitting(true);
    setShowSubmitConfirm(false);

    try {
      const result = await quizService.submitQuiz(session.attempt_id, session.selected_answers);
      setSubmittedResult(result);
      onFinishAttempt(result.attempt);
      confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } });
      notify(
        `Hoàn thành bài thi! Điểm số: ${result.attempt.score}% (${result.attempt.correctCount}/${result.attempt.totalCount} câu)`,
        'success'
      );
    } catch (err: any) {
      notify(`Không thể nộp bài: ${err.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRestart = async () => {
    setIsLoading(true);
    setSubmittedResult(null);
    setTimeLeft((activeQuiz.timeLimitMinutes || 10) * 60);

    try {
      const newSession = await quizService.startQuiz(activeQuiz.id);
      setSession(newSession);
      notify('Bắt đầu lượt thi mới!', 'info');
    } catch (err: any) {
      notify(`Không thể làm lại bài: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-600 text-sm font-semibold">Đang nạp câu hỏi và khởi tạo ngăn xếp thi (2-Stack)...</p>
      </div>
    );
  }

  if (!session && !submittedResult) {
    return (
      <div className="max-w-3xl mx-auto p-8 text-center bg-white rounded-3xl border border-slate-200 space-y-4">
        <p className="text-slate-600">Không tìm thấy bài thi hoặc bài thi không có câu hỏi.</p>
        <button
          onClick={onExit}
          className="px-4 py-2 bg-blue-600 text-white font-bold rounded-xl text-sm"
        >
          Quay lại danh sách bài thi
        </button>
      </div>
    );
  }

  const currentQ = session?.current_question;
  const currentAnswer = session?.current_answer;
  const answeredCount = session
    ? Object.values(session.selected_answers).filter((a) => a !== null && a !== undefined).length
    : 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header info (chỉ hiển thị khi đang làm bài) */}
      {!submittedResult && session && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <h2 className="font-bold text-slate-900 text-base">{activeQuiz.title}</h2>
            <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-2">
              <span>Đã trả lời: {answeredCount} / {session.total_questions} câu</span>
              <span className="text-slate-300">|</span>
              <span className="text-blue-600 font-semibold flex items-center gap-1">
                <ListOrdered className="w-3.5 h-3.5" /> Điều hướng bằng 2-Stack
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setShowSubmitConfirm(true)}
              disabled={isSubmitting}
              className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1 shadow-xs disabled:opacity-50"
            >
              <Check className="w-3.5 h-3.5" /> Nộp bài
            </button>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm font-bold">
              <Clock className="w-4 h-4 text-amber-600" />
              {Math.floor(timeLeft / 60)
                .toString()
                .padStart(2, '0')}
              :
              {(timeLeft % 60).toString().padStart(2, '0')}
            </div>
          </div>
        </div>
      )}

      {/* QUIZ SUBMITTED RESULTS REVIEW */}
      {submittedResult ? (
        <div className="space-y-6">
          {/* Result Hero */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 text-center shadow-lg space-y-4">
            <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mx-auto text-2xl font-black">
              🏆
            </div>
            <h2 className="text-2xl font-black text-slate-900">Kết quả bài thi</h2>
            <div className="text-5xl font-black text-blue-600">
              {submittedResult.attempt.score}%
            </div>
            <p className="text-slate-600 text-sm">
              Bạn đã trả lời đúng <b>{submittedResult.attempt.correctCount} / {submittedResult.attempt.totalCount}</b> câu hỏi.
            </p>

            <div className="flex justify-center gap-3 pt-2">
              <button
                onClick={handleRestart}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-sm transition-colors cursor-pointer flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" /> Làm lại bài thi này
              </button>
              <button
                onClick={onExit}
                className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-colors cursor-pointer"
              >
                Quay lại danh sách
              </button>
            </div>
          </div>

          {/* Detailed Question Review from Backend Snapshot */}
          <div className="space-y-4">
            <h3 className="font-extrabold text-lg text-slate-900">Chi tiết câu trả lời & đối chiếu đáp án:</h3>
            {submittedResult.answers.map((ans, idx) => {
              const isCorrect = ans.is_correct;
              return (
                <div
                  key={ans.answer_id || idx}
                  className={`p-6 rounded-2xl border bg-white shadow-xs ${
                    isCorrect ? 'border-emerald-200' : 'border-rose-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <h4 className="font-bold text-slate-900 text-base">
                      Câu {idx + 1}: {ans.question_text_snapshot}
                    </h4>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
                        +{ans.points_earned} điểm
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                          isCorrect
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {isCorrect ? 'Chính xác' : 'Chưa đúng'}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2 mt-4 text-sm">
                    <div
                      className={`p-3 rounded-xl border ${
                        isCorrect
                          ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
                          : 'bg-rose-50 border-rose-300 text-rose-900'
                      }`}
                    >
                      <span>
                        <b>Bạn đã chọn: </b>
                        {ans.selected_answer
                          ? `Đáp án ${ans.selected_answer} (${ans.selected_option_text_snapshot || 'N/A'})`
                          : 'Chưa chọn'}
                      </span>
                    </div>

                    {!isCorrect && (
                      <div className="p-3 rounded-xl border bg-emerald-50/70 border-emerald-300 text-emerald-900 font-semibold flex items-center justify-between">
                        <span>
                          <b>Đáp án đúng: </b>
                          Đáp án {ans.correct_answer_snapshot} ({ans.correct_option_text_snapshot})
                        </span>
                        <span className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                          <Check className="w-4 h-4" /> Chuẩn xác
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* ACTIVE QUESTION FORM */
        currentQ && (
          <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                  Câu hỏi #{currentQ.position || currentQ.id}
                </span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {currentQ.points ?? 1} điểm
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
                {currentQ.question}
              </h3>
            </div>

            <div className="space-y-3">
              {(['A', 'B', 'C', 'D'] as const).map((opt) => {
                const optText =
                  opt === 'A'
                    ? currentQ.optionA
                    : opt === 'B'
                    ? currentQ.optionB
                    : opt === 'C'
                    ? currentQ.optionC
                    : currentQ.optionD;
                const isSelected = currentAnswer === opt;

                return (
                  <button
                    key={opt}
                    onClick={() => handleSelectAnswer(opt)}
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
                disabled={!session?.can_back}
                onClick={handleBack}
                className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold text-xs hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer shrink-0"
              >
                <ChevronLeft className="w-4 h-4" /> Quay lại (Back Stack)
              </button>

              <div className="flex items-center gap-2 shrink-0 justify-end">
                {session?.can_forward ? (
                  <button
                    onClick={handleForward}
                    className="px-4 py-2.5 rounded-xl text-xs flex items-center justify-center gap-1 transition-colors min-w-24 bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-xs cursor-pointer"
                  >
                    Tiến tới (Forward Stack) <ChevronRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => setShowSubmitConfirm(true)}
                    className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-emerald-600/20 cursor-pointer"
                  >
                    <Check className="w-4 h-4" /> Nộp bài
                  </button>
                )}
              </div>
            </div>
          </div>
        )
      )}

      {/* CONFIRM QUIZ SUBMIT MODAL */}
      <ConfirmModal
        isOpen={showSubmitConfirm}
        title="Nộp bài thi ngay bây giờ?"
        description={`Bạn đã trả lời ${answeredCount} / ${session?.total_questions || 0} câu hỏi. Hệ thống sẽ tự động lưu bài làm và chấm điểm qua QuizService.`}
        confirmText="Nộp bài & Chấm điểm"
        cancelText="Xem lại câu hỏi"
        type="success"
        onConfirm={handleSubmitQuiz}
        onCancel={() => setShowSubmitConfirm(false)}
      />
    </div>
  );
};
