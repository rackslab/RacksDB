import './index.css'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { initRuntimeConfiguration, runtimeConfiguration } from './plugins/runtimeConfiguration'
import { httpPlugin } from './plugins/http'

const app = createApp(App)
app.use(router)
app.use(runtimeConfiguration, await initRuntimeConfiguration())
app.use(httpPlugin)
app.mount('#app')
