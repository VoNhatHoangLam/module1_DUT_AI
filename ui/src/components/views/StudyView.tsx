import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  ChevronLeft,
  RotateCw,
  CheckCircle,
  XCircle,
  Layers,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { FlashcardSet, StudySessionState } from '../../types';
import { studyService } from '../../services/studyService';

interface StudyViewProps {
  activeStudySet: FlashcardSet;
  initialSession?: StudySessionState | null;
  onExit: () => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const StudyView: React.FC<StudyViewProps> = ({
  activeStudySet,
  initialSession = null,
  onExit,
  notify,
}) => {
  const [session, setSession] = useState<StudySessionState | null>(initialSession);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(!initialSession);

  // Khởi tạo phiên học qua Backend Queue nếu chưa có
  useEffect(() => {
    let isMounted = true;
    if (!session) {
      setIsLoading(true);
      studyService
        .startStudy(activeStudySet.id)
        .then((newSession) => {
          if (isMounted) {
            setSession(newSession);
            setIsLoading(false);
          }
        })
        .catch((err) => {
          if (isMounted) {
            notify(`Không thể khởi tạo phiên học: ${err.message}`, 'error');
            setIsLoading(false);
          }
        });
    }
    return () => {
      isMounted = false;
    };
  }, [activeStudySet.id]);

  const handleMarkCard = async (known: boolean) => {
    if (!session || session.is_completed) return;

    try {
      const updated = await studyService.markCard(session.session_id, known);
      setSession(updated);
      setIsFlipped(false);

      if (updated.is_completed) {
        confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } });
        notify('Chúc mừng! Bạn đã hoàn thành toàn bộ thẻ trong phiên học này!', 'success');
      }
    } catch (err: any) {
      notify(`Lỗi khi đánh dấu thẻ: ${err.message}`, 'error');
    }
  };

  const handleRestart = async () => {
    setIsLoading(true);
    try {
      const newSession = await studyService.startStudy(activeStudySet.id);
      setSession(newSession);
      setIsFlipped(false);
      notify('Đã khởi động lại phiên ôn tập từ đầu!', 'info');
    } catch (err: any) {
      notify(`Không thể khởi động lại: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-600 text-sm font-semibold">Đang chuẩn bị hàng đợi thẻ (Queue FIFO)...</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center bg-white rounded-3xl border border-slate-200 space-y-4">
        <p className="text-slate-600">Không có thẻ nào để học trong bộ thẻ này.</p>
        <button
          onClick={onExit}
          className="px-4 py-2 bg-blue-600 text-white font-bold rounded-xl text-sm"
        >
          Quay lại danh sách
        </button>
      </div>
    );
  }

  const currentCard = session.current_card;
  const progressPercent = session.total_cards > 0
    ? Math.round((session.known_count / session.total_cards) * 100)
    : 0;

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
          <span className="text-xs text-slate-500">{activeStudySet.category || 'Học flashcard'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`text-xs font-bold px-2.5 py-1 rounded-full flex items-center gap-1 ${
              session.is_initial_phase
                ? 'bg-blue-100 text-blue-800'
                : 'bg-amber-100 text-amber-800'
            }`}
            title={
              session.is_initial_phase
                ? 'Giai đoạn 1: Duyệt thẻ ban đầu'
                : 'Giai đoạn 2: Ôn tập thẻ trong hàng đợi FIFO'
            }
          >
            <Layers className="w-3.5 h-3.5" />
            {session.is_initial_phase ? 'Giai đoạn 1 (Lướt thẻ)' : 'Giai đoạn 2 (Hàng đợi Queue)'}
          </span>
        </div>
      </div>

      {/* Study Progress Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
        <div className="flex items-center justify-between text-xs font-bold text-slate-600">
          <span>
            Đã thuộc: {session.known_count} / {session.total_cards} thẻ
          </span>
          <span className="text-blue-600 font-extrabold">{progressPercent}% hoàn thành</span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
          <span className="text-emerald-600 font-semibold">Đã nhớ: {session.known_count} thẻ</span>
          <span className="text-amber-600 font-semibold">
            Trong hàng đợi (Queue): {session.unknown_count} thẻ
          </span>
          <span className="text-slate-500 font-semibold">
            Còn cần xem: {session.remaining_count} lượt
          </span>
        </div>
      </div>

      {/* COMPLETION SCREEN OR FLASHCARD */}
      {session.is_completed ? (
        <div className="bg-white rounded-3xl border border-slate-200 p-10 text-center shadow-lg space-y-6">
          <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto text-3xl">
            🎉
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-black text-slate-900">Tuyệt vời! Bạn đã hoàn thành phiên ôn tập!</h2>
            <p className="text-slate-500 text-sm max-w-md mx-auto">
              Tất cả {session.total_cards} thẻ đã được đưa qua cơ chế hàng đợi hai giai đoạn FIFO và bạn đã đánh dấu thuộc thành công.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-3 pt-4">
            <button
              onClick={handleRestart}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-sm transition-colors cursor-pointer flex items-center gap-2"
            >
              <RotateCw className="w-4 h-4" /> Ôn lại toàn bộ từ đầu
            </button>
            <button
              onClick={onExit}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Quay lại danh sách bộ thẻ
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
              {/* Card Position Badge */}
              <div className="w-full flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-100">
                  Thẻ #{currentCard?.position || 1}
                </span>
                <span>{!isFlipped ? 'Mặt trước (Thuật ngữ)' : 'Mặt sau (Định nghĩa)'}</span>
              </div>

              {/* Content */}
              <div className="my-auto py-6">
                <div
                  className={`font-black tracking-tight leading-snug transition-all ${
                    !isFlipped
                      ? 'text-2xl sm:text-3xl text-slate-900'
                      : 'text-xl sm:text-2xl text-blue-100 font-medium'
                  }`}
                >
                  {!isFlipped ? currentCard?.term : currentCard?.definition}
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
              Chưa nhớ (Xếp vào Queue)
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
