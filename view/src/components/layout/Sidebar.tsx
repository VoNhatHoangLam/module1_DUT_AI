import React from 'react';
import {
  Layers,
  Award,
  Clock,
  Shield,
  ShieldAlert,
  Globe,
  User,
  Users,
  ChevronLeft,
  X,
  LogIn,
  UserPlus,
} from 'lucide-react';
import { UserProfile, TabType } from '../../types';

interface SidebarProps {
  currentTab: TabType;
  navigateTo: (tab: TabType) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  isMobileOpen: boolean;
  setIsMobileOpen: (open: boolean) => void;
  currentUser: UserProfile;
  setCurrentUser: (user: UserProfile) => void;
  users: UserProfile[];
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  navigateTo,
  isOpen,
  setIsOpen,
  isMobileOpen,
  setIsMobileOpen,
  currentUser,
  setCurrentUser,
  users,
  notify,
}) => {
  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-40 md:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Aside Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 w-64 bg-white border-r border-slate-200 z-50 flex flex-col justify-between transition-transform duration-300 ease-in-out ${
          isMobileOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
        } ${isOpen ? 'md:translate-x-0' : 'md:-translate-x-full'}`}
      >
        {/* Top: Logo & Branding */}
        <div>
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <div
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => navigateTo('dashboard')}
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-blue-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <Layers className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-xl tracking-tight text-blue-900">FlashLearn</span>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 uppercase tracking-wide">
                  Quizlet Style
                </span>
              </div>
            </div>

            {/* Close / Collapse button */}
            <button
              onClick={() => {
                setIsOpen(false);
                setIsMobileOpen(false);
              }}
              className="p-1.5 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer flex items-center justify-center group"
              title="Đóng / Thu gọn thanh bên"
              aria-label="Đóng / Thu gọn thanh bên"
            >
              <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
            </button>
          </div>

          {/* Vertical Menu Items */}
          <nav className="p-3 space-y-1">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-3 py-1.5">
              Menu điều hướng
            </div>

            {/* 1. Tổng quan */}
            <button
              onClick={() => navigateTo('dashboard')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'dashboard'
                  ? 'bg-blue-50 text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Layers className={`w-5 h-5 ${currentTab === 'dashboard' ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>Tổng quan</span>
            </button>

            {/* 2. Flashcard (hiển thị bộ thẻ công khai của cộng đồng) */}
            <button
              onClick={() => navigateTo('community')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'community'
                  ? 'bg-blue-50 text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Globe className={`w-5 h-5 ${currentTab === 'community' ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>Flashcard</span>
            </button>

            {/* 3. Quiz */}
            <button
              onClick={() => navigateTo('quiz_list')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'quiz_list'
                  ? 'bg-blue-50 text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Award className={`w-5 h-5 ${currentTab === 'quiz_list' ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>Quiz</span>
            </button>

            {/* 4. Lịch sử thi */}
            <button
              onClick={() => navigateTo('history')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'history'
                  ? 'bg-blue-50 text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Clock className={`w-5 h-5 ${currentTab === 'history' ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>Lịch sử thi</span>
            </button>

            {/* 5. Profile */}
            <button
              onClick={() => navigateTo('profile')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'profile'
                  ? 'bg-blue-50 text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <User className={`w-5 h-5 ${currentTab === 'profile' ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>Profile</span>
            </button>

            {/* Auth section */}
            <div className="pt-2 pb-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-3 py-1">
                Tài khoản
              </div>
            </div>

            {/* Đăng nhập */}
            <button
              onClick={() => navigateTo('login')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'login'
                  ? 'bg-blue-50 text-blue-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <LogIn className={`w-5 h-5 ${currentTab === 'login' ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>Đăng nhập</span>
            </button>

            {/* Đăng ký */}
            <button
              onClick={() => navigateTo('register')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                currentTab === 'register'
                  ? 'bg-emerald-50 text-emerald-700 font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <UserPlus className={`w-5 h-5 ${currentTab === 'register' ? 'text-emerald-600' : 'text-slate-400'}`} />
              <span>Đăng ký</span>
            </button>

            {/* Admin Tabs */}
            {currentUser.role === 'admin' && (
              <>
                <div className="pt-2 pb-1">
                  <div className="text-[10px] font-extrabold text-indigo-500 uppercase tracking-wider px-3 py-1 bg-indigo-50/60 rounded-lg flex items-center gap-1.5">
                    <Shield className="w-3 h-3" /> Dành cho Admin
                  </div>
                </div>

                {/* 6. Quản lý tài khoản */}
                <button
                  onClick={() => navigateTo('admin_users')}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                    currentTab === 'admin_users'
                      ? 'bg-indigo-50 text-indigo-700 font-bold shadow-xs'
                      : 'text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50/70'
                  }`}
                >
                  <Users className={`w-5 h-5 ${currentTab === 'admin_users' ? 'text-indigo-600' : 'text-indigo-500'}`} />
                  <span>Quản lý tài khoản</span>
                </button>

                {/* 7. Kiểm duyệt Flashcards */}
                <button
                  onClick={() => navigateTo('admin_moderation')}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left ${
                    currentTab === 'admin_moderation'
                      ? 'bg-rose-50 text-rose-700 font-bold shadow-xs'
                      : 'text-rose-600 hover:text-rose-800 hover:bg-rose-50/70'
                  }`}
                >
                  <ShieldAlert className={`w-5 h-5 ${currentTab === 'admin_moderation' ? 'text-rose-600' : 'text-rose-500'}`} />
                  <span>Kiểm duyệt Flashcards</span>
                </button>
              </>
            )}
          </nav>
        </div>

        {/* Bottom: Role Switcher & User Profile Info */}
        <div className="p-4 border-t border-slate-100 space-y-3 bg-slate-50/60">
          {/* Quick Role Switcher */}
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
              Chuyển vai trò demo
            </div>
            <div className="grid grid-cols-2 gap-1.5 bg-slate-200/70 p-1 rounded-xl">
              <button
                onClick={() => {
                  const u = users.find((x) => x.role === 'user') || users[0];
                  setCurrentUser(u);
                  notify(`Đã chuyển sang Học viên: ${u.name}`, 'info');
                }}
                className={`py-1 text-xs font-bold rounded-lg transition-all ${
                  currentUser.role === 'user' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Học viên
              </button>
              <button
                onClick={() => {
                  const adminUser = users.find((x) => x.role === 'admin') || users[2];
                  setCurrentUser(adminUser);
                  notify('Đã chuyển sang Quản trị viên (Admin)', 'info');
                }}
                className={`py-1 text-xs font-bold rounded-lg transition-all ${
                  currentUser.role === 'admin' ? 'bg-rose-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Admin
              </button>
            </div>
          </div>

          {/* Current User Card */}
          <div
            onClick={() => navigateTo('profile')}
            className={`flex items-center gap-3 p-2 rounded-xl border transition-all cursor-pointer shadow-xs ${
              currentTab === 'profile'
                ? 'bg-blue-50/80 border-blue-400 ring-2 ring-blue-500/20'
                : 'bg-white border-slate-200 hover:border-blue-400'
            }`}
            title="Xem hồ sơ cá nhân"
          >
            <img
              src={currentUser.avatar}
              alt={currentUser.name}
              className="w-9 h-9 rounded-full object-cover ring-2 ring-blue-500/30 shrink-0"
            />
            <div className="min-w-0 flex-1">
              <div className="text-xs font-bold text-slate-800 truncate">{currentUser.name}</div>
              <div className="text-[11px] text-slate-500 truncate">{currentUser.email}</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
