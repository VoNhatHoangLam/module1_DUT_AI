import React, { useState, useMemo, useEffect } from 'react';
import { Menu, Loader2 } from 'lucide-react';

// Data types
import {
  UserProfile,
  FlashcardSet,
  QuizSet,
  QuizAttempt,
  TabType,
  QuizQuestionInput,
  StudySessionState,
  QuizSessionState,
} from './types';

// Business Services (API client layer)
import { deckService } from './services/deckService';
import { studyService } from './services/studyService';
import { quizService } from './services/quizService';
import { historyService } from './services/historyService';

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

const DEFAULT_USER: UserProfile = {
  id: '1',
  name: 'Học viên DUT',
  email: 'hocvien@dut.udn.vn',
  role: 'user',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces',
  joinDate: '2026-10-01',
  status: 'active',
  bio: 'Sinh viên Khoa CNTT - Đại học Bách Khoa ĐN',
};

export default function App() {
  // Navigation & User state
  const [currentUser] = useState<UserProfile>(DEFAULT_USER);
  const [currentTab, setCurrentTab] = useState<TabType>('sets');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Application Data States (Đồng bộ với Python CSV Backend)
  const [sets, setSets] = useState<FlashcardSet[]>([]);
  const [quizzes, setQuizzes] = useState<QuizSet[]>([]);
  const [history, setHistory] = useState<QuizAttempt[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Study & Quiz Active sessions
  const [activeStudySet, setActiveStudySet] = useState<FlashcardSet | null>(null);
  const [activeStudySession, setActiveStudySession] = useState<StudySessionState | null>(null);
  const [activeQuiz, setActiveQuiz] = useState<QuizSet | null>(null);
  const [activeQuizSession, setActiveQuizSession] = useState<QuizSessionState | null>(null);

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

  // Nạp toàn bộ dữ liệu từ Backend khi khởi chạy
  const loadInitialData = async () => {
    setIsLoadingData(true);
    try {
      const [decksRes, quizzesRes, historyRes] = await Promise.allSettled([
        deckService.getDecks(undefined, 1, 100),
        quizService.getQuizzes(undefined, 1, 100),
        historyService.listAttempts(),
      ]);

      if (decksRes.status === 'fulfilled') {
        setSets(decksRes.value.items || []);
      } else {
        console.warn('Không thể nạp danh sách bộ thẻ từ backend:', decksRes.reason);
      }

      if (quizzesRes.status === 'fulfilled') {
        setQuizzes(quizzesRes.value.items || []);
      } else {
        console.warn('Không thể nạp danh sách quiz từ backend:', quizzesRes.reason);
      }

      if (historyRes.status === 'fulfilled') {
        setHistory(historyRes.value || []);
      } else {
        console.warn('Không thể nạp lịch sử thi từ backend:', historyRes.reason);
      }
    } catch (err: any) {
      console.error('Lỗi khi nạp dữ liệu từ backend:', err);
      notify('Không thể kết nối đến máy chủ Backend (FastAPI). Vui lòng đảm bảo `python main.py` đang chạy!', 'error');
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // --- DERIVED / FILTERED DATA MEMOS ---
  const myPersonalSets = useMemo(() => {
    return sets.filter((s) => Boolean(s));
  }, [sets]);

  const myPersonalQuizzes = useMemo(() => {
    return quizzes.filter((q) => Boolean(q));
  }, [quizzes]);

  // --- ACTIONS TÍCH HỢP VỚI SERVICES ---

  const handleStartStudy = async (set: FlashcardSet) => {
    try {
      const session = await studyService.startStudy(set.id);
      setActiveStudySet(set);
      setActiveStudySession(session);
      navigateTo('study');
    } catch (err: any) {
      notify(`Không thể bắt đầu học: ${err.message}`, 'error');
    }
  };

  const handleStartQuiz = async (quiz: QuizSet) => {
    try {
      const session = await quizService.startQuiz(quiz.id);
      setActiveQuiz(quiz);
      setActiveQuizSession(session);
      navigateTo('quiz_mode');
    } catch (err: any) {
      notify(`Không thể bắt đầu làm bài quiz: ${err.message}`, 'error');
    }
  };

  const handleCreateSet = async (data: {
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

    try {
      const created = await deckService.createDeck({
        title: data.title.trim(),
        description: data.description.trim() || 'Bộ thẻ tự tạo bởi học viên.',
        category: data.category,
        privacy: data.privacy,
        cards: validCards,
      });

      setSets((prev) => [created, ...prev]);
      setShowCreateSetModal(false);
      notify('Đã tạo và lưu bộ flashcard thành công vào hệ thống!', 'success');
    } catch (err: any) {
      notify(`Lỗi tạo bộ thẻ: ${err.message}`, 'error');
    }
  };

  const handleDeleteSet = async (id: string) => {
    if (!id) return;
    try {
      await deckService.deleteDeck(id);
      setSets((prev) => prev.filter((s) => s && s.id !== id));
      setShowDeleteConfirm(null);
      notify('Đã xóa bộ flashcard thành công khỏi hệ thống!', 'info');
    } catch (err: any) {
      notify(`Lỗi xóa bộ thẻ: ${err.message}`, 'error');
    }
  };

  const handleConfirmImportSet = async (cards: { term: string; definition: string }[]) => {
    try {
      const created = await deckService.createDeck({
        title: `Bộ thẻ nhập từ file (${new Date().toLocaleDateString('vi-VN')})`,
        description: 'Dữ liệu được nhập tự động từ tệp CSV mẫu.',
        category: 'Công nghệ thông tin',
        privacy: 'public',
        cards,
      });

      setSets((prev) => [created, ...prev]);
      setShowImportModal(false);
      notify(`Đã nhập thành công ${created.cards?.length || cards.length} flashcard vào hệ thống!`, 'success');
    } catch (err: any) {
      notify(`Lỗi nhập bộ thẻ: ${err.message}`, 'error');
    }
  };

  const handleForwardImportToManualCreate = (cards: { term: string; definition: string }[]) => {
    setShowImportModal(false);
    setPrefilledCardsForCreate(cards);
    setShowCreateSetModal(true);
    notify(`Đã chuyển ${cards.length} thẻ sang giao diện tạo bộ thẻ thủ công!`, 'info');
  };

  const handleCreateQuiz = async (data: {
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

    try {
      const sourceDeckId = selectedDeckForQuiz
        ? selectedDeckForQuiz.deck_id || Number(selectedDeckForQuiz.id)
        : null;

      const createdQuiz = await quizService.createQuiz({
        title: data.title.trim(),
        description: data.description.trim() || 'Bộ đề thi trắc nghiệm do học viên tạo.',
        category: data.category,
        privacy: data.privacy || 'public',
        time_limit_minutes: Number(data.timeLimitMinutes) || 10,
        source_deck_id: sourceDeckId,
        questions: validQuestions,
      });

      setQuizzes((prev) => [createdQuiz, ...prev]);
      setShowCreateQuizModal(false);
      setSelectedDeckForQuiz(null);
      notify('Đã tạo và lưu bộ đề Quiz mới thành công vào hệ thống!', 'success');
    } catch (err: any) {
      notify(`Lỗi tạo bài quiz: ${err.message}`, 'error');
    }
  };

  const handleOpenCreateQuizForDeck = (set: FlashcardSet) => {
    setSelectedDeckForQuiz(set);
    setShowCreateQuizModal(true);
  };

  const handleOpenImportQuizForDeck = (set: FlashcardSet) => {
    setSelectedDeckForQuiz(set);
    setShowImportQuizModal(true);
  };

  const handleDeleteQuiz = async (id: string) => {
    if (!id) return;
    try {
      await quizService.deleteQuiz(id);
      setQuizzes((prev) => prev.filter((q) => q && q.id !== id));
      setShowDeleteQuizConfirm(null);
      notify('Đã xóa bộ đề Quiz thành công khỏi hệ thống!', 'info');
    } catch (err: any) {
      notify(`Lỗi xóa bài quiz: ${err.message}`, 'error');
    }
  };

  const handleConfirmImportQuiz = async (
    questions: QuizQuestionInput[],
    privacy: 'public' | 'private' = 'public'
  ) => {
    try {
      const sourceDeckId = selectedDeckForQuiz
        ? selectedDeckForQuiz.deck_id || Number(selectedDeckForQuiz.id)
        : null;

      const importedQuiz = await quizService.createQuiz({
        title: selectedDeckForQuiz
          ? `Quiz: ${selectedDeckForQuiz.title}`
          : `Đề thi trắc nghiệm nhập từ file (${new Date().toLocaleDateString('vi-VN')})`,
        description: selectedDeckForQuiz
          ? `Đề thi trắc nghiệm được tạo từ bộ thẻ flashcard "${selectedDeckForQuiz.title}".`
          : 'Đề thi được tạo tự động từ tệp CSV câu hỏi.',
        category: selectedDeckForQuiz?.category || 'Công nghệ thông tin',
        privacy: privacy,
        time_limit_minutes: 15,
        source_deck_id: sourceDeckId,
        questions,
      });

      setQuizzes((prev) => [importedQuiz, ...quizzes]);
      setShowImportQuizModal(false);
      setSelectedDeckForQuiz(null);
      notify(
        selectedDeckForQuiz
          ? `Đã tạo đề thi từ bộ thẻ "${selectedDeckForQuiz.title}" với ${questions.length} câu hỏi!`
          : `Đã nhập và lưu thành công bộ đề với ${questions.length} câu hỏi!`,
        'success'
      );
    } catch (err: any) {
      notify(`Lỗi nhập đề thi quiz: ${err.message}`, 'error');
    }
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
          {isLoadingData ? (
            <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
              <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              <p className="text-sm font-semibold text-slate-600">
                Đang nạp dữ liệu từ hệ thống lưu trữ...
              </p>
            </div>
          ) : (
            <>
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
              {currentTab === 'history' && <HistoryView history={history} />}

              {/* VIEW: HỌC FLASHCARD (HÀNG ĐỢI FIFO QUEUE) */}
              {currentTab === 'study' && activeStudySet && (
                <StudyView
                  activeStudySet={activeStudySet}
                  initialSession={activeStudySession}
                  onExit={() => {
                    setActiveStudySet(null);
                    setActiveStudySession(null);
                    navigateTo('sets');
                  }}
                  notify={notify}
                />
              )}

              {/* VIEW: LÀM BÀI THI QUIZ (NGĂN XẾP 2-STACK) */}
              {currentTab === 'quiz_mode' && activeQuiz && (
                <QuizRunnerView
                  activeQuiz={activeQuiz}
                  initialSession={activeQuizSession}
                  onFinishAttempt={handleFinishQuizAttempt}
                  onExit={() => {
                    setActiveQuiz(null);
                    setActiveQuizSession(null);
                    navigateTo('my_quizzes');
                  }}
                  notify={notify}
                />
              )}
            </>
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
        description="Hành động này sẽ xóa vĩnh viễn bộ thẻ khỏi hệ thống và xóa toàn bộ thẻ con liên kết (Cascade Delete). Không thể hoàn tác."
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
        description="Hành động này sẽ xóa bài thi khỏi hệ thống và xóa liên đới các câu hỏi cùng kết quả thi liên quan. Không thể hoàn tác."
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
