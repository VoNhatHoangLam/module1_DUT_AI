import React, { useState, useMemo } from 'react';
import confetti from 'canvas-confetti';
import {
  ChevronLeft,
  RotateCw,
  Shuffle,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { FlashcardSet } from '../../types';

interface StudyViewProps {
  activeStudySet: FlashcardSet;
  onExit: () => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const StudyView: React.FC<StudyViewProps> = ({
  activeStudySet,
  onExit,
  notify,
}) => {
  const [cards, setCards] = useState(activeStudySet.cards || []);
  const [studyCardIndex, setStudyCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [knownCardIds, setKnownCardIds] = useState<string[]>([]);
  const [unknownCardIds, setUnknownCardIds] = useState<string[]>([]);
  const [studyOnlyUnknown, setStudyOnlyUnknown] = useState(false);
  const [studyFinished, setStudyFinished] = useState(false);

  const currentStudyCards = useMemo(() => {
    if (!cards || !cards.length) return [];
    if (studyOnlyUnknown) {
      const filtered = cards.filter((c) => c && unknownCardIds.includes(c.id));
      return filtered.length > 0 ? filtered : cards;
    }
    return cards;
  }, [cards, studyOnlyUnknown, unknownCardIds]);

  const handleShuffle = () => {
    const shuffled = [...cards].sort(() => Math.random() - 0.5);
    setCards(shuffled);
    setStudyCardIndex(0);
    setIsFlipped(false);
    notify('Đã xáo trộn ngẫu nhiên thứ tự các thẻ!', 'info');
  };

  const handleMarkCard = (known: boolean) => {
    if (!currentStudyCards || !currentStudyCards.length) return;
    const safeIdx = Math.min(studyCardIndex, currentStudyCards.length - 1);
    const currentCard = currentStudyCards[safeIdx];
    if (!currentCard || !currentCard.id) return;
    const cardId = currentCard.id;

    if (known) {
      setKnownCardIds((prev) => Array.from(new Set([...prev, cardId])));
      setUnknownCardIds((prev) => prev.filter((id) => id !== cardId));
    } else {
      setUnknownCardIds((prev) => Array.from(new Set([...prev, cardId])));
      setKnownCardIds((prev) => prev.filter((id) => id !== cardId));
    }

    if (safeIdx < currentStudyCards.length - 1) {
      setStudyCardIndex(safeIdx + 1);
      setIsFlipped(false);
    } else {
      setStudyFinished(true);
      confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header with Exit & Set Info */}
      <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <button
          onClick={onExit}
          className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 flex items-center gap-1 transition-colors cursor-pointer"
        >
          <ChevronLeft className="w-4 h-4" /> Thoát chế độ ôn
        </button>
        <div className="text-center">
          <h2 className="font-extrabold text-slate-900 text-base">{activeStudySet.title}</h2>
          <span className="text-xs text-slate-500">{activeStudySet.category}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleShuffle}
            className="p-2 rounded-xl hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
            title="Xáo trộn ngẫu nhiên thứ tự thẻ"
          >
            <Shuffle className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Study Progress Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
        <div className="flex items-center justify-between text-xs font-bold text-slate-600">
          <span>
            Thẻ hiện tại: {studyCardIndex + 1} / {currentStudyCards.length}
          </span>
          <span className="text-blue-600">
            {Math.round(((studyCardIndex + 1) / (currentStudyCards.length || 1)) * 100)}% hoàn thành
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-300"
            style={{
              width: `${((studyCardIndex + 1) / (currentStudyCards.length || 1)) * 100}%`,
            }}
          />
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
          <span className="text-emerald-600 font-semibold">Đã nhớ: {knownCardIds.length} thẻ</span>
          <span className="text-rose-500 font-semibold">Cần ôn lại: {unknownCardIds.length} thẻ</span>
        </div>
      </div>

      {/* COMPLETION SCREEN OR FLASHCARD */}
      {studyFinished ? (
        <div className="bg-white rounded-3xl border border-slate-200 p-10 text-center shadow-lg space-y-6">
          <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto text-3xl">
            🎉
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-black text-slate-900">Tuyệt vời! Bạn đã hoàn thành phiên ôn tập!</h2>
            <p className="text-slate-500 text-sm max-w-md mx-auto">
              Bạn đã ghi nhớ {knownCardIds.length} trên tổng số {activeStudySet.cards.length} thẻ trong bộ này.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-3 pt-4">
            {unknownCardIds.length > 0 && (
              <button
                onClick={() => {
                  setStudyOnlyUnknown(true);
                  setStudyCardIndex(0);
                  setIsFlipped(false);
                  setStudyFinished(false);
                  notify('Bắt đầu ôn tập lại các thẻ chưa nhớ!', 'info');
                }}
                className="px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-sm shadow-sm transition-colors cursor-pointer"
              >
                Học lại {unknownCardIds.length} thẻ chưa nhớ
              </button>
            )}
            <button
              onClick={() => {
                setStudyOnlyUnknown(false);
                setStudyCardIndex(0);
                setKnownCardIds([]);
                setUnknownCardIds([]);
                setIsFlipped(false);
                setStudyFinished(false);
              }}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-sm transition-colors cursor-pointer"
            >
              Ôn lại toàn bộ từ đầu
            </button>
            <button
              onClick={onExit}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Quay lại danh sách
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* 3D FLASHCARD CONTAINER */}
          <div
            className="perspective-1000 w-full cursor-pointer select-none"
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <div
              className={`relative w-full min-h-[340px] rounded-3xl p-8 sm:p-12 transition-all duration-500 transform preserve-3d shadow-xl border flex flex-col justify-between items-center text-center ${
                !isFlipped
                  ? 'bg-gradient-to-b from-white to-blue-50/50 border-blue-200'
                  : 'bg-gradient-to-b from-blue-900 to-indigo-950 text-white border-blue-700'
              }`}
            >
              {/* Content */}
              <div className="my-auto py-6">
                <div
                  className={`font-black tracking-tight leading-snug transition-all ${
                    !isFlipped
                      ? 'text-2xl sm:text-3xl text-slate-900'
                      : 'text-xl sm:text-2xl text-blue-100 font-medium'
                  }`}
                >
                  {!isFlipped
                    ? currentStudyCards[studyCardIndex]?.term
                    : currentStudyCards[studyCardIndex]?.definition}
                </div>
              </div>

              {/* Bottom instruction */}
              <div className="text-xs font-medium text-slate-400 flex items-center gap-1">
                <RotateCw className="w-3.5 h-3.5" />
                Bấm vào thẻ để lật mặt trước / sau
              </div>
            </div>
          </div>

          {/* Knowledge Mark Buttons */}
          <div className="flex items-center justify-center gap-4 pt-2">
            <button
              onClick={() => handleMarkCard(false)}
              className="flex-1 max-w-[220px] py-3 rounded-2xl bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700 font-bold text-sm flex items-center justify-center gap-2 transition-colors shadow-xs cursor-pointer"
            >
              <XCircle className="w-5 h-5 text-rose-500" />
              Chưa nhớ (Cần ôn)
            </button>

            <button
              onClick={() => handleMarkCard(true)}
              className="flex-1 max-w-[220px] py-3 rounded-2xl bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 text-emerald-700 font-bold text-sm flex items-center justify-center gap-2 transition-colors shadow-xs cursor-pointer"
            >
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              Đã ghi nhớ ✅
            </button>
          </div>
        </>
      )}
    </div>
  );
};
