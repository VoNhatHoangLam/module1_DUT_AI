import React, { useState } from 'react';
import {
  UserPlus,
  User,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';
import { UserProfile, TabType } from '../../types';

interface RegisterViewProps {
  users: UserProfile[];
  onRegisterSuccess: (newUser: UserProfile) => void;
  navigateTo: (tab: TabType) => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const RegisterView: React.FC<RegisterViewProps> = ({
  users,
  onRegisterSuccess,
  navigateTo,
  notify,
}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    const cleanUsername = username.trim();
    const cleanPassword = password.trim();
    const cleanConfirm = confirmPassword.trim();

    if (!cleanUsername) {
      setErrorMessage('Vui lòng nhập tên đăng nhập (username).');
      return;
    }

    if (cleanUsername.length < 3) {
      setErrorMessage('Tên đăng nhập phải chứa ít nhất 3 ký tự.');
      return;
    }

    // Check alphanumeric or underscore
    if (!/^[a-zA-Z0-9_]+$/.test(cleanUsername)) {
      setErrorMessage('Tên đăng nhập chỉ được gồm chữ cái, số hoặc dấu gạch dưới (_), không dấu cách.');
      return;
    }

    // Check username unique
    const exists = users.some(
      (u) =>
        u.username?.toLowerCase() === cleanUsername.toLowerCase() ||
        u.name.toLowerCase() === cleanUsername.toLowerCase()
    );
    if (exists) {
      setErrorMessage(`Tên đăng nhập "${cleanUsername}" đã có người sử dụng. Vui lòng chọn tên khác!`);
      return;
    }

    if (!cleanPassword) {
      setErrorMessage('Vui lòng nhập mật khẩu.');
      return;
    }

    if (cleanPassword.length < 6) {
      setErrorMessage('Mật khẩu cần tối thiểu 6 ký tự để bảo mật an toàn.');
      return;
    }

    if (cleanPassword !== cleanConfirm) {
      setErrorMessage('Mật khẩu xác nhận không khớp. Vui lòng kiểm tra lại!');
      return;
    }

    const finalEmail = `${cleanUsername.toLowerCase()}@flashlearn.vn`;

    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      const randomAvatarSeed = Math.floor(Math.random() * 70) + 1;
      const newUser: UserProfile = {
        id: `u_${Date.now()}`,
        name: fullName.trim() || cleanUsername,
        username: cleanUsername,
        password: cleanPassword,
        email: finalEmail,
        role: 'user',
        avatar: `https://images.unsplash.com/photo-${1534528741775 + randomAvatarSeed}?auto=format&fit=crop&w=200&h=200&q=80`,
        joinDate: new Date().toLocaleDateString('vi-VN'),
        status: 'active',
        bio: 'Học viên mới tham gia cộng đồng FlashLearn.',
      };

      notify(`Tạo tài khoản "${cleanUsername}" thành công! Đang tự động đăng nhập...`, 'success');
      onRegisterSuccess(newUser);
    }, 400);
  };

  return (
    <div className="max-w-md mx-auto py-6 sm:py-10">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden p-6 sm:p-8">
        <div className="mb-6">
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
            <UserPlus className="w-6 h-6 text-emerald-600" /> Tạo tài khoản mới
          </h1>
        </div>

          {/* Error Notice */}
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2.5 animate-shake">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            {/* 1. Username (Required) */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Tên đăng nhập (Username) <span className="text-rose-500">*</span>
                </label>
                <span className="text-[11px] text-slate-400 font-medium">Chữ, số hoặc _</span>
              </div>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Ví dụ: hocvien_2024"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white bg-slate-50/50 font-medium"
                  required
                  autoFocus
                />
              </div>
            </div>

            {/* 2. Full Name / Display Name (Optional) */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Họ và tên hiển thị <span className="text-slate-400 font-normal">(tùy chọn)</span>
              </label>
              <input
                type="text"
                placeholder="Ví dụ: Lê Minh Anh"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white bg-slate-50/50"
              />
            </div>

            {/* 3. Password (Required) */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Mật khẩu <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Nhập ít nhất 6 ký tự"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-11 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white bg-slate-50/50"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* 4. Confirm Password (Required) */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Nhập lại mật khẩu <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Xác nhận lại mật khẩu"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-11 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white bg-slate-50/50"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1 cursor-pointer"
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-sm shadow-md shadow-emerald-500/20 hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60 mt-2"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  <span>Hoàn tất đăng ký tài khoản</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Switch to Login */}
          <div className="mt-8 pt-6 border-t border-slate-100 text-center text-xs text-slate-600">
            <span>Bạn đã có tài khoản FlashLearn? </span>
            <button
              type="button"
              onClick={() => navigateTo('login')}
              className="font-bold text-emerald-600 hover:text-emerald-800 hover:underline cursor-pointer ml-1"
            >
              Đăng nhập ngay
            </button>
          </div>
      </div>
    </div>
  );
};
