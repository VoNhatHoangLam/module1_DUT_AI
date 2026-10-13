import React from 'react';
import { AlertCircle, Check } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmText: string;
  cancelText?: string;
  type?: 'danger' | 'primary' | 'success';
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  description,
  confirmText,
  cancelText = 'Hủy bỏ',
  type = 'danger',
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-sm w-full p-6 text-center space-y-4 shadow-2xl">
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto ${
            type === 'danger'
              ? 'bg-rose-100 text-rose-600'
              : type === 'success'
              ? 'bg-emerald-100 text-emerald-600'
              : 'bg-blue-100 text-blue-600'
          }`}
        >
          {type === 'danger' ? (
            <AlertCircle className="w-6 h-6" />
          ) : (
            <Check className="w-6 h-6" />
          )}
        </div>
        <h4 className="font-extrabold text-slate-900 text-base">{title}</h4>
        <p className="text-xs text-slate-500">{description}</p>
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50 transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 rounded-xl text-white text-xs font-bold transition-colors ${
              type === 'danger'
                ? 'bg-rose-600 hover:bg-rose-700'
                : type === 'success'
                ? 'bg-emerald-600 hover:bg-emerald-700'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};
