import React, { useState, useMemo } from 'react';
import { Menu } from 'lucide-react';

// Data types & initial data
import {
  UserProfile,
  FlashcardSet,
  QuizSet,
  QuizAttempt,
  FlashcardReport,
  TabType,
} from './types';
import {
  INITIAL_USERS,
  INITIAL_SETS,
  INITIAL_QUIZZES,
  INITIAL_HISTORY,
  INITIAL_REPORTS,
} from './data/mockData';

// Layout components
import { Sidebar } from './components/layout/Sidebar';
import { NotificationToast } from './components/layout/NotificationToast';

// Views
import { DashboardView } from './components/views/DashboardView';
import { CommunityView } from './components/views/CommunityView';
import { QuizListView } from './components/views/QuizListView';
import { HistoryView } from './components/views/HistoryView';
import { MySetsView } from './components/views/MySetsView';
import { MyQuizzesView } from './components/views/MyQuizzesView';
import { StudyView } from './components/views/StudyView';
import { QuizRunnerView } from './components/views/QuizRunnerView';
import { ProfileView } from './components/views/ProfileView';
import { AdminUsersView } from './components/views/AdminUsersView';
import { AdminModerationView } from './components/views/AdminModerationView';
import { CodeViewerView } from './components/views/CodeViewerView';

// Modals
import { CreateSetModal } from './components/modals/CreateSetModal';
import { ImportSetModal } from './components/modals/ImportSetModal';
import { CreateQuizModal } from './components/modals/CreateQuizModal';
import { ImportQuizModal } from './components/modals/ImportQuizModal';
import { ReportModal } from './components/modals/ReportModal';
import { ConfirmModal } from './components/modals/ConfirmModal';

export default function App() {
  // Navigation & Role states
  const [currentUser, setCurrentUser] = useState<UserProfile>(INITIAL_USERS[0]);
  const [currentTab, setCurrentTab] = useState<TabType>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Application Data States (Mock DB)
  const [users, setUsers] = useState<UserProfile[]>(INITIAL_USERS);
  const [sets, setSets] = useState<FlashcardSet[]>(INITIAL_SETS);
  const [quizzes, setQuizzes] = useState<QuizSet[]>(INITIAL_QUIZZES);
  const [history, setHistory] = useState<QuizAttempt[]>(INITIAL_HISTORY);
  const [reports, setReports] = useState<FlashcardReport[]>(INITIAL_REPORTS);

  // Search & Filter (for Community & Quiz List tabs)
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');

  // Study & Quiz Active sessions
  const [activeStudySet, setActiveStudySet] = useState<FlashcardSet>(INITIAL_SETS[0]);
  const [activeQuiz, setActiveQuiz] = useState<QuizSet>(INITIAL_QUIZZES[0]);

  // Modals Visibility
  const [showCreateSetModal, setShowCreateSetModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showCreateQuizModal, setShowCreateQuizModal] = useState(false);
  const [showImportQuizModal, setShowImportQuizModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [showDeleteQuizConfirm, setShowDeleteQuizConfirm] = useState<string | null>(null);

  // Reporting State
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [targetReportSet, setTargetReportSet] = useState<FlashcardSet | null>(null);
  const [targetReportCard, setTargetReportCard] = useState<{ id: string; term: string } | null>(null);

  // Notifications
  const [notification, setNotification] = useState<{
    message: string;
    type: 'success' | 'error' | 'info';
  } | null>(null);

  const notify = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Navigation Helper
  const navigateTo = (tab: TabType) => {
    setCurrentTab(tab);
    setIsMobileSidebarOpen(false);
  };

  // --- DERIVED / FILTERED DATA MEMOS ---
  // 1. "Flashcard của tôi": Sets owned by current user
  const mySets = useMemo(() => {
    if (!currentUser?.id) return [];
    return sets.filter((s) => s && (s.userId === currentUser.id || s.createdBy === currentUser.name));
  }, [sets, currentUser]);

  // 2. "Flashcard": Public sets
  const publicSets = useMemo(() => {
    return sets.filter((s) => {
      if (!s) return false;
      const isPublic = s.privacy === 'public';
      const matchSearch =
        (s.title || '').toLowerCase().includes(searchKeyword.toLowerCase()) ||
        (s.category || '').toLowerCase().includes(searchKeyword.toLowerCase());
      const matchCategory = filterCategory === 'All' || s.category === filterCategory;
      return isPublic && matchSearch && matchCategory;
    });
  }, [sets, searchKeyword, filterCategory]);

  // 3. "Quiz": Public & approved quizzes
  const publicQuizzes = useMemo(() => {
    return quizzes.filter((q) => {
      if (!q) return false;
      const isPublicApproved = q.status === 'approved';
      const matchSearch =
        (q.title || '').toLowerCase().includes(searchKeyword.toLowerCase()) ||
        (q.category || '').toLowerCase().includes(searchKeyword.toLowerCase());
      const matchCategory = filterCategory === 'All' || q.category === filterCategory;
      return isPublicApproved && matchSearch && matchCategory;
    });
  }, [quizzes, searchKeyword, filterCategory]);

  // 4. Personal Sets for Profile
  const myPersonalSets = useMemo(() => {
    if (!currentUser?.id) return [];
    return sets.filter((s) => s && (s.userId === currentUser.id || s.createdBy === currentUser.name));
  }, [sets, currentUser]);

  // 5. Personal Quizzes for Profile
  const myPersonalQuizzes = useMemo(() => {
    if (!currentUser?.id) return [];
    return quizzes.filter((q) => q && (q.userId === currentUser.id || q.createdBy === currentUser.name));
  }, [quizzes, currentUser]);

  // --- ACTIONS ---
  const handleStartStudy = (set: FlashcardSet) => {
    setActiveStudySet(set);
    navigateTo('study');
  };

  const handleStartQuiz = (quiz: QuizSet) => {
    setActiveQuiz(quiz);
    navigateTo('quiz_mode');
  };

  const handleCreateSet = (data: {
    title: string;
    description: string;
    category: string;
    privacy: 'public' | 'private';
    cards: { term: string; definition: string }[];
  }) => {
    if (!data.title.trim()) {
      notify('Vui lòng nhập tên bộ thẻ!', 'error');
      return;
    }
    const validCards = data.cards.filter((c) => c.term.trim() && c.definition.trim());
    if (validCards.length === 0) {
      notify('Bộ thẻ cần ít nhất 1 flashcard hợp lệ!', 'error');
      return;
    }

    const created: FlashcardSet = {
      id: `set_${Date.now()}`,
      title: data.title.trim(),
      description: data.description.trim() || 'Bộ thẻ tự tạo bởi học viên.',
      category: data.category,
      createdBy: currentUser.name,
      userId: currentUser.id,
      privacy: data.privacy,
      status: 'approved',
      updatedAt: new Date().toLocaleDateString('vi-VN'),
      cards: validCards.map((c, i) => ({
        id: `c_${Date.now()}_${i}`,
        term: c.term.trim(),
        definition: c.definition.trim(),
      })),
    };

    setSets([created, ...sets]);
    setShowCreateSetModal(false);
    if (data.privacy === 'public') {
      notify('Bộ flashcard đã được đăng công khai ngay lập tức!', 'success');
    } else {
      notify('Tạo bộ flashcard cá nhân thành công!', 'success');
    }
  };

  const handleDeleteSet = (id: string) => {
    if (!id) return;
    setSets((prev) => prev.filter((s) => s && s.id !== id));
    setShowDeleteConfirm(null);
    notify('Đã xóa bộ flashcard thành công!', 'info');
  };

  const handleConfirmImportSet = (cards: { term: string; definition: string }[]) => {
    const importedSet: FlashcardSet = {
      id: `set_import_${Date.now()}`,
      title: `Bộ thẻ nhập từ file (${new Date().toLocaleDateString('vi-VN')})`,
      description: 'Dữ liệu được nhập tự động từ tệp CSV/JSON mẫu.',
      category: 'Công nghệ thông tin',
      createdBy: currentUser.name,
      userId: currentUser.id,
      privacy: 'public',
      status: 'approved',
      updatedAt: new Date().toLocaleDateString('vi-VN'),
      cards: cards.map((d, i) => ({
        id: `c_imp_${Date.now()}_${i}`,
        term: d.term,
        definition: d.definition,
      })),
    };

    setSets([importedSet, ...sets]);
    setShowImportModal(false);
    notify(`Đã nhập thành công ${importedSet.cards.length} flashcard!`, 'success');
  };

  const handleCreateQuiz = (data: {
    title: string;
    description: string;
    category: string;
    timeLimitMinutes: number;
    questions: {
      question: string;
      optionA: string;
      optionB: string;
      optionC: string;
      optionD: string;
      correctAnswer: 'A' | 'B' | 'C' | 'D';
      explanation: string;
    }[];
  }) => {
    if (!data.title.trim()) {
      notify('Vui lòng nhập tên bộ đề Quiz!', 'error');
      return;
    }
    const validQuestions = data.questions.filter(
      (q) => q.question.trim() && q.optionA.trim() && q.optionB.trim()
    );
    if (validQuestions.length === 0) {
      notify('Bộ đề cần ít nhất 1 câu hỏi hợp lệ với ít nhất 2 phương án!', 'error');
      return;
    }

    const createdQuiz: QuizSet = {
      id: `quiz_${Date.now()}`,
      title: data.title.trim(),
      description: data.description.trim() || 'Bộ đề thi trắc nghiệm do học viên tạo.',
      category: data.category,
      createdBy: currentUser.name,
      userId: currentUser.id,
      privacy: 'private',
      status: 'pending',
      timeLimitMinutes: Number(data.timeLimitMinutes) || 10,
      questions: validQuestions.map((q, idx) => ({
        id: idx + 1,
        question: q.question.trim(),
        optionA: q.optionA.trim(),
        optionB: q.optionB.trim(),
        optionC: q.optionC.trim() || 'None',
        optionD: q.optionD.trim() || 'None',
        correctAnswer: q.correctAnswer,
        explanation: q.explanation.trim() || 'Chưa có giải thích chi tiết.',
      })),
    };

    setQuizzes([createdQuiz, ...quizzes]);
    setShowCreateQuizModal(false);
    notify('Đã tạo bộ đề Quiz mới! Bộ đề được lưu ở trạng thái cá nhân / chờ duyệt.', 'success');
  };

  const handleDeleteQuiz = (id: string) => {
    if (!id) return;
    setQuizzes((prev) => prev.filter((q) => q && q.id !== id));
    setShowDeleteQuizConfirm(null);
    notify('Đã xóa bộ đề Quiz thành công!', 'info');
  };

  const handleConfirmImportQuiz = (
    questions: {
      question: string;
      optionA: string;
      optionB: string;
      optionC: string;
      optionD: string;
      correctAnswer: 'A' | 'B' | 'C' | 'D';
      explanation: string;
    }[]
  ) => {
    const importedQuiz: QuizSet = {
      id: `quiz_import_${Date.now()}`,
      title: `Đề thi trắc nghiệm nhập từ file (${new Date().toLocaleDateString('vi-VN')})`,
      description: 'Đề thi được tạo tự động từ tệp CSV/JSON câu hỏi.',
      category: 'Công nghệ thông tin',
      createdBy: currentUser.name,
      userId: currentUser.id,
      privacy: 'public',
      status: 'approved',
      timeLimitMinutes: 15,
      questions: questions.map((q, idx) => ({
        id: idx + 1,
        ...q,
      })),
    };

    setQuizzes([importedQuiz, ...quizzes]);
    setShowImportQuizModal(false);
    notify(`Đã nhập thành công bộ đề với ${importedQuiz.questions.length} câu hỏi!`, 'success');
  };

  const handleToggleUserStatus = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) => {
        if (u.id === userId) {
          const newStatus = u.status === 'active' ? 'locked' : 'active';
          return { ...u, status: newStatus };
        }
        return u;
      })
    );
    notify('Đã cập nhật trạng thái tài khoản thành công!', 'info');
  };

  const handleChangeUserRole = (userId: string, newRole: 'user' | 'admin') => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
    );
    notify(`Đã chuyển vai trò người dùng thành ${newRole === 'admin' ? 'Quản trị viên' : 'Học viên'}!`, 'info');
  };

  const handleAddUser = (newUserData: Partial<UserProfile>) => {
    setUsers((prev) => [...prev, newUserData as UserProfile]);
  };

  const handleOpenReportModal = (set: FlashcardSet, card?: { id: string; term: string }) => {
    setTargetReportSet(set);
    setTargetReportCard(card || null);
    setReportModalOpen(true);
  };

  const handleSubmitReport = (data: {
    setId: string;
    setTitle: string;
    cardId?: string;
    cardTerm?: string;
    reason: string;
    description: string;
  }) => {
    const newReport: FlashcardReport = {
      id: `rep_${Date.now()}`,
      setId: data.setId,
      setTitle: data.setTitle,
      cardId: data.cardId,
      cardTerm: data.cardTerm,
      reporterName: currentUser.name,
      reporterEmail: currentUser.email,
      reason: data.reason,
      description: data.description,
      createdAt: new Date().toLocaleString('vi-VN'),
      status: 'pending',
    };
    setReports((prev) => [newReport, ...prev]);
    notify('Đã gửi tố cáo thành công! Quản trị viên sẽ xử lý trong thời gian sớm nhất.', 'success');
  };

  const handleDismissReport = (reportId: string) => {
    setReports((prev) =>
      prev.map((r) => (r.id === reportId ? { ...r, status: 'dismissed' } : r))
    );
  };

  const handleResolveReport = (reportId: string, actionNote?: string) => {
    setReports((prev) =>
      prev.map((r) => (r.id === reportId ? { ...r, status: 'resolved' } : r))
    );
  };

  const handleToggleSetPrivacy = (setId: string) => {
    setSets((prev) =>
      prev.map((s) => {
        if (s.id === setId) {
          return {
            ...s,
            privacy: s.privacy === 'public' ? 'private' : 'public',
          };
        }
        return s;
      })
    );
  };

  const handleFinishQuizAttempt = (attempt: QuizAttempt) => {
    setHistory((prev) => [attempt, ...prev]);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex font-sans">
      {/* Toast Notification */}
      <NotificationToast notification={notification} />

      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        navigateTo={navigateTo}
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        isMobileOpen={isMobileSidebarOpen}
        setIsMobileOpen={setIsMobileSidebarOpen}
        currentUser={currentUser}
        setCurrentUser={setCurrentUser}
        users={users}
        notify={notify}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 min-h-screen transition-all duration-300 ${
          isSidebarOpen ? 'md:ml-64' : 'md:ml-0'
        }`}
      >
        {/* Top bar header when sidebar is closed (or on mobile) */}
        {(!isSidebarOpen || !isMobileSidebarOpen) && (
          <header
            className={`sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-4 sm:px-6 py-2.5 flex items-center justify-between shadow-xs transition-all ${
              isSidebarOpen ? 'md:hidden' : ''
            }`}
          >
            <button
              onClick={() => {
                setIsSidebarOpen(true);
                setIsMobileSidebarOpen(true);
              }}
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-blue-600 transition-colors flex items-center gap-2 text-xs font-bold cursor-pointer"
              title="Mở thanh menu"
              aria-label="Mở thanh menu"
            >
              <Menu className="w-4 h-4 text-blue-600" />
              <span>Mở thanh menu</span>
            </button>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-blue-900 text-sm tracking-tight">FlashLearn</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 uppercase">
                Quizlet Style
              </span>
            </div>
          </header>
        )}

        {/* Page Content Container */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* VIEW: DASHBOARD */}
          {currentTab === 'dashboard' && (
            <DashboardView
              currentUser={currentUser}
              publicSets={publicSets}
              mySets={mySets}
              publicQuizzes={publicQuizzes}
              history={history}
              navigateTo={navigateTo}
              handleStartStudy={handleStartStudy}
              handleStartQuiz={handleStartQuiz}
            />
          )}

          {/* VIEW: FLASHCARD (CỘNG ĐỒNG) */}
          {currentTab === 'community' && (
            <CommunityView
              publicSets={publicSets}
              searchKeyword={searchKeyword}
              setSearchKeyword={setSearchKeyword}
              filterCategory={filterCategory}
              setFilterCategory={setFilterCategory}
              handleStartStudy={handleStartStudy}
              onOpenReportModal={handleOpenReportModal}
            />
          )}

          {/* VIEW: QUIZ (DANH SÁCH ĐỀ THI CÔNG KHAI) */}
          {currentTab === 'quiz_list' && (
            <QuizListView
              publicQuizzes={publicQuizzes}
              searchKeyword={searchKeyword}
              setSearchKeyword={setSearchKeyword}
              filterCategory={filterCategory}
              setFilterCategory={setFilterCategory}
              onOpenCreateQuizModal={() => setShowCreateQuizModal(true)}
              onOpenImportQuizModal={() => setShowImportQuizModal(true)}
              handleStartQuiz={handleStartQuiz}
            />
          )}

          {/* VIEW: LỊCH SỬ THI */}
          {currentTab === 'history' && (
            <HistoryView history={history} />
          )}

          {/* VIEW: TRANG RIÊNG - FLASHCARD CỦA TÔI */}
          {currentTab === 'sets' && (
            <MySetsView
              currentUser={currentUser}
              myPersonalSets={myPersonalSets}
              onOpenCreateSetModal={() => setShowCreateSetModal(true)}
              onOpenImportSetModal={() => setShowImportModal(true)}
              onDeleteSetConfirm={(id) => setShowDeleteConfirm(id)}
              handleStartStudy={handleStartStudy}
              onBackToProfile={() => navigateTo('profile')}
            />
          )}

          {/* VIEW: TRANG RIÊNG - QUIZ CỦA TÔI */}
          {currentTab === 'my_quizzes' && (
            <MyQuizzesView
              currentUser={currentUser}
              myPersonalQuizzes={myPersonalQuizzes}
              onOpenCreateQuizModal={() => setShowCreateQuizModal(true)}
              onOpenImportQuizModal={() => setShowImportQuizModal(true)}
              onDeleteQuizConfirm={(id) => setShowDeleteQuizConfirm(id)}
              handleStartQuiz={handleStartQuiz}
              onBackToProfile={() => navigateTo('profile')}
            />
          )}

          {/* VIEW: HỌC FLASHCARD (LẬT THẺ 3D) */}
          {currentTab === 'study' && (
            <StudyView
              activeStudySet={activeStudySet}
              onExit={() => navigateTo('sets')}
              notify={notify}
              onOpenReportModal={handleOpenReportModal}
            />
          )}

          {/* VIEW: LÀM BÀI THI QUIZ */}
          {currentTab === 'quiz_mode' && (
            <QuizRunnerView
              activeQuiz={activeQuiz}
              onFinishAttempt={handleFinishQuizAttempt}
              onExit={() => navigateTo('quiz_list')}
              notify={notify}
            />
          )}

          {/* VIEW: HỒ SƠ CÁ NHÂN (PROFILE) */}
          {currentTab === 'profile' && (
            <ProfileView
              currentUser={currentUser}
              setCurrentUser={setCurrentUser}
              myPersonalSets={myPersonalSets}
              myPersonalQuizzes={myPersonalQuizzes}
              history={history}
              onOpenCreateSetModal={() => setShowCreateSetModal(true)}
              onOpenCreateQuizModal={() => setShowCreateQuizModal(true)}
              onDeleteSetConfirm={(id) => setShowDeleteConfirm(id)}
              onDeleteQuizConfirm={(id) => setShowDeleteQuizConfirm(id)}
              handleStartStudy={handleStartStudy}
              handleStartQuiz={handleStartQuiz}
              navigateTo={navigateTo}
              notify={notify}
            />
          )}

          {/* VIEW: ADMIN - QUẢN LÝ TÀI KHOẢN */}
          {(currentTab === 'admin_users' || currentTab === 'admin') && (
            <AdminUsersView
              users={users}
              currentUser={currentUser}
              onToggleUserStatus={handleToggleUserStatus}
              onChangeUserRole={handleChangeUserRole}
              onAddUser={handleAddUser}
              notify={notify}
            />
          )}

          {/* VIEW: ADMIN - KIỂM DUYỆT FLASHCARDS */}
          {currentTab === 'admin_moderation' && (
            <AdminModerationView
              sets={sets}
              reports={reports}
              onDismissReport={handleDismissReport}
              onResolveReport={handleResolveReport}
              onToggleSetPrivacy={handleToggleSetPrivacy}
              onDeleteSetConfirm={(id) => setShowDeleteConfirm(id)}
              handleStartStudy={handleStartStudy}
              notify={notify}
            />
          )}

          {/* VIEW: GRADIO CODE VIEWER */}
          {currentTab === 'code_viewer' && (
            <CodeViewerView />
          )}
        </main>
      </div>

      {/* MODALS */}
      <ReportModal
        isOpen={reportModalOpen}
        onClose={() => {
          setReportModalOpen(false);
          setTargetReportSet(null);
          setTargetReportCard(null);
        }}
        targetSet={targetReportSet}
        targetCard={targetReportCard}
        currentUser={currentUser}
        onSubmitReport={handleSubmitReport}
      />
      <CreateSetModal
        isOpen={showCreateSetModal}
        onClose={() => setShowCreateSetModal(false)}
        onSubmit={handleCreateSet}
      />

      <ImportSetModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onConfirmImport={handleConfirmImportSet}
        onNotify={notify}
      />

      <CreateQuizModal
        isOpen={showCreateQuizModal}
        onClose={() => setShowCreateQuizModal(false)}
        onSubmit={handleCreateQuiz}
      />

      <ImportQuizModal
        isOpen={showImportQuizModal}
        onClose={() => setShowImportQuizModal(false)}
        onConfirmImport={handleConfirmImportQuiz}
        onNotify={notify}
      />

      {/* CONFIRM DELETE FLASHCARD MODAL */}
      <ConfirmModal
        isOpen={!!showDeleteConfirm}
        title="Xác nhận xóa bộ Flashcard này?"
        description='Hành động này sẽ xóa bộ thẻ khỏi danh sách "Flashcard của tôi" và loại bỏ khỏi bộ nhớ demo. Không ảnh hưởng đến các bộ flashcard khác.'
        confirmText="Xác nhận xóa"
        type="danger"
        onConfirm={() => {
          if (showDeleteConfirm) handleDeleteSet(showDeleteConfirm);
        }}
        onCancel={() => setShowDeleteConfirm(null)}
      />

      {/* CONFIRM DELETE QUIZ MODAL */}
      <ConfirmModal
        isOpen={!!showDeleteQuizConfirm}
        title="Xác nhận xóa đề Quiz này?"
        description="Hành động này sẽ xóa bộ đề thi trắc nghiệm khỏi danh sách của bạn và không thể hoàn tác."
        confirmText="Xác nhận xóa"
        type="danger"
        onConfirm={() => {
          if (showDeleteQuizConfirm) handleDeleteQuiz(showDeleteQuizConfirm);
        }}
        onCancel={() => setShowDeleteQuizConfirm(null)}
      />
    </div>
  );
}
