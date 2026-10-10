/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect } from 'vitest'
import {
  BoxGeometry,
  Mesh,
  MeshBasicMaterial,
  Object3D,
  PerspectiveCamera,
  Vector3
} from 'three'
import {
  clampTurntableRadius,
  computeRackFocusBox,
  createTurntableEntryTransition,
  defaultTurntableHeight,
  defaultTurntableRadius,
  stepCameraTransition,
  turntableCameraPosition
} from '@/lib/infrastructureScene3d'

describe('infrastructureScene3d helpers', () => {
  test('computeRackFocusBox uses rack nodes only', () => {
    const root = new Object3D()
    const room = new Object3D()
    room.userData = { category: 'room' }
    room.position.set(0, 0, 0)
    root.add(room)

    const rack = new Object3D()
    rack.userData = { category: 'rack' }
    rack.position.set(10, 0, 0)
    const mesh = new Mesh(new BoxGeometry(0.6, 2, 1), new MeshBasicMaterial())
    mesh.position.set(0.3, 1, 0.5)
    rack.add(mesh)
    root.add(rack)

    const focus = computeRackFocusBox(root)
    expect(focus.center.x).toBeGreaterThan(9)
    expect(focus.radius).toBeLessThan(5)
  })

  test('defaultTurntableRadius is clamped to max distance', () => {
    const focus = {
      center: new Vector3(),
      size: new Vector3(2, 2, 2),
      radius: 4
    }
    expect(defaultTurntableRadius(focus, 6)).toBe(6)
    expect(defaultTurntableHeight(focus)).toBeCloseTo(0.7)
  })

  test('clampTurntableRadius respects bounds', () => {
    expect(clampTurntableRadius(0.1, 0.4, 10)).toBe(0.4)
    expect(clampTurntableRadius(20, 0.4, 10)).toBe(10)
  })

  test('camera mode transition moves toward turntable pose', () => {
    const focus = {
      center: new Vector3(1, 1, 2),
      size: new Vector3(2, 2, 2),
      radius: 2
    }
    const camera = new PerspectiveCamera()
    camera.position.set(4, 3, 8)
    const controls = { target: new Vector3(0, 0, 0) }
    const transition = createTurntableEntryTransition(
      camera,
      controls as import('three/examples/jsm/controls/OrbitControls.js').OrbitControls,
      focus,
      0,
      3,
      1.5,
      1
    )

    expect(camera.position.z).toBe(8)
    stepCameraTransition(camera, transition, 0.5)
    expect(camera.position.z).toBeLessThan(8)
    expect(camera.position.z).toBeGreaterThan(
      turntableCameraPosition(focus, 0, 3, 1.5).z
    )

    stepCameraTransition(camera, transition, 0.5)
    expect(camera.position.x).toBeCloseTo(turntableCameraPosition(focus, 0, 3, 1.5).x)
    expect(camera.position.y).toBeCloseTo(1.5)
    expect(camera.position.z).toBeCloseTo(turntableCameraPosition(focus, 0, 3, 1.5).z)
  })
})
