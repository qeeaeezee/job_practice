import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Job, JobListItem, JobCreate, JobUpdate, JobFilter, PaginationParams } from '@/types'
import JobService from '@/services/jobService'

export const useJobStore = defineStore('job', () => {
  // State
  const jobs = ref<JobListItem[]>([])
  const currentJob = ref<Job | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)

  // Getters
  const hasJobs = computed(() => jobs.value.length > 0)
  const hasError = computed(() => !!error.value)

  // Actions
  async function fetchJobs(filters: JobFilter = {}, paginationParams: PaginationParams = {}, orderBy: string = '-posting_date') {
    loading.value = true
    error.value = null
    
    try {
      const response = await JobService.getJobs(filters, paginationParams, orderBy)
      
      jobs.value = response.items || []
      total.value = response.count || 0
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || '載入職缺失敗'
      console.error('Fetch jobs error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchJob(id: number) {
    loading.value = true
    error.value = null
    
    try {
      currentJob.value = await JobService.getJob(id)
      return currentJob.value
    } catch (err: any) {
      error.value = err.response?.data?.message || '載入職缺詳情失敗'
      console.error('Fetch job error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createJob(jobData: JobCreate) {
    loading.value = true
    error.value = null
    
    try {
      const newJob = await JobService.createJob(jobData)
      return newJob
    } catch (err: any) {
      error.value = err.response?.data?.message || '建立職缺失敗'
      console.error('Create job error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateJob(id: number, jobData: JobUpdate) {
    loading.value = true
    error.value = null
    
    try {
      const updatedJob = await JobService.updateJob(id, jobData)
      if (currentJob.value?.id === id) {
        currentJob.value = updatedJob
      }
      return updatedJob
    } catch (err: any) {
      error.value = err.response?.data?.message || '更新職缺失敗'
      console.error('Update job error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteJob(id: number) {
    loading.value = true
    error.value = null
    
    try {
      await JobService.deleteJob(id)
      if (currentJob.value?.id === id) {
        currentJob.value = null
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || '刪除職缺失敗'
      console.error('Delete job error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrentJob() {
    currentJob.value = null
  }

  return {
    // State
    jobs,
    currentJob,
    loading,
    error,
    total,
    
    // Getters
    hasJobs,
    hasError,
    
    // Actions
    fetchJobs,
    fetchJob,
    createJob,
    updateJob,
    deleteJob,
    clearError,
    clearCurrentJob
  }
})
