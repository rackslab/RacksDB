<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI, type GltfEquipmentUserData } from '@/composables/RacksDBAPI'
import {
  applyFreeCameraDefaults,
  clampTurntableRadius,
  computeRackFocusBox,
  createTurntableEntryTransition,
  defaultTurntableHeight,
  defaultTurntableRadius,
  stepCameraTransition,
  TURNTABLE_SPEED,
  updateTurntableCamera,
  type CameraTransition,
  type RackFocus
} from '@/lib/infrastructureScene3d'
import { ref, onMounted, onUnmounted, shallowRef, watch, nextTick } from 'vue'
import type { Object3D, Mesh, MeshStandardMaterial, PerspectiveCamera } from 'three'
import type { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps({
  infrastructureName: {
    type: String,
    required: true
  }
})

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)

const containerRef = ref<HTMLElement | null>(null)
const loading = ref(true)
const errorMessage = ref<string | null>(null)
const hoverLabel = ref<string | null>(null)
const isFullscreen = ref(false)
const cameraMode = ref<'free' | 'turntable'>('free')

const EQUIPMENT_CATEGORIES = new Set(['node', 'storage', 'network', 'misc'])

type SceneBundle = {
  renderer: import('three').WebGLRenderer
  controls: OrbitControls
  scene: import('three').Scene
  camera: PerspectiveCamera
  clock: import('three').Clock
  animationId: number
  resizeObserver: ResizeObserver
  root: Object3D
  raycaster: import('three').Raycaster
  pointer: import('three').Vector2
  pointerClientX: number
  pointerClientY: number
  pointerDirty: boolean
  hoveredEquipment: Object3D | null
  onPointerMove: (event: PointerEvent) => void
  onPointerLeave: () => void
  onWheel: (event: WheelEvent) => void
  focus: RackFocus
  minDistance: number
  maxDistance: number
  turntableAngle: number
  turntableRadius: number
  turntableHeight: number
  cameraTransition: CameraTransition | null
  resize: () => void
}

const sceneBundle = shallowRef<SceneBundle | null>(null)

function findEquipmentAncestor(object: Object3D): Object3D | null {
  let current: Object3D | null = object
  while (current) {
    const category = current.userData?.category as string | undefined
    if (category && EQUIPMENT_CATEGORIES.has(category)) {
      return current
    }
    current = current.parent
  }
  return null
}

function equipmentMesh(equipment: Object3D): Mesh | null {
  for (const child of equipment.children) {
    const mesh = child as Mesh
    if (mesh.isMesh && mesh.userData?.category !== 'equipment-border') {
      return mesh
    }
  }
  return null
}

function equipmentEmissiveColor(equipment: Object3D): number {
  const mesh = equipmentMesh(equipment)
  if (!mesh) {
    return 0xffffff
  }
  const material = mesh.material as MeshStandardMaterial
  return material.color.getHex()
}

function setEquipmentEmissive(mesh: Mesh, color: number, intensity: number) {
  const material = mesh.material as MeshStandardMaterial
  material.emissive.setHex(color)
  material.emissiveIntensity = intensity
}

function applyHoverHighlight(bundle: SceneBundle, equipment: Object3D | null) {
  if (bundle.hoveredEquipment && bundle.hoveredEquipment !== equipment) {
    const mesh = equipmentMesh(bundle.hoveredEquipment)
    if (mesh) {
      setEquipmentEmissive(mesh, 0x000000, 0)
    }
  }
  bundle.hoveredEquipment = equipment
  if (equipment) {
    const mesh = equipmentMesh(equipment)
    if (mesh) {
      setEquipmentEmissive(mesh, equipmentEmissiveColor(equipment), 0.35)
    }
    bundle.renderer.domElement.style.cursor = 'pointer'
  } else {
    bundle.renderer.domElement.style.cursor = 'default'
  }
}

function pickEquipmentAt(
  renderer: import('three').WebGLRenderer,
  camera: PerspectiveCamera,
  root: Object3D,
  raycaster: import('three').Raycaster,
  pointer: import('three').Vector2,
  clientX: number,
  clientY: number
): Object3D | null {
  const rect = renderer.domElement.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    return null
  }
  pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  const hits = raycaster.intersectObjects(root.children, true)
  for (const hit of hits) {
    const mesh = hit.object as Mesh
    if (!mesh.isMesh) {
      continue
    }
    const equipment = findEquipmentAncestor(mesh)
    if (equipment?.name) {
      return equipment
    }
  }
  return null
}

function updateHoverFromPointer(bundle: SceneBundle) {
  const equipment = pickEquipmentAt(
    bundle.renderer,
    bundle.camera,
    bundle.root,
    bundle.raycaster,
    bundle.pointer,
    bundle.pointerClientX,
    bundle.pointerClientY
  )
  if (bundle.hoveredEquipment === equipment) {
    return
  }
  applyHoverHighlight(bundle, equipment)
  if (equipment) {
    const userData = equipment.userData as GltfEquipmentUserData
    hoverLabel.value = `${equipment.name} (${userData.category})`
  } else {
    hoverLabel.value = null
  }
}

function applyFloorAnisotropy(root: Object3D, anisotropy: number) {
  root.traverse((child) => {
    if (child.userData?.category !== 'floor') {
      return
    }
    const mesh = child as Mesh
    if (!mesh.isMesh) {
      return
    }
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material]
    for (const materialRef of materials) {
      const material = materialRef as MeshStandardMaterial
      if (material.map) {
        material.map.anisotropy = anisotropy
      }
    }
  })
}

function applyEquipmentDepthBias(root: Object3D) {
  root.traverse((child) => {
    const mesh = child as Mesh
    if (!mesh.isMesh) {
      return
    }
    if (child.userData?.category === 'equipment-border') {
      mesh.renderOrder = 2
      return
    }
    const equipment = findEquipmentAncestor(mesh)
    if (!equipment) {
      return
    }
    // glTF reuses one material per color; clone so hover emissive affects one device.
    const material = (mesh.material as MeshStandardMaterial).clone()
    material.polygonOffset = true
    material.polygonOffsetFactor = 1
    material.polygonOffsetUnits = 1
    mesh.material = material
  })
}

function disposeObject(object: Object3D) {
  object.traverse((child) => {
    const mesh = child as Mesh
    if (mesh.isMesh) {
      mesh.geometry?.dispose()
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material]
      materials.forEach((material) => material?.dispose())
    }
  })
}

function applyCameraModeChange(mode: 'free' | 'turntable') {
  const bundle = sceneBundle.value
  if (!bundle) {
    return
  }

  bundle.cameraTransition = null

  if (mode === 'turntable') {
    bundle.controls.enabled = false
    const { camera, controls, focus } = bundle
    const offsetX = camera.position.x - focus.center.x
    const offsetZ = camera.position.z - focus.center.z
    bundle.turntableAngle = Math.atan2(offsetX, offsetZ)
    bundle.turntableRadius = defaultTurntableRadius(focus, bundle.maxDistance)
    bundle.turntableHeight = defaultTurntableHeight(focus)
    bundle.cameraTransition = createTurntableEntryTransition(
      camera,
      controls,
      focus,
      bundle.turntableAngle,
      bundle.turntableRadius,
      bundle.turntableHeight
    )
    return
  }

  bundle.controls.target.copy(bundle.focus.center)
  bundle.controls.update()
  bundle.controls.enabled = true
}

watch(cameraMode, (mode) => {
  applyCameraModeChange(mode)
})

function onEscapeKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && isFullscreen.value) {
    isFullscreen.value = false
  }
}

watch(isFullscreen, async (open) => {
  if (open) {
    window.addEventListener('keydown', onEscapeKey)
    document.documentElement.classList.add('overflow-hidden')
    document.body.classList.add('overflow-hidden')
  } else {
    window.removeEventListener('keydown', onEscapeKey)
    document.documentElement.classList.remove('overflow-hidden')
    document.body.classList.remove('overflow-hidden')
  }
  await nextTick()
  sceneBundle.value?.resize()
})

function teardown() {
  const bundle = sceneBundle.value
  if (!bundle) {
    return
  }
  cancelAnimationFrame(bundle.animationId)
  bundle.resizeObserver.disconnect()
  document.documentElement.classList.remove('overflow-hidden')
  document.body.classList.remove('overflow-hidden')
  bundle.controls.dispose()
  applyHoverHighlight(bundle, null)
  hoverLabel.value = null
  bundle.renderer.domElement.removeEventListener('pointermove', bundle.onPointerMove)
  bundle.renderer.domElement.removeEventListener('pointerleave', bundle.onPointerLeave)
  bundle.renderer.domElement.removeEventListener('wheel', bundle.onWheel)
  disposeObject(bundle.root)
  bundle.renderer.dispose()
  if (bundle.renderer.domElement.parentElement) {
    bundle.renderer.domElement.parentElement.removeChild(bundle.renderer.domElement)
  }
  sceneBundle.value = null
  window.removeEventListener('keydown', onEscapeKey)
}

async function initScene() {
  const container = containerRef.value
  if (!container) {
    return
  }

  loading.value = true
  errorMessage.value = null
  hoverLabel.value = null

  try {
    const gltfDocument = await racksDBAPI.infrastructureGltf(props.infrastructureName)

    const THREE = await import('three')
    const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js')
    const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js')

    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x1f2937)

    const camera = new THREE.PerspectiveCamera(50, 1, 0.01, 5000)
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.setPixelRatio(window.devicePixelRatio)
    const canvas = renderer.domElement
    canvas.style.display = 'block'
    canvas.style.width = '100%'
    canvas.style.height = '100%'
    container.appendChild(canvas)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true

    scene.add(new THREE.AmbientLight(0xffffff, 0.82))
    scene.add(new THREE.HemisphereLight(0xf5f7ff, 0x8a9099, 0.48))
    const key = new THREE.DirectionalLight(0xffffff, 0.75)
    key.position.set(5, 14, 8)
    scene.add(key)
    const fill = new THREE.DirectionalLight(0xffffff, 0.35)
    fill.position.set(-6, 9, -4)
    scene.add(fill)

    const loader = new GLTFLoader()
    const gltf = await new Promise<import('three/examples/jsm/loaders/GLTFLoader.js').GLTF>(
      (resolve, reject) => {
        loader.parse(
          JSON.stringify(gltfDocument),
          '',
          (result) => resolve(result),
          (error) => reject(error)
        )
      }
    )

    const root = gltf.scene
    applyFloorAnisotropy(root, renderer.capabilities.getMaxAnisotropy())
    applyEquipmentDepthBias(root)
    scene.add(root)
    root.updateMatrixWorld(true)

    const focus = computeRackFocusBox(root)
    const { minDistance, maxDistance } = applyFreeCameraDefaults(camera, controls, focus)
    const turntableRadius = defaultTurntableRadius(focus, maxDistance)
    const turntableHeight = defaultTurntableHeight(focus)

    controls.enabled = cameraMode.value === 'free'

    const resize = () => {
      const width = container.clientWidth
      const height = isFullscreen.value
        ? container.clientHeight
        : Math.max(container.clientHeight, 384)
      if (width === 0 || height === 0) {
        return
      }
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }
    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(container)
    resize()

    const raycaster = new THREE.Raycaster()
    const pointer = new THREE.Vector2()

    const onPointerMove = (event: PointerEvent) => {
      const bundle = sceneBundle.value
      if (!bundle) {
        return
      }
      bundle.pointerClientX = event.clientX
      bundle.pointerClientY = event.clientY
      bundle.pointerDirty = true
    }

    const onPointerLeave = () => {
      const bundle = sceneBundle.value
      if (!bundle) {
        return
      }
      bundle.pointerDirty = false
      if (bundle.hoveredEquipment) {
        applyHoverHighlight(bundle, null)
        hoverLabel.value = null
      }
    }

    const onWheel = (event: WheelEvent) => {
      const bundle = sceneBundle.value
      if (!bundle || cameraMode.value !== 'turntable') {
        return
      }
      event.preventDefault()
      const delta = event.deltaY > 0 ? 0.15 : -0.15
      bundle.turntableRadius = clampTurntableRadius(
        bundle.turntableRadius + delta,
        bundle.minDistance,
        bundle.maxDistance
      )
    }

    renderer.domElement.addEventListener('pointermove', onPointerMove)
    renderer.domElement.addEventListener('pointerleave', onPointerLeave)
    renderer.domElement.addEventListener('wheel', onWheel, { passive: false })

    const clock = new THREE.Clock()
    const bundleState: SceneBundle = {
      renderer,
      controls,
      scene,
      camera,
      clock,
      animationId: 0,
      resizeObserver,
      root,
      raycaster,
      pointer,
      pointerClientX: 0,
      pointerClientY: 0,
      pointerDirty: false,
      hoveredEquipment: null,
      onPointerMove,
      onPointerLeave,
      onWheel,
      focus,
      minDistance,
      maxDistance,
      turntableAngle: 0,
      turntableRadius,
      turntableHeight,
      cameraTransition: null,
      resize
    }
    sceneBundle.value = bundleState

    const animate = () => {
      bundleState.animationId = requestAnimationFrame(animate)
      const delta = clock.getDelta()
      if (bundleState.pointerDirty) {
        bundleState.pointerDirty = false
        updateHoverFromPointer(bundleState)
      }
      if (bundleState.cameraTransition) {
        const finished = stepCameraTransition(camera, bundleState.cameraTransition, delta)
        if (finished) {
          controls.target.copy(bundleState.cameraTransition.toTarget)
          bundleState.cameraTransition = null
        }
      } else if (cameraMode.value === 'turntable') {
        bundleState.turntableAngle += delta * TURNTABLE_SPEED
        updateTurntableCamera(
          camera,
          bundleState.focus,
          bundleState.turntableAngle,
          bundleState.turntableRadius,
          bundleState.turntableHeight
        )
      } else {
        controls.update()
      }
      renderer.render(scene, camera)
    }
    animate()
  } catch (error: any) {
    errorMessage.value =
      error?.response?.data?.description ?? error?.message ?? 'Failed to load 3D scene'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initScene()
})

onUnmounted(() => {
  teardown()
})
</script>

<template>
  <Teleport to="body" :disabled="!isFullscreen">
    <div
      class="flex flex-col"
      :class="
        isFullscreen
          ? 'fixed inset-0 z-50 h-dvh w-screen overflow-hidden bg-gray-100 dark:bg-gray-900'
          : 'w-[60vw] mx-auto'
      "
      :data-fullscreen="isFullscreen ? 'true' : 'false'"
      :data-camera-mode="cameraMode"
    >
      <div
        class="relative w-full overflow-hidden bg-gray-100 dark:bg-gray-900"
        :class="
          isFullscreen
            ? 'h-full min-h-0 flex-1'
            : 'min-h-96 h-96 rounded-lg border border-gray-200 dark:border-gray-700'
        "
        role="img"
        :aria-label="`3D layout of infrastructure ${infrastructureName}`"
      >
      <div ref="containerRef" class="absolute inset-0" />

      <div
        class="pointer-events-none absolute inset-x-0 top-0 z-10 flex flex-wrap items-center justify-between gap-2 p-2"
      >
        <div class="pointer-events-auto flex gap-2">
          <button
            type="button"
            class="rounded-lg px-3 py-1.5 text-sm font-medium border shadow-sm"
            :class="
              cameraMode === 'free'
                ? 'bg-purple-700 text-white border-purple-700'
                : 'bg-white/95 text-gray-700 border-gray-300 dark:bg-gray-800/95 dark:text-gray-200 dark:border-gray-600'
            "
            @click="cameraMode = 'free'"
          >
            Free
          </button>
          <button
            type="button"
            class="rounded-lg px-3 py-1.5 text-sm font-medium border shadow-sm"
            :class="
              cameraMode === 'turntable'
                ? 'bg-purple-700 text-white border-purple-700'
                : 'bg-white/95 text-gray-700 border-gray-300 dark:bg-gray-800/95 dark:text-gray-200 dark:border-gray-600'
            "
            @click="cameraMode = 'turntable'"
          >
            Orbit racks
          </button>
        </div>
        <button
          type="button"
          class="pointer-events-auto rounded-lg px-3 py-1.5 text-sm font-medium border border-gray-300 bg-white/95 text-gray-700 shadow-sm dark:border-gray-600 dark:bg-gray-800/95 dark:text-gray-200"
          @click="isFullscreen = !isFullscreen"
        >
          {{ isFullscreen ? 'Exit fullscreen' : 'Fullscreen' }}
        </button>
      </div>
      <div
        v-if="loading"
        class="absolute inset-0 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300"
      >
        Loading 3D layout…
      </div>
      <div
        v-else-if="errorMessage"
        class="absolute inset-0 flex items-center justify-center px-6 text-center text-sm text-red-600"
      >
        {{ errorMessage }}
      </div>
      <p
        v-if="hoverLabel && !loading && !errorMessage"
        class="pointer-events-none absolute top-12 left-1/2 z-10 -translate-x-1/2 rounded-md border border-gray-200 bg-white/90 px-3 py-1 text-sm text-gray-800 shadow-sm dark:border-gray-600 dark:bg-gray-800/90 dark:text-gray-100"
      >
        {{ hoverLabel }}
      </p>
      </div>
    </div>
  </Teleport>
</template>
