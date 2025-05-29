import api from './api'
import type { Job, JobCreate, JobUpdate, JobFilter, PaginationParams, PagedJobListSchema } from '@/types'

export class JobService {
  static async getJobs(
    filters: JobFilter = {},
    pagination: PaginationParams = {},
    orderBy?: string
  ): Promise<PagedJobListSchema> {
    const params = new URLSearchParams()
    
    // 添加篩選參數
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })
    
    // 處理技能篩選，如果是數組，轉為逗號分隔字符串
    if (filters.required_skills && Array.isArray(filters.required_skills)) {
      params.delete('required_skills')
      params.append('required_skills', filters.required_skills.join(','))
    }
    
    // 添加分頁參數
    if (pagination.page) params.append('page', pagination.page.toString())
    if (pagination.page_size) params.append('page_size', pagination.page_size.toString())
    
    // 添加排序參數
    if (orderBy) params.append('order_by', orderBy)
    
    const response = await api.get(`/jobs?${params.toString()}`)
    return response.data
  }

  static async getJob(id: number): Promise<Job> {
    const response = await api.get(`/jobs/${id}`)
    return response.data
  }

  static async createJob(job: JobCreate): Promise<Job> {
    const response = await api.post('/jobs', job)
    return response.data
  }

  static async updateJob(id: number, job: JobUpdate): Promise<Job> {
    const response = await api.put(`/jobs/${id}`, job)
    return response.data
  }

  static async deleteJob(id: number): Promise<void> {
    await api.delete(`/jobs/${id}`)
  }
}

export default JobService
