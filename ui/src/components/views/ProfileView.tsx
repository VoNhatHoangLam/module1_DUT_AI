import React from 'react';
import {
  Plus,
  BookmarkCheck,
  Award,
  ChevronRight,
  Trash2,
  FileText,
  Clock,
} from 'lucide-react';
import { UserProfile, FlashcardSet, QuizSet, QuizAttempt, TabType } from '../../types';

interface ProfileViewProps {
  currentUser: UserProfile;
  setCurrentUser: React.Dispatch<React.SetStateAction<UserProfile>>;
  myPersonalSets: FlashcardSet[];
  myPersonalQuizzes: QuizSet[];
  history: QuizAttempt[];
  onOpenCreateSetModal: () => void;
  onOpenCreateQuizModal: () => void;
  onDeleteSetConfirm: (id: string) => void;
  onDeleteQuizConfirm: (id: string) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  handleStartQuiz: (quiz: QuizSet) => void;
  navigateTo: (tab: TabType) => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({
  currentUser,
  setCurrentUser,
  myPersonalSets,
  myPersonalQuizzes,
  history,
  onOpenCreateSetModal,
  onOpenCreateQuizModal,
  onDeleteSetConfirm,
  onDeleteQuizConfirm,
  handleStartStudy,
  handleStartQuiz,
  navigateTo,
  notify,
}) => {
  return (
    <div className="max-w-5xl mx-auto space-y-10">
      {/* SECTION 1: PROFILE INFORMATION CARD */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <img
              src={currentUser.avatar}
              alt={currentUser.name}
              className="w-20 h-20 rounded-2xl object-cover ring-4 ring-blue-500/20 shadow-md shrink-0"
            />
            <div>
              <h3 className="text-xl font-extrabold text-slate-900">{currentUser.name}</h3>
              <p className="text-sm text-slate-500">{currentUser.email}</p>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 uppercase tracking-wide">
                  Vai trò: {currentUser.role}
                </span>
                <span className="text-xs text-slate-400">Tham gia từ: {currentUser.joinDate}</span>
              </div>
            </div>
          </div>

          {/* Summary Metric Counters */}
          <div className="grid grid-cols-3 gap-3 bg-slate-50/80 p-3 rounded-2xl border border-slate-200/80 text-center sm:min-w-64">
            <div className="px-2 py-1">
              <div className="text-xl font-black text-blue-600">{myPersonalSets.length}</div>
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Flashcard</div>
            </div>
            <div className="px-2 py-1 border-x border-slate-200">
              <div className="text-xl font-black text-indigo-600">{myPersonalQuizzes.length}</div>
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Đề Quiz</div>
            </div>
            <div className="px-2 py-1">
              <div className="text-xl font-black text-emerald-600">{history.length}</div>
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Lượt thi</div>
            </div>
          </div>
        </div>

        <div className="space-y-4 pt-4 border-t border-slate-100">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Tên hiển thị
            </label>
            <input
              type="text"
              value={currentUser.name}
              onChange={(e) => setCurrentUser({ ...currentUser, name: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white bg-slate-50/50"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Tiểu sử & Mục tiêu học tập
            </label>
            <textarea
              rows={3}
              value={currentUser.bio}
              onChange={(e) => setCurrentUser({ ...currentUser, bio: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white bg-slate-50/50"
            />
          </div>

          <button
            onClick={() => notify('Đã cập nhật hồ sơ cá nhân thành công!', 'success')}
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-xs transition-colors cursor-pointer"
          >
            Lưu thay đổi
          </button>
        </div>
      </div>

      {/* SECTION 2: FLASHCARD CỦA TÔI (HIỂN THỊ VÀI BỘ + NÚT XEM THÊM TẤT CẢ) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
                <BookmarkCheck className="w-5 h-5 text-blue-600" />
                Flashcard của tôi
              </h2>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
                {myPersonalSets.length} bộ
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Các bộ flashcard do bạn ({currentUser.name}) tự tạo để ghi nhớ kiến thức
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onOpenCreateSetModal}
              className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-xs cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" /> Tạo bộ mới
            </button>
            <button
              onClick={() => navigateTo('sets')}
              className="px-3.5 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs transition-colors flex items-center gap-1 shadow-xs border border-blue-200 cursor-pointer"
            >
              Xem thêm <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {myPersonalSets.length > 0 ? (
          <div className="space-y-4">
            {/* Flashcards Grid (preview: 3 items) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {myPersonalSets.slice(0, 3).map((set) => (
                <div
                  key={set.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
                        {set.category}
                      </span>
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-md ${
                          set.privacy === 'public'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {set.privacy === 'public' ? '🌐 Công khai' : '🔒 Riêng tư'}
                      </span>
                    </div>

                    <h3 className="font-bold text-base text-slate-900 line-clamp-1">{set.title}</h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{set.description}</p>
                  </div>

                  <div className="mt-5 pt-3.5 border-t border-slate-100">
                    <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
                      <span className="font-medium">{set.cards.length} thẻ ghi nhớ</span>
                      <span className="text-slate-400">{set.updatedAt}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleStartStudy(set)}
                        className="flex-1 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs text-center transition-colors shadow-xs cursor-pointer"
                      >
                        Bắt đầu ôn tập 🎯
                      </button>
                      <button
                        onClick={() => onDeleteSetConfirm(set.id)}
                        className="p-2 rounded-xl border border-rose-200 bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors cursor-pointer"
                        title="Xóa bộ flashcard này"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-500 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
              <BookmarkCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-800 text-sm">Chưa có bộ flashcard nào</h4>
              <p className="text-xs text-slate-500 mt-1">
                Tạo bộ thẻ đầu tiên để bắt đầu ghi nhớ kiến thức theo phương pháp lặp lại ngắt quãng.
              </p>
            </div>
            <button
              onClick={onOpenCreateSetModal}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs inline-flex items-center gap-1.5 shadow-xs cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Tạo bộ thẻ mới
            </button>
          </div>
        )}
      </div>

      {/* SECTION 3: QUIZ CỦA TÔI (HIỂN THỊ TƯƠNG TỰ NHƯ FLASHCARD CỦA TÔI) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
                <Award className="w-5 h-5 text-indigo-600" />
                Quiz của tôi
              </h2>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800">
                {myPersonalQuizzes.length} đề thi
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Các bộ đề thi trắc nghiệm do bạn ({currentUser.name}) tự biên soạn và quản lý
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onOpenCreateQuizModal}
              className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-xs cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" /> Tạo đề Quiz mới
            </button>
            <button
              onClick={() => navigateTo('my_quizzes')}
              className="px-3.5 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs transition-colors flex items-center gap-1 shadow-xs border border-indigo-200 cursor-pointer"
            >
              Xem thêm <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {myPersonalQuizzes.length > 0 ? (
          <div className="space-y-4">
            {/* Quiz Grid (preview: 3 items) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {myPersonalQuizzes.slice(0, 3).map((quiz) => (
                <div
                  key={quiz.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
                        {quiz.category}
                      </span>
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-md ${
                          quiz.status === 'approved'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : quiz.status === 'pending'
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {quiz.status === 'approved'
                          ? '🌐 Đã duyệt (Công khai)'
                          : quiz.status === 'pending'
                          ? '⏳ Chờ duyệt (Cá nhân)'
                          : '⛔ Bị từ chối'}
                      </span>
                    </div>

                    <h3 className="font-bold text-base text-slate-900 line-clamp-1">{quiz.title}</h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{quiz.description}</p>
                  </div>

                  <div className="mt-5 pt-3.5 border-t border-slate-100">
                    <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
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
                        className="p-2 rounded-xl border border-rose-200 bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors cursor-pointer"
                        title="Xóa bộ đề Quiz này"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-500 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-800 text-sm">Chưa có bộ đề Quiz nào</h4>
              <p className="text-xs text-slate-500 mt-1">
                Hãy tạo bài kiểm tra trắc nghiệm đầu tiên để tự luyện thi hoặc chia sẻ cùng bạn bè.
              </p>
            </div>
            <button
              onClick={onOpenCreateQuizModal}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs inline-flex items-center gap-1.5 shadow-xs cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Tạo bộ đề Quiz mới
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
