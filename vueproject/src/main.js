import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

const app = createApp(App)

// 注册路由对象
import router from './router'
app.use(router)

// axios 全局配置
import axios from 'axios'   // 导入axios包
axios.defaults.baseURL = 'http://localhost:8000/' // 服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json' // post请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json' // put请求发送json数据给服务器

// 请求拦截器
axios.interceptors.request.use(
    config => {
        // 获取token
        const token = localStorage.getItem('token')
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;//自动加载到请求头中
        }
        return config
    },
    err => {
        return Promise.reject(err)
    }
)

// 响应拦截器
axios.interceptors.response.use(
    response => {
        return response
    },
    err => {
        if (err.response && err.response.status === 401) {
            // 删除旧token 和 username
            localStorage.removeItem('token');
            sessionStorage.removeItem('username');
            router.push('/')
        }
        return Promise.reject(err)
    }
)

// 挂载axios，使用对象.$axios替代原生的axios（只挂载一次）
app.config.globalProperties.$axios = axios

// 通过导航守卫实现未登录拦截
router.beforeEach((to, from, next) => {
    // to：去哪里
    // from：从哪里来
    // next：是否放行处理
    if (to.meta.isLogin) {
        // 取出sessionStorage中的username
        let username = sessionStorage.getItem('username');
        // 判断是否有数据，有数据放行，没数据拦截
        if (username) {
            // 放行
            next();
        } else {
            // 拦截 --- 让它回到登录界面
            next('/');
        }
    } else {
        next(); // 放行
    }
})

// 注册Element-Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
app.use(ElementPlus)

app.mount('#app')
