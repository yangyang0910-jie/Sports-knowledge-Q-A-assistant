<template>
  <div class="register-container">
    <form class="register-card" @submit.prevent>
      <div class="form-header">
        <!-- 运动风闪电图标 -->
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>
        <h2 class="form-title">用户注册</h2>
      </div>

      <div class="form-item">
        <label>用户名</label>
        <div class="input-wrapper">
          <!-- 用户图标 -->
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <input type="text" v-model="username" placeholder="请输入用户名" @keyup.enter="register">
        </div>
      </div>

      <div class="form-item">
        <label>邮箱</label>
        <div class="input-wrapper">
          <!-- 邮箱图标 -->
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>
          <input type="text" v-model="email" placeholder="请输入邮箱" @keyup.enter="register">
        </div>
      </div>

      <div class="form-item">
        <label>密码</label>
        <div class="input-wrapper">
          <!-- 锁图标 -->
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <input type="password" v-model="password" placeholder="请输入密码" @keyup.enter="register">
        </div>
      </div>

      <button type="button" @click="register" class="submit-btn">立 即 注 册</button>

      <!-- 底部跳转登录 -->
      <div class="footer-text">
        已有账号？<span class="login-link" @click="goToLogin">去登录</span>
      </div>
    </form>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance} from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from 'element-plus';
// 初始化路由和全局代理
const router = useRouter();
const proxy = getCurrentInstance().proxy;
let isChange =ref(false);//不能加''那是字符串不是bool值
let email =ref("");
let password=ref("");
let username=ref("");
//跳转到登录页面的方法
function goToLogin(){
  router.push('/');
}
function register(){
  //判断是否为空
  if (!email.value || !password.value || !username.value) {
    ElMessage.info("账号或密码用户名不能为空");
    return; // 阻止继续发请求
  }
  try {
    proxy.$axios({
      url: "/users/register",
      method: "post",
      data: {
        email: email.value,
        password: password.value,
        username: username.value,
      }
    }).then(res => {
      if (res.data.code == 201) {
        ElMessage.info("用户已存在");
      }
      if (res.data.code == 200) {
        ElMessage.success("注册成功");
        setTimeout(() => {
          router.push('/');
        }, 1000);
      } else {
        ElMessage.error(res.data.msg);
      }
    })
  } catch (error) {
    // 捕获网络错误或 422/500 等错误
    console.error("请求失败:", error);
    ElMessage.error("网络请求失败，请检查接口或控制台报错");
  }
}
</script>

<style scoped>
/* CSS 变量：运动风配色 */
:root {
  --sport-blue: #0052D4;       /* 动感深蓝 */
  --sport-blue-light: #4364F7; /* 亮蓝 */
  --neon-green: #CCFF00;       /* 荧光绿（核心活力色） */
  --text-dark: #1E293B;        /* 深灰蓝替代纯黑 */
  --text-gray: #64748B;        /* 次要文字 */
  --bg-base: #F0F4F8;          /* 冰灰白背景 */
  --surface: #FFFFFF;          /* 卡片白 */
  --border-color: #E2E8F0;     /* 浅灰边框 */
}

/* 整体背景 - 清爽的浅灰白 */
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--bg-base);
  padding: 20px;
  box-sizing: border-box;
}

/* 卡片样式 - 大圆角与柔和阴影 */
.register-card {
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
  letter-spacing: 1px;
}

/* 表单项 */
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

/* 包装器用于定位图标 */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

/* SVG 图标样式 */
.input-icon {
  position: absolute;
  left: 16px;
  width: 18px;
  height: 18px;
  color: #94A3B8;
  pointer-events: none; /* 防止图标遮挡输入框点击 */
  transition: color 0.2s;
}

/* 输入框 - 圆角增大，聚焦时蓝色光晕 */
.form-item input {
  width: 100%;
  padding: 14px 16px 14px 44px; /* 左侧留出图标位置 */
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

/* 聚焦状态：背景变白，边框变蓝，图标变蓝 */
.form-item input:focus {
  background-color: var(--surface);
  border-color: var(--sport-blue);
  box-shadow: 0 0 0 3px rgba(0, 82, 212, 0.1);
}

.input-wrapper:focus-within .input-icon {
  color: var(--sport-blue);
}

/* 按钮 - 荧光绿底黑字，极具运动冲击力 */
.submit-btn {
  width: 100%;
  padding: 15px;
  background: var(--neon-green);
  color: var(--text-dark);
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 3px; /* 按钮文字拉开间距 */
  cursor: pointer;
  transition: all 0.25s ease;
  margin-top: 10px;
  box-shadow: 0 4px 15px rgba(204, 255, 0, 0.4);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 20px rgba(204, 255, 0, 0.5);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 底部跳转样式 */
.footer-text {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
  text-align: center;
  font-size: 14px;
  color: var(--text-gray);
  font-weight: 500;
}

.login-link {
  color: var(--sport-blue);
  font-weight: 700;
  text-decoration: none;
  margin-left: 6px;
  border-bottom: 2px solid var(--sport-blue);
  padding-bottom: 2px;
  transition: all 0.2s;
  cursor: pointer;
}

.login-link:hover {
  color: var(--sport-blue-light);
  border-color: var(--sport-blue-light);
}
</style>