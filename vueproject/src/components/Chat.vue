<template>
  <div class="chat-page">
    <!-- ===== 侧栏：历史会话 ===== -->
    <div class="sidebar" :class="{ open: sidebarOpen }">
      <el-button type="primary" class="new-btn" @click="newConversation">
        ＋ 新建对话
      </el-button>
      <el-input v-model="searchKeyword" placeholder="搜索历史"
                @input="handleSearchInput" clearable />
      <div class="history-list">
        <div v-for="(h, i) in filteredHistory" :key="i"
             class="history-item" :class="{ active: currentId.value === h.id }"
             @click="viewHistory(h)">
          <span class="h-title">{{ h.q }}</span>
          <el-icon class="del" @click.stop="deleteHistory(i)">
            <Delete />
          </el-icon>
        </div>
        <div v-if="!filteredHistory.length" class="empty">暂无历史</div>
      </div>
    </div>

    <!-- ===== 主聊天区 ===== -->
    <div class="main">
      <div class="topbar">
        <span>💬 AI 职业咨询</span>
        <el-button link @click="logout">退出登录</el-button>
      </div>
      <div class="messages" ref="msgBox">
        <div v-if="!messages.length" class="welcome">
          <h3>你好，我是你的职业规划助手 🧭</h3>
          <p>问我任何行业趋势、薪资水平、学习路线的问题</p>
        </div>
        <div v-for="(m, i) in messages" :key="i"
             :class="['msg', m.role === 'user' ? 'user' : 'ai']">
          <div class="bubble">{{ m.content }}</div>
        </div>
      </div>
      <div class="input-bar">
        <el-input v-model="question" placeholder="问我任何职业相关的问题..."
                  @keyup.enter="chat" :disabled="generating" />
        <el-button type="primary" :loading="generating" @click="chat">发送</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { getCurrentInstance } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'

const proxy = getCurrentInstance().proxy
const router = useRouter()
const msgBox = ref(null)

const messages = ref([])
const question = ref('')
const generating = ref(false)
const sidebarOpen = ref(true)
const searchKeyword = ref('')

// ===== 会话与历史（localStorage 版）=====
const sessionId = ref(`chat_${Date.now()}`)     // 当前会话id（记忆thread_id）
const history = ref([])                          // [{id, q, a, time}]
const currentId = ref(null)

const filteredHistory = computed(() => {
  if (!searchKeyword.value) return history.value
  return history.value.filter(h => h.q.includes(searchKeyword.value))
})

// ===== 新建对话 =====
function newConversation() {
  sessionId.value = `chat_${Date.now()}`         // 新会话=新记忆thread
  messages.value = []
  currentId.value = null
}

// ===== 查看历史（回显+接回记忆线）=====
function viewHistory(h) {
  currentId.value = h.id
  sessionId.value = h.sessionId                  // ★ 接回当时的记忆thread
  messages.value = [
    {role: 'user', content: h.q},
    {role: 'assistant', content: h.a},
  ]
}

// ===== 删除历史 =====
function deleteHistory(i) {
  history.value.splice(i, 1)
  localStorage.setItem('chat_history', JSON.stringify(history.value))
  if (currentId.value !== null) newConversation()
}

// ===== 搜索 =====
function handleSearchInput() { /* computed 自动过滤，无需处理 */
}

// ===== 聊天（fetchEventSource 流式）=====
function chat() {
  const myquestion = question.value.trim()
  question.value = ''
  if (!myquestion) return ElMessage.warning('输入内容不能为空')

  messages.value.push({role: 'user', content: myquestion})
  messages.value.push({role: 'assistant', content: 'AI正在思考...'})
  generating.value = true

  const params = new URLSearchParams({
    question: myquestion,
    sessionId: sessionId.value,        // ★ 记忆thread_id（多轮上下文）
  })
  let s = ''
  const token = localStorage.getItem('token')
  const ctrl = new AbortController()

  fetchEventSource('chat?' + params.toString(), {
    method: 'GET',
    headers: {Authorization: `Bearer ${token}`},
    signal: ctrl.signal,
    openWhenHidden: true,
    onmessage(e) {
      const obj = JSON.parse(e.data)
      if (obj.error) {
        messages.value[messages.value.length - 1].content = `[出错] ${obj.error}`
        generating.value = false
        ctrl.abort()
        return
      }
      if (obj.done) {
        ctrl.abort()
        generating.value = false
        saveConversation(myquestion, s)
        return
      }
      if (obj.delta) {
        s += obj.delta
        messages.value[messages.value.length - 1].content = s   // ★ 打字机
        scrollBottom()
      }
    },
    onerror(err) {
      console.log('SSE错误，停止重试')
      generating.value = false
      ctrl.abort()
      throw new Error('STOP_RETRY')
    },
    onclose() {
      generating.value = false
      ctrl.abort()
      throw new Error('STOP_RETRY')
    },
  })
}

// ===== 保存到 localStorage =====
function saveConversation(q, a) {
  const id = Date.now()
  currentId.value = id
  history.value.unshift({
    id, q, a, time: new Date().toLocaleString(),
    sessionId: sessionId.value
  })
  localStorage.setItem('chat_history', JSON.stringify(history.value.slice(0, 30)))
}

// ===== 退出登录 =====
function logout() {
  localStorage.removeItem('token')
  sessionStorage.removeItem('username')
  proxy.$router.push('/')
}

const scrollBottom = () => nextTick(() => {
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
})

onMounted(() => {
  const saved = localStorage.getItem('chat_history')
  if (saved) history.value = JSON.parse(saved)
})
</script>

<style scoped>
.chat-page {
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: #f7f8fa;
  border-right: 1px solid #e4e7ed;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.new-btn {
  width: 100%;
}

.history-list {
  flex: 1;
  overflow-y: auto;
}

.history-item {
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #303133;
}

.history-item:hover {
  background: #f0f2f5;
}

.history-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.h-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.del {
  color: #c0c4cc;
}

.del:hover {
  color: #f56c6c;
}

.empty {
  color: #c0c4cc;
  font-size: 12px;
  text-align: center;
  padding: 20px 0;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.topbar {
  padding: 12px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  color: #303133;
  font-weight: bold;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome {
  text-align: center;
  color: #909399;
  margin-top: 60px;
}

.msg {
  display: flex;
  margin: 10px 0;
}

.msg.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 10px;
  line-height: 1.7;
  white-space: pre-wrap;
  font-size: 14px;
}

.msg.user .bubble {
  background: #409eff;
  color: #fff;
}

.msg.ai .bubble {
  background: #f4f4f5;
  color: #303133;
}

.input-bar {
  padding: 14px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
}
</style>