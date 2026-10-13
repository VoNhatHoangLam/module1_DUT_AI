import React from 'react';
import { Globe, Search, AlertCircle, BookmarkCheck, Layers } from 'lucide-react';
import { FlashcardSet, TabType } from '../../types';

interface CommunityViewProps {
  publicSets: FlashcardSet[];
  searchKeyword: string;
  setSearchKeyword: (val: string) => void;
  filterCategory: string;
  setFilterCategory: (val: string) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  navigateTo?: (tab: TabType) => void;
  onOpenCreateQuizForDeck?: (set: FlashcardSet) => void;
  onOpenImportQuizForDeck?: (set: FlashcardSet) => void;
}

export const CommunityView: React.FC<CommunityViewProps> = ({
  publicSets,
  searchKeyword,
  setSearchKeyword,
  filterCategory,
  setFilterCategory,
  handleStartStudy,
  navigateTo,
}) => {
  return (
    <div className="space-y-6">
      {/* Sub-tabs: Cộng đồng & Của tôi */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
        <button
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold bg-blue-600 text-white shadow-xs cursor-default"
        >
          <Globe className="w-4 h-4" />
          <span>Cộng đồng</span>
        </button>
        {navigateTo && (
          <button
            onClick={() => navigateTo('sets')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:text-blue-600 hover:bg-slate-100 transition-all cursor-pointer"
          >
            <BookmarkCheck className="w-4 h-4" />
            <span>Của tôi</span>
          </button>
        )}
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <Globe className="w-6 h-6 text-blue-600" />
            Flashcard
          </h1>
          <p className="text-sm text-slate-500">
            Khám phá tất cả các bộ flashcard công khai được chia sẻ từ cộng đồng học viên
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Tìm kiếm bộ flashcard công khai..."
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

      {/* Public Flashcard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {publicSets.map((set) => {
          return (
            <div
              key={set.id}
              className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
                    {set.category}
                  </span>
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 flex items-center gap-1">
                    <Globe className="w-3 h-3" /> Công khai
                  </span>
                </div>

                <h3 className="font-bold text-lg text-slate-900 line-clamp-1">{set.title}</h3>
                <p className="text-sm text-slate-500 mt-1 line-clamp-2">{set.description}</p>

                <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-500">
                  <Layers className="w-3.5 h-3.5 text-blue-600" />
                  <span><strong className="font-bold text-slate-700">{set.cards.length} thẻ</strong></span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100">
                <button
                  onClick={() => handleStartStudy(set)}
                  className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs text-center transition-colors shadow-xs cursor-pointer"
                >
                  Bắt đầu ôn tập 🎯
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {publicSets.length === 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-2">
          <p className="text-base font-bold">Không tìm thấy bộ flashcard công khai nào phù hợp.</p>
          <p className="text-xs">Hãy thử thay đổi từ khóa tìm kiếm hoặc bộ lọc chủ đề.</p>
        </div>
      )}
    </div>
  );
};
