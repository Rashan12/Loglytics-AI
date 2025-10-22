export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
  preferences?: string
}

export interface LogFile {
  id: number
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  file_type: string
  upload_status: string
  user_id: number
  created_at: string
  updated_at?: string
  is_processed: boolean
  processing_error?: string
  metadata?: string
}

export interface LogEntry {
  id: number
  log_file_id: number
  line_number: number
  timestamp?: string
  level?: string
  message: string
  source?: string
  thread_id?: string
  user_id?: string
  session_id?: string
  ip_address?: string
  user_agent?: string
  raw_data?: string
  parsed_data?: string
  created_at: string
  is_anomaly: boolean
  anomaly_score?: number
  tags?: string
}

export interface Analysis {
  id: number
  name: string
  description?: string
  analysis_type: string
  log_file_id?: number
  user_id: number
  results: string
  status: string
  created_at: string
  completed_at?: string
  error_message?: string
  execution_time?: number
  is_public: boolean
}

export interface ChatSession {
  id: number
  session_id: string
  user_id: number
  title?: string
  context?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  last_message_at?: string
}

export interface ChatMessage {
  id: number
  session_id: number
  role: string
  content: string
  metadata?: string
  created_at: string
  token_count?: number
  model_used?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
