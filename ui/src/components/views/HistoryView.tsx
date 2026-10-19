import React, { useState } from 'react';
import { Clock, CheckCircle, Eye, X, Check } from 'lucide-react';
import { QuizAttempt, QuizAttemptResult } from '../../types';
import { historyService } from '../../services/historyService';

interface HistoryViewProps {
  history: QuizAttempt[];
}

export const HistoryView: React.FC<HistoryViewProps> = ({ history }) => {
  const [selectedAttemptResult, setSelectedAttemptResult] = useState<QuizAttemptResult | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  const handleViewDetail = async (attemptId: string) => {
    setIsLoadingDetail(true);
    try {
      const res = await historyService.getAttemptResult(attemptId);
      setSelectedAttemptResult(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
          <Clock className="w-6 h-6 text-emerald-600" />
          Lịch sử làm bài thi
        </h1>
        <p className="text-slate-500 text-xs mt-1">
          Dữ liệu được lưu trữ tự động trong quiz_attempts.csv và quiz_answers.csv.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {history.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            Chưa có bài thi nào được hoàn thành. Hãy chọn một bài Quiz để làm bài!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3.5">Tên bài thi</th>
                  <th className="px-6 py-3.5">Ngày làm bài</th>
                  <th className="px-6 py-3.5">Số câu đúng</th>
                  <th className="px-6 py-3.5">Tỷ lệ chính xác</th>
                  <th className="px-6 py-3.5">Trạng thái</th>
                  <th className="px-6 py-3.5 text-right">Chi tiết</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-900">{item.quizTitle}</td>
                    <td className="px-6 py-4 text-slate-500 text-xs">{item.takenDate}</td>
                    <td className="px-6 py-4 font-semibold">
                      {item.correctCount} / {item.totalCount} câu
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-black ${
                          item.score >= 80
                            ? 'bg-emerald-100 text-emerald-800'
                            : item.score >= 50
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {item.accuracy}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-emerald-600 font-semibold text-xs flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" /> {item.status}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleViewDetail(item.id)}
                        className="p-1.5 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors cursor-pointer inline-flex items-center gap-1 text-xs font-semibold"
                        title="Xem chi tiết câu trả lời"
                      >
                        <Eye className="w-4 h-4" /> Xem
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* DETAIL MODAL */}
      {selectedAttemptResult && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-2xl max-h-[85vh] rounded-3xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="font-extrabold text-slate-900 text-lg">
                  {selectedAttemptResult.attempt.quizTitle}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Làm vào: {selectedAttemptResult.attempt.takenDate} • Điểm:{' '}
                  <span className="font-bold text-blue-600">
                    {selectedAttemptResult.attempt.score}%
                  </span>
                </p>
              </div>
              <button
                onClick={() => setSelectedAttemptResult(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4">
              {selectedAttemptResult.answers.map((ans, idx) => (
                <div
                  key={ans.answer_id}
                  className={`p-4 rounded-2xl border text-sm ${
                    ans.is_correct
                      ? 'bg-emerald-50/50 border-emerald-200'
                      : 'bg-rose-50/50 border-rose-200'
                  }`}
                >
                  <div className="font-bold text-slate-900 mb-2">
                    Câu {idx + 1}: {ans.question_text_snapshot}
                  </div>
                  <div className="space-y-1 text-xs">
                    <div>
                      <span className="font-semibold text-slate-500">Bạn đã chọn: </span>
                      <span className={ans.is_correct ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}>
                        {ans.selected_answer
                          ? `Đáp án ${ans.selected_answer} (${ans.selected_option_text_snapshot})`
                          : 'Bỏ trống'}
                      </span>
                    </div>
                    {!ans.is_correct && (
                      <div>
                        <span className="font-semibold text-slate-500">Đáp án đúng: </span>
                        <span className="text-emerald-700 font-bold">
                          Đáp án {ans.correct_answer_snapshot} ({ans.correct_option_text_snapshot})
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedAttemptResult(null)}
                className="px-5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs cursor-pointer transition-colors"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
