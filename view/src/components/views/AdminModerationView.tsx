import React, { useState, useMemo } from 'react';
import {
  Flag,
  CheckCircle,
  XCircle,
  Trash2,
  BookOpen,
  Search,
  Eye,
  AlertTriangle,
  Lock,
  Globe,
  Layers,
  Clock,
  User,
} from 'lucide-react';
import { FlashcardSet, FlashcardReport } from '../../types';

interface AdminModerationViewProps {
  sets: FlashcardSet[];
  reports: FlashcardReport[];
  onDismissReport: (reportId: string) => void;
  onResolveReport: (reportId: string, actionNote?: string) => void;
  onToggleSetPrivacy: (setId: string) => void;
  onDeleteSetConfirm: (id: string) => void;
  handleStartStudy: (set: FlashcardSet) => void;
  notify: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const AdminModerationView: React.FC<AdminModerationViewProps> = ({
  sets,
  reports,
  onDismissReport,
  onResolveReport,
  onToggleSetPrivacy,
  onDeleteSetConfirm,
  handleStartStudy,
  notify,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'reports' | 'all_sets'>('reports');
  const [reportFilter, setReportFilter] = useState<'all' | 'pending' | 'resolved' | 'dismissed'>('pending');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  // Stats
  const pendingReports = reports.filter((r) => r.status === 'pending');
  const totalReports = reports.length;
  const totalSets = sets.length;
  const publicSets = sets.filter((s) => s.privacy === 'public').length;

  const filteredReports = useMemo(() => {
    return reports.filter((r) => {
      const matchStatus = reportFilter === 'all' || r.status === reportFilter;
      const matchSearch =
        r.setTitle.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        (r.cardTerm || '').toLowerCase().includes(searchKeyword.toLowerCase()) ||
        r.reason.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        r.reporterName.toLowerCase().includes(searchKeyword.toLowerCase());
      return matchStatus && matchSearch;
    });
  }, [reports, reportFilter, searchKeyword]);

  const filteredSets = useMemo(() => {
    return sets.filter((s) => {
      const matchCategory = categoryFilter === 'All' || s.category === categoryFilter;
      const matchSearch =
        s.title.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        s.createdBy.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        (s.description || '').toLowerCase().includes(searchKeyword.toLowerCase());
      return matchCategory && matchSearch;
    });
  }, [sets, categoryFilter, searchKeyword]);

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Tố cáo cần xử lý</span>
            <Flag className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-3xl font-black text-rose-600 mt-2">{pendingReports.length}</div>
          <div className="text-xs text-rose-500 font-semibold mt-1">
            {pendingReports.length > 0 ? 'Cần xem xét ngay' : 'Đã xử lý hết'}
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Tổng số lượt tố cáo</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-slate-800 mt-2">{totalReports}</div>
          <div className="text-xs text-slate-500 mt-1">Bao gồm đã duyệt & bỏ qua</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Tổng số bộ thẻ</span>
            <Layers className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-3xl font-black text-blue-600 mt-2">{totalSets}</div>
          <div className="text-xs text-slate-500 mt-1">
            {sets.reduce((sum, s) => sum + s.cards.length, 0)} thẻ học
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase">Bộ thẻ công khai</span>
            <Globe className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-black text-emerald-600 mt-2">{publicSets}</div>
          <div className="text-xs text-emerald-600 font-semibold mt-1">
            {((publicSets / (totalSets || 1)) * 100).toFixed(0)}% chia sẻ cộng đồng
          </div>
        </div>
      </div>

      {/* Main Sub Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveSubTab('reports')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all cursor-pointer ${
            activeSubTab === 'reports'
              ? 'bg-rose-600 text-white shadow-sm shadow-rose-600/30'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Flag className="w-4 h-4" />
          Danh sách bị tố cáo
          {pendingReports.length > 0 && (
            <span
              className={`px-1.5 py-0.2 rounded-full text-[10px] font-black ${
                activeSubTab === 'reports' ? 'bg-white text-rose-700' : 'bg-rose-500 text-white'
              }`}
            >
              {pendingReports.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('all_sets')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all cursor-pointer ${
            activeSubTab === 'all_sets'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Layers className="w-4 h-4" />
          Tất cả bộ thẻ Flashcards ({sets.length})
        </button>
      </div>

      {/* TAB 1: REPORTS VIEW */}
      {activeSubTab === 'reports' && (
        <div className="space-y-4">
          {/* Filter Bar for Reports */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
            <div className="relative w-full md:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Tìm tố cáo theo tiêu đề, người báo cáo..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:bg-white"
              />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto">
              <span className="text-xs font-semibold text-slate-500">Trạng thái:</span>
              <select
                value={reportFilter}
                onChange={(e) => setReportFilter(e.target.value as any)}
                className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-700 font-medium focus:ring-2 focus:ring-rose-500"
              >
                <option value="pending">Chờ xử lý ({pendingReports.length})</option>
                <option value="all">Tất cả ({totalReports})</option>
                <option value="resolved">Đã giải quyết</option>
                <option value="dismissed">Đã bỏ qua</option>
              </select>
            </div>
          </div>

          {/* Reports Grid */}
          <div className="space-y-3">
            {filteredReports.map((report) => {
              const matchedSet = sets.find((s) => s.id === report.setId);
              return (
                <div
                  key={report.id}
                  className={`bg-white rounded-2xl border p-5 shadow-xs transition-all ${
                    report.status === 'pending'
                      ? 'border-rose-300 ring-2 ring-rose-500/10'
                      : 'border-slate-200 opacity-80'
                  }`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            report.status === 'pending'
                              ? 'bg-rose-100 text-rose-800'
                              : report.status === 'resolved'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          <Flag className="w-3 h-3" />
                          {report.status === 'pending'
                            ? 'Chờ xử lý'
                            : report.status === 'resolved'
                            ? 'Đã xử lý vi phạm'
                            : 'Đã bỏ qua (Hợp lệ)'}
                        </span>

                        <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 text-xs font-bold border border-amber-200">
                          {report.reason}
                        </span>

                        <span className="text-slate-400 text-xs flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {report.createdAt}
                        </span>
                      </div>

                      <div>
                        <h4 className="font-extrabold text-base text-slate-900">
                          Bộ thẻ: {report.setTitle}
                        </h4>
                        {report.cardTerm && (
                          <div className="text-xs text-rose-700 font-semibold mt-0.5">
                            Thẻ bị phản ánh: <span className="underline">"{report.cardTerm}"</span>
                          </div>
                        )}
                        {report.description && (
                          <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100 mt-2 italic">
                            "{report.description}"
                          </p>
                        )}
                      </div>

                      <div className="text-[11px] text-slate-500 flex items-center gap-2">
                        <User className="w-3 h-3 text-slate-400" />
                        <span>
                          Người tố cáo: <b>{report.reporterName}</b> ({report.reporterEmail})
                        </span>
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex flex-wrap lg:flex-col items-center gap-2 shrink-0">
                      {matchedSet && (
                        <button
                          onClick={() => handleStartStudy(matchedSet)}
                          className="px-3 py-1.5 rounded-xl bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer w-full justify-center"
                        >
                          <BookOpen className="w-3.5 h-3.5" /> Xem nội dung bộ thẻ
                        </button>
                      )}

                      {report.status === 'pending' && (
                        <>
                          {matchedSet && (
                            <button
                              onClick={() => {
                                onToggleSetPrivacy(matchedSet.id);
                                onResolveReport(report.id, 'Đã ẩn bộ thẻ khỏi cộng đồng');
                                notify(`Đã chuyển bộ thẻ "${matchedSet.title}" về chế độ Riêng tư!`, 'info');
                              }}
                              className="px-3 py-1.5 rounded-xl bg-amber-50 text-amber-700 hover:bg-amber-100 text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer w-full justify-center"
                              title="Ẩn khỏi cộng đồng"
                            >
                              <Lock className="w-3.5 h-3.5" /> Ẩn khỏi công khai
                            </button>
                          )}

                          <button
                            onClick={() => {
                              onDismissReport(report.id);
                              notify('Đã bỏ qua tố cáo này (nội dung hợp lệ)', 'info');
                            }}
                            className="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer w-full justify-center"
                          >
                            <CheckCircle className="w-3.5 h-3.5 text-slate-500" /> Bỏ qua tố cáo
                          </button>

                          {matchedSet && (
                            <button
                              onClick={() => {
                                onDeleteSetConfirm(matchedSet.id);
                              }}
                              className="px-3 py-1.5 rounded-xl bg-rose-600 text-white hover:bg-rose-700 text-xs font-bold flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer w-full justify-center"
                            >
                              <Trash2 className="w-3.5 h-3.5" /> Xóa bộ thẻ
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {filteredReports.length === 0 && (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-2">
                <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto" />
                <p className="font-bold text-base text-slate-800">
                  Không có tố cáo vi phạm nào trong danh mục này!
                </p>
                <p className="text-xs text-slate-400">
                  Hệ thống flashcard hiện tại an toàn và tuân thủ đúng quy định.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: ALL SETS MODERATION */}
      {activeSubTab === 'all_sets' && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
            <div className="relative w-full md:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Tìm bộ flashcard theo tiêu đề, tác giả..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto">
              <span className="text-xs font-semibold text-slate-500">Chủ đề:</span>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-700 font-medium focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">Tất cả chủ đề</option>
                <option value="Công nghệ thông tin">Công nghệ thông tin</option>
                <option value="Ngoại ngữ">Ngoại ngữ</option>
                <option value="Thiết kế">Thiết kế</option>
              </select>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-700">
                <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3">Tiêu đề bộ thẻ</th>
                    <th className="px-4 py-3">Người tạo</th>
                    <th className="px-4 py-3">Chủ đề</th>
                    <th className="px-4 py-3">Số thẻ</th>
                    <th className="px-4 py-3">Quyền riêng tư</th>
                    <th className="px-4 py-3 text-right">Thao tác kiểm duyệt</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredSets.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-bold text-slate-900">{s.title}</div>
                        <div className="text-xs text-slate-400 line-clamp-1">{s.description}</div>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-600 font-medium">{s.createdBy}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-medium">
                          {s.category}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold">{s.cards.length} thẻ</td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => {
                            onToggleSetPrivacy(s.id);
                            notify(
                              `Đã chuyển bộ thẻ sang ${s.privacy === 'public' ? 'Riêng tư' : 'Công khai'}!`,
                              'info'
                            );
                          }}
                          className={`px-2.5 py-0.5 rounded-full text-xs font-bold inline-flex items-center gap-1 cursor-pointer transition-colors ${
                            s.privacy === 'public'
                              ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200'
                              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                          }`}
                          title="Bấm để đổi quyền riêng tư"
                        >
                          {s.privacy === 'public' ? (
                            <>
                              <Globe className="w-3 h-3" /> Công khai
                            </>
                          ) : (
                            <>
                              <Lock className="w-3 h-3" /> Riêng tư
                            </>
                          )}
                        </button>
                      </td>
                      <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                        <button
                          onClick={() => handleStartStudy(s)}
                          className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-bold transition-colors inline-flex items-center gap-1 cursor-pointer"
                        >
                          <BookOpen className="w-3.5 h-3.5" /> Xem
                        </button>
                        <button
                          onClick={() => onDeleteSetConfirm(s.id)}
                          className="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100 text-xs font-bold transition-colors inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" /> Xóa
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
