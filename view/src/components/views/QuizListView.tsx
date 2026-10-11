import React from 'react';
import { Award, Search, Upload, Plus, Clock } from 'lucide-react';
import { QuizSet } from '../../types';

interface QuizListViewProps {
  publicQuizzes: QuizSet[];
  searchKeyword: string;
  setSearchKeyword: (val: string) => void;
  filterCategory: string;
  setFilterCategory: (val: string) => void;
  onOpenCreateQuizModal: () => void;
  onOpenImportQuizModal: () => void;
  handleStartQuiz: (quiz: QuizSet) => void;
}

export const QuizListView: React.FC<QuizListViewProps> = ({
  publicQuizzes,
  searchKeyword,
  setSearchKeyword,
  filterCategory,
  setFilterCategory,
  onOpenCreateQuizModal,
  onOpenImportQuizModal,
  handleStartQuiz,
}) => {
  return (
    <div className="space-y-6">
      {/* Header with action buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <Award className="w-6 h-6 text-indigo-600" />
            Quiz
          </h1>
          <p className="text-sm text-slate-500">
            Khám phá và làm các bài thi trắc nghiệm công khai của mọi người, tự tạo đề hoặc nhập từ file
          </p>
        </div>

        {/* Hai nút thao tác: "Nhập từ file" và "Tạo bộ đề mới" */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenImportQuizModal}
            className="px-4 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm transition-all flex items-center gap-2 shadow-xs cursor-pointer"
          >
            <Upload className="w-4 h-4 text-slate-500" />
            Nhập từ file
          </button>
          <button
            onClick={onOpenCreateQuizModal}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all flex items-center gap-2 shadow-sm cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Tạo bộ đề mới
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Tìm kiếm bộ đề quiz..."
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <label className="text-xs font-semibold text-slate-500 whitespace-nowrap">Chủ đề:</label>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">Tất cả chủ đề</option>
            <option value="Công nghệ thông tin">Công nghệ thông tin</option>
            <option value="Ngoại ngữ">Ngoại ngữ</option>
            <option value="Thiết kế">Thiết kế</option>
          </select>
        </div>
      </div>

      {/* Quiz Grid: All public, approved quizzes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {publicQuizzes.map((quiz) => (
          <div
            key={quiz.id}
            className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
                  {quiz.category}
                </span>
                <span className="text-xs text-slate-500 flex items-center gap-1 font-semibold">
                  <Clock className="w-3.5 h-3.5 text-amber-500" />
                  {quiz.timeLimitMinutes} phút
                </span>
              </div>
              <h3 className="font-bold text-lg text-slate-900">{quiz.title}</h3>
              <p className="text-sm text-slate-500 mt-1.5">{quiz.description}</p>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-semibold">
                {quiz.questions.length} câu hỏi • Tác giả: <b>{quiz.createdBy}</b>
              </span>
              <button
                onClick={() => handleStartQuiz(quiz)}
                className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-colors shadow-xs cursor-pointer"
              >
                Bắt đầu thi ngay
              </button>
            </div>
          </div>
        ))}
      </div>

      {publicQuizzes.length === 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-2">
          <p className="text-base font-bold">Không tìm thấy bài thi quiz công khai nào.</p>
          <p className="text-xs">Hãy thử đổi từ khóa tìm kiếm hoặc tạo một bộ đề mới.</p>
        </div>
      )}
    </div>
  );
};
