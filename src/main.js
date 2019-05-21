import Vue from 'vue'
import VueRouter from 'vue-router'
import VueResource from 'vue-resource'
import store from './store'

import App from './App'
import 'bootstrap/dist/css/bootstrap.css'
import 'font-awesome/css/font-awesome.css'
import Home from './components/Home'
import Search from './components/Search'
import Articles from './components/Articles'
import Article from './components/Article'

Vue.use(VueRouter)
Vue.use(VueResource)

const routes = [{
    path: '/',
    component: Home,
    // beforeEnter: (to, from, next) => {
    //     // ...
    // }
},{
    path: '/articles',
    // redirect: '/',
    component: Articles
},{
    path: '/article/:id',
    name: 'article',
    // redirect: '/',
    component: Article
},{
	path: '/home',
    // redirect: '/',
    component: Home
},{
    path: '/search',
    // redirect: '/',
    component: Search
}]

const router = new VueRouter( {
    routes
})

/* eslint-disable no-new */
new Vue({
    // el: '#app',
    router,
    store,
    ...App
}).$mount('#app')

