/*
Copyright (c) 2026 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect } from 'vitest'
import { BoxGeometry, Group, Mesh, Object3D, Vector3 } from 'three'
import type { GLTF } from 'three/examples/jsm/loaders/GLTFLoader.js'

import {
  cameraAzimuth,
  cameraPosition,
  computeFocus,
  createTransition,
  easeInOutCubic,
  findEquipment,
  originalName,
  stepTransition
} from '@/lib/scene3d'

function box(width: number, height: number, depth: number): Mesh {
  return new Mesh(new BoxGeometry(width, height, depth))
}

describe('findEquipment', () => {
  test('returns equipment ancestor', () => {
    const rack = new Group()
    rack.userData = { category: 'rack' }
    const equipment = new Group()
    equipment.userData = { category: 'node', type: 'sm220bt' }
    const body = box(1, 1, 1)
    body.userData = { part: 'body' }
    rack.add(equipment)
    equipment.add(body)
    expect(findEquipment(body)).toBe(equipment)
    expect(findEquipment(equipment)).toBe(equipment)
  })

  test('returns null outside equipment', () => {
    const rack = new Group()
    rack.userData = { category: 'rack' }
    const panel = box(1, 1, 1)
    rack.add(panel)
    expect(findEquipment(panel)).toBeNull()
    expect(findEquipment(null)).toBeNull()
  })
})

describe('computeFocus', () => {
  test('focuses on racks', () => {
    const root = new Group()
    // Large floor must be ignored
    root.add(box(100, 0.1, 100))
    for (const x of [0, 2]) {
      const rack = new Group()
      rack.userData = { category: 'rack' }
      rack.position.set(x, 1, 0)
      rack.add(box(1, 2, 1))
      root.add(rack)
    }
    const focus = computeFocus(root)
    expect(focus.center.toArray()).toEqual([1, 1, 0])
    expect(focus.size.toArray()).toEqual([3, 2, 1])
    expect(focus.radius).toBeCloseTo(Math.sqrt(14) / 2)
  })

  test('falls back on whole scene without racks', () => {
    const root = new Group()
    root.add(box(4, 2, 2))
    const focus = computeFocus(root)
    expect(focus.center.toArray()).toEqual([0, 0, 0])
    expect(focus.size.toArray()).toEqual([4, 2, 2])
  })
})

describe('cameraPosition', () => {
  test('is in front and above focus', () => {
    const root = new Group()
    root.add(box(2, 2, 2))
    const focus = computeFocus(root)
    const position = cameraPosition(focus)
    expect(position.x).toBeCloseTo(0)
    expect(position.y).toBeGreaterThan(focus.center.y)
    expect(position.z).toBeGreaterThan(focus.center.z)
    // Distance increases with focus radius
    focus.radius *= 2
    expect(cameraPosition(focus).z).toBeGreaterThan(position.z)
  })
})

describe('cameraPosition azimuth', () => {
  test('rotates camera around focus vertical axis', () => {
    const root = new Group()
    root.add(box(2, 2, 2))
    const focus = computeFocus(root)
    const front = cameraPosition(focus)
    const side = cameraPosition(focus, undefined, Math.PI / 2)
    // Camera on the +X side, at the same height and distance from focus center
    expect(side.x).toBeCloseTo(front.z - focus.center.z)
    expect(side.y).toBeCloseTo(front.y)
    expect(side.z).toBeCloseTo(focus.center.z)
    expect(side.distanceTo(focus.center)).toBeCloseTo(front.distanceTo(focus.center))
  })
})

describe('cameraAzimuth', () => {
  test('returns azimuth of camera position', () => {
    const root = new Group()
    root.add(box(2, 2, 2))
    root.position.set(3, 0, -1)
    const focus = computeFocus(root)
    for (const azimuth of [0, Math.PI / 3, -2, 3]) {
      expect(cameraAzimuth(cameraPosition(focus, undefined, azimuth), focus)).toBeCloseTo(azimuth)
    }
  })
})

describe('easeInOutCubic', () => {
  test('eases from 0 to 1', () => {
    expect(easeInOutCubic(0)).toBe(0)
    expect(easeInOutCubic(0.5)).toBeCloseTo(0.5)
    expect(easeInOutCubic(1)).toBe(1)
    // Slow start and slow end
    expect(easeInOutCubic(0.1)).toBeLessThan(0.1)
    expect(easeInOutCubic(0.9)).toBeGreaterThan(0.9)
  })
})

describe('stepTransition', () => {
  test('moves camera position and target with easing', () => {
    const transition = createTransition(
      new Vector3(0, 0, 0),
      new Vector3(10, 0, 0),
      new Vector3(0, 0, 0),
      new Vector3(0, 4, 0),
      1
    )
    const position = new Vector3()
    const target = new Vector3()
    expect(stepTransition(transition, 0.25, position, target)).toBe(false)
    expect(position.x).toBeCloseTo(10 * easeInOutCubic(0.25))
    expect(target.y).toBeCloseTo(4 * easeInOutCubic(0.25))
    expect(stepTransition(transition, 0.25, position, target)).toBe(false)
    expect(position.x).toBeCloseTo(5)
    // Overshooting delta ends exactly on destination
    expect(stepTransition(transition, 2, position, target)).toBe(true)
    expect(position.toArray()).toEqual([10, 0, 0])
    expect(target.toArray()).toEqual([0, 4, 0])
  })

  test('ends immediately without duration', () => {
    const transition = createTransition(
      new Vector3(),
      new Vector3(1, 2, 3),
      new Vector3(),
      new Vector3(),
      0
    )
    const position = new Vector3()
    expect(stepTransition(transition, 0, position, new Vector3())).toBe(true)
    expect(position.toArray()).toEqual([1, 2, 3])
  })

  test('does not modify transition source vectors', () => {
    const from = new Vector3(1, 1, 1)
    const transition = createTransition(from, new Vector3(), new Vector3(), new Vector3(), 1)
    stepTransition(transition, 0.5, from, new Vector3())
    expect(transition.fromPosition.toArray()).toEqual([1, 1, 1])
  })
})

describe('originalName', () => {
  test('returns glTF node name', () => {
    const object = new Object3D()
    object.name = 'rack1' // sanitized by three.js
    const gltf = {
      parser: {
        associations: new Map([[object, { nodes: 1 }]]),
        json: { nodes: [{ name: 'room' }, { name: 'rack.1' }] }
      }
    } as unknown as GLTF
    expect(originalName(gltf, object)).toBe('rack.1')
  })

  test('falls back on object name', () => {
    const object = new Object3D()
    object.name = 'rack1'
    const gltf = {
      parser: { associations: new Map(), json: { nodes: [] } }
    } as unknown as GLTF
    expect(originalName(gltf, object)).toBe('rack1')
  })
})
