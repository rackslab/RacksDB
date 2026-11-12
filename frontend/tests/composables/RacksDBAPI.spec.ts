/*
Copyright (c) 2026 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi } from 'vitest'
import type { AxiosInstance } from 'axios'

import { useRacksDBAPI } from '@/composables/RacksDBAPI'

describe('infrastructureGlb', () => {
  test('requests glb format as array buffer', async () => {
    const data = new ArrayBuffer(8)
    const post = vi.fn().mockResolvedValue({ data })
    const api = useRacksDBAPI({ post } as unknown as AxiosInstance)
    expect(await api.infrastructureGlb('mercury')).toBe(data)
    expect(post).toHaveBeenCalledWith('/draw/infrastructure/mercury.glb', undefined, {
      responseType: 'arraybuffer'
    })
  })

  test('throws on error', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const post = vi.fn().mockRejectedValue(new Error('fail'))
    const api = useRacksDBAPI({ post } as unknown as AxiosInstance)
    await expect(api.infrastructureGlb('mercury')).rejects.toThrow('fail')
  })
})
