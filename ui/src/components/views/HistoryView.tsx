import React from 'react';
import { Clock, CheckCircle } from 'lucide-react';
import { QuizAttempt } from '../../types';

interface HistoryViewProps {
  history: QuizAttempt[];
}

export const HistoryView: React.FC<HistoryViewProps> = ({ history }) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
          <Clock className="w-6 h-6 text-emerald-600" />
          Lịch sử làm bài thi
        </h1>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="px-6 py-3.5">Tên bài thi</th>
                <th className="px-6 py-3.5">Ngày làm bài</th>
                <th className="px-6 py-3.5">Số câu đúng</th>
                <th className="px-6 py-3.5">Tỷ lệ chính xác</th>
                <th className="px-6 py-3.5">Trạng thái</th>
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
