export interface Job {
  id: number
  title: string
  description: string
  location: string
  salary_range: string
  company_name: string
  posting_date: string
  expiration_date: string
  required_skills: string[]
  status: string
}

export interface JobListItem {
  id: number
  title: string
  company_name: string
  location: string
  posting_date: string
  expiration_date: string
  required_skills: string[]
  status: string
}

export interface JobCreate {
  title: string
  description: string
  location: string
  salary_range: string
  company_name: string
  expiration_date: string
  required_skills: string[]
  posting_date?: string
}

export interface JobUpdate {
  title?: string
  description?: string
  location?: string
  salary_range?: string
  expiration_date?: string
  required_skills?: string[]
  posting_date?: string
}

export interface JobFilter {
  title?: string
  description?: string
  company_name?: string
  location?: string
  required_skills?: string[] | string
  status?: string
}

export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PagedJobListSchema {
  items: JobListItem[]
  count: number
}

export interface ApiError {
  message: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
}

export interface TokenRefreshRequest {
  refresh: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active?: boolean
}

export interface MessageResponse {
  message: string
}
