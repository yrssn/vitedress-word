import { defineConfig } from 'vitepress'

export default defineConfig({
  "title": "文档中心",
  "description": "企业文档管理系统",
  "themeConfig": {
    "nav": [
      {
        "text": "进销存系统",
        "link": "/inventory/"
      }
    ],
    "sidebar": {
      "/inventory/": [
        {
          "text": "日联部",
          "collapsed": false,
          "items": [
            {
              "text": "担当待办",
              "link": "/inventory/ed531ecc/担当待办"
            },
            {
              "text": "订单池-担当",
              "link": "/inventory/ed531ecc/订单池-担当"
            },
            {
              "text": "订单池-负责人",
              "link": "/inventory/ed531ecc/订单池-负责人"
            }
          ]
        },
        {
          "text": "平台注册部",
          "collapsed": false,
          "items": [
            {
              "text": "注册表",
              "link": "/inventory/53e6b27d/注册表"
            },
            {
              "text": "订单池",
              "link": "/inventory/53e6b27d/订单池"
            }
          ]
        }
      ]
    },
    "socialLinks": [],
    "search": {
      "provider": "local"
    }
  }
})
