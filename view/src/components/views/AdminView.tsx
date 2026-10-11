import React from 'react';
import {
  Shield,
  RefreshCw,
  Users,
  Layers,
  BookOpen,
  Trash2,
} from 'lucide-react';
import { UserProfile, FlashcardSet, QuizSet } from '../../types';

interface AdminViewProps {
  users: UserProfile[];
  sets: FlashcardSet[];
  quizzes: QuizSet[];
  publicQuizzes: QuizSet[];
  onToggleUserStatus: (userId: string) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  onDeleteSetConfirm: (id: string) => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const AdminView: React.FC<AdminViewProps> = ({
  users,
  sets,
  quizzes,
  publicQuizzes,
  onToggleUserStatus,
  handleStartStudy,
  onDeleteSetConfirm,
  notify,
}) => {
  return (
    <div className="space-y-8">
      <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 text-xs font-bold uppercase tracking-wider mb-2">
            <Shield className="w-3.5 h-3.5" /> Bảng điều khiển Quản trị hệ thống
          </div>
          <h1 className="text-2xl sm:text-3xl font-black">FlashLearn Admin Center</h1>
          <p className="text-slate-400 text-sm mt-1">
            Kiểm duyệt nội dung flashcard, phân quyền và giám sát hoạt động người dùng toàn hệ thống.
          </p>
        </div>
        <button
          onClick={() => notify('Đã làm mới dữ liệu hệ thống!', 'info')}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs border border-slate-700 flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Làm mới số liệu
        </button>
      </div>

      {/* Admin Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-slate-500 uppercase">Tổng số tài khoản</div>
          <div className="text-3xl font-black text-slate-800 mt-2">{users.length}</div>
          <div className="text-xs text-emerald-600 font-semibold mt-1">
            {users.filter((u) => u.status === 'active').length} đang hoạt động
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-slate-500 uppercase">Tổng số bộ thẻ</div>
          <div className="text-3xl font-black text-blue-600 mt-2">{sets.length}</div>
          <div className="text-xs text-slate-500 mt-1">
            {sets.reduce((acc, s) => acc + s.cards.length, 0)} thẻ học tổng
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-slate-500 uppercase">Tổng số đề Quiz</div>
          <div className="text-3xl font-black text-amber-500 mt-2">
            {quizzes.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">{publicQuizzes.length} đề thi công khai</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold text-slate-500 uppercase">Tài khoản bị khóa</div>
          <div className="text-3xl font-black text-rose-600 mt-2">
            {users.filter((u) => u.status === 'locked').length}
          </div>
          <div className="text-xs text-rose-500 font-semibold mt-1">Vi phạm tiêu chuẩn</div>
        </div>
      </div>

      {/* User Management */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="font-extrabold text-lg text-slate-900 flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-600" /> Quản lý tài khoản người dùng
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Người dùng</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Vai trò</th>
                <th className="px-4 py-3">Trạng thái</th>
                <th className="px-4 py-3 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-semibold flex items-center gap-2">
                    <img src={u.avatar} alt={u.name} className="w-7 h-7 rounded-full object-cover" />
                    {u.name}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{u.email}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-md text-xs font-bold uppercase ${
                        u.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        u.status === 'active'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {u.status === 'active' ? 'Hoạt động' : 'Bị khóa'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {u.role !== 'admin' && (
                      <button
                        onClick={() => onToggleUserStatus(u.id)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors cursor-pointer ${
                          u.status === 'active'
                            ? 'bg-rose-50 text-rose-700 hover:bg-rose-100'
                            : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                        }`}
                      >
                        {u.status === 'active' ? 'Khóa tài khoản' : 'Mở khóa'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Flashcard Management */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-extrabold text-lg text-slate-900 flex items-center gap-2">
              <Layers className="w-5 h-5 text-blue-600" /> Quản lý bộ thẻ Flashcard
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Xem nội dung chi tiết hoặc xóa bộ thẻ trong toàn hệ thống. Người dùng có thể đăng công khai ngay lập tức không cần kiểm duyệt.
            </p>
          </div>
          <span className="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full self-start sm:self-auto">
            Tổng: {sets.length} bộ thẻ
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Tiêu đề bộ thẻ</th>
                <th className="px-4 py-3">Người tạo</th>
                <th className="px-4 py-3">Chủ đề</th>
                <th className="px-4 py-3">Số thẻ</th>
                <th className="px-4 py-3">Quyền riêng tư</th>
                <th className="px-4 py-3 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sets.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-semibold text-slate-900">
                    <div>{s.title}</div>
                    <div className="text-[11px] text-slate-400 font-normal line-clamp-1">{s.description}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-600 text-xs">{s.createdBy}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-medium">
                      {s.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-medium">{s.cards.length} thẻ</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        s.privacy === 'public'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {s.privacy === 'public' ? '🌐 Công khai' : '🔒 Riêng tư'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                    <button
                      onClick={() => handleStartStudy(s)}
                      className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-bold transition-colors inline-flex items-center gap-1 cursor-pointer"
                      title="Xem chi tiết và ôn tập bộ thẻ"
                    >
                      <BookOpen className="w-3.5 h-3.5" />
                      Xem
                    </button>
                    <button
                      onClick={() => onDeleteSetConfirm(s.id)}
                      className="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100 text-xs font-bold transition-colors inline-flex items-center gap-1 cursor-pointer"
                      title="Xóa bộ flashcard này"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Xóa
                    </button>
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
