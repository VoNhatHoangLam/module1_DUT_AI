import React, { useState, useMemo, useEffect } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  BookmarkCheck,
  Plus,
  Search,
  Trash2,
  Layers,
  MoreVertical,
  Sparkles,
  Loader2,
  X,
} from 'lucide-react';
import { FlashcardSet, UserProfile, TabType } from '../../types';
import { deckService } from '../../services/deckService';

interface MySetsViewProps {
  currentUser: UserProfile;
  myPersonalSets: FlashcardSet[];
  onOpenCreateSetModal: () => void;
  onOpenImportSetModal: () => void;
  onDeleteSetConfirm: (id: string) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  navigateTo?: (tab: TabType) => void;
  onOpenCreateQuizForDeck?: (set: FlashcardSet) => void;
  onOpenImportQuizForDeck?: (set: FlashcardSet) => void;
}

export const MySetsView: React.FC<MySetsViewProps> = ({
  currentUser,
  myPersonalSets,
  onOpenCreateSetModal,
  onOpenImportSetModal,
  onDeleteSetConfirm,
  handleStartStudy,
  navigateTo,
  onOpenCreateQuizForDeck,
  onOpenImportQuizForDeck,
}) => {
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [searchResults, setSearchResults] = useState<FlashcardSet[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const PAGE_SIZE = 10;

  // Lắng nghe từ khóa tìm kiếm và gọi API tìm tiền tố tiêu đề bằng Cây AVL O(log N + K)
  useEffect(() => {
    const cleanPrefix = search.trim();
    if (!cleanPrefix) {
      setSearchResults(null);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const res = await deckService.getDecks(cleanPrefix, 1, 100);
        setSearchResults(res.items || []);
      } catch (err) {
        console.error('Lỗi tìm kiếm bộ thẻ qua Cây AVL:', err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  // Chỉ cho phép tìm kiếm theo Tiêu đề (Title) thông qua Cây AVL
  const displayedSets = useMemo(() => {
    if (searchResults !== null) {
      return searchResults;
    }
    return myPersonalSets;
  }, [searchResults, myPersonalSets]);

  const totalPages = Math.max(1, Math.ceil(displayedSets.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);

  const pagedSets = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return displayedSets.slice(start, start + PAGE_SIZE);
  }, [displayedSets, currentPage]);

  return (
    <div className="space-y-6">
      {/* Header with Title and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <BookmarkCheck className="w-6 h-6 text-blue-600" />
            Flashcard của tôi
          </h1>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenCreateSetModal}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all flex items-center gap-2 shadow-sm cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Tạo bộ thẻ mới
          </button>
        </div>
      </div>

      {/* Search Bar - Chỉ tìm kiếm theo Title bằng Cây AVL */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
        <div className="relative w-full">
          {isSearching ? (
            <Loader2 className="w-4 h-4 text-blue-600 animate-spin absolute left-3.5 top-1/2 -translate-y-1/2" />
          ) : (
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          )}
          <input
            type="text"
            placeholder="Tìm kiếm tiền tố tiêu đề qua Cây AVL (VD: Oxford, IELTS, English, Python)..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-10 py-2.5 text-sm bg-slate-50 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-colors"
          />
          {search && (
            <button
              type="button"
              onClick={() => {
                setSearch('');
                setPage(1);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-200 transition-colors cursor-pointer"
              title="Xóa tìm kiếm"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {search.trim() && (
          <div className="flex items-center justify-between text-xs text-slate-500 px-1 pt-0.5">
            <div className="flex items-center gap-1.5 text-blue-600 font-medium">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <span>
              {isSearching ? 'Đang truy vấn Cây AVL...' : `Tìm thấy ${displayedSets.length} bộ thẻ`}
            </span>
          </div>
        )}
      </div>

      {/* Personal Sets Grid - Paginated */}
      {pagedSets.length > 0 ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pagedSets.map((set) => (
              <div
                key={set.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-bold text-lg text-slate-900 line-clamp-1 flex-1">{set.title}</h3>
                    <div className="relative shrink-0 -mt-1 -mr-1">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveMenuId(activeMenuId === set.id ? null : set.id);
                        }}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                        title="Tùy chọn tạo Quiz"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>

                      {activeMenuId === set.id && (
                        <>
                          <div
                            className="fixed inset-0 z-20 cursor-default"
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveMenuId(null);
                            }}
                          />
                          <div className="absolute right-0 top-full mt-1.5 w-52 bg-white rounded-2xl shadow-xl border border-slate-200 py-1.5 z-30 animate-in fade-in zoom-in-95 duration-100">
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setActiveMenuId(null);
                                onOpenCreateQuizForDeck?.(set);
                              }}
                              className="w-full px-3.5 py-2.5 text-left text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center gap-2 transition-colors cursor-pointer"
                            >
                              <Sparkles className="w-4 h-4 text-indigo-500" />
                              <span>Tạo quiz từ deck này</span>
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  <p className="text-sm text-slate-500 mt-1.5 line-clamp-2">{set.description}</p>

                  <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-500">
                    <Layers className="w-3.5 h-3.5 text-blue-600" />
                    <span><strong className="font-bold text-slate-700">{set.cards.length} thẻ</strong></span>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100">
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
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
                      className="px-3 py-2 rounded-xl border border-rose-200 bg-rose-50 text-rose-600 hover:bg-rose-100 hover:text-rose-700 font-bold text-xs flex items-center gap-1 transition-colors cursor-pointer"
                      title="Xóa bộ flashcard này"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Xóa
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Centered Pagination Bar */}
          {displayedSets.length > 0 && (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-center">
              <div className="flex items-center justify-center gap-1.5">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <ChevronLeft className="w-3.5 h-3.5" /> Trước
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`w-8 h-8 rounded-lg text-xs font-bold transition-all cursor-pointer ${pageNum === currentPage
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'text-slate-600 hover:bg-slate-100 border border-slate-200'
                      }`}
                  >
                    {pageNum}
                  </button>
                ))}

                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer"
                >
                  Sau <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-3">
          <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center mx-auto">
            <BookmarkCheck className="w-6 h-6" />
          </div>
          <p className="text-base font-bold text-slate-800">
            {search.trim()
              ? `Không tìm thấy bộ flashcard nào có tiêu đề bắt đầu bằng "${search.trim()}".`
              : 'Không tìm thấy bộ flashcard nào phù hợp.'}
          </p>
          <p className="text-xs max-w-md mx-auto">
            {search.trim()
              ? 'Hệ thống chỉ tìm kiếm theo tiền tố Tiêu đề (Title) bằng Cây AVL. Hãy thử nhập tiền tố khác.'
              : 'Hãy thử tạo bộ thẻ mới.'}
          </p>
          <button
            onClick={() => {
              setSearch('');
            }}
            className="px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold cursor-pointer"
          >
            Xóa tìm kiếm
          </button>
        </div>
      )}
    </div>
  );
};
