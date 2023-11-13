import type { App, InjectionKey, Plugin } from 'vue'
import { inject } from 'vue'

export interface RuntimeConfiguration {
  api_server: string
}

export const injectionKey = Symbol('rc') as InjectionKey<RuntimeConfiguration>

export const runtimeConfiguration: Plugin = {
  install: (app: App, configuration: RuntimeConfiguration) => {
    app.provide(injectionKey, configuration)
    app.config.globalProperties.$rc = configuration
  }
}

export const initRuntimeConfiguration = async (): Promise<RuntimeConfiguration> => {
  const resp = await fetch('/config.json')
  const value = await resp.json()

  return {
    api_server: value.API_SERVER
  } as RuntimeConfiguration
}

export const loadRuntimeConfiguration = () => inject(injectionKey) as RuntimeConfiguration
