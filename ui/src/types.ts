export interface Flashcard {
  id: string;
  card_id?: number;
  deck_id?: number;
  term: string;
  definition: string;
  position?: number;
}

export interface FlashcardSet {
  id: string;
  deck_id?: number;
  title: string;
  description: string;
  category: string;
  createdBy: string;
  userId: string;
  privacy: 'public' | 'private';
  status: 'approved' | 'pending' | 'rejected';
  updatedAt: string;
  cards: Flashcard[];
}

export interface QuizQuestion {
  id: number;
  question_id?: number;
  quiz_id?: number;
  question: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  points?: number;
  position?: number;
}

export type QuizQuestionInput = Omit<QuizQuestion, 'id'>;

export interface QuizSet {
  id: string;
  quiz_id?: number;
  title: string;
  description: string;
  category: string;
  createdBy: string;
  userId?: string;
  privacy?: 'public' | 'private';
  status: 'approved' | 'pending' | 'rejected';
  timeLimitMinutes: number;
  questions: QuizQuestion[];
  source_deck_id?: number | null;
}

export interface QuizAttempt {
  id: string;
  attempt_id?: number;
  quizId: string;
  quizTitle: string;
  takenDate: string;
  score: number;
  correctCount: number;
  totalCount: number;
  accuracy: string;
  status: string;
  userAnswers: Record<number, string>;
}

export interface QuizAnswerDetail {
  answer_id: number;
  attempt_id: number;
  selected_answer: string | null;
  correct_answer_snapshot: string;
  is_correct: boolean;
  points_earned: number;
  question_text_snapshot: string;
  selected_option_text_snapshot: string | null;
  correct_option_text_snapshot: string;
}

export interface QuizAttemptResult {
  attempt: QuizAttempt;
  answers: QuizAnswerDetail[];
}

export interface StudySessionState {
  session_id: string;
  deck_id: number;
  deck_title: string;
  current_card: Flashcard | null;
  remaining_count: number;
  unknown_count: number;
  known_count: number;
  total_cards: number;
  is_completed: boolean;
  is_initial_phase: boolean;
}

export interface QuizSessionState {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  total_questions: number;
  current_question: QuizQuestion | null;
  current_answer: string | null;
  can_back: boolean;
  can_forward: boolean;
  remaining_count: number;
  is_completed: boolean;
  selected_answers: Record<number, string | null>;
}

export interface UserProfile {
  id: string;
  name: string;
  username?: string;
  password?: string;
  email: string;
  role: 'guest' | 'user' | 'admin';
  avatar: string;
  joinDate: string;
  status: 'active' | 'locked';
  bio: string;
}

export type TabType =
  | 'sets'
  | 'my_quizzes'
  | 'history'
  | 'study'
  | 'quiz_mode';
