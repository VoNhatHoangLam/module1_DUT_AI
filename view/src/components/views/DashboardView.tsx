import React from 'react';
import {
  Globe,
  Layers,
  Award,
  Clock,
  ChevronRight,
  CheckCircle,
} from 'lucide-react';
import { UserProfile, FlashcardSet, QuizSet, QuizAttempt, TabType } from '../../types';

interface DashboardViewProps {
  currentUser: UserProfile;
  publicSets: FlashcardSet[];
  mySets: FlashcardSet[];
  publicQuizzes: QuizSet[];
  history: QuizAttempt[];
  navigateTo: (tab: TabType) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  handleStartQuiz: (quiz: QuizSet) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  currentUser: _currentUser,
  publicSets,
  mySets: _mySets,
  publicQuizzes,
  history,
  navigateTo,
  handleStartStudy,
  handleStartQuiz,
}) => {
  return (
    <div className="space-y-8">
      {/* Quick Section: Featured Public Flashcards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Các bộ Flashcard nổi bật</h2>
            <p className="text-sm text-slate-500">Bộ thẻ cộng đồng công khai sẵn sàng để bạn ôn tập ngay</p>
          </div>
          <button
            onClick={() => navigateTo('community')}
            className="text-sm font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 cursor-pointer"
          >
            Xem tất cả ({publicSets.length}) <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {publicSets.slice(0, 3).map((set) => (
            <div
              key={set.id}
              className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
                    {set.category}
                  </span>
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md flex items-center gap-1">
                    <Globe className="w-3 h-3" /> Công khai
                  </span>
                </div>
                <h3 className="font-bold text-lg text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1">
                  {set.title}
                </h3>
                <p className="text-sm text-slate-500 mt-1 line-clamp-2">{set.description}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                  <Layers className="w-3.5 h-3.5 text-blue-500" />
                  {set.cards.length} thẻ • bởi {set.createdBy}
                </span>
                <button
                  onClick={() => handleStartStudy(set)}
                  className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-colors shadow-xs cursor-pointer"
                >
                  Học ngay
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Ready Quizzes & History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ready Quizzes */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-base text-slate-900">Đề thi Quiz sẵn sàng</h3>
            </div>
            <button
              onClick={() => navigateTo('quiz_list')}
              className="text-xs font-semibold text-blue-600 hover:underline cursor-pointer"
            >
              Xem tất cả ({publicQuizzes.length})
            </button>
          </div>
          <div className="space-y-3">
            {publicQuizzes.slice(0, 3).map((q) => (
              <div
                key={q.id}
                className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between hover:border-blue-300 transition-colors"
              >
                <div>
                  <div className="font-bold text-sm text-slate-900 line-clamp-1">{q.title}</div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    {q.questions.length} câu hỏi • Thời gian: {q.timeLimitMinutes} phút • bởi {q.createdBy}
                  </div>
                </div>
                <button
                  onClick={() => handleStartQuiz(q)}
                  className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-colors shadow-xs shrink-0 cursor-pointer"
                >
                  Thi ngay
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Recent History */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-emerald-600" />
              <h3 className="font-bold text-base text-slate-900">Lịch sử làm bài gần đây</h3>
            </div>
            <button
              onClick={() => navigateTo('history')}
              className="text-xs font-semibold text-blue-600 hover:underline cursor-pointer"
            >
              Xem tất cả ({history.length})
            </button>
          </div>
          <div className="space-y-3">
            {history.slice(0, 3).map((h) => (
              <div
                key={h.id}
                className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between"
              >
                <div>
                  <div className="font-bold text-sm text-slate-900 line-clamp-1">{h.quizTitle}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{h.takenDate}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-black ${
                      h.score >= 80
                        ? 'bg-emerald-100 text-emerald-800'
                        : h.score >= 50
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {h.accuracy}
                  </span>
                  <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" /> Xong
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
