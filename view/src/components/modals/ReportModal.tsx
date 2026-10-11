import React, { useState } from 'react';
import { Flag, X, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { FlashcardSet, UserProfile } from '../../types';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetSet: FlashcardSet | null;
  targetCard?: { id: string; term: string } | null;
  currentUser: UserProfile;
  onSubmitReport: (data: {
    setId: string;
    setTitle: string;
    cardId?: string;
    cardTerm?: string;
    reason: string;
    description: string;
  }) => void;
}

const REPORT_REASONS = [
  'Nội dung phản cảm, không phù hợp',
  'Sai lệch kiến thức hoặc công thức',
  'Spam, quảng cáo hoặc nội dung vô nghĩa',
  'Vi phạm bản quyền sở hữu trí tuệ',
  'Từ ngữ thô tục, công kích cá nhân',
  'Lý do khác',
];

export const ReportModal: React.FC<ReportModalProps> = ({
  isOpen,
  onClose,
  targetSet,
  targetCard,
  currentUser,
  onSubmitReport,
}) => {
  const [selectedReason, setSelectedReason] = useState(REPORT_REASONS[0]);
  const [description, setDescription] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  if (!isOpen || !targetSet) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmitReport({
      setId: targetSet.id,
      setTitle: targetSet.title,
      cardId: targetCard?.id,
      cardTerm: targetCard?.term,
      reason: selectedReason,
      description: description.trim(),
    });
    setIsSubmitted(true);
    setTimeout(() => {
      setIsSubmitted(false);
      setDescription('');
      setSelectedReason(REPORT_REASONS[0]);
      onClose();
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl border border-slate-100 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-rose-50/50">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center shrink-0">
              <Flag className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 text-base">
                Tố cáo nội dung vi phạm
              </h3>
              <p className="text-xs text-slate-500">
                Báo cáo sẽ được gửi đến Quản trị viên để kiểm duyệt
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        {isSubmitted ? (
          <div className="p-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h4 className="text-lg font-bold text-slate-900">
              Đã gửi tố cáo thành công!
            </h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Cảm ơn bạn đã hỗ trợ FlashLearn xây dựng môi trường học tập lành mạnh và chính xác. Đội ngũ kiểm duyệt sẽ xử lý trong thời gian sớm nhất.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4 overflow-y-auto">
            {/* Target Item Summary */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
              <div className="font-semibold text-slate-500 uppercase tracking-wide text-[10px]">
                Nội dung bị tố cáo
              </div>
              <div className="font-bold text-slate-800 text-sm">
                Bộ thẻ: {targetSet.title}
              </div>
              {targetCard && (
                <div className="text-slate-600">
                  Thẻ cụ thể: <span className="font-semibold text-rose-600">"{targetCard.term}"</span>
                </div>
              )}
              <div className="text-slate-500 text-[11px]">
                Người tạo: {targetSet.createdBy} • Thể loại: {targetSet.category}
              </div>
            </div>

            {/* Reason selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">
                Lý do tố cáo <span className="text-rose-500">*</span>
              </label>
              <div className="space-y-1.5">
                {REPORT_REASONS.map((r) => (
                  <label
                    key={r}
                    className={`flex items-center gap-2.5 p-2.5 rounded-xl border text-xs cursor-pointer transition-all ${
                      selectedReason === r
                        ? 'bg-rose-50/80 border-rose-300 text-rose-900 font-semibold'
                        : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="reportReason"
                      value={r}
                      checked={selectedReason === r}
                      onChange={() => setSelectedReason(r)}
                      className="text-rose-600 focus:ring-rose-500"
                    />
                    <span>{r}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Detailed Description */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Mô tả chi tiết vi phạm (nếu có)</span>
                <span className="text-[10px] text-slate-400 font-normal">Không bắt buộc</span>
              </label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Vui lòng cung cấp thêm thông tin hoặc giải thích chi tiết lỗi sai để ban quản trị đối chiếu..."
                className="w-full p-3 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-rose-500 focus:bg-white resize-none"
              />
            </div>

            {/* Reporter disclaimer */}
            <div className="flex items-start gap-2 p-3 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-800 text-[11px]">
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600 mt-0.5" />
              <span>
                Người báo cáo: <b>{currentUser.name}</b> ({currentUser.email}). Việc gửi báo cáo sai sự thật có thể ảnh hưởng đến điểm uy tín tài khoản của bạn.
              </span>
            </div>

            {/* Actions */}
            <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors"
              >
                Hủy bỏ
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white shadow-md shadow-rose-600/20 transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <Flag className="w-3.5 h-3.5" />
                Gửi tố cáo vi phạm
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
