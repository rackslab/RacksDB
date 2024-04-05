/*Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later */

import type { App, Plugin } from 'vue'
import { inject } from 'vue'
import axios from 'axios'
import type { AxiosInstance } from 'axios'

const injectionKey = Symbol('http')

export const useHttp = () => inject(injectionKey) as AxiosInstance

export const httpPlugin: Plugin = {
  install(app: App) {
    const http = axios.create({
      baseURL: `${app.config.globalProperties.$rc.api_server}${app.config.globalProperties.$rc.api_version}`
    })
    app.provide(injectionKey, http)
  }
}
