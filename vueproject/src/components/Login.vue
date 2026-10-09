<template>
  <div class="login-container">
    <div class="login-card">
      <div class="form-header">
        <!-- 运动风闪电图标 -->
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>
        <h2 class="form-title">登 录</h2>
      </div>

      <!-- 密码登录 -->
      <form v-show="isShow" class="login-form" @submit.prevent>
        <div class="form-item">
          <label>邮箱</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
            <input type="text" v-model="email" placeholder="请输入邮箱" @keyup.enter="login">
          </div>
        </div>

        <div class="form-item">
          <label>密码</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <input type="password" v-model="password" placeholder="请输入密码" @keyup.enter="login">
          </div>
        </div>

        <button type="button" class="submit-btn" @click="login">登 录</button>
        <div class="switch-mode" @click="change">使用验证码登录</div>
      </form>

      <!-- 验证码登录 -->
      <form v-show="!isShow" class="login-form" @submit.prevent>
        <div class="form-item">
          <label>邮箱</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
            <input type="text" v-model="email" placeholder="请输入邮箱" @keyup.enter="checkcode">
          </div>
        </div>

        <div class="form-item">
          <label>验证码</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <input type="password" v-model="code" placeholder="请输入验证码" @keyup.enter="checkcode">
          </div>
        </div>

        <div class="btn-group">
          <button type="button" class="submit-btn btn-outline" @click="sendcode">发送验证码</button>
          <button type="button" class="submit-btn" @click="checkcode">验 证</button>
        </div>
        <div class="switch-mode" @click="change">使用密码登录</div>
      </form>

      <!-- 注册跳转 (改为点击事件) -->
      <div class="footer-text">
        还没有账号？<span class="register-link" @click="goToRegister">去注册</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";

const router = useRouter();
const proxy = getCurrentInstance().proxy;
let email = ref("")
let password = ref("")
let isShow = ref(true)
let code = ref("")

function change() {
  isShow.value = !isShow.value
}

// 跳转注册逻辑
function goToRegister() {
  router.push('/register');
}

//密码登录
function login() {
  proxy.$axios({
    url: "/users/login",
    method: "post",
    data: {
      email: email.value,
      password: password.value,
    }
  }).then(res => {
    if (res.data.code == 200) {
      ElMessage.success("登录成功")
      sessionStorage.setItem("username", res.data.data.username); // 缓存用户名
      // 存到本地存储里，刷新页面也不会丢
      localStorage.setItem('token', res.data.data.access_token);
      setTimeout(() => {
        router.push('/Chat');
      }, 1000);
    } else {
      ElMessage.error(res.data.msg)
    }
  }).catch(err => {
    //网络异常捕获
    console.log("请求报错了：", err);
    ElMessage.error("网络请求失败，请检查后端服务是否启动！");
  });
}

//验证码登录
//发送验证码
function sendcode() {
  if (!email.value) {
    ElMessage.info("账号不能为空");
    return; // 阻止继续发请求
  }
  proxy.$axios({
    url: "/users/sendcode",
    method: "get",
    params: {
      email: email.value
    }
  }).then(res => {
    if (res.data.code == 200) {
      ElMessage.success("已发送验证码");
    } else {
      ElMessage.error(res.data.msg);
    }
  }).catch(err => {
    console.log("请求报错了：", err);
    alert("网络请求失败，请检查后端服务是否启动！");
  })
}

//验证验证码
function checkcode() {
  if (!code.value) {
    ElMessage.info("验证码不能为空");
    return; // 阻止继续发请求
  }
  proxy.$axios({
    url: "/users/checkcode",
    method: "get",
    params: {
      email: email.value,
      code: code.value
    }
  }).then(res => {
    if (res.data.code == 200) {
      ElMessage.success("登录成功");
      sessionStorage.setItem("username", res.data.data.username); // 缓存用户名
      localStorage.setItem('token', res.data.data.access_token);
      setTimeout(() => {
        router.push('/Chat');
      }, 1000);
    } else {
      ElMessage.error("验证失败");
    }
  }).catch(err => {
    // 网络异常捕获
    console.log("请求报错了：", err);
    ElMessage.error("网络请求失败，请检查后端服务是否启动！");
  });
}
</script>

<style scoped>
/* CSS 变量：运动风配色 */
:root {
  --sport-blue: #0052D4; /* 动感深蓝 */
  --sport-blue-light: #4364F7; /* 亮蓝 */
  --neon-green: #CCFF00; /* 荧光绿（核心活力色） */
  --text-dark: #1E293B; /* 深灰蓝替代纯黑 */
  --text-gray: #64748B; /* 次要文字 */
  --bg-base: #F0F4F8; /* 冰灰白背景 */
  --surface: #FFFFFF; /* 卡片白 */
  --border-color: #E2E8F0; /* 浅灰边框 */
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--bg-base);
  padding: 20px;
  box-sizing: border-box;
}

.login-card {
  background: var(--surface);
  padding: 45px 40px;
  border-radius: 24px;
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
  box-shadow: 0 10px 30px rgba(0, 82, 212, 0.08);
}

/* 顶部图标与标题 */
.form-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: var(--neon-green);
  color: var(--text-dark);
  padding: 16px;
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(204, 255, 0, 0.4);
  transform: rotate(-5deg);
  margin-bottom: 16px;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.form-title {
  color: var(--text-dark);
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 3px;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 22px;
}

.form-item label {
  margin-bottom: 8px;
  color: var(--text-gray);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  width: 18px;
  height: 18px;
  color: #94A3B8;
  pointer-events: none;
  transition: color 0.2s;
}

.form-item input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  background-color: #F8FAFC;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 14px;
  color: var(--text-dark);
  transition: all 0.2s ease-in-out;
  box-sizing: border-box;
  outline: none;
}

.form-item input::placeholder {
  color: #94A3B8;
}

.form-item input:focus {
  background-color: var(--surface);
  border-color: var(--sport-blue);
  box-shadow: 0 0 0 3px rgba(0, 82, 212, 0.1);
}

.input-wrapper:focus-within .input-icon {
  color: var(--sport-blue);
}

/* 按钮组样式 (发送验证码 / 验证) */
.btn-group {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.submit-btn {
  flex: 1;
  padding: 14px;
  background: var(--neon-green);
  color: var(--text-dark);
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-top: 10px;
  box-shadow: 0 4px 15px rgba(204, 255, 0, 0.4);
}

/* 验证码页面第一个按钮改为深蓝线框风格 */
.btn-outline {
  background: var(--surface);
  color: var(--sport-blue);
  border: 1px solid var(--sport-blue);
  box-shadow: none;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 20px rgba(204, 255, 0, 0.5);
}

.btn-outline:hover {
  background: #EFF6FF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 82, 212, 0.15);
}

/* 切换登录方式文本 */
.switch-mode {
  text-align: center;
  margin-top: 22px;
  font-size: 14px;
  color: var(--sport-blue);
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.switch-mode:hover {
  color: var(--sport-blue-light);
}

/* 底部注册跳转 */
.footer-text {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
  text-align: center;
  font-size: 14px;
  color: var(--text-gray);
  font-weight: 500;
}

.register-link {
  color: var(--sport-blue);
  font-weight: 700;
  text-decoration: none;
  margin-left: 6px;
  border-bottom: 2px solid var(--sport-blue);
  padding-bottom: 2px;
  transition: all 0.2s;
  cursor: pointer;
}

.register-link:hover {
  color: var(--sport-blue-light);
  border-color: var(--sport-blue-light);
}
</style>