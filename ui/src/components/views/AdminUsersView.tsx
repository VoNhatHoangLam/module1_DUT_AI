import React, { useState, useMemo } from 'react';
import {
  Users,
  Search,
  UserCheck,
  UserX,
  Shield,
  ChevronLeft,
  ChevronRight,
  Lock,
  Unlock,
  CheckCircle2,
} from 'lucide-react';
import { UserProfile } from '../../types';

interface AdminUsersViewProps {
  users: UserProfile[];
  currentUser: UserProfile;
  onToggleUserStatus: (userId: string) => void;
  onChangeUserRole: (userId: string, newRole: 'user' | 'admin') => void;
  onAddUser: (user: Partial<UserProfile>) => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const AdminUsersView: React.FC<AdminUsersViewProps> = ({
  users,
  currentUser,
  onToggleUserStatus,
  onChangeUserRole,
  onAddUser,
  notify,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | 'user' | 'admin'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'locked'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 8;

  // Stats
  const totalUsers = users.length;
  const activeUsers = users.filter((u) => u.status === 'active').length;
  const lockedUsers = users.filter((u) => u.status === 'locked').length;
  const adminUsers = users.filter((u) => u.role === 'admin').length;

  const filteredUsers = useMemo(() => {
    return users.filter((u) => {
      const matchSearch =
        u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (u.bio || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchRole = roleFilter === 'all' || u.role === roleFilter;
      const matchStatus = statusFilter === 'all' || u.status === statusFilter;
      return matchSearch && matchRole && matchStatus;
    });
  }, [users, searchTerm, roleFilter, statusFilter]);

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / pageSize));
  const validCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (validCurrentPage - 1) * pageSize;
  const paginatedUsers = filteredUsers.slice(startIndex, startIndex + pageSize);

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Tổng số người dùng</span>
            <Users className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-3xl font-black text-slate-900 mt-2">{totalUsers}</div>
          <div className="text-xs text-slate-500 mt-1">Bao gồm học viên & admin</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Đang hoạt động</span>
            <UserCheck className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-black text-emerald-600 mt-2">{activeUsers}</div>
          <div className="text-xs text-emerald-600 font-semibold mt-1">
            {((activeUsers / (totalUsers || 1)) * 100).toFixed(0)}% tổng số
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Tài khoản bị khóa</span>
            <UserX className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-3xl font-black text-rose-600 mt-2">{lockedUsers}</div>
          <div className="text-xs text-rose-500 font-semibold mt-1">Bị giới hạn quyền truy cập</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Quản trị viên</span>
            <Shield className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-black text-indigo-600 mt-2">{adminUsers}</div>
          <div className="text-xs text-indigo-600 font-semibold mt-1">Có toàn quyền hệ thống</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="relative flex-1 min-w-0 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Tìm theo tên, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
          />
        </div>

        <div className="flex flex-row items-center gap-2.5 sm:gap-4 shrink-0">
          <div className="flex items-center gap-1.5 text-xs text-slate-600 whitespace-nowrap">
            <span className="font-semibold">Vai trò:</span>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as any)}
              className="bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="all">Tất cả vai trò</option>
              <option value="user">Học viên (User)</option>
              <option value="admin">Quản trị (Admin)</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-600 whitespace-nowrap">
            <span className="font-semibold">Trạng thái:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="all">Tất cả trạng thái</option>
              <option value="active">Đang hoạt động</option>
              <option value="locked">Bị khóa</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <h3 className="font-extrabold text-slate-900 text-sm flex items-center gap-2">
            <Users className="w-4 h-4 text-indigo-600" /> Danh sách tài khoản ({filteredUsers.length})
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="px-6 py-3.5">Học viên</th>
                <th className="px-6 py-3.5 w-44">Vai trò</th>
                <th className="px-6 py-3.5 w-44">Trạng thái</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedUsers.map((u) => {
                const isSelf = u.id === currentUser.id;
                return (
                  <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3.5">
                        <img
                          src={u.avatar}
                          alt={u.name}
                          className="w-10 h-10 rounded-full object-cover ring-2 ring-slate-100 shrink-0"
                        />
                        <div className="min-w-0">
                          <div className="font-bold text-slate-900 text-sm flex items-center gap-2">
                            <span>{u.name}</span>
                            {isSelf && (
                              <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-bold shrink-0">
                                Bạn
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5 line-clamp-1">{u.bio || 'Chưa có tiểu sử'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={u.role}
                        disabled={isSelf}
                        onChange={(e) => {
                          const newRole = e.target.value as 'user' | 'admin';
                          onChangeUserRole(u.id, newRole);
                        }}
                        className={`text-xs font-semibold rounded-lg px-2.5 py-1.5 border transition-all cursor-pointer ${
                          u.role === 'admin'
                            ? 'bg-purple-50 text-purple-800 border-purple-200 focus:ring-purple-400'
                            : 'bg-slate-50 text-slate-700 border-slate-200 focus:ring-indigo-400'
                        } ${isSelf ? 'opacity-60 cursor-not-allowed' : ''}`}
                        title={isSelf ? 'Không thể tự đổi vai trò của chính mình' : 'Chọn vai trò'}
                      >
                        <option value="user">USER</option>
                        <option value="admin">ADMIN</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={u.status}
                        disabled={isSelf}
                        onChange={(e) => {
                          onToggleUserStatus(u.id);
                        }}
                        className={`text-xs font-semibold rounded-lg px-2.5 py-1.5 border transition-all cursor-pointer ${
                          u.status === 'active'
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200 focus:ring-emerald-400'
                            : 'bg-rose-50 text-rose-800 border-rose-200 focus:ring-rose-400'
                        } ${isSelf ? 'opacity-60 cursor-not-allowed' : ''}`}
                        title={isSelf ? 'Không thể tự khóa tài khoản của chính mình' : 'Chọn trạng thái'}
                      >
                        <option value="active">Hoạt động</option>
                        <option value="locked">Bị Khóa</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            Không tìm thấy tài khoản nào khớp với bộ lọc.
          </div>
        ) : (
          /* Pagination Bar */
          <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-center text-xs text-slate-600">
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={validCurrentPage <= 1}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title="Trang trước"
              >
                <ChevronLeft className="w-4 h-4 text-slate-700" />
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNumber) => (
                  <button
                    key={pageNumber}
                    onClick={() => setCurrentPage(pageNumber)}
                    className={`w-7 h-7 rounded-lg text-xs font-bold transition-all ${
                      pageNumber === validCurrentPage
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {pageNumber}
                  </button>
                ))}
              </div>

              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={validCurrentPage >= totalPages}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title="Trang sau"
              >
                <ChevronRight className="w-4 h-4 text-slate-700" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
