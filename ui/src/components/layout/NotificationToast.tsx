import React from 'react';
import { CheckCircle, AlertCircle, Sparkles } from 'lucide-react';

interface NotificationToastProps {
  notification: {
    message: string;
    type: 'success' | 'error' | 'info';
  } | null;
}

export const NotificationToast: React.FC<NotificationToastProps> = ({ notification }) => {
  if (!notification) return null;

  return (
    <div
      className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-xl flex items-center gap-3 text-white transition-all duration-300 ${
        notification.type === 'success'
          ? 'bg-emerald-600'
          : notification.type === 'error'
          ? 'bg-rose-600'
          : 'bg-blue-600'
      }`}
    >
      {notification.type === 'success' ? (
        <CheckCircle className="w-5 h-5 shrink-0" />
      ) : notification.type === 'error' ? (
        <AlertCircle className="w-5 h-5 shrink-0" />
      ) : (
        <Sparkles className="w-5 h-5 shrink-0" />
      )}
      <span className="font-medium text-sm">{notification.message}</span>
    </div>
  );
};
