//引入路由
import {createRouter, createWebHistory} from "vue-router";

const routes=[
    {
        path: "/Register",
        component: () => import('../components/Register.vue')
    },
    {
        path: "/",

        component: () => import('../components/Login.vue')
    },
     {
         path: "/Chat",
         meta:{
                isLogin:true,//isLogin自定义属性，false表示未登录直接访问
            },
        component: () => import('../components/Chat.vue')
    },

]

const router =createRouter({
        history:createWebHistory(),
        routes
})
export  default  router