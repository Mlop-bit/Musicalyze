"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";

type Props = { image: string | null; active: boolean; busy: boolean };

const VIOLET = 0x1ed760;
const REST_ANGLE = 0.1;
const PLAY_ANGLE = 0.62;
const IDLE_SPEED = 0.55;
const BUSY_SPEED = 3.2;

function grooveTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 1024;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);
  ctx.fillStyle = "#111216";
  ctx.fillRect(0, 0, 1024, 1024);
  for (let radius = 170; radius < 500; radius += 3.2) {
    ctx.strokeStyle = `rgba(255,255,255,${0.035 + ((radius * 7) % 5) / 160})`;
    ctx.beginPath();
    ctx.arc(512, 512, radius, 0, Math.PI * 2);
    ctx.stroke();
  }
  const sheen = ctx.createConicGradient(0, 512, 512);
  sheen.addColorStop(0, "rgba(255,255,255,0)");
  sheen.addColorStop(0.12, "rgba(255,255,255,0.16)");
  sheen.addColorStop(0.25, "rgba(255,255,255,0)");
  sheen.addColorStop(0.62, "rgba(255,255,255,0)");
  sheen.addColorStop(0.75, "rgba(255,255,255,0.12)");
  sheen.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = sheen;
  ctx.beginPath();
  ctx.arc(512, 512, 500, 0, Math.PI * 2);
  ctx.fill();
  return new THREE.CanvasTexture(canvas);
}

function platterTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 512;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);
  ctx.fillStyle = "#2a2b30";
  ctx.fillRect(0, 0, 512, 512);
  ctx.fillStyle = "#c9cad1";
  for (let dot = 0; dot < 72; dot++) {
    const angle = (dot / 72) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(
      256 + Math.cos(angle) * 244,
      256 + Math.sin(angle) * 244,
      3,
      0,
      Math.PI * 2,
    );
    ctx.fill();
  }
  return new THREE.CanvasTexture(canvas);
}

function labelTexture(image: HTMLImageElement | null) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 512;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);
  ctx.fillStyle = "#1ed760";
  ctx.fillRect(0, 0, 512, 512);
  if (image) ctx.drawImage(image, 0, 0, 512, 512);
  ctx.fillStyle = "#0b0b0d";
  ctx.beginPath();
  ctx.arc(256, 256, 14, 0, Math.PI * 2);
  ctx.fill();
  return new THREE.CanvasTexture(canvas);
}

export function Turntable({ image, active, busy }: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const state = useRef({ active, busy });
  const labelRef = useRef<THREE.MeshStandardMaterial | null>(null);
  useEffect(() => {
    state.current = { active, busy };
  }, [active, busy]);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    mount.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
    camera.position.set(0, 6.4, 7.6);
    camera.lookAt(0, 0, 0.1);
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = 0.45;
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(-3, 6, 4);
    scene.add(key);
    const rim = new THREE.PointLight(VIOLET, 18, 14);
    rim.position.set(3.5, 2, -2);
    scene.add(rim);

    const deck = new THREE.Mesh(
      new RoundedBoxGeometry(5.6, 0.34, 4.2, 6, 0.16),
      new THREE.MeshStandardMaterial({
        color: 0x17181b,
        roughness: 0.55,
        metalness: 0.4,
      }),
    );
    deck.position.y = -0.2;
    scene.add(deck);

    const platter = new THREE.Mesh(
      new THREE.CylinderGeometry(1.75, 1.75, 0.08, 64),
      [
        new THREE.MeshStandardMaterial({
          color: 0x2a2b30,
          roughness: 0.4,
          metalness: 0.8,
        }),
        new THREE.MeshStandardMaterial({
          map: platterTexture(),
          roughness: 0.4,
          metalness: 0.8,
        }),
        new THREE.MeshStandardMaterial({
          color: 0x2a2b30,
          roughness: 0.4,
          metalness: 0.8,
        }),
      ],
    );
    platter.position.set(-0.55, 0.02, 0);
    scene.add(platter);

    const grooves = grooveTexture();
    const record = new THREE.Group();
    record.position.set(-0.55, 0.1, 0);
    const disc = new THREE.Mesh(
      new THREE.CylinderGeometry(1.65, 1.65, 0.04, 96),
      [
        new THREE.MeshStandardMaterial({ color: 0x0b0b0d }),
        new THREE.MeshStandardMaterial({
          map: grooves,
          roughness: 0.28,
          metalness: 0.35,
        }),
        new THREE.MeshStandardMaterial({
          map: grooves,
          roughness: 0.28,
          metalness: 0.35,
        }),
      ],
    );
    const label = new THREE.MeshStandardMaterial({
      map: labelTexture(null),
      roughness: 0.6,
    });
    labelRef.current = label;
    const labelDisc = new THREE.Mesh(
      new THREE.CylinderGeometry(0.55, 0.55, 0.045, 48),
      [new THREE.MeshStandardMaterial({ color: 0x0b0b0d }), label, label],
    );
    record.add(disc, labelDisc);
    scene.add(record);

    const slot = new THREE.Mesh(
      new THREE.BoxGeometry(0.14, 0.02, 1.5),
      new THREE.MeshStandardMaterial({ color: 0x050506 }),
    );
    slot.position.set(2.3, -0.02, 0.7);
    const fader = new THREE.Mesh(
      new THREE.BoxGeometry(0.32, 0.1, 0.18),
      new THREE.MeshStandardMaterial({
        color: 0x1ed760,
        roughness: 0.3,
        metalness: 0.4,
      }),
    );
    fader.position.set(2.3, 0.04, 0.55);
    const buttons = [-0.9, 0].map((x) => {
      const button = new THREE.Mesh(
        new THREE.CylinderGeometry(0.17, 0.17, 0.08, 32),
        new THREE.MeshStandardMaterial({
          color: 0xcfd0d6,
          roughness: 0.25,
          metalness: 0.9,
        }),
      );
      button.position.set(-2.1 + x * 0.6, -0.02, 1.7);
      return button;
    });
    scene.add(slot, fader, ...buttons);

    const owned: THREE.Material[] = [];
    const arm = new THREE.Group();
    arm.position.set(2.15, 0.25, -1.35);
    const metal = new THREE.MeshStandardMaterial({
      color: 0xcfd0d6,
      roughness: 0.25,
      metalness: 0.9,
    });
    owned.push(metal);
    const base = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.26, 0.3, 32),
      metal,
    );
    const tube = new THREE.Mesh(
      new THREE.CylinderGeometry(0.035, 0.035, 2.5, 16),
      metal,
    );
    tube.rotation.z = Math.PI / 2;
    tube.rotation.y = 0;
    tube.position.set(-1.25, 0.12, 0);
    const head = new THREE.Mesh(
      new THREE.BoxGeometry(0.34, 0.1, 0.2),
      new THREE.MeshStandardMaterial({ color: VIOLET }),
    );
    head.position.set(-2.5, 0.1, 0);
    arm.add(base, tube, head);
    scene.add(arm);

    const resize = () => {
      const { clientWidth: width, clientHeight: height } = mount;
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(mount);
    resize();

    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let speed = 0;
    let angle = REST_ANGLE;
    let last = performance.now();
    let visible = true;
    let drawn = false;
    const visibility = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
    });
    visibility.observe(mount);
    const tick = (now: number) => {
      if (!visible) {
        last = now;
        return;
      }
      const delta = Math.min((now - last) / 1000, 0.1);
      last = now;
      const target = state.current.active
        ? state.current.busy
          ? BUSY_SPEED
          : IDLE_SPEED
        : 0;
      speed += (target - speed) * Math.min(delta * 2.5, 1);
      angle +=
        ((state.current.active ? PLAY_ANGLE : REST_ANGLE) - angle) *
        Math.min(delta * 2, 1);
      if (!reduced) record.rotation.y -= speed * delta;
      arm.rotation.y = angle;
      const settled =
        !state.current.active &&
        Math.abs(speed) < 0.01 &&
        Math.abs(angle - REST_ANGLE) < 0.001;
      if (settled && drawn) return;
      renderer.render(scene, camera);
      drawn = true;
    };
    renderer.setAnimationLoop(tick);

    return () => {
      renderer.setAnimationLoop(null);
      observer.disconnect();
      visibility.disconnect();
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          for (const material of [object.material].flat()) {
            if ("map" in material && material.map) material.map.dispose();
            material.dispose();
          }
        }
      });
      for (const material of owned) material.dispose();
      pmrem.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    };
  }, []);

  useEffect(() => {
    const material = labelRef.current;
    if (!material) return;
    const swap = (texture: THREE.Texture) => {
      material.map?.dispose();
      material.map = texture;
      material.needsUpdate = true;
    };
    if (!image) {
      swap(labelTexture(null));
      return;
    }
    let cancelled = false;
    const cover = new Image();
    cover.crossOrigin = "anonymous";
    cover.onload = () => {
      if (cancelled) return;
      swap(labelTexture(cover));
    };
    cover.src = image;
    return () => {
      cancelled = true;
    };
  }, [image]);

  return (
    <div
      ref={mountRef}
      role="img"
      aria-label="Turntable"
      className="h-full w-full"
    />
  );
}
