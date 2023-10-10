import type { App, Plugin } from 'vue'
import type { AxiosInstance } from 'axios'
import { inject } from 'vue'
import axios from 'axios'

const injectionKey = Symbol('http')

export const useHttp = () => inject(injectionKey) as AxiosInstance

export const httpPlugin: Plugin = {
    install(app: App) {
        const http = axios.create({
            baseURL: app.config.globalProperties.$rc.api_server
        })
        app.provide(injectionKey, http)
    }
}