<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-icon">&#9672;</span>
        PREDICT
      </div>
      <div class="nav-links">
        <span class="nav-tagline">by FounderConsole</span>
      </div>
    </nav>
    <div class="main-content">
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">Swarm Intelligence Prediction Engine</span>
            <span class="version-text">/ v0.1-preview</span>
          </div>
          <h1 class="main-title">See What Happens<br><span class="gradient-text">Before It Happens</span></h1>
          <p class="subtitle">Upload any report, article, or dataset. Our AI-powered swarm agents simulate thousands of possible futures - so you can make decisions with confidence, not guesswork.</p>
          <div class="feature-pills">
            <span class="pill">Multi-Agent Simulation</span>
            <span class="pill">Real-Time Predictions</span>
            <span class="pill">Visual Reports</span>
          </div>
        </div>
        <div class="hero-right">
          <div class="upload-console">
            <div class="console-header">
              <span class="console-dot red"></span>
              <span class="console-dot yellow"></span>
              <span class="console-dot green"></span>
              <span class="console-title">New Prediction</span>
            </div>
            <div class="console-body">
              <div class="upload-zone" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
                <input type="file" ref="fileInput" @change="handleFileSelect" style="display:none" accept=".txt,.pdf,.doc,.docx,.csv,.json,.xlsx,.xls,.md">
                <div class="upload-icon">&#8682;</div>
                <p class="upload-text">Drop your file here or click to browse</p>
                <p class="upload-hint">Supports PDF, TXT, DOC, CSV, JSON, Excel, Markdown</p>
              </div>
              <div v-if="selectedFile" class="file-info">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
              </div>
              <div class="prompt-section">
                <label class="prompt-label">What do you want to predict?</label>
                <textarea v-model="userPrompt" class="prompt-input" placeholder="e.g. How will this policy affect public sentiment over the next 6 months?" rows="3"></textarea>
              </div>
              <button class="start-btn" @click="startPrediction" :disabled="!selectedFile || !userPrompt"><span class="btn-icon">&#9654;</span> Start Prediction</button>
            </div>
          </div>
        </div>
      </section>
      <section class="how-section">
        <h2 class="section-title">How It Works</h2>
        <p class="section-subtitle">Five simple steps from upload to actionable insight</p>
        <div class="steps-grid">
          <div class="step-card"><div class="step-number">01</div><h3>Upload Your Content</h3><p>Drop in any document - a report, news article, dataset, or research paper.</p></div>
          <div class="step-card"><div class="step-number">02</div><h3>Build the Knowledge Graph</h3><p>Our AI extracts key entities, relationships, and context from your content automatically.</p></div>
          <div class="step-card"><div class="step-number">03</div><h3>Configure the Simulation</h3><p>Set the environment - choose agent count, rounds, and what you want to explore.</p></div>
          <div class="step-card"><div class="step-number">04</div><h3>Run the Prediction</h3><p>Thousands of AI agents debate, analyze, and simulate outcomes in real time.</p></div>
          <div class="step-card"><div class="step-number">05</div><h3>Get Your Report</h3><p>Receive a visual, interactive report with predictions, confidence scores, and key insights.</p></div>
        </div>
      </section>
      <section class="usecases-section">
        <h2 class="section-title">What Can You Predict?</h2>
        <div class="usecases-grid">
          <div class="usecase-card"><div class="usecase-icon">&#128200;</div><h3>Market Trends</h3><p>Forecast how markets, industries, or sectors will shift based on current signals and data.</p></div>
          <div class="usecase-card"><div class="usecase-icon">&#128483;</div><h3>Public Sentiment</h3><p>Predict how people will react to announcements, policies, or product launches.</p></div>
          <div class="usecase-card"><div class="usecase-icon">&#128240;</div><h3>News Impact</h3><p>Understand how breaking news or events will ripple through industries and communities.</p></div>
          <div class="usecase-card"><div class="usecase-icon">&#9878;</div><h3>Strategic Decisions</h3><p>Simulate the outcomes of business decisions before you commit to them.</p></div>
        </div>
      </section>
      <footer class="footer"><p>Powered by <strong>FounderConsole</strong> - AI Decision Intelligence for Founders</p></footer>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { uploadFile } from '../api/index'
export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const selectedFile = ref(null)
    const userPrompt = ref('')
    const fileInput = ref(null)
    const isUploading = ref(false)
    const triggerFileInput = () => { fileInput.value.click() }
    const handleFileSelect = (event) => { const file = event.target.files[0]; if (file) selectedFile.value = file }
    const handleDrop = (event) => { const file = event.dataTransfer.files[0]; if (file) selectedFile.value = file }
    const formatFileSize = (bytes) => { if (bytes < 1024) return bytes + ' B'; if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'; return (bytes / 1048576).toFixed(1) + ' MB' }
    const startPrediction = () => {
      if (!selectedFile.value || !userPrompt.value) return
      isUploading.value = true
      uploadFile(selectedFile.value, userPrompt.value).then(response => {
        if (response && response.project_id) router.push({ name: 'simulation', params: { projectId: response.project_id } })
      }).catch(error => { console.error('Upload failed:', error); alert('Upload failed. Please try again.') }).finally(() => { isUploading.value = false })
    }
    return { selectedFile, userPrompt, fileInput, isUploading, triggerFileInput, handleFileSelect, handleDrop, formatFileSize, startPrediction }
  }
}
</script>

<style scoped>
.home-container { min-height: 100vh; background-color: #121317; color: #F3F4F6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow-y: auto; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 40px; background: rgba(18, 19, 23, 0.8); backdrop-filter: blur(12px); border-bottom: 1px solid #23272E; position: sticky; top: 0; z-index: 100; }
.nav-brand { font-size: 20px; font-weight: 700; letter-spacing: 2px; background: linear-gradient(to right, #3C83F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 8px; }
.brand-icon { font-size: 24px; }
.nav-tagline { color: #9CA3AF; font-size: 14px; }
.main-content { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
.hero-section { display: flex; gap: 60px; align-items: center; padding: 80px 0 60px; }
.hero-left { flex: 1; }
.tag-row { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.orange-tag { background: rgba(60, 131, 246, 0.15); color: #3C83F6; padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; border: 1px solid rgba(60, 131, 246, 0.3); }
.version-text { color: #9CA3AF; font-size: 13px; }
.main-title { font-size: 48px; font-weight: 800; line-height: 1.15; margin-bottom: 24px; color: #F3F4F6; }
.gradient-text { background: linear-gradient(to right, #3C83F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { font-size: 17px; color: #9CA3AF; line-height: 1.7; margin-bottom: 28px; max-width: 480px; }
.feature-pills { display: flex; gap: 10px; flex-wrap: wrap; }
.pill { background: #16181D; border: 1px solid #23272E; color: #9CA3AF; padding: 6px 16px; border-radius: 20px; font-size: 13px; }
.hero-right { flex: 1; max-width: 480px; }
.upload-console { background: #16181D; border: 1px solid #23272E; border-radius: 16px; overflow: hidden; }
.console-header { display: flex; align-items: center; gap: 8px; padding: 14px 20px; background: rgba(35, 39, 46, 0.5); border-bottom: 1px solid #23272E; }
.console-dot { width: 12px; height: 12px; border-radius: 50%; }
.console-dot.red { background: #EF4444; }
.console-dot.yellow { background: #F59E0B; }
.console-dot.green { background: #10B981; }
.console-title { margin-left: 8px; font-size: 13px; color: #9CA3AF; font-weight: 500; }
.console-body { padding: 24px; }
.upload-zone { border: 2px dashed #23272E; border-radius: 12px; padding: 32px; text-align: center; cursor: pointer; transition: all 0.2s; }
.upload-zone:hover { border-color: #3C83F6; background: rgba(60, 131, 246, 0.05); }
.upload-icon { font-size: 36px; color: #3C83F6; margin-bottom: 12px; }
.upload-text { color: #F3F4F6; font-size: 15px; margin-bottom: 6px; }
.upload-hint { color: #9CA3AF; font-size: 12px; }
.file-info { display: flex; justify-content: space-between; align-items: center; background: rgba(60, 131, 246, 0.1); border: 1px solid rgba(60, 131, 246, 0.2); border-radius: 8px; padding: 10px 16px; margin-top: 12px; }
.file-name { color: #3C83F6; font-size: 14px; font-weight: 500; }
.file-size { color: #9CA3AF; font-size: 12px; }
.prompt-section { margin-top: 20px; }
.prompt-label { display: block; color: #F3F4F6; font-size: 14px; font-weight: 500; margin-bottom: 8px; }
.prompt-input { width: 100%; background: #121317; border: 1px solid #23272E; border-radius: 10px; padding: 12px 16px; color: #F3F4F6; font-size: 14px; resize: none; outline: none; transition: border-color 0.2s; font-family: inherit; box-sizing: border-box; }
.prompt-input:focus { border-color: #3C83F6; }
.prompt-input::placeholder { color: #6B7280; }
.start-btn { width: 100%; margin-top: 20px; padding: 14px; border: none; border-radius: 10px; background: linear-gradient(to right, #3C83F6, #8B5CF6); color: white; font-size: 15px; font-weight: 600; cursor: pointer; transition: opacity 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
.start-btn:hover { opacity: 0.9; }
.start-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-icon { font-size: 12px; }
.how-section { padding: 80px 0; border-top: 1px solid #23272E; }
.section-title { font-size: 32px; font-weight: 700; text-align: center; margin-bottom: 8px; color: #F3F4F6; }
.section-subtitle { text-align: center; color: #9CA3AF; font-size: 16px; margin-bottom: 48px; }
.steps-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }
.step-card { background: #16181D; border: 1px solid #23272E; border-radius: 14px; padding: 28px 20px; text-align: center; transition: border-color 0.2s; }
.step-card:hover { border-color: #3C83F6; }
.step-number { font-size: 28px; font-weight: 800; background: linear-gradient(to right, #3C83F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 14px; }
.step-card h3 { font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #F3F4F6; }
.step-card p { font-size: 13px; color: #9CA3AF; line-height: 1.6; }
.usecases-section { padding: 80px 0; border-top: 1px solid #23272E; }
.usecases-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 48px; }
.usecase-card { background: #16181D; border: 1px solid #23272E; border-radius: 14px; padding: 32px 24px; text-align: center; transition: border-color 0.2s; }
.usecase-card:hover { border-color: #8B5CF6; }
.usecase-icon { font-size: 36px; margin-bottom: 16px; }
.usecase-card h3 { font-size: 17px; font-weight: 600; margin-bottom: 10px; color: #F3F4F6; }
.usecase-card p { font-size: 14px; color: #9CA3AF; line-height: 1.6; }
.footer { padding: 40px 0; text-align: center; border-top: 1px solid #23272E; color: #9CA3AF; font-size: 14px; }
.footer strong { color: #F3F4F6; }
@media (max-width: 1024px) { .hero-section { flex-direction: column; padding: 40px 0; } .hero-right { max-width: 100%; width: 100%; } .steps-grid { grid-template-columns: repeat(3, 1fr); } .usecases-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .main-content { padding: 0 20px; } .navbar { padding: 14px 20px; } .main-title { font-size: 32px; } .steps-grid { grid-template-columns: 1fr; } .usecases-grid { grid-template-columns: 1fr; } }
</style>
