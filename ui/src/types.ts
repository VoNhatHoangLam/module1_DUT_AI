export interface Flashcard {
  id: string;
  term: string;
  definition: string;
}

export interface FlashcardSet {
  id: string;
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
  question: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  points?: number;
}

export type QuizQuestionInput = Omit<QuizQuestion, 'id'>;

export interface QuizSet {
  id: string;
  title: string;
  description: string;
  category: string;
  createdBy: string;
  userId?: string;
  privacy?: 'public' | 'private';
  status: 'approved' | 'pending' | 'rejected';
  timeLimitMinutes: number;
  questions: QuizQuestion[];
}

export interface QuizAttempt {
  id: string;
  quizTitle: string;
  takenDate: string;
  score: number;
  correctCount: number;
  totalCount: number;
  accuracy: string;
  status: string;
  userAnswers: Record<number, string>;
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
