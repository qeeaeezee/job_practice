<template>
  <div class="job-edit-view">
    <div class="header">
      <div class="breadcrumb">
        <router-link to="/jobs">{{ $t('job.jobList') }}</router-link>
        <span> / </span>
        <router-link :to="`/jobs/${jobId}`">{{ jobData.title || $t('job.jobDetail') }}</router-link>
        <span> / </span>
        <span>{{ $t('job.editJob') }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="jobData.title" class="job-form-container">
      <h1>{{ $t('job.editJob') }}</h1>
      
      <form @submit.prevent="handleSubmit" class="job-form">
        <div class="form-row">
          <div class="form-group">
            <label for="title">{{ $t('job.title') }} *</label>
            <input
              id="title"
              v-model="jobData.title"
              type="text"
              required
              :placeholder="$t('job.titlePlaceholder')"
            />
            <span v-if="errors.title" class="error">{{ errors.title }}</span>
          </div>

          <div class="form-group">
            <label for="company_name">{{ $t('job.company') }}</label>
            <input
              id="company_name"
              v-model="jobData.company_name"
              type="text"
              disabled
              readonly
              :title="$t('job.companyNameReadOnly')"
              :placeholder="$t('job.companyPlaceholder')"
            />
            <small class="field-note">{{ $t('job.companyNameReadOnly') }}</small>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="location">{{ $t('job.location') }} *</label>
            <select id="location" v-model="jobData.location" required>
              <option value="">{{ $t('job.selectLocation') }}</option>
              <option :value="$t('job.taipei')">{{ $t('job.taipei') }}</option>
              <option :value="$t('job.taichung')">{{ $t('job.taichung') }}</option>
              <option :value="$t('job.kaohsiung')">{{ $t('job.kaohsiung') }}</option>
              <option :value="$t('job.remote')">{{ $t('job.remote') }}</option>
            </select>
            <span v-if="errors.location" class="error">{{ errors.location }}</span>
          </div>

          <div class="form-group">
            <label for="salary_range">{{ $t('job.salaryRange') }} *</label>
            <input
              id="salary_range"
              v-model="jobData.salary_range"
              type="text"
              required
              :placeholder="$t('job.salaryRangePlaceholder')"
            />
            <span v-if="errors.salary_range" class="error">{{ errors.salary_range }}</span>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="status">{{ $t('job.status') }}</label>
            <div class="status-display">
              <span class="status-badge" :class="'status-' + jobData.status.toLowerCase()">
                {{ $t(`job.statusTypes.${jobData.status?.toLowerCase()}`) }}
              </span>
            </div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="jobData.is_active"
                :disabled="jobData.status === 'expired'"
              />
              {{ $t('job.isActive') }}
            </label>
            <small class="field-note" v-if="jobData.status === 'expired'">
              {{ $t('job.expiredJobNotActive') }}
            </small>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="posting_date">{{ $t('job.postingDate') }}</label>
            <input
              id="posting_date"
              v-model="jobData.posting_date"
              type="date"
              :min="minPostingDate"
              :disabled="!jobData.is_scheduled || jobData.status === 'active'"
              :placeholder="$t('job.postingDatePlaceholder')"
            />
            <span v-if="errors.posting_date" class="error">{{ errors.posting_date }}</span>
            <small class="field-note" v-if="jobData.status === 'active'">
              {{ $t('job.activeJobNoSchedule') }}
            </small>
          </div>

          <div class="form-group">
            <label for="expiration_date">{{ $t('job.expirationDate') }} *</label>
            <input
              id="expiration_date"
              v-model="jobData.expiration_date"
              type="date"
              required
              :min="minPostingDate"
              :placeholder="$t('job.expirationDatePlaceholder')"
            />
            <span v-if="errors.expiration_date" class="error">{{ errors.expiration_date }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="description">{{ $t('job.description') }} *</label>
          <textarea
            id="description"
            v-model="jobData.description"
            rows="6"
            required
            :placeholder="$t('job.descriptionPlaceholder')"
          ></textarea>
          <span v-if="errors.description" class="error">{{ errors.description }}</span>
        </div>

        <div class="form-group">
          <label for="required_skills">{{ $t('job.requiredSkills') }}</label>
          <div class="skills-input">
            <input
              id="skill_input"
              v-model="newSkill"
              type="text"
              @keydown.enter.prevent="addSkill"
              :placeholder="$t('job.addSkillPlaceholder')"
            />
            <button type="button" @click="addSkill" class="add-skill-btn">{{ $t('common.add') }}</button>
          </div>
          <div class="skills-tags" v-if="jobData.required_skills && jobData.required_skills.length > 0">
            <span v-for="(skill, index) in jobData.required_skills" :key="index" class="skill-tag">
              {{ skill }}
              <button type="button" @click="removeSkill(index)" class="remove-skill">×</button>
            </span>
          </div>
          <span v-if="errors.required_skills" class="error">{{ errors.required_skills }}</span>
        </div>
        
        <div class="form-group scheduling-option">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="jobData.is_scheduled"
              @change="handleSchedulingChange"
              :disabled="jobData.status === 'active'"
            />
            {{ $t('job.scheduleForLater') }}
          </label>
          <p class="scheduling-note" v-if="jobData.is_scheduled && jobData.status !== 'active'">
            {{ $t('job.schedulingNote') }}
          </p>
        </div>



        <div class="form-actions">
          <button type="button" @click="goBack" class="cancel-btn">
            {{ $t('common.cancel') }}
          </button>
          <button type="submit" :disabled="isSubmitting" class="submit-btn">
            {{ isSubmitting ? $t('common.saving') : $t('common.save') }}
          </button>
        </div>
      </form>

      <div v-if="submitError" class="error-message">
        {{ submitError }}
      </div>
    </div>

    <div v-else class="not-found">
      <h1>{{ $t('job.notFound') }}</h1>
      <p>{{ $t('job.notFoundMessage') }}</p>
      <router-link to="/jobs" class="back-btn">
        {{ $t('job.backToList') }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useJobStore } from '@/stores/jobStore'
import type { JobUpdate } from '@/types'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const jobStore = useJobStore()

const jobId = computed(() => parseInt(route.params.id as string))

// 添加 minPostingDate 計算屬性，用於限制發布日期必須在今天之後
const minPostingDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0] // 返回 YYYY-MM-DD 格式的今天日期
})

const jobData = reactive<JobUpdate>({
  title: '',
  company_name: '',
  location: '',
  salary_range: '',
  description: '',
  expiration_date: '',
  required_skills: [],
  is_active: true,
  status: '',
  is_scheduled: false,
  posting_date: undefined
})

const errors = reactive<Record<string, string>>({})
const loading = ref(false)
const isSubmitting = ref(false)
const submitError = ref('')
const newSkill = ref('')

onMounted(async () => {
  await loadJob()
})

const loadJob = async () => {
  try {
    loading.value = true
    await jobStore.fetchJob(jobId.value)
    
    const job = jobStore.currentJob
    if (job) {
      // Copy job data to the form
      jobData.title = job.title
      jobData.company_name = job.company_name
      jobData.location = job.location
      jobData.description = job.description
      jobData.salary_range = job.salary_range
      jobData.expiration_date = job.expiration_date ? new Date(job.expiration_date).toISOString().split('T')[0] : ''
      jobData.posting_date = job.posting_date ? new Date(job.posting_date).toISOString().split('T')[0] : undefined
      jobData.required_skills = [...job.required_skills]
      jobData.is_active = job.is_active
      jobData.status = job.status?.toLowerCase()
      jobData.is_scheduled = Boolean(job.is_scheduled)
    }
  } catch (error) {
    console.error('Failed to load job:', error)
  } finally {
    loading.value = false
  }
}

const validateForm = (): boolean => {
  // Clear previous errors
  Object.keys(errors).forEach(key => {
    delete errors[key]
  })

  let isValid = true

  // Required field validation
  if (!jobData.title?.trim()) {
    errors.title = t('validation.required', { field: t('job.title') })
    isValid = false
  }

  if (!jobData.location) {
    errors.location = t('validation.required', { field: t('job.location') })
    isValid = false
  }

  if (!jobData.description?.trim()) {
    errors.description = t('validation.required', { field: t('job.description') })
    isValid = false
  }

  if (!jobData.salary_range?.trim()) {
    errors.salary_range = t('validation.required', { field: t('job.salaryRange') })
    isValid = false
  }

  if (!jobData.expiration_date) {
    errors.expiration_date = t('validation.required', { field: t('job.expirationDate') })
    isValid = false
  }
  
  // Scheduled posting validation
  if (jobData.is_scheduled && jobData.status !== 'active') {
    // 檢查排程職位必須有發布日期
    if (!jobData.posting_date) {
      errors.posting_date = t('validation.required', { field: t('job.postingDate') })
      isValid = false
    } 
    // 檢查排程職位的發布日期必須在未來
    else {
      const now = new Date()
      const postingDate = new Date(jobData.posting_date)
      now.setHours(0, 0, 0, 0) // 設置為當天開始時間，只比較日期
      
      if (postingDate <= now) {
        errors.posting_date = t('job.futureDateRequired')
        isValid = false
      }
    }
  }

  return isValid
}

const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  try {
    isSubmitting.value = true
    submitError.value = ''

    // Format dates to ISO format for API
    const formattedData = { ...jobData }
    
    // 移除 company_name，根據規格要求，公司名稱無法修改
    delete formattedData.company_name
    
    if (formattedData.posting_date) {
      formattedData.posting_date = new Date(formattedData.posting_date).toISOString()
    }
    
    if (formattedData.expiration_date) {
      formattedData.expiration_date = new Date(formattedData.expiration_date).toISOString()
    }

    await jobStore.updateJob(jobId.value, formattedData)
    router.push(`/jobs/${jobId.value}`)
  } catch (error: any) {
    submitError.value = error.message || t('job.updateError')
  } finally {
    isSubmitting.value = false
  }
}

const goBack = () => {
  router.go(-1)
}

const addSkill = () => {
  const skill = newSkill.value.trim()
  if (skill && jobData.required_skills && !jobData.required_skills.includes(skill)) {
    if (!jobData.required_skills) {
      jobData.required_skills = []
    }
    jobData.required_skills.push(skill)
    newSkill.value = ''
  }
}

const removeSkill = (index: number) => {
  if (jobData.required_skills) {
    jobData.required_skills.splice(index, 1)
  }
}

const handleSchedulingChange = () => {
  if (!jobData.is_scheduled) {
    // Clear posting date if scheduling is disabled
    jobData.posting_date = undefined
  }
}

// 使用 minPostingDate 代替此函數
const getCurrentDate = () => {
  return minPostingDate.value
}
</script>

<style scoped>
.job-edit-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

.breadcrumb {
  color: #666;
}

.breadcrumb a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.job-form-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.job-form-container h1 {
  margin: 0 0 2rem 0;
  color: #333;
}

.job-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.cancel-btn:hover {
  background-color: #f8f9fa;
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.submit-btn:hover:not(:disabled) {
  background-color: #218838;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.not-found {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.not-found h1 {
  color: #dc3545;
  margin-bottom: 1rem;
}

.not-found p {
  color: #666;
  margin-bottom: 2rem;
}

.back-btn {
  background-color: #007bff;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
}

.back-btn:hover {
  background-color: #0056b3;
}

@media (max-width: 768px) {
  .job-edit-view {
    padding: 1rem;
  }
  
  .job-form-container {
    padding: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
