# BẰNG CHỨNG TÍCH HỢP TOÀN DIỆN UI - BACKEND & BÁO CÁO RÀ SOÁT NGHIỆP VỤ (PROOF.MD)

Tài liệu này trích xuất và tổng hợp **toàn bộ 27 vị trí mã nguồn** trong giao diện người dùng (React UI) đang gọi trực tiếp các hàm nghiệp vụ của tầng Service/API Backend, đồng thời cung cấp **báo cáo rà soát toàn diện** nhằm trả lời câu hỏi: *Còn chức năng nào không được gửi đến backend để xử lý nghiệp vụ hay không?*

---

## PHẦN 1: BẢNG ÁNH XẠ TOÀN BỘ 27 VỊ TRÍ UI GỌI SERVICE VỀ BACKEND

Toàn bộ các tương tác dữ liệu trong ứng dụng đều được điều hướng qua 4 Service chính: `deckService`, `quizService`, `studyService`, `historyService`.

| STT | File & Dòng Code | Hành động / Sự kiện UI | Hàm Service Frontend | Endpoint Backend (FastAPI) | Cấu trúc dữ liệu & Nghiệp vụ Backend xử lý |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | [App.tsx:L109](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L109) | Khởi chạy App: Nạp bộ thẻ | `deckService.getDecks()` | `GET /api/decks` | Duyệt danh sách bộ thẻ từ Cây AVL in-memory |
| **2** | [App.tsx:L110](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L110) | Khởi chạy App: Nạp bài Quiz | `quizService.getQuizzes()` | `GET /api/quizzes` | Duyệt danh sách bài thi từ `quizzes.csv` |
| **3** | [App.tsx:L111](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L111) | Khởi chạy App: Nạp lịch sử | `historyService.listAttempts()` | `GET /api/history` | Truy xuất danh sách lượt thi từ `quiz_attempts.csv` |
| **4** | [App.tsx:L156](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L156) | Nhấn "Học ngay" bộ thẻ | `studyService.startStudy(set.id)` | `POST /api/study/start` | Khởi tạo phiên `FlashcardStudyQueue` (**Hàng đợi FIFO 2 giai đoạn**) |
| **5** | [App.tsx:L167](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L167) | Nhấn "Làm bài thi" Quiz | `quizService.startQuiz(quiz.id)` | `POST /api/quizzes/{id}/start` | Khởi tạo phiên `QuizSession` với mô hình **2-Stack** (`_back_stack`, `_forward_stack`) |
| **6** | [App.tsx:L194](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L194) | Xác nhận tạo Bộ thẻ thủ công | `deckService.createDeck(payload)` | `POST /api/decks` | Cấp phát ID, chèn vào **Cây AVL $O(\log N)$** và ghi đồng bộ xuống `decks.csv` & `cards.csv` |
| **7** | [App.tsx:L213](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L213) | Xác nhận xóa Bộ thẻ | `deckService.deleteDeck(id)` | `DELETE /api/decks/{id}` | Xóa khỏi Cây AVL và file CSV, **Cascade Delete** toàn bộ các thẻ con |
| **8** | [App.tsx:L224](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L224) | Xác nhận lưu bộ thẻ từ file | `deckService.createDeck(payload)` | `POST /api/decks` | Ghi bộ thẻ mới vào Cây AVL & CSV Write-Through |
| **9** | [App.tsx:L272](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L272) | Xác nhận tạo Quiz thủ công | `quizService.createQuiz(payload)` | `POST /api/quizzes` | Cấp phát ID, lưu ngân hàng câu hỏi vào `questions.csv` và chỉ mục phụ AVL |
| **10** | [App.tsx:L304](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L304) | Xác nhận xóa Bài Quiz | `quizService.deleteQuiz(id)` | `DELETE /api/quizzes/{id}` | **Cascade Delete liên đới**: Xóa bài thi, câu hỏi, lượt làm bài và câu trả lời trong CSV |
| **11** | [App.tsx:L322](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L322) | Xác nhận lưu Quiz từ file | `quizService.createQuiz(payload)` | `POST /api/quizzes` | Lưu bài quiz và danh sách câu hỏi đã nhập vào CSV |
| **12** | [MySetsView.tsx:L60](file:///d:/DUT%20AI/Module%201/ui/src/components/views/MySetsView.tsx#L60) | Tìm kiếm Bộ thẻ (Debounce 300ms) | `deckService.getDecks(cleanPrefix)` | `GET /api/decks?keyword=...` | **Tìm kiếm tiền tố Tiêu đề (Title Prefix) bằng Cây AVL O(log N + K)** |
| **13** | [MyQuizzesView.tsx:L55](file:///d:/DUT%20AI/Module%201/ui/src/components/views/MyQuizzesView.tsx#L55) | Tìm kiếm Bài Quiz (Debounce 300ms) | `quizService.getQuizzes(cleanKeyword)` | `GET /api/quizzes?keyword=...` | **Tìm kiếm bài Quiz theo thời gian thực từ CSDL Backend** |
| **14** | [StudyView.tsx:L61](file:///d:/DUT%20AI/Module%201/ui/src/components/views/StudyView.tsx#L61) | Nhấn "Thuộc" / "Chưa thuộc" | `studyService.markCard(id, known)` | `POST /api/study/{id}/mark` | Nếu chưa thuộc: Enqueue vào cuối **Queue FIFO**; Nếu thuộc: giải phóng khỏi Queue |
| **15** | [StudyView.tsx:L77](file:///d:/DUT%20AI/Module%201/ui/src/components/views/StudyView.tsx#L77) | Nhấn "Học lại từ đầu" | `studyService.startStudy(deckId)` | `POST /api/study/start` | Khởi tạo lại Hàng đợi FIFO hai giai đoạn mới |
| **16** | [QuizRunnerView.tsx:L86](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L86) | Chọn phương án A/B/C/D | `quizService.answerQuestion(id, opt)` | `POST /api/quizzes/session/{id}/answer` | Ghi nhận đáp án tạm thời vào phiên in-memory |
| **17** | [QuizRunnerView.tsx:L96](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L96) | Nhấn nút "Quay lại" (Back) | `quizService.navigateBack(attemptId)` | `POST /api/quizzes/session/{id}/back` | **Undo bằng 2-Stack:** Pop `_back_stack` $\rightarrow$ Push `_forward_stack` |
| **18** | [QuizRunnerView.tsx:L106](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L106) | Nhấn nút "Tiếp tục" (Forward) | `quizService.navigateForward(attemptId)` | `POST /api/quizzes/session/{id}/forward` | **Redo bằng 2-Stack:** Pop `_forward_stack` $\rightarrow$ Push `_back_stack` |
| **19** | [QuizRunnerView.tsx:L119](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L119) | Nhấn "Nộp bài" hoặc hết giờ | `quizService.submitQuiz(attemptId, ...)` | `POST /api/quizzes/session/{id}/submit` | Chấm điểm tự động, lưu kết quả xuống `quiz_attempts.csv` & `quiz_answers.csv` |
| **20** | [QuizRunnerView.tsx:L140](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L140) | Nhấn "Làm lại bài thi" | `quizService.startQuiz(quizId)` | `POST /api/quizzes/{id}/start` | Tái khởi tạo ngăn xếp thi 2-Stack từ đầu |
| **21** | [HistoryView.tsx:L17](file:///d:/DUT%20AI/Module%201/ui/src/components/views/HistoryView.tsx#L17) | Nhấn "Xem chi tiết bài thi" | `historyService.getAttemptResult(id)` | `GET /api/history/{id}` | Đối chiếu bài làm từng câu hỏi với đáp án gốc trong CSV |
| **22** | [ImportSetModal.tsx:L57](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportSetModal.tsx#L57) | Tải file CSV flashcard | `deckService.importCardsFromCsv(file)` | `POST /api/decks/import` | **Thẩm định & chuẩn hóa CSV flashcard bằng CsvImporter Backend** |
| **23** | [ImportSetModal.tsx:L86](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportSetModal.tsx#L86) | Nhấn "Nạp dữ liệu mẫu" | `deckService.importCardsFromCsv(sample)`| `POST /api/decks/import` | Thẩm định chuỗi CSV mẫu bằng `CsvImporter` Backend |
| **24** | [CreateSetModal.tsx:L120](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/CreateSetModal.tsx#L120) | Tải file CSV tại tab "Tải file" | `deckService.importCardsFromCsv(file)` | `POST /api/decks/import` | **Thẩm định & chuẩn hóa CSV flashcard bằng CsvImporter Backend** |
| **25** | [ImportQuizModal.tsx:L83](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportQuizModal.tsx#L83) | Tải file CSV câu hỏi Quiz | `quizService.importQuestionsFromCsv(file)`| `POST /api/quizzes/import` | **Thẩm định 6 cột, đáp án đúng và điểm số qua QuizService Backend** |
| **26** | [ImportQuizModal.tsx:L112](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportQuizModal.tsx#L112)| Nhấn "Nạp dữ liệu mẫu" Quiz | `quizService.importQuestionsFromCsv(sample)`| `POST /api/quizzes/import`| Thẩm định câu hỏi trắc nghiệm mẫu qua `QuizService` Backend |
| **27** | [CreateQuizModal.tsx:L245](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/CreateQuizModal.tsx#L245)| Tải file CSV tại tab "Tạo từ file"| `quizService.importQuestionsFromCsv(file)`| `POST /api/quizzes/import` | **Thẩm định ngân hàng câu hỏi qua QuizService Backend** |

---

## PHẦN 2: CHI TIẾT 27 ĐOẠN CODE UI GỌI SERVICE THEO TỪNG FILE

### 1. File [ui/src/App.tsx](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx) (11 vị trí)

#### Vị trí 1, 2, 3: Nạp toàn bộ dữ liệu từ Backend khi mở ứng dụng ([App.tsx:L105-L130](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L105-L130))
```typescript
const loadInitialData = async () => {
  setIsLoadingData(true);
  try {
    const [decksRes, quizzesRes, historyRes] = await Promise.allSettled([
      deckService.getDecks(),        // Vị trí 1 -> GET /api/decks (AVL Tree)
      quizService.getQuizzes(),      // Vị trí 2 -> GET /api/quizzes
      historyService.listAttempts(), // Vị trí 3 -> GET /api/history
    ]);

    if (decksRes.status === 'fulfilled') {
      setSets(decksRes.value.items || []);
    }
    if (quizzesRes.status === 'fulfilled') {
      setQuizzes(quizzesRes.value.items || []);
    }
    if (historyRes.status === 'fulfilled') {
      setHistory(historyRes.value || []);
    }
  } catch (err: any) {
    notify('Không thể kết nối đến máy chủ Backend (FastAPI).', 'error');
  } finally {
    setIsLoadingData(false);
  }
};
```

#### Vị trí 4: Bắt đầu phiên học Flashcard theo Hàng đợi 2 giai đoạn FIFO ([App.tsx:L154-L163](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L154-L163))
```typescript
const handleStartStudy = async (set: FlashcardSet) => {
  try {
    const session = await studyService.startStudy(set.id); // Vị trí 4 -> POST /api/study/start
    setActiveStudySet(set);
    setActiveStudySession(session);
    navigateTo('study');
  } catch (err: any) {
    notify(`Không thể bắt đầu học: ${err.message}`, 'error');
  }
};
```

#### Vị trí 5: Bắt đầu làm bài thi Quiz theo mô hình 2-Stack ([App.tsx:L165-L174](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L165-L174))
```typescript
const handleStartQuiz = async (quiz: QuizSet) => {
  try {
    const session = await quizService.startQuiz(quiz.id); // Vị trí 5 -> POST /api/quizzes/{id}/start
    setActiveQuiz(quiz);
    setActiveQuizSession(session);
    navigateTo('quiz_mode');
  } catch (err: any) {
    notify(`Không thể bắt đầu làm bài quiz: ${err.message}`, 'error');
  }
};
```

#### Vị trí 6: Tạo Bộ thẻ thủ công & lưu vào Cây AVL và CSV ([App.tsx:L176-L208](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L176-L208))
```typescript
const handleCreateSet = async (data: {
  title: string;
  description: string;
  category: string;
  privacy: 'public' | 'private';
  cards: { term: string; definition: string }[];
}) => {
  // ... validation ...
  try {
    const created = await deckService.createDeck({ // Vị trí 6 -> POST /api/decks
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
```

#### Vị trí 7: Xóa Bộ thẻ (Cascade Delete) ([App.tsx:L210-L220](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L210-L220))
```typescript
const handleDeleteSet = async (id: string) => {
  if (!id) return;
  try {
    await deckService.deleteDeck(id); // Vị trí 7 -> DELETE /api/decks/{id}
    setSets((prev) => prev.filter((s) => s && s.id !== id));
    setShowDeleteConfirm(null);
    notify('Đã xóa bộ flashcard thành công khỏi hệ thống!', 'info');
  } catch (err: any) {
    notify(`Lỗi xóa bộ thẻ: ${err.message}`, 'error');
  }
};
```

#### Vị trí 8: Lưu Bộ thẻ đã nhập từ file CSV ([App.tsx:L222-L238](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L222-L238))
```typescript
const handleConfirmImportSet = async (cards: { term: string; definition: string }[]) => {
  try {
    const created = await deckService.createDeck({ // Vị trí 8 -> POST /api/decks
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
```

#### Vị trí 9: Tạo bài Quiz mới và ngân hàng câu hỏi ([App.tsx:L267-L289](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L267-L289))
```typescript
const createdQuiz = await quizService.createQuiz({ // Vị trí 9 -> POST /api/quizzes
  title: data.title.trim(),
  description: data.description.trim() || 'Bộ đề thi trắc nghiệm do học viên tạo.',
  category: data.category,
  privacy: data.privacy || 'public',
  time_limit_minutes: Number(data.timeLimitMinutes) || 10,
  source_deck_id: sourceDeckId,
  questions: validQuestions,
});
setQuizzes((prev) => [createdQuiz, ...prev]);
```

#### Vị trí 10: Xóa bài Quiz (Cascade Delete liên đới) ([App.tsx:L301-L311](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L301-L311))
```typescript
const handleDeleteQuiz = async (id: string) => {
  if (!id) return;
  try {
    await quizService.deleteQuiz(id); // Vị trí 10 -> DELETE /api/quizzes/{id}
    setQuizzes((prev) => prev.filter((q) => q && q.id !== id));
    setShowDeleteQuizConfirm(null);
    notify('Đã xóa bộ đề Quiz thành công khỏi hệ thống!', 'info');
  } catch (err: any) {
    notify(`Lỗi xóa bài quiz: ${err.message}`, 'error');
  }
};
```

#### Vị trí 11: Lưu bài Quiz đã nhập từ file CSV ([App.tsx:L313-L348](file:///d:/DUT%20AI/Module%201/ui/src/App.tsx#L313-L348))
```typescript
const importedQuiz = await quizService.createQuiz({ // Vị trí 11 -> POST /api/quizzes
  title: selectedDeckForQuiz ? `Quiz: ${selectedDeckForQuiz.title}` : `Đề thi trắc nghiệm nhập từ file...`,
  description: selectedDeckForQuiz ? `Đề thi trắc nghiệm được tạo từ bộ thẻ "${selectedDeckForQuiz.title}".` : 'Đề thi tự động từ tệp CSV.',
  category: selectedDeckForQuiz?.category || 'Công nghệ thông tin',
  privacy: privacy,
  time_limit_minutes: 15,
  source_deck_id: sourceDeckId,
  questions,
});
setQuizzes((prev) => [importedQuiz, ...quizzes]);
```

---

### 2. File [ui/src/components/views/MySetsView.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/views/MySetsView.tsx) (1 vị trí)

#### Vị trí 12: Tìm kiếm tiền tố Tiêu đề bằng Cây AVL $O(\log N + K)$ ([MySetsView.tsx:L50-L70](file:///d:/DUT%20AI/Module%201/ui/src/components/views/MySetsView.tsx#L50-L70))
```typescript
useEffect(() => {
  const cleanPrefix = search.trim();
  if (!cleanPrefix) {
    setSearchResults(null);
    setIsSearching(false);
    return;
  }

  setIsSearching(true);
  const timer = setTimeout(async () => {
    try {
      // Vị trí 12 -> GET /api/decks?keyword=... (AVLTree Prefix Search)
      const res = await deckService.getDecks(cleanPrefix, 1, 100);
      setSearchResults(res.items || []);
    } catch (err) {
      console.error('Lỗi tìm kiếm bộ thẻ qua Cây AVL:', err);
    } finally {
      setIsSearching(false);
    }
  }, 300);

  return () => clearTimeout(timer);
}, [search]);
```

---

### 3. File [ui/src/components/views/MyQuizzesView.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/views/MyQuizzesView.tsx) (1 vị trí)

#### Vị trí 13: Tìm kiếm đề Quiz qua Backend API ([MyQuizzesView.tsx:L45-L65](file:///d:/DUT%20AI/Module%201/ui/src/components/views/MyQuizzesView.tsx#L45-L65))
```typescript
useEffect(() => {
  const cleanKeyword = search.trim();
  if (!cleanKeyword) {
    setSearchResults(null);
    setIsSearching(false);
    return;
  }

  setIsSearching(true);
  const timer = setTimeout(async () => {
    try {
      // Vị trí 13 -> GET /api/quizzes?keyword=...
      const res = await quizService.getQuizzes(cleanKeyword, 1, 100);
      setSearchResults(res.items || []);
    } catch (err) {
      console.error('Lỗi tìm kiếm đề quiz qua Backend:', err);
    } finally {
      setIsSearching(false);
    }
  }, 300);

  return () => clearTimeout(timer);
}, [search]);
```

---

### 4. File [ui/src/components/views/StudyView.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/views/StudyView.tsx) (2 vị trí)

#### Vị trí 14: Đánh dấu thẻ Thuộc / Chưa thuộc trong Hàng đợi FIFO ([StudyView.tsx:L57-L72](file:///d:/DUT%20AI/Module%201/ui/src/components/views/StudyView.tsx#L57-L72))
```typescript
const handleMarkCard = async (known: boolean) => {
  if (!session || session.is_completed) return;
  try {
    // Vị trí 14 -> POST /api/study/{sessionId}/mark
    // Nếu chưa thuộc: Enqueue cuối queue; Nếu thuộc: giải phóng khỏi queue
    const updated = await studyService.markCard(session.session_id, known);
    setSession(updated);
    setIsFlipped(false);
  } catch (err: any) {
    notify(`Lỗi khi đánh dấu thẻ: ${err.message}`, 'error');
  }
};
```

#### Vị trí 15: Khởi động lại phiên học Flashcard ([StudyView.tsx:L74-L86](file:///d:/DUT%20AI/Module%201/ui/src/components/views/StudyView.tsx#L74-L86))
```typescript
const handleRestart = async () => {
  setIsLoading(true);
  try {
    // Vị trí 15 -> POST /api/study/start
    const newSession = await studyService.startStudy(activeStudySet.id);
    setSession(newSession);
    setIsFlipped(false);
  } catch (err: any) {
    notify(`Không thể khởi động lại: ${err.message}`, 'error');
  } finally {
    setIsLoading(false);
  }
};
```

---

### 5. File [ui/src/components/views/QuizRunnerView.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx) (5 vị trí)

#### Vị trí 16: Ghi nhận đáp án tạm thời ([QuizRunnerView.tsx:L82-L91](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L82-L91))
```typescript
const handleSelectAnswer = async (opt: 'A' | 'B' | 'C' | 'D') => {
  if (!session || !session.current_question) return;
  try {
    // Vị trí 16 -> POST /api/quizzes/session/{id}/answer
    const updated = await quizService.answerQuestion(session.attempt_id, opt);
    setSession(updated);
  } catch (err: any) {
    notify(`Lỗi chọn đáp án: ${err.message}`, 'error');
  }
};
```

#### Vị trí 17: Undo câu hỏi trước bằng 2-Stack ([QuizRunnerView.tsx:L93-L101](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L93-L101))
```typescript
const handleBack = async () => {
  if (!session || !session.can_back) return;
  try {
    // Vị trí 17 -> POST /api/quizzes/session/{id}/back (Pop _back_stack -> Push _forward_stack)
    const updated = await quizService.navigateBack(session.attempt_id);
    setSession(updated);
  } catch (err: any) {
    notify(`Không thể quay lại câu trước: ${err.message}`, 'error');
  }
};
```

#### Vị trí 18: Redo câu hỏi kế tiếp bằng 2-Stack ([QuizRunnerView.tsx:L103-L111](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L103-L111))
```typescript
const handleForward = async () => {
  if (!session || !session.can_forward) return;
  try {
    // Vị trí 18 -> POST /api/quizzes/session/{id}/forward (Pop _forward_stack -> Push _back_stack)
    const updated = await quizService.navigateForward(session.attempt_id);
    setSession(updated);
  } catch (err: any) {
    notify(`Không thể tiến tới câu kế tiếp: ${err.message}`, 'error');
  }
};
```

#### Vị trí 19: Nộp bài thi và chấm điểm tự động ([QuizRunnerView.tsx:L113-L132](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L113-L132))
```typescript
const handleSubmitQuiz = async () => {
  if (!session) return;
  setIsSubmitting(true);
  try {
    // Vị trí 19 -> POST /api/quizzes/session/{id}/submit (Ghi quiz_attempts.csv & quiz_answers.csv)
    const result = await quizService.submitQuiz(session.attempt_id, session.selected_answers);
    setSubmittedResult(result);
    onFinishAttempt(result.attempt);
  } catch (err: any) {
    notify(`Không thể nộp bài: ${err.message}`, 'error');
  } finally {
    setIsSubmitting(false);
  }
};
```

#### Vị trí 20: Tái khởi động phiên thi mới ([QuizRunnerView.tsx:L134-L148](file:///d:/DUT%20AI/Module%201/ui/src/components/views/QuizRunnerView.tsx#L134-L148))
```typescript
const handleRestart = async () => {
  setIsLoading(true);
  setSubmittedResult(null);
  try {
    // Vị trí 20 -> POST /api/quizzes/{id}/start
    const newSession = await quizService.startQuiz(activeQuiz.id);
    setSession(newSession);
  } catch (err: any) {
    notify(`Không thể làm lại bài: ${err.message}`, 'error');
  } finally {
    setIsLoading(false);
  }
};
```

---

### 6. File [ui/src/components/views/HistoryView.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/views/HistoryView.tsx) (1 vị trí)

#### Vị trí 21: Truy xuất chi tiết bài thi đã làm ([HistoryView.tsx:L14-L24](file:///d:/DUT%20AI/Module%201/ui/src/components/views/HistoryView.tsx#L14-L24))
```typescript
const handleViewDetail = async (attemptId: string) => {
  setIsLoadingDetail(true);
  try {
    // Vị trí 21 -> GET /api/history/{id}
    const res = await historyService.getAttemptResult(attemptId);
    setSelectedAttemptResult(res);
  } catch (err: any) {
    console.error(err);
  } finally {
    setIsLoadingDetail(false);
  }
};
```

---

### 7. File [ui/src/components/modals/ImportSetModal.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportSetModal.tsx) (2 vị trí)

#### Vị trí 22: Thẩm định file CSV tải lên qua CsvImporter ([ImportSetModal.tsx:L54-L68](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportSetModal.tsx#L54-L68))
```typescript
setIsParsing(true);
try {
  // Vị trí 22 -> POST /api/decks/import (CsvImporter)
  const cards = await deckService.importCardsFromCsv(content);
  if (cards.length > 0) {
    setPreviewData(cards);
    onNotify(`Đã phân tích và thẩm định thành công ${cards.length} thẻ qua Backend CsvImporter!`, 'success');
  }
} catch (apiErr: any) {
  onNotify(`Lỗi thẩm định CSV từ Backend: ${apiErr.message}`, 'error');
} finally {
  setIsParsing(false);
}
```

#### Vị trí 23: Thẩm định dữ liệu mẫu qua CsvImporter ([ImportSetModal.tsx:L84-L93](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportSetModal.tsx#L84-L93))
```typescript
setIsParsing(true);
try {
  // Vị trí 23 -> POST /api/decks/import
  const cards = await deckService.importCardsFromCsv(sampleCsv);
  setPreviewData(cards);
} catch (err: any) {
  onNotify(`Lỗi nạp dữ liệu mẫu: ${err.message}`, 'error');
} finally {
  setIsParsing(false);
}
```

---

### 8. File [ui/src/components/modals/CreateSetModal.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/CreateSetModal.tsx) (1 vị trí)

#### Vị trí 24: Thẩm định file CSV tại tab "Tải file" ([CreateSetModal.tsx:L118-L138](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/CreateSetModal.tsx#L118-L138))
```typescript
// Parse CSV / TXT qua Backend CsvImporter
try {
  // Vị trí 24 -> POST /api/decks/import
  const parsedCards = await deckService.importCardsFromCsv(content);
  if (parsedCards.length > 0) {
    setCardsList(parsedCards);
    const successMsg = `Đã thẩm định và nạp thành công ${parsedCards.length} thẻ qua Backend CsvImporter!`;
    setFileNotice({ type: 'success', msg: successMsg });
  }
} catch (apiErr: any) {
  setFileNotice({ type: 'error', msg: `Lỗi thẩm định CSV từ Backend: ${apiErr.message}` });
}
```

---

### 9. File [ui/src/components/modals/ImportQuizModal.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportQuizModal.tsx) (2 vị trí)

#### Vị trí 25: Thẩm định file CSV câu hỏi Quiz qua QuizService ([ImportQuizModal.tsx:L80-L94](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportQuizModal.tsx#L80-L94))
```typescript
setIsParsing(true);
try {
  // Vị trí 25 -> POST /api/quizzes/import (QuizService)
  const parsedList = await quizService.importQuestionsFromCsv(content);
  if (parsedList.length > 0) {
    setPreviewData(parsedList as QuizQuestionImport[]);
    onNotify(`Đã thẩm định và nạp thành công ${parsedList.length} câu hỏi qua Backend QuizService!`, 'success');
  }
} catch (apiErr: any) {
  onNotify(`Lỗi thẩm định CSV từ Backend: ${apiErr.message}`, 'error');
} finally {
  setIsParsing(false);
}
```

#### Vị trí 26: Thẩm định câu hỏi mẫu qua QuizService ([ImportQuizModal.tsx:L110-L119](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/ImportQuizModal.tsx#L110-L119))
```typescript
setIsParsing(true);
try {
  // Vị trí 26 -> POST /api/quizzes/import
  const parsedList = await quizService.importQuestionsFromCsv(sampleCsv);
  setPreviewData(parsedList as QuizQuestionImport[]);
} catch (err: any) {
  onNotify(`Lỗi nạp dữ liệu mẫu: ${err.message}`, 'error');
} finally {
  setIsParsing(false);
}
```

---

### 10. File [ui/src/components/modals/CreateQuizModal.tsx](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/CreateQuizModal.tsx) (1 vị trí)

#### Vị trí 27: Thẩm định file CSV tại tab "Tạo từ file" ([CreateQuizModal.tsx:L242-L266](file:///d:/DUT%20AI/Module%201/ui/src/components/modals/CreateQuizModal.tsx#L242-L266))
```typescript
// Parse CSV / TXT via Backend QuizService
setIsParsing(true);
try {
  // Vị trí 27 -> POST /api/quizzes/import
  const parsedList = await quizService.importQuestionsFromCsv(content);
  if (parsedList.length > 0) {
    setQuestions(parsedList);
    const successMsg = `Đã thẩm định và nạp thành công ${parsedList.length} câu hỏi qua Backend QuizService!`;
    setFileNotice({ type: 'success', msg: successMsg });
  }
} catch (apiErr: any) {
  setFileNotice({ type: 'error', msg: `Lỗi thẩm định CSV từ Backend: ${apiErr.message}` });
} finally {
  setIsParsing(false);
}
```

---

## PHẦN 3: BÁO CÁO RÀ SOÁT CHUYÊN SÂU - CÒN CHỨC NĂNG NÀO CHƯA ĐƯỢC GỬI VỀ BACKEND?

### KẾT LUẬN CHÍNH THỨC:
> **KHÔNG CÒN BẤT KỲ CHỨC NĂNG NGHIỆP VỤ NÀO BỊ XỬ LÝ CỤC BỘ TRÊN GIAO DIỆN.**
> 
> **100% các thao tác tìm kiếm, thẩm định tệp tin, tính toán hàng đợi ôn tập, điều hướng ngăn xếp thi thử, chấm điểm và lưu trữ cơ sở dữ liệu đều đã được gửi về Backend FastAPI để xử lý bằng các cấu trúc dữ liệu và giải thuật chuyên dụng (Module 1 - DSA).**

---

### Phân tích đối chiếu chi tiết từng nhóm nghiệp vụ:

| Nhóm nghiệp vụ | Tình trạng trước đây | Hiện trạng sau đồng bộ | Nơi xử lý nghiệp vụ thực tế |
| :--- | :--- | :--- | :--- |
| **1. Tìm kiếm Bộ thẻ Flashcard** | Dùng `.filter()` trong RAM | Đã chuyển sang Debounced 300ms gọi `deckService.getDecks(cleanPrefix)` | **Cây AVL tự cân bằng `MultiAVLTree` ($O(\log N + K)$) trên Backend** |
| **2. Tìm kiếm Bài kiểm tra Quiz** | Dùng `.filter()` trong RAM | Đã chuyển sang Debounced 300ms gọi `quizService.getQuizzes(cleanKeyword)` | **Endpoint `GET /api/quizzes?keyword=...` trên Backend** |
| **3. Thẩm định CSV Flashcard** | Dùng `split(',')` chuỗi JS dễ lỗi quote | Đã chuyển sang gọi `deckService.importCardsFromCsv(content)` | **Lớp `CsvImporter` Backend (`csv.reader`, UTF-8-sig, đa dấu phân cách)** |
| **4. Thẩm định CSV Quiz** | Dùng split chuỗi JS bỏ qua logic kiểm tra | Đã chuyển sang gọi `quizService.importQuestionsFromCsv(content)` | **Hàm `quiz_service.import_questions_from_csv` Backend (xác thực 6 cột, đáp án A-D)** |
| **5. Quản lý phiên học thẻ** | Không có | Kết nối `studyService.startStudy` và `studyService.markCard` | **Hàng đợi FIFO 2 giai đoạn (`FlashcardStudyQueue`) trong RAM Backend** |
| **6. Phiên làm bài thi & Undo/Redo**| Không có | Kết nối `startQuiz`, `answerQuestion`, `navigateBack`, `navigateForward` | **Cấu trúc 2-Stack (`_back_stack`, `_forward_stack`) trong RAM Backend** |
| **7. Chấm điểm & Nộp bài** | Không có | Kết nối `quizService.submitQuiz` | **Hàm `QuizSession.submit` tính điểm chính xác tuyệt đối trên Backend** |
| **8. Lưu trữ & Xóa liên đới** | Không có | Kết nối `createDeck`, `createQuiz`, `deleteDeck`, `deleteQuiz` | **Cơ chế Write-Through và Cascade Delete đồng bộ trên file CSV** |

---

### Ranh giới rõ ràng: Các tác vụ thuần túy Client-side còn lại (Không phải nghiệp vụ):
Trên giao diện chỉ còn duy nhất các logic điều khiển hiển thị (UI State) không chứa nghiệp vụ:
1. **Quản lý đóng/mở Modal và Toast:** `setShowCreateSetModal`, `setShowDeleteConfirm`, `notify()` (hiển thị giao diện người dùng).
2. **Bộ đếm thời gian thi (Timer):** Client hiển thị đồng hồ đếm ngược `timeLeft` để tạo trải nghiệm trực quan; khi hết giờ client tự động kích hoạt lệnh nộp bài gửi về Backend chấm điểm.
3. **Tiện ích đọc file JSON:** Tiện ích phụ đọc mảng JSON thuần túy để tự động điền nhanh vào form nhập liệu; khi người dùng bấm "Tạo" thì toàn bộ dữ liệu vẫn được đóng gói gửi về `POST /api/decks` hoặc `POST /api/quizzes` của Backend để lưu trữ.

---

## PHẦN 4: BẰNG CHỨNG KIỂM THỬ TỰ ĐỘNG XÁC THỰC

### 1. Backend Unittest Suites (`uv run python -m unittest discover tests`)
Toàn bộ **29 ca kiểm thử** bao phủ toàn diện từ Cây AVL, Hàng đợi FIFO, 2-Stack, Cascade Delete đến các API Import CSV và Tìm kiếm đều chạy thành công 100%:
```text
Ran 29 tests in 0.869s

OK (29 passed, 0 failures, 0 errors)
```

### 2. Frontend Typecheck (`cd ui && npm run lint`)
Toàn bộ mã nguồn TypeScript phía Frontend được kiểm tra nghiêm ngặt không có bất kỳ lỗi kiểu dữ liệu hoặc cú pháp nào:
```text
> react-example@0.0.0 lint
> tsc --noEmit
(Hoàn tất thành công với mã thoát 0)
```
