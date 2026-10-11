import React, { useState } from 'react';
import { Globe, Search, Flag, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { FlashcardSet } from '../../types';

interface CommunityViewProps {
  publicSets: FlashcardSet[];
  searchKeyword: string;
  setSearchKeyword: (val: string) => void;
  filterCategory: string;
  setFilterCategory: (val: string) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  onOpenReportModal: (set: FlashcardSet, card?: { id: string; term: string }) => void;
}

export const CommunityView: React.FC<CommunityViewProps> = ({
  publicSets,
  searchKeyword,
  setSearchKeyword,
  filterCategory,
  setFilterCategory,
  handleStartStudy,
  onOpenReportModal,
}) => {
  const [expandedSetId, setExpandedSetId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedSetId((prev) => (prev === id ? null : id));
  };
  return (
    <div className="space-y-6">
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
          const isExpanded = expandedSetId === set.id;
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
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 flex items-center gap-1">
                      <Globe className="w-3 h-3" /> Công khai
                    </span>
                    <button
                      type="button"
                      onClick={() => onOpenReportModal(set)}
                      className="px-2 py-0.5 rounded-md text-[11px] font-bold text-slate-500 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 transition-colors inline-flex items-center gap-1 cursor-pointer"
                      title="Tố cáo bộ flashcard này vi phạm tiêu chuẩn"
                    >
                      <Flag className="w-3 h-3 text-rose-500" />
                      <span>Tố cáo</span>
                    </button>
                  </div>
                </div>

                <h3 className="font-bold text-lg text-slate-900 line-clamp-1">{set.title}</h3>
                <p className="text-sm text-slate-500 mt-1 line-clamp-2">{set.description}</p>

                {/* Toggle Preview Cards */}
                <button
                  type="button"
                  onClick={() => toggleExpand(set.id)}
                  className="mt-3 text-xs text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="w-3.5 h-3.5" /> Thu gọn danh sách thẻ
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-3.5 h-3.5" /> Xem trước {set.cards.length} thẻ
                    </>
                  )}
                </button>

                {/* Expanded card preview with individual card report button */}
                {isExpanded && (
                  <div className="mt-3 space-y-2 max-h-48 overflow-y-auto pr-1 border-t border-slate-100 pt-2 text-xs">
                    {set.cards.map((c, idx) => (
                      <div
                        key={c.id || idx}
                        className="p-2 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between gap-2"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="font-bold text-slate-800 truncate">{c.term}</div>
                          <div className="text-[11px] text-slate-500 truncate">{c.definition}</div>
                        </div>
                        <button
                          type="button"
                          onClick={() => onOpenReportModal(set, { id: c.id, term: c.term })}
                          className="px-1.5 py-1 text-[10px] text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded font-semibold transition-colors shrink-0 flex items-center gap-0.5 cursor-pointer"
                          title="Tố cáo thẻ này sai kiến thức hoặc vi phạm"
                        >
                          <Flag className="w-3 h-3 text-rose-400" />
                          <span>Báo cáo</span>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                  <span>
                    Người tạo: <b>{set.createdBy}</b>
                  </span>
                  <span>{set.cards.length} thẻ</span>
                </div>

                <div className="flex items-center">
                  <button
                    onClick={() => handleStartStudy(set)}
                    className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs text-center transition-colors shadow-xs cursor-pointer"
                  >
                    Bắt đầu ôn tập 🎯
                  </button>
                </div>
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
