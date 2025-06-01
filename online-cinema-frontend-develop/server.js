const express = require('express')
const cors = require('cors')
const { createProxyMiddleware } = require('http-proxy-middleware')

const app = express()

app.use(cors())

// Прокси для S3
app.use(
  '/s3',
  createProxyMiddleware({
    target:
      'https://mai-study-projects-online-cinema.s3.eu-north-1.amazonaws.com',
    changeOrigin: true,
    pathRewrite: {
      '^/s3': '',
    },
  })
)

const port = process.env.PORT || 3001
app.listen(port, () => {
  console.log(`Proxy server running on port ${port}`)
})
