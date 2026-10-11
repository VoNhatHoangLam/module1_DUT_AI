import React, { useState } from 'react';
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { UserProfile, TabType } from '../../types';

interface LoginViewProps {
  users: UserProfile[];
  onLoginSuccess: (user: UserProfile) => void;
  navigateTo: (tab: TabType) => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

type LoginMethod = 'username' | 'email';

export const LoginView: React.FC<LoginViewProps> = ({
  users,
  onLoginSuccess,
  navigateTo,
  notify,
}) => {
  const [loginMethod, setLoginMethod] = useState<LoginMethod>('username');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    if (loginMethod === 'username') {
      const trimmedUser = username.trim();
      if (!trimmedUser) {
        setErrorMessage('Vui lòng nhập tên đăng nhập (username).');
        return;
      }
      if (!password) {
        setErrorMessage('Vui lòng nhập mật khẩu.');
        return;
      }

      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        const matched = users.find(
          (u) =>
            u.username?.toLowerCase() === trimmedUser.toLowerCase() ||
            u.name.toLowerCase() === trimmedUser.toLowerCase()
        );

        if (!matched) {
          setErrorMessage('Tên đăng nhập không tồn tại trong hệ thống.');
          return;
        }

        if (matched.status === 'locked') {
          setErrorMessage('Tài khoản này đã bị khóa bởi Quản trị viên.');
          return;
        }

        if (matched.password && matched.password !== password) {
          setErrorMessage('Mật khẩu không chính xác. Vui lòng thử lại!');
          return;
        }

        notify(`Đăng nhập thành công! Chào mừng ${matched.name} quay trở lại.`, 'success');
        onLoginSuccess(matched);
      }, 400);
    } else {
      // Login with Email
      const trimmedEmail = email.trim().toLowerCase();
      if (!trimmedEmail) {
        setErrorMessage('Vui lòng nhập địa chỉ email của bạn.');
        return;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(trimmedEmail)) {
        setErrorMessage('Định dạng email không hợp lệ (ví dụ: user@example.com).');
        return;
      }

      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        const matched = users.find((u) => u.email.toLowerCase() === trimmedEmail);

        if (!matched) {
          setErrorMessage('Không tìm thấy tài khoản liên kết với địa chỉ email này.');
          return;
        }

        if (matched.status === 'locked') {
          setErrorMessage('Tài khoản này đã bị khóa bởi Quản trị viên.');
          return;
        }

        notify(`Đăng nhập bằng email thành công! Xin chào ${matched.name}.`, 'success');
        onLoginSuccess(matched);
      }, 400);
    }
  };

  return (
    <div className="max-w-md mx-auto py-6 sm:py-10">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden p-6 sm:p-8">
        {/* Login Method Tabs */}
          <div className="p-1 rounded-2xl bg-slate-100 grid grid-cols-2 gap-1 mb-6 border border-slate-200">
            <button
              type="button"
              onClick={() => {
                setLoginMethod('username');
                setErrorMessage('');
              }}
              className={`py-2.5 px-3 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                loginMethod === 'username'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
              }`}
            >
              <User className="w-4 h-4" />
              <span>Username & Mật khẩu</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setLoginMethod('email');
                setErrorMessage('');
              }}
              className={`py-2.5 px-3 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                loginMethod === 'email'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
              }`}
            >
              <Mail className="w-4 h-4" />
              <span>Đăng nhập qua Email</span>
            </button>
          </div>

          {/* Error Notice */}
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2.5 animate-shake">
              <ShieldCheck className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            {/* METHOD 1: USERNAME + PASSWORD */}
            {loginMethod === 'username' ? (
              <>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Tên đăng nhập (Username)
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder="Nhập username (ví dụ: namnguyen hoặc admin)"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white bg-slate-50/50"
                      required
                      autoFocus
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Mật khẩu
                    </label>
                    <span className="text-xs text-slate-400 font-medium">
                      Demo mật khẩu: password123 hoặc admin123
                    </span>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Nhập mật khẩu của bạn"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-10 pr-11 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white bg-slate-50/50"
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
              </>
            ) : (
              /* METHOD 2: LOGIN WITH EMAIL */
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Địa chỉ Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    placeholder="Nhập email (ví dụ: user@flashlearn.vn hoặc admin@flashlearn.vn)"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white bg-slate-50/50"
                    required
                    autoFocus
                  />
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Đăng nhập nhanh tiện lợi chỉ cần nhập đúng địa chỉ email đã đăng ký.
                </p>
              </div>
            )}

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-600">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                />
                <span>Ghi nhớ đăng nhập</span>
              </label>
              <button
                type="button"
                onClick={() => notify('Vui lòng liên hệ Admin để đặt lại mật khẩu của bạn!', 'info')}
                className="text-xs font-bold text-blue-600 hover:text-blue-700 hover:underline cursor-pointer"
              >
                Quên mật khẩu?
              </button>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-sm shadow-md shadow-blue-500/20 hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Đăng nhập ngay</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Switch to Register */}
          <div className="mt-8 pt-6 border-t border-slate-100 text-center text-xs text-slate-600">
            <span>Bạn chưa có tài khoản FlashLearn? </span>
            <button
              type="button"
              onClick={() => navigateTo('register')}
              className="font-bold text-blue-600 hover:text-blue-800 hover:underline cursor-pointer ml-1"
            >
              Đăng ký tài khoản mới ngay
            </button>
          </div>
        </div>
      </div>
    );
  };
