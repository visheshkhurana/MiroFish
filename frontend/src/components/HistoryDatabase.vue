<template>
  <div
    class="history-database"
    :class="{ 'no-projects': projects.length === 0 && !loading }"
    ref="historyContainer"
  >
    <div v-if="projects.length > 0 || loading" class="tech-grid-bg">
      <div class="grid-pattern"></div>
      <div class="gradient-overlay"></div>
    </div>
    <div class="section-header">
      <div class="section-line"></div>
      <span class="section-title">Prediction History</span>
      <div class="section-line"></div>
    </div>
    <div v-if="projects.length > 0" class="cards-container" :class="{ expanded: isExpanded }" :style="containerStyle">
      <div
        v-for="(project, index) in projects"
        :key="project.simulation_id"
        class="project-card"
        :class="{ 'status-completed': project.status === 'completed' }"
        :style="{ animationDelay: (index * 0.1) + 's' }"
        @click="openProject(project)"
      >
        <div class="card-header">
          <div class="card-id">
            <span class="id-prefix">#</span>
            <span>{{ project.simulation_id?.substring(0, 8) || 'N/A' }}</span>
          </div>
          <div class="card-status" :class="getStatusClass(project.status)">
            <span class="status-dot"></span>
            <span>{{ getStatusText(project.status) }}</span>
          </div>
        </div>
        <div class="card-body">
          <div class="card-requirement">{{ project.simulation_requirement || 'No description' }}</div>
        </div>
        <div class="card-footer">
          <div class="card-meta">
            <span class="meta-item">
              <span class="meta-icon">⏱</span>
              {{ formatDate(project.created_at) }}
            </span>
          </div>
          <div class="card-arrow">→</div>
        </div>
      </div>
    </div>
    <div v-if="projects.length > defaultVisibleCount" class="expand-toggle">
      <button @click="toggleExpand" class="expand-btn">
        <span>{{ isExpanded ? 'Show Less' : 'Show All (' + projects.length + ')' }}</span>
        <span class="expand-icon" :class="{ rotated: isExpanded }">▼</span>
      </button>
    </div>
    <div v-if="loading" class="loading-state">
      <div class="loading-dots"><span></span><span></span><span></span></div>
      <span class="loading-text">Loading prediction history...</span>
    </div>
    <div v-if="projects.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">◇</div>
      <span class="empty-text">No predictions yet</span>
      <span class="empty-sub">Upload a document above to start your first prediction</span>
    </div>
    <div v-if="selectedProject" class="modal-overlay" @click.self="closeDetail">
      <div class="modal-card">
        <div class="modal-header">
          <div class="modal-title-row">
            <span class="modal-label">Prediction Details</span>
            <span class="modal-id">#{{ selectedProject.simulation_id?.substring(0, 8) }}</span>
          </div>
          <button class="modal-close" @click="closeDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-label">Status</div>
            <div class="detail-value">
              <span class="status-badge" :class="getStatusClass(selectedProject.status)">
                <span class="status-dot"></span>
                {{ getStatusText(selectedProject.status) }}
              </span>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-label">Prediction Requirement</div>
            <div class="detail-value requirement-text">{{ selectedProject.simulation_requirement || 'None' }}</div>
          </div>
          <div class="detail-section">
            <div class="detail-label">Created</div>
            <div class="detail-value">{{ formatDate(selectedProject.created_at) }}</div>
          </div>
          <div class="detail-grid">
            <div class="detail-card">
              <div class="detail-card-value">{{ selectedProject.agent_count || '-' }}</div>
              <div class="detail-card-label">Agents</div>
            </div>
            <div class="detail-card">
              <div class="detail-card-value">{{ selectedProject.rounds || '-' }}</div>
              <div class="detail-card-label">Rounds</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="canContinue(selectedProject)" class="action-btn primary" @click="continueProject(selectedProject)">Continue Prediction <span class="btn-arrow">→</span></button>
          <button v-if="selectedProject.status === 'completed'" class="action-btn primary" @click="viewReport(selectedProject)">View Report <span class="btn-arrow">→</span></button>
          <button class="action-btn danger" @click="deleteProject(selectedProject)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects, deleteSimulation } from '../api/api.js'

const router = useRouter()
const projects = ref([])
const loading = ref(false)
const selectedProject = ref(null)
const isExpanded = ref(false)
const historyContainer = ref(null)
const defaultVisibleCount = 6

const containerStyle = computed(() => {
  if (!isExpanded.value && projects.value.length > defaultVisibleCount) {
    return { maxHeight: '520px', overflow: 'hidden' }
  }
  return {}
})

const formatDate = (dateStr) => {
  if (!dateStr) return 'Unknown'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const getStatusClass = (status) => {
  const map = { completed: 'status-completed', running: 'status-running', simulating: 'status-running', graph_building: 'status-building', ontology_generated: 'status-building', env_ready: 'status-building', report_generated: 'status-completed', failed: 'status-failed' }
  return map[status] || 'status-pending'
}

const getStatusText = (status) => {
  const map = { completed: 'Completed', running: 'Running', simulating: 'Simulating', graph_building: 'Building Graph', ontology_generated: 'Ontology Ready', env_ready: 'Env Ready', report_generated: 'Report Ready', failed: 'Failed' }
  return map[status] || status || 'Unknown'
}

const canContinue = (project) => {
  return project.status && project.status !== 'completed' && project.status !== 'failed'
}

const openProject = (project) => { selectedProject.value = project }
const closeDetail = () => { selectedProject.value = null }

const continueProject = (project) => {
  closeDetail()
  const routeName = getRouteForStatus(project.status)
  router.push({ name: routeName, params: { projectId: project.simulation_id } })
}

const viewReport = (project) => {
  closeDetail()
  router.push({ name: 'Report', params: { projectId: project.simulation_id } })
}

const getRouteForStatus = (status) => {
  const map = { ontology_generated: 'Process', graph_building: 'Process', env_ready: 'Simulation', simulating: 'SimulationRun', running: 'SimulationRun', report_generated: 'Report', completed: 'Report' }
  return map[status] || 'Process'
}

const deleteProject = async (project) => {
  if (!confirm('Are you sure you want to delete this prediction?')) return
  try {
    await deleteSimulation(project.simulation_id)
    projects.value = projects.value.filter(p => p.simulation_id !== project.simulation_id)
    closeDetail()
  } catch (err) {
    console.error('Failed to delete:', err)
    alert('Failed to delete prediction. Please try again.')
  }
}

const toggleExpand = () => { isExpanded.value = !isExpanded.value }

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await getProjects()
    if (res.success) { projects.value = res.data || [] }
  } catch (err) {
    console.error('Failed to load projects:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadProjects() })
</script>

<style scoped>
.history-database { position: relative; padding: 60px 40px; max-width: 1200px; margin: 0 auto; }
.history-database.no-projects { padding: 40px; }
.tech-grid-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; overflow: hidden; }
.grid-pattern { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: linear-gradient(rgba(60,131,246,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(60,131,246,0.03) 1px, transparent 1px); background-size: 40px 40px; }
.gradient-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(180deg, #121317 0%, transparent 15%, transparent 85%, #121317 100%); }
.section-header { display: flex; align-items: center; gap: 20px; margin-bottom: 40px; position: relative; z-index: 1; }
.section-line { flex: 1; height: 1px; background: #23272E; }
.section-title { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 600; color: #9CA3AF; letter-spacing: 2px; text-transform: uppercase; white-space: nowrap; }
.cards-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; position: relative; z-index: 1; transition: max-height 0.5s ease; }
.project-card { background: #16181D; border: 1px solid #23272E; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.25s ease; animation: fadeInUp 0.4s ease forwards; opacity: 0; }
.project-card:hover { border-color: rgba(60,131,246,0.3); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-id { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #6B7280; }
.id-prefix { color: #3C83F6; margin-right: 2px; }
.card-status { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 500; padding: 3px 8px; border-radius: 4px; background: rgba(107,114,128,0.1); color: #9CA3AF; }
.card-status.status-completed { background: rgba(16,185,129,0.1); color: #10B981; }
.card-status.status-running { background: rgba(60,131,246,0.1); color: #3C83F6; }
.card-status.status-building { background: rgba(139,92,246,0.1); color: #8B5CF6; }
.card-status.status-failed { background: rgba(239,68,68,0.1); color: #EF4444; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.card-status.status-running .status-dot { animation: pulse 1.5s infinite; }
@keyframes pulse { 50% { opacity: 0.4; } }
.card-body { margin-bottom: 14px; }
.card-requirement { font-size: 0.88rem; line-height: 1.5; color: #F3F4F6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.card-meta { display: flex; gap: 12px; }
.meta-item { font-size: 0.72rem; color: #6B7280; display: flex; align-items: center; gap: 4px; }
.card-arrow { color: #3C83F6; font-size: 1rem; opacity: 0; transition: opacity 0.2s, transform 0.2s; }
.project-card:hover .card-arrow { opacity: 1; transform: translateX(3px); }
.expand-toggle { text-align: center; margin-top: 24px; position: relative; z-index: 1; }
.expand-btn { background: transparent; border: 1px solid #23272E; color: #9CA3AF; padding: 8px 20px; font-size: 0.82rem; cursor: pointer; border-radius: 6px; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
.expand-btn:hover { border-color: #3C83F6; color: #3C83F6; }
.expand-icon { font-size: 0.6rem; transition: transform 0.3s; }
.expand-icon.rotated { transform: rotate(180deg); }
.loading-state { text-align: center; padding: 40px 0; position: relative; z-index: 1; }
.loading-dots { display: flex; justify-content: center; gap: 6px; margin-bottom: 12px; }
.loading-dots span { width: 6px; height: 6px; background: #3C83F6; border-radius: 50%; animation: loadingDot 1.2s infinite; }
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes loadingDot { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.2); } }
.loading-text { font-size: 0.82rem; color: #6B7280; }
.empty-state { text-align: center; padding: 40px 0; }
.empty-icon { font-size: 2rem; color: #23272E; margin-bottom: 12px; }
.empty-text { display: block; font-size: 0.92rem; color: #9CA3AF; margin-bottom: 6px; }
.empty-sub { display: block; font-size: 0.78rem; color: #6B7280; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-card { background: #16181D; border: 1px solid #23272E; border-radius: 12px; width: 90%; max-width: 520px; overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #23272E; }
.modal-title-row { display: flex; align-items: center; gap: 12px; }
.modal-label { font-weight: 600; font-size: 1rem; }
.modal-id { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #6B7280; }
.modal-close { background: none; border: none; color: #6B7280; font-size: 1.4rem; cursor: pointer; }
.modal-close:hover { color: #F3F4F6; }
.modal-body { padding: 24px; }
.detail-section { margin-bottom: 20px; }
.detail-label { font-size: 0.72rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.detail-value { font-size: 0.92rem; color: #F3F4F6; }
.requirement-text { line-height: 1.6; }
.status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 4px; font-size: 0.82rem; font-weight: 500; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
.detail-card { background: #1a1b21; border: 1px solid #23272E; border-radius: 8px; padding: 16px; text-align: center; }
.detail-card-value { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #F3F4F6; }
.detail-card-label { font-size: 0.72rem; color: #6B7280; margin-top: 4px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid #23272E; display: flex; gap: 10px; justify-content: flex-end; }
.action-btn { padding: 10px 20px; border: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s; }
.action-btn.primary { background: #3C83F6; color: #fff; }
.action-btn.primary:hover { background: #2563EB; }
.action-btn.danger { background: transparent; border: 1px solid #23272E; color: #EF4444; }
.action-btn.danger:hover { background: rgba(239,68,68,0.1); border-color: #EF4444; }
@media (max-width: 1024px) { .cards-container { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .history-database { padding: 40px 20px; } .cards-container { grid-template-columns: 1fr; } }
</style>
