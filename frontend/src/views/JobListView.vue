<template>
  <div class="job-list-view">
    <div class="header">
      <h1>{{ $t('job.jobList') }}</h1>
      <router-link to="/jobs/create" class="create-btn">
        {{ $t('job.createJob') }}
      </router-link>
    </div>

    <!-- 搜尋和篩選 -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('job.searchPlaceholder')"
          @input="handleSearch"
        />
      </div>
      
      <div class="filter-group">
        <select v-model="filters.status" @change="handleFilter">
          <option value="">{{ $t('job.allStatus') }}</option>
          <option value="active">{{ $t('job.statusActive') }}</option>
          <option value="scheduled">{{ $t('job.statusScheduled') }}</option>
          <option value="expired">{{ $t('job.statusExpired') }}</option>
        </select>

        <select v-model="filters.location" @change="handleFilter">
          <option value="">{{ $t('job.allLocations') }}</option>
          <option :value="$t('job.taipei')">{{ $t('job.taipei') }}</option>
          <option :value="$t('job.taichung')">{{ $t('job.taichung') }}</option>
          <option :value="$t('job.kaohsiung')">{{ $t('job.kaohsiung') }}</option>
          <option :value="$t('job.remote')">{{ $t('job.remote') }}</option>
        </select>

        <select v-model="orderBy" @change="handleFilter">
          <option value="-posting_date">{{ $t('job.postingDateDesc') }}</option>
          <option value="posting_date">{{ $t('job.postingDateAsc') }}</option>
          <option value="-expiration_date">{{ $t('job.expirationDateDesc') }}</option>
          <option value="expiration_date">{{ $t('job.expirationDateAsc') }}</option>
        </select>
      </div>
    </div>

    <!-- 載入狀態 -->
    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <!-- 職缺列表 -->
    <div v-else-if="jobs.length > 0" class="job-list">
      <div v-for="job in jobs" :key="job.id" class="job-card">
        <div class="job-header">
          <h3>
            <router-link :to="`/jobs/${job.id}`">
              {{ job.title }}
            </router-link>
          </h3>
          <div class="job-actions">
            <router-link :to="`/jobs/${job.id}/edit`" class="edit-btn">
              {{ $t('common.edit') }}
            </router-link>
            <button @click="deleteJob(job.id)" class="delete-btn">
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
        
        <div class="job-info">
          <p class="company">{{ job.company_name }}</p>
          <p class="location">{{ job.location }}</p>
          <p class="status" :class="getStatusClass(job.status)">
            {{ getStatusText(job.status) }}
          </p>
        </div>
        
        <div class="job-skills" v-if="job.required_skills && job.required_skills.length > 0">
          <span v-for="(skill, index) in job.required_skills" :key="index" class="skill-tag">
            {{ skill }}
          </span>
        </div>
        
        <div class="job-footer">
          <span class="date">
            {{ formatDate(job.posting_date) }}
          </span>
          <span class="expiry">
            {{ $t('job.expiry') }}: {{ formatDate(job.expiration_date) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 無資料 -->
    <div v-else class="no-data">
      {{ $t('job.noJobs') }}
    </div>

    <!-- 分頁 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage <= 1"
        class="page-btn"
      >
        {{ $t('pagination.previous') }}
      </button>
      
      <span class="page-info">
        {{ $t('pagination.pageInfo', { current: currentPage, total: totalPages }) }}
      </span>
      
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage >= totalPages"
        class="page-btn"
      >
        {{ $t('pagination.next') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useJobStore } from '@/stores/jobStore'
import type { JobFilter } from '@/types'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const jobStore = useJobStore()

const searchQuery = ref(route.query.title || '')
const filters = ref<JobFilter>({
  status: route.query.status?.toString() || '',
  location: route.query.location?.toString() || ''
})
const orderBy = ref(route.query.order_by?.toString() || '-posting_date')
const currentPage = ref(Number(route.query.page) || 1)
const pageSize = ref(10)

const jobs = computed(() => jobStore.jobs)
const loading = computed(() => jobStore.loading)
const total = computed(() => jobStore.total)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

onMounted(() => {
  loadJobs()
})

watch(
  () => route.query,
  (newQuery) => {
    searchQuery.value = newQuery.title?.toString() || ''
    filters.value.status = newQuery.status?.toString() || ''
    filters.value.location = newQuery.location?.toString() || ''
    orderBy.value = newQuery.order_by?.toString() || '-posting_date'
    currentPage.value = Number(newQuery.page) || 1
    loadJobs()
  }
)

const loadJobs = async () => {
  const searchFilters: JobFilter = { ...filters.value }
  if (searchQuery.value) {
    // 使用 title 作為主要搜尋條件
    searchFilters.title = searchQuery.value
  }

  await jobStore.fetchJobs(
    searchFilters,
    { page: currentPage.value, page_size: pageSize.value },
    orderBy.value
  )
}

const updateRouteQuery = () => {
  router.push({
    query: {
      title: searchQuery.value || undefined,
      status: filters.value.status || undefined,
      location: filters.value.location || undefined,
      order_by: orderBy.value || undefined,
      page: currentPage.value > 1 ? currentPage.value : undefined
    }
  })
}

const handleSearch = () => {
  currentPage.value = 1
  updateRouteQuery()
}

const handleFilter = () => {
  currentPage.value = 1
  updateRouteQuery()
}

const goToPage = (page: number) => {
  currentPage.value = page
  updateRouteQuery()
}

const deleteJob = async (id: number) => {
  if (confirm(t('job.confirmDelete'))) {
    await jobStore.deleteJob(id)
    loadJobs()
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// 獲取職缺狀態對應的文字
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'active': t('job.statusActive'),
    'scheduled': t('job.statusScheduled'),
    'expired': t('job.statusExpired')
  }
  
  return statusMap[status] || status
}

// 獲取職缺狀態對應的樣式類名
const getStatusClass = (status: string) => {
  return {
    'status-active': status === 'active',
    'status-scheduled': status === 'scheduled',
    'status-expired': status === 'expired'
  }
}
</script>

<style scoped>
.job-list-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8f9fa;
  min-height: calc(100vh - 4rem);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.header h1 {
  margin: 0;
  font-size: 2rem;
  color: #343a40;
  font-weight: 600;
}

.create-btn {
  background-color: #2ecc71;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease-in-out;
}

.create-btn:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.filters {
  margin-bottom: 2.5rem;
  padding: 1.75rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.search-box {
  margin-bottom: 1.75rem;
}

.search-box input {
  width: 100%;
  padding: 0.9rem 1rem;
  border: 1px solid #e1e5eb;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.search-box input:focus {
  border-color: #4dabf7;
  outline: none;
  box-shadow: 0 0 0 3px rgba(77, 171, 247, 0.1);
}

.filter-group {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-group select {
  padding: 0.8rem 1rem;
  border: 1px solid #e1e5eb;
  border-radius: 6px;
  flex: 1;
  min-width: 180px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  font-size: 0.95rem;
  cursor: pointer;
  transition: border-color 0.2s;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23343a40' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 16px;
  -webkit-appearance: none;
  appearance: none;
}

.filter-group select:focus {
  border-color: #4dabf7;
  outline: none;
  box-shadow: 0 0 0 3px rgba(77, 171, 247, 0.1);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
  font-size: 1.1rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.job-list {
  display: grid;
  gap: 1.75rem;
  margin-bottom: 2rem;
}

.job-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 5px solid #4dabf7;
}

.job-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.12);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.job-header h3 {
  margin: 0;
  font-size: 1.5rem;
  line-height: 1.3;
}

.job-header a {
  color: #343a40;
  text-decoration: none;
  transition: color 0.2s;
}

.job-header a:hover {
  color: #4dabf7;
}

.job-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.edit-btn,
.delete-btn {
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.875rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn {
  background-color: #ffd43b;
  color: #212529;
}

.edit-btn:hover {
  background-color: #fcc419;
  transform: translateY(-2px);
}

.delete-btn {
  background-color: #fa5252;
  color: white;
}

.delete-btn:hover {
  background-color: #e03131;
  transform: translateY(-2px);
}

.job-info {
  display: flex;
  gap: 1.75rem;
  color: #495057;
  flex-wrap: wrap;
  padding-bottom: 1rem;
  border-bottom: 1px dashed #e9ecef;
}

.job-info p {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.job-info .company {
  font-weight: 600;
  color: #343a40;
}

.job-info .status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-active {
  background-color: #d3f9d8;
  color: #2b8a3e;
}

.status-scheduled {
  background-color: #e7f5ff;
  color: #1971c2;
}

.status-expired {
  background-color: #ffe3e3;
  color: #c92a2a;
}

.job-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.75rem 0;
}

.skill-tag {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #495057;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px dashed #e9ecef;
}

.date, .expiry {
  font-style: italic;
  color: #868e96;
  font-size: 0.9rem;
}

.no-data {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
  background: white;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  font-size: 1.1rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-top: 3rem;
  padding: 1.5rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.page-btn {
  padding: 0.7rem 1.5rem;
  border: none;
  background: #e9ecef;
  color: #495057;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #4dabf7;
  color: white;
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #495057;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .job-list-view {
    padding: 1.5rem 1rem;
  }
  
  .header {
    flex-direction: column;
    gap: 1.5rem;
    align-items: stretch;
  }
  
  .header h1 {
    text-align: center;
  }
  
  .filters {
    padding: 1.25rem;
  }

  .filter-group {
    flex-direction: column;
    gap: 1rem;
  }
  
  .job-card {
    padding: 1.5rem;
  }

  .job-header {
    flex-direction: column;
    gap: 1rem; 
  }
  
  .job-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .job-info {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .job-skills {
    justify-content: flex-start;
  }
  
  .pagination {
    margin-top: 2rem;
    padding: 1rem;
    flex-wrap: wrap;
  }
}
</style>
