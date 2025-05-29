<template>
  <div class="job-create-view">
    <div class="header">
      <div class="breadcrumb">
        <router-link to="/jobs">{{ $t('job.jobList') }}</router-link>
        <span> / </span>
        <span>{{ $t('job.createJob') }}</span>
      </div>
    </div>

    <div class="job-form-container">
      <h1>{{ $t('job.createJob') }}</h1>
      
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
            <label for="company_name">{{ $t('job.company') }} *</label>
            <input
              id="company_name"
              v-model="jobData.company_name"
              type="text"
              required
              :placeholder="$t('job.companyPlaceholder')"
            />
            <span v-if="errors.company_name" class="error">{{ errors.company_name }}</span>
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
            <label for="posting_date">{{ $t('job.postingDate') }}</label>
            <input
              id="posting_date"
              v-model="jobData.posting_date"
              type="date"
              :min="minPostingDate"
              :placeholder="$t('job.postingDatePlaceholder')"
            />
            <span v-if="errors.posting_date" class="error">{{ errors.posting_date }}</span>
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
          <div class="skills-tags" v-if="jobData.required_skills.length > 0">
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
            />
            {{ $t('job.scheduleForLater') }}
          </label>
          <p class="scheduling-note" v-if="jobData.is_scheduled">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useJobStore } from '@/stores/jobStore'
import type { JobCreate } from '@/types'

const router = useRouter()
const { t } = useI18n()
const jobStore = useJobStore()

// 添加 minPostingDate 計算屬性，用於限制發布日期必須在今天之後
const minPostingDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0] // 返回 YYYY-MM-DD 格式的今天日期
})

const jobData = reactive<JobCreate>({
  title: '',
  company_name: '',
  location: '',
  description: '',
  salary_range: '',
  expiration_date: '',
  required_skills: [],
  is_scheduled: false,
  posting_date: undefined
})

const newSkill = ref('')

const errors = reactive<Record<string, string>>({})
const isSubmitting = ref(false)
const submitError = ref('')

const validateForm = (): boolean => {
  // 清除之前的錯誤
  Object.keys(errors).forEach(key => {
    delete errors[key]
  })

  let isValid = true

  // 必填欄位驗證
  if (!jobData.title.trim()) {
    errors.title = t('form.titleRequired')
    isValid = false
  }

  if (!jobData.company_name.trim()) {
    errors.company_name = t('form.companyRequired')
    isValid = false
  }

  if (!jobData.location) {
    errors.location = t('form.locationRequired')
    isValid = false
  }

  if (!jobData.salary_range.trim()) {
    errors.salary_range = t('form.salaryRequired')
    isValid = false
  }

  if (!jobData.description.trim()) {
    errors.description = t('form.descriptionRequired')
    isValid = false
  }

  if (!jobData.expiration_date) {
    errors.expiration_date = t('form.expirationRequired')
    isValid = false
  }
  
  // 排程發布邏輯驗證
  if (jobData.is_scheduled) {
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

const addSkill = () => {
  const skill = newSkill.value.trim()
  if (skill && !jobData.required_skills.includes(skill)) {
    jobData.required_skills.push(skill)
    newSkill.value = ''
  }
}

const removeSkill = (index: number) => {
  jobData.required_skills.splice(index, 1)
}

const handleSchedulingChange = () => {
  if (!jobData.is_scheduled) {
    // 如果取消排程，清除發佈日期
    jobData.posting_date = undefined
  }
}

// 使用 minPostingDate 代替此函數
const getCurrentDate = () => {
  return minPostingDate.value
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  try {
    isSubmitting.value = true
    submitError.value = ''

    // 格式化日期為 ISO 格式
    const formattedData = { ...jobData }
    
    if (formattedData.posting_date) {
      formattedData.posting_date = new Date(formattedData.posting_date).toISOString()
    }
    
    if (formattedData.expiration_date) {
      formattedData.expiration_date = new Date(formattedData.expiration_date).toISOString()
    }

    await jobStore.createJob(formattedData)
    router.push('/jobs')
  } catch (error: any) {
    submitError.value = error.message || t('message.jobCreateFailed')
  } finally {
    isSubmitting.value = false
  }
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.job-create-view {
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

.job-form-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.skills-input {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.skills-input input {
  flex: 1;
}

.add-skill-btn {
  background-color: #5c6bc0;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.add-skill-btn:hover {
  background-color: #3f51b5;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.skill-tag {
  display: flex;
  align-items: center;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.remove-skill {
  background: none;
  border: none;
  color: #1976d2;
  margin-left: 0.25rem;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  padding: 0 0.25rem;
}

.remove-skill:hover {
  color: #d32f2f;
}

.scheduling-option {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.scheduling-note {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #666;
  font-style: italic;
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

@media (max-width: 768px) {
  .job-create-view {
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
