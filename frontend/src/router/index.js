import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/doc-types',
    name: 'DocTypes',
    component: () => import('../views/DocTypes.vue')
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue')
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('../views/Documents.vue')
  },
  {
    path: '/documents/edit/:id?',
    name: 'DocumentEdit',
    component: () => import('../views/DocumentEdit.vue')
  },
  {
    path: '/generate',
    name: 'Generate',
    component: () => import('../views/Generate.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
