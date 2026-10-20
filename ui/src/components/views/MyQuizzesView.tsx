import React, { useState, useMemo } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Award,
  Plus,
  Search,
  Trash2,
  FileText,
  Clock,
} from 'lucide-react';
import { QuizSet, UserProfile, TabType } from '../../types';

interface MyQuizzesViewProps {
  currentUser: UserProfile;
  myPersonalQuizzes: QuizSet[];
  onOpenCreateQuizModal: () => void;
  onOpenImportQuizModal: () => void;
  onDeleteQuizConfirm: (id: string) => void;
  handleStartQuiz: (quiz: QuizSet) => void;
  navigateTo?: (tab: TabType) => void;
}

export const MyQuizzesView: React.FC<MyQuizzesViewProps> = ({
  currentUser,
  myPersonalQuizzes,
  onOpenCreateQuizModal,
  onOpenImportQuizModal,
  onDeleteQuizConfirm,
  handleStartQuiz,
  navigateTo,
}) => {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 6;

  const filteredQuizzes = useMemo(() => {
    return myPersonalQuizzes.filter((q) => {
      const matchSearch =
        (q.title || '').toLowerCase().includes(search.toLowerCase()) ||
        (q.description || '').toLowerCase().includes(search.toLowerCase()) ||
        (q.category || '').toLowerCase().includes(search.toLowerCase());
      return matchSearch;
    });
  }, [myPersonalQuizzes, search]);

  const totalPages = Math.max(1, Math.ceil(filteredQuizzes.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);

  const pagedQuizzes = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredQuizzes.slice(start, start + PAGE_SIZE);
  }, [filteredQuizzes, currentPage]);

  return (
    <div className="space-y-6">
      {/* Header with Title and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <Award className="w-6 h-6 text-indigo-600" />
            Quiz của tôi
          </h1>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenCreateQuizModal}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition-all flex items-center gap-2 shadow-sm cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Tạo đề Quiz mới
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Tìm kiếm trong các đề quiz của bạn..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
          />
        </div>
      </div>

      {/* Personal Quizzes Grid - Paginated */}
      {pagedQuizzes.length > 0 ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pagedQuizzes.map((quiz) => (
              <div
                key={quiz.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <h3 className="font-bold text-lg text-slate-900 line-clamp-1">{quiz.title}</h3>
                  <p className="text-sm text-slate-500 mt-1.5 line-clamp-2">{quiz.description}</p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100">
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                    <span className="flex items-center gap-1 font-medium">
                      <FileText className="w-3.5 h-3.5 text-indigo-500" />
                      {quiz.questions.length} câu hỏi
                    </span>
                    <span className="flex items-center gap-1 font-semibold text-amber-700">
                      <Clock className="w-3.5 h-3.5 text-amber-500" />
                      {quiz.timeLimitMinutes} phút
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleStartQuiz(quiz)}
                      className="flex-1 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs text-center transition-colors shadow-xs cursor-pointer"
                    >
                      Làm bài thi 📝
                    </button>
                    <button
                      onClick={() => onDeleteQuizConfirm(quiz.id)}
                      className="px-3 py-2 rounded-xl border border-rose-200 bg-rose-50 text-rose-600 hover:bg-rose-100 hover:text-rose-700 font-bold text-xs flex items-center gap-1 transition-colors cursor-pointer"
                      title="Xóa bộ đề Quiz này"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Xóa
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Centered Pagination Bar (đã xóa dòng số lượng và căn giữa theo yêu cầu) */}
          {filteredQuizzes.length > 0 && (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-center">
              <div className="flex items-center justify-center gap-1.5">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <ChevronLeft className="w-3.5 h-3.5" /> Trước
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`w-8 h-8 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      pageNum === currentPage
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'text-slate-600 hover:bg-slate-100 border border-slate-200'
                    }`}
                  >
                    {pageNum}
                  </button>
                ))}

                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer"
                >
                  Sau <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-3">
          <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-500 flex items-center justify-center mx-auto">
            <Award className="w-6 h-6" />
          </div>
          <p className="text-base font-bold text-slate-800">Không tìm thấy bộ đề Quiz nào phù hợp.</p>
          <p className="text-xs max-w-md mx-auto">
            Hãy thử xóa từ khóa tìm kiếm hoặc tạo đề thi mới.
          </p>
          <button
            onClick={() => {
              setSearch('');
            }}
            className="px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold cursor-pointer"
          >
            Xóa tìm kiếm
          </button>
        </div>
      )}
    </div>
  );
};
