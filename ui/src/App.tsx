import React, { useState, useMemo } from 'react';
import { Menu } from 'lucide-react';

// Data types & initial data
import {
  UserProfile,
  FlashcardSet,
  QuizSet,
  QuizAttempt,
  TabType,
  QuizQuestionInput,
} from './types';
import {
  INITIAL_USERS,
  INITIAL_SETS,
  INITIAL_QUIZZES,
  INITIAL_HISTORY,
} from './data/mockData';

// Layout components
import { Sidebar } from './components/layout/Sidebar';
import { NotificationToast } from './components/layout/NotificationToast';

// Views
import { HistoryView } from './components/views/HistoryView';
import { MySetsView } from './components/views/MySetsView';
import { MyQuizzesView } from './components/views/MyQuizzesView';
import { StudyView } from './components/views/StudyView';
import { QuizRunnerView } from './components/views/QuizRunnerView';

// Modals
import { CreateSetModal } from './components/modals/CreateSetModal';
import { ImportSetModal } from './components/modals/ImportSetModal';
import { CreateQuizModal } from './components/modals/CreateQuizModal';
import { ImportQuizModal } from './components/modals/ImportQuizModal';
import { ConfirmModal } from './components/modals/ConfirmModal';

export default function App() {
  // Navigation & User state
  const [currentUser] = useState<UserProfile>(INITIAL_USERS[0]);
  const [currentTab, setCurrentTab] = useState<TabType>('sets');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Application Data States (Mock DB)
  const [sets, setSets] = useState<FlashcardSet[]>(INITIAL_SETS);
  const [quizzes, setQuizzes] = useState<QuizSet[]>(INITIAL_QUIZZES);
  const [history, setHistory] = useState<QuizAttempt[]>(INITIAL_HISTORY);

  // Study & Quiz Active sessions
  const [activeStudySet, setActiveStudySet] = useState<FlashcardSet>(INITIAL_SETS[0]);
  const [activeQuiz, setActiveQuiz] = useState<QuizSet>(INITIAL_QUIZZES[0]);

  // Modals Visibility
  const [showCreateSetModal, setShowCreateSetModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [prefilledCardsForCreate, setPrefilledCardsForCreate] = useState<
    { term: string; definition: string }[] | null
  >(null);
  const [showCreateQuizModal, setShowCreateQuizModal] = useState(false);
  const [prefilledQuizForCreate, setPrefilledQuizForCreate] = useState<{
    questions: QuizQuestionInput[];
    privacy?: 'public' | 'private';
    deck?: FlashcardSet | null;
  } | null>(null);
  const [showImportQuizModal, setShowImportQuizModal] = useState(false);
  const [selectedDeckForQuiz, setSelectedDeckForQuiz] = useState<FlashcardSet | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [showDeleteQuizConfirm, setShowDeleteQuizConfirm] = useState<string | null>(null);

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
  // Flashcard sets displayed
  const myPersonalSets = useMemo(() => {
    return sets.filter((s) => Boolean(s));
  }, [sets]);

  // Quizzes displayed
  const myPersonalQuizzes = useMemo(() => {
    return quizzes.filter((q) => Boolean(q));
  }, [quizzes]);

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

  const handleForwardImportToManualCreate = (cards: { term: string; definition: string }[]) => {
    setShowImportModal(false);
    setPrefilledCardsForCreate(cards);
    setShowCreateSetModal(true);
    notify(`Đã chuyển ${cards.length} thẻ sang giao diện tạo bộ thẻ thủ công!`, 'info');
  };

  const handleCreateQuiz = (data: {
    title: string;
    description: string;
    category: string;
    privacy?: 'public' | 'private';
    timeLimitMinutes: number;
    questions: QuizQuestionInput[];
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
      privacy: data.privacy || 'public',
      status: data.privacy === 'private' ? 'approved' : 'pending',
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
        points: typeof q.points === 'number' ? q.points : 1,
      })),
    };

    setQuizzes([createdQuiz, ...quizzes]);
    setShowCreateQuizModal(false);
    setSelectedDeckForQuiz(null);
    notify(
      data.privacy === 'public'
        ? 'Đã tạo bộ đề Quiz mới! Bộ đề ở chế độ Công khai (chờ duyệt để hiển thị cho cộng đồng).'
        : 'Đã tạo bộ đề Quiz mới ở chế độ Riêng tư (chỉ mình bạn xem được)!',
      'success'
    );
  };

  const handleOpenCreateQuizForDeck = (set: FlashcardSet) => {
    setSelectedDeckForQuiz(set);
    setShowCreateQuizModal(true);
  };

  const handleOpenImportQuizForDeck = (set: FlashcardSet) => {
    setSelectedDeckForQuiz(set);
    setShowImportQuizModal(true);
  };

  const handleDeleteQuiz = (id: string) => {
    if (!id) return;
    setQuizzes((prev) => prev.filter((q) => q && q.id !== id));
    setShowDeleteQuizConfirm(null);
    notify('Đã xóa bộ đề Quiz thành công!', 'info');
  };

  const handleConfirmImportQuiz = (
    questions: QuizQuestionInput[],
    privacy: 'public' | 'private' = 'public'
  ) => {
    const importedQuiz: QuizSet = {
      id: `quiz_import_${Date.now()}`,
      title: selectedDeckForQuiz
        ? `Quiz: ${selectedDeckForQuiz.title}`
        : `Đề thi trắc nghiệm nhập từ file (${new Date().toLocaleDateString('vi-VN')})`,
      description: selectedDeckForQuiz
        ? `Đề thi trắc nghiệm được tạo từ bộ thẻ flashcard "${selectedDeckForQuiz.title}".`
        : 'Đề thi được tạo tự động từ tệp CSV/JSON câu hỏi.',
      category: selectedDeckForQuiz?.category || 'Công nghệ thông tin',
      createdBy: currentUser.name,
      userId: currentUser.id,
      privacy: privacy,
      status: 'approved',
      timeLimitMinutes: 15,
      questions: questions.map((q, idx) => ({
        id: idx + 1,
        ...q,
        points: typeof q.points === 'number' ? q.points : 1,
      })),
    };

    setQuizzes([importedQuiz, ...quizzes]);
    setShowImportQuizModal(false);
    setSelectedDeckForQuiz(null);
    notify(
      selectedDeckForQuiz
        ? `Đã tạo đề thi trắc nghiệm từ bộ thẻ "${selectedDeckForQuiz.title}" với ${importedQuiz.questions.length} câu hỏi (${privacy === 'public' ? 'Công khai' : 'Riêng tư'})!`
        : `Đã nhập thành công bộ đề với ${importedQuiz.questions.length} câu hỏi (${privacy === 'public' ? 'Công khai' : 'Riêng tư'})!`,
      'success'
    );
  };

  const handleForwardImportQuizToManualCreate = (
    questions: QuizQuestionInput[],
    privacy: 'public' | 'private' = 'public',
    deck?: FlashcardSet | null
  ) => {
    setShowImportQuizModal(false);
    setPrefilledQuizForCreate({ questions, privacy, deck: deck || selectedDeckForQuiz });
    setShowCreateQuizModal(true);
    notify(`Đã chuyển ${questions.length} câu hỏi sang giao diện tạo quiz thủ công!`, 'info');
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
          {/* VIEW: FLASHCARD */}
          {currentTab === 'sets' && (
            <MySetsView
              currentUser={currentUser}
              myPersonalSets={myPersonalSets}
              onOpenCreateSetModal={() => setShowCreateSetModal(true)}
              onOpenImportSetModal={() => setShowImportModal(true)}
              onDeleteSetConfirm={(id) => setShowDeleteConfirm(id)}
              handleStartStudy={handleStartStudy}
              navigateTo={navigateTo}
              onOpenCreateQuizForDeck={handleOpenCreateQuizForDeck}
              onOpenImportQuizForDeck={handleOpenImportQuizForDeck}
            />
          )}

          {/* VIEW: QUIZ */}
          {currentTab === 'my_quizzes' && (
            <MyQuizzesView
              currentUser={currentUser}
              myPersonalQuizzes={myPersonalQuizzes}
              onOpenCreateQuizModal={() => {
                setSelectedDeckForQuiz(null);
                setShowCreateQuizModal(true);
              }}
              onOpenImportQuizModal={() => {
                setSelectedDeckForQuiz(null);
                setShowImportQuizModal(true);
              }}
              onDeleteQuizConfirm={(id) => setShowDeleteQuizConfirm(id)}
              handleStartQuiz={handleStartQuiz}
              navigateTo={navigateTo}
            />
          )}

          {/* VIEW: LỊCH SỬ THI */}
          {currentTab === 'history' && (
            <HistoryView history={history} />
          )}

          {/* VIEW: HỌC FLASHCARD (LẬT THẺ 3D) */}
          {currentTab === 'study' && (
            <StudyView
              activeStudySet={activeStudySet}
              onExit={() => navigateTo('sets')}
              notify={notify}
            />
          )}

          {/* VIEW: LÀM BÀI THI QUIZ */}
          {currentTab === 'quiz_mode' && (
            <QuizRunnerView
              activeQuiz={activeQuiz}
              onFinishAttempt={handleFinishQuizAttempt}
              onExit={() => navigateTo('my_quizzes')}
              notify={notify}
            />
          )}
        </main>
      </div>

      {/* MODALS */}
      <CreateSetModal
        isOpen={showCreateSetModal}
        initialCards={prefilledCardsForCreate || undefined}
        onNotify={notify}
        onClose={() => {
          setShowCreateSetModal(false);
          setPrefilledCardsForCreate(null);
        }}
        onSubmit={(data) => {
          handleCreateSet(data);
          setPrefilledCardsForCreate(null);
        }}
      />

      <ImportSetModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onConfirmImport={handleConfirmImportSet}
        onForwardToManualCreate={handleForwardImportToManualCreate}
        onNotify={notify}
      />

      <CreateQuizModal
        isOpen={showCreateQuizModal}
        targetDeck={prefilledQuizForCreate?.deck || selectedDeckForQuiz}
        availableSets={sets}
        initialQuestions={prefilledQuizForCreate?.questions}
        initialPrivacy={prefilledQuizForCreate?.privacy}
        onNotify={notify}
        onClose={() => {
          setShowCreateQuizModal(false);
          setSelectedDeckForQuiz(null);
          setPrefilledQuizForCreate(null);
        }}
        onSubmit={(data) => {
          handleCreateQuiz(data);
          setPrefilledQuizForCreate(null);
        }}
      />

      <ImportQuizModal
        isOpen={showImportQuizModal}
        targetDeck={selectedDeckForQuiz}
        onClose={() => {
          setShowImportQuizModal(false);
          setSelectedDeckForQuiz(null);
        }}
        onConfirmImport={handleConfirmImportQuiz}
        onForwardToManualCreate={handleForwardImportQuizToManualCreate}
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
