import React from 'react';
import {
  Layers,
  Award,
  Clock,
  ChevronLeft,
} from 'lucide-react';
import { TabType } from '../../types';

interface SidebarProps {
  currentTab: TabType;
  navigateTo: (tab: TabType) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  isMobileOpen: boolean;
  setIsMobileOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  navigateTo,
  isOpen,
  setIsOpen,
  isMobileOpen,
  setIsMobileOpen,
}) => {
  const isFlashcardActive = currentTab === 'sets' || currentTab === 'study';
  const isQuizActive = currentTab === 'my_quizzes' || currentTab === 'quiz_mode';
  const isHistoryActive = currentTab === 'history';

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
              onClick={() => navigateTo('sets')}
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
          <nav className="p-3 space-y-1.5">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-3 py-1.5">
              Menu điều hướng
            </div>

            {/* 1. Flashcard */}
            <button
              onClick={() => navigateTo('sets')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left cursor-pointer ${
                isFlashcardActive
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Layers className={`w-5 h-5 ${isFlashcardActive ? 'text-white' : 'text-slate-400'}`} />
              <span>Flashcard</span>
            </button>

            {/* 2. Quiz */}
            <button
              onClick={() => navigateTo('my_quizzes')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left cursor-pointer ${
                isQuizActive
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Award className={`w-5 h-5 ${isQuizActive ? 'text-white' : 'text-slate-400'}`} />
              <span>Quiz</span>
            </button>

            {/* 3. Lịch sử thi */}
            <button
              onClick={() => navigateTo('history')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all text-left cursor-pointer ${
                isHistoryActive
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Clock className={`w-5 h-5 ${isHistoryActive ? 'text-white' : 'text-slate-400'}`} />
              <span>Lịch sử thi</span>
            </button>
          </nav>
        </div>

        {/* Bottom footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/60 text-center">
          <div className="text-xs font-bold text-slate-600">
            FlashLearn • Nền tảng học tập
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Flashcard & Trắc nghiệm
          </div>
        </div>
      </aside>
    </>
  );
};
