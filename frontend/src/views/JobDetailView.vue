<template>
  <div class="job-detail-view">
    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="job" class="job-detail">
      <div class="job-header">
        <div class="breadcrumb">
          <router-link to="/jobs">{{ $t('job.jobList') }}</router-link>
          <span> / </span>
          <span>{{ job.title }}</span>
        </div>
        
        <div class="job-actions">
          <router-link :to="`/jobs/${job.id}/edit`" class="edit-btn">
            {{ $t('common.edit') }}
          </router-link>
          <button @click="deleteJob" class="delete-btn">
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>

      <div class="job-content">
        <div class="job-main">
          <h1>{{ job.title }}</h1>
          
          <div class="job-meta">
            <div class="meta-item">
              <strong>{{ $t('job.company') }}:</strong>
              <span>{{ job.company_name }}</span>
            </div>
            
            <div class="meta-item">
              <strong>{{ $t('job.location') }}:</strong>
              <span>{{ job.location }}</span>
            </div>
            
            <div class="meta-item">
              <strong>{{ $t('job.status') }}:</strong>
              <span class="status-badge" :class="getStatusClass(job.status)">{{ getStatusText(job.status) }}</span>
            </div>
            
            <div class="meta-item">
              <strong>{{ $t('job.salary') }}:</strong>
              <span>{{ job.salary_range }}</span>
            </div>
            
            <div class="meta-item">
              <strong>{{ $t('job.postedDate') }}:</strong>
              <span>{{ formatDate(job.posting_date) }}</span>
            </div>
            
            <div class="meta-item">
              <strong>{{ $t('job.expirationDate') }}:</strong>
              <span>{{ formatDate(job.expiration_date) }}</span>
            </div>
          </div>

          <div class="job-description">
            <h2>{{ $t('job.description') }}</h2>
            <div class="description-content">
              {{ job.description }}
            </div>
          </div>

          <div class="job-required-skills" v-if="job.required_skills && job.required_skills.length > 0">
            <h2>{{ $t('job.requiredSkills') }}</h2>
            <div class="skills-content">
              <div class="skills-tags">
                <span v-for="(skill, index) in job.required_skills" :key="index" class="skill-tag">
                  {{ skill }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="job-sidebar">
          <div class="company-section">
            <h3>{{ $t('job.company') }}</h3>
            <div class="company-info">
              <p><strong>{{ $t('job.company') }}:</strong> {{ job.company_name }}</p>
            </div>
          </div>
        </div>
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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useJobStore } from '@/stores/jobStore'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const jobStore = useJobStore()

const jobId = computed(() => parseInt(route.params.id as string))
const job = computed(() => jobStore.currentJob)
const loading = computed(() => jobStore.loading)

onMounted(async () => {
  await jobStore.fetchJob(jobId.value)
})

const deleteJob = async () => {
  if (confirm(t('job.confirmDelete'))) {
    await jobStore.deleteJob(jobId.value)
    router.push('/jobs')
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// 獲取職缺狀態對應的文字
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'active': t('job.statusTypes.active'),
    'scheduled': t('job.statusTypes.scheduled'),
    'expired': t('job.statusTypes.expired')
  }
  
  return statusMap[status.toLowerCase()] || status
}

// 獲取職缺狀態對應的樣式類名
const getStatusClass = (status: string) => {
  return `status-${status.toLowerCase()}`
}
</script>

<style scoped>
.job-detail-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.job-actions {
  display: flex;
  gap: 1rem;
}

.edit-btn {
  background-color: #ffc107;
  color: #212529;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
}

.edit-btn:hover {
  background-color: #e0a800;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #c82333;
}

.job-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.job-main {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.job-main h1 {
  margin: 0 0 1.5rem 0;
  color: #333;
}

.job-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-item strong {
  color: #495057;
  font-size: 0.875rem;
}

.meta-item span {
  color: #333;
  font-weight: 500;
}

.job-description,
.job-requirements,
.job-benefits {
  margin-bottom: 2rem;
}

.job-description h2,
.job-requirements h2,
.job-benefits h2 {
  color: #333;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
}

.description-content,
.requirements-content,
.benefits-content {
  line-height: 1.6;
  color: #555;
  white-space: pre-wrap;
}

.skills-content {
  margin-top: 1rem;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-weight: 500;
  font-size: 0.875rem;
}

.status-active {
  background-color: #d4edda;
  color: #155724;
}

.status-expired {
  background-color: #f8d7da;
  color: #721c24;
}

.status-scheduled {
  background-color: #fff3cd;
  color: #856404;
}

.job-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.company-section,
.contact-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.contact-section h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.contact-info p {
  margin: 0.5rem 0;
  color: #555;
}

.contact-info a {
  color: #007bff;
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
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
  .job-detail-view {
    padding: 1rem;
  }
  
  .job-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .job-content {
    grid-template-columns: 1fr;
  }
  
  .job-meta {
    grid-template-columns: 1fr;
  }
  
  .job-main {
    padding: 1.5rem;
  }
}
</style>
