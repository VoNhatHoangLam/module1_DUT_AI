import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';

export const CodeViewerView: React.FC = () => {
  const [selectedCodeFile, setSelectedCodeFile] = useState<
    'app.py' | 'style.css' | 'requirements.txt' | 'README.md' | 'sample_data'
  >('app.py');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Mã nguồn & Hướng dẫn Gradio</h1>
        <p className="text-sm text-slate-500">
          Xem mã nguồn triển khai ứng dụng Gradio tương đương và hướng dẫn chạy cục bộ
        </p>
      </div>

      {/* Callout */}
      <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 sm:p-5 text-sm text-blue-900 space-y-2">
        <div className="font-bold flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-600" /> Cách khởi chạy ứng dụng Gradio trên máy cá nhân:
        </div>
        <div className="font-mono text-xs bg-white/80 p-3 rounded-xl border border-blue-200">
          # 1. Cài đặt các gói phụ thuộc:<br />
          pip install -r requirements.txt<br /><br />
          # 2. Khởi chạy ứng dụng Gradio:<br />
          python app.py
        </div>
        <p className="text-xs text-blue-700">
          Sau khi chạy, mở trình duyệt tại địa chỉ <b>http://127.0.0.1:7860</b> để trải nghiệm giao diện Gradio!
        </p>
      </div>

      {/* Switcher Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        {[
          { id: 'app.py', label: 'app.py (Mã nguồn Gradio chính)' },
          { id: 'style.css', label: 'assets/style.css (CSS Quizlet)' },
          { id: 'requirements.txt', label: 'requirements.txt' },
          { id: 'README.md', label: 'README.md (Hướng dẫn)' },
          { id: 'sample_data', label: 'sample_data/flashcards.csv' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedCodeFile(tab.id as any)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
              selectedCodeFile === tab.id
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Code Pre Area */}
      <div className="bg-slate-900 text-slate-100 rounded-2xl p-6 shadow-xl font-mono text-xs overflow-x-auto max-h-[550px] border border-slate-800">
        {selectedCodeFile === 'app.py' && (
          <pre>{`"""
FlashLearn - Nền tảng học tập Flashcard & Ôn thi trắc nghiệm phong cách Quizlet
Xây dựng hoàn toàn bằng Python và Gradio (gr.Blocks) với CSS tùy biến cao cấp.

Lệnh chạy:
    pip install -r requirements.txt
    python app.py
"""

import json
import random
import os
import io
import pandas as pd
import plotly.express as px
import gradio as gr

# [Đã triển khai đầy đủ State, Callbacks, Lật thẻ 3D, Chấm điểm trắc nghiệm và Admin Moderation]
# Xem tệp /app.py trong thư mục dự án!`}</pre>
        )}

        {selectedCodeFile === 'style.css' && (
          <pre>{`/* assets/style.css - Quizlet-Inspired Modern Theme for Gradio */
:root {
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --navy: #1e3a8a;
  --bg-main: #f8fafc;
  --card-bg: #ffffff;
}

.flashcard-stage {
  perspective: 1200px;
  width: 100%;
  max-width: 680px;
  height: 380px;
  margin: 1.5rem auto;
  cursor: pointer;
}
/* ... đầy đủ trong /assets/style.css */`}</pre>
        )}

        {selectedCodeFile === 'requirements.txt' && (
          <pre>{`gradio>=4.38.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.2`}</pre>
        )}

        {selectedCodeFile === 'README.md' && (
          <pre>{`# FlashLearn - Nền tảng học tập Flashcard & Ôn thi trắc nghiệm

Hướng dẫn chạy trên Windows / Linux:
1. Mở terminal, tạo môi trường ảo:
   python -m venv venv
   venv\\Scripts\\activate (trên Windows)
2. Cài đặt thư viện:
   pip install -r requirements.txt
3. Chạy ứng dụng:
   python app.py

Mở trình duyệt tại http://127.0.0.1:7860`}</pre>
        )}

        {selectedCodeFile === 'sample_data' && (
          <pre>{`term,definition
Algorithm,Tập hợp hữu hạn các chỉ dẫn rõ ràng để giải quyết bài toán.
Machine Learning,Nhánh AI cho phép hệ thống học hỏi từ dữ liệu.
API,Giao diện lập trình ứng dụng kết nối các dịch vụ phần mềm.
Database Index,Cấu trúc dữ liệu tăng tốc độ truy xuất bản ghi trong bảng CSDL.`}</pre>
        )}
      </div>
    </div>
  );
};
