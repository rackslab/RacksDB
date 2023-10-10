import type { App, Plugin } from 'vue'
import { inject } from 'vue'

export interface RuntimeConfiguration {
    api_server: string
}

const injectionKey = Symbol('rc')

export const runtimeConfiguration: Plugin = {
    install: (app: App, configuration: RuntimeConfiguration) => {
        app.provide(injectionKey, configuration)
        app.config.globalProperties.$rc = configuration
    }
}

export const initRuntimeConfiguration = async (): Promise<RuntimeConfiguration> => {
    const resp = await fetch('config.json')
    const value = await resp.json()

    return {
        api_server: value.API_SERVER
    } as RuntimeConfiguration
}

export const loadRuntimeConfiguration = () => inject(injectionKey) as RuntimeConfiguration