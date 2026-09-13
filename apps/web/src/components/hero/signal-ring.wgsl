struct Params {
  resolution: vec2f,
  time: f32,
}
@group(0) @binding(0) var<uniform> params: Params;

const RADIUS: f32 = 1.0;
const HALF_THICKNESS: f32 = 0.05;
const LABEL_RADIUS: f32 = 0.32;
const SPINDLE_RADIUS: f32 = 0.035;
const SPIN_SPEED: f32 = 0.5;

const PAPER = vec3f(0.914, 0.906, 0.886);
const VINYL = vec3f(0.075, 0.078, 0.086);
const VINYL_LIGHT = vec3f(0.135, 0.140, 0.152);
const VIOLET = vec3f(0.310, 0.275, 0.898);

fn rotateZ(p: vec3f, angle: f32) -> vec3f {
  let c = cos(angle);
  let s = sin(angle);
  return vec3f(c * p.x + s * p.y, -s * p.x + c * p.y, p.z);
}

fn discDistance(p: vec3f) -> f32 {
  let r = length(p.xy);
  var thickness = HALF_THICKNESS;
  if (r > LABEL_RADIUS && r < RADIUS) {
    let groove = sin(r * 150.0) * 0.5 + 0.5;
    thickness = HALF_THICKNESS - 0.007 * groove;
  }
  let d = vec2f(r - RADIUS, abs(p.z) - thickness);
  return length(max(d, vec2f(0.0))) + min(max(d.x, d.y), 0.0);
}

fn normalAt(p: vec3f, e: f32) -> vec3f {
  let k0 = vec3f(1.0, -1.0, -1.0);
  let k1 = vec3f(-1.0, -1.0, 1.0);
  let k2 = vec3f(-1.0, 1.0, -1.0);
  let k3 = vec3f(1.0, 1.0, 1.0);
  return normalize(
    k0 * discDistance(p + k0 * e) + k1 * discDistance(p + k1 * e) +
    k2 * discDistance(p + k2 * e) + k3 * discDistance(p + k3 * e)
  );
}

fn ambientOcclusion(p: vec3f, n: vec3f) -> f32 {
  let d0 = discDistance(p + n * 0.02);
  let d1 = discDistance(p + n * 0.05);
  let d2 = discDistance(p + n * 0.11);
  let occlusion = max(0.0, 0.02 - d0) * 7.0 + max(0.0, 0.05 - d1) * 3.0 + max(0.0, 0.11 - d2) * 1.1;
  return clamp(1.0 - occlusion, 0.45, 1.0);
}

fn surfaceAlbedo(spinP: vec3f, n: vec3f) -> vec3f {
  let r = length(spinP.xy);
  let isFace = abs(n.z) > 0.6;

  if (!isFace) {
    return VINYL_LIGHT;
  }

  if (r < SPINDLE_RADIUS) {
    return PAPER;
  }

  if (r < LABEL_RADIUS) {
    return PAPER;
  }

  let sheen = sin(r * 150.0) * 0.5 + 0.5;
  return mix(VINYL, VINYL_LIGHT, sheen * 0.25);
}

@fragment fn fs_main(@location(0) uv: vec2f) -> @location(0) vec4f {
  let t = params.time;
  let spinAngle = t * SPIN_SPEED;

  let yaw = 0.14;
  let pitch = 0.05;
  let camDist = 1.85;
  let ro = vec3f(
    camDist * sin(yaw) * cos(pitch),
    camDist * sin(pitch),
    camDist * cos(yaw) * cos(pitch)
  );
  let forward = normalize(-ro);
  let right = normalize(cross(forward, vec3f(0.0, 1.0, 0.0)));
  let up = cross(right, forward);

  var screen = uv * 2.0 - 1.0;
  screen.y = -screen.y;
  screen.x *= params.resolution.x / max(params.resolution.y, 1.0);
  let rd = normalize(forward + (right * screen.x + up * screen.y) * 0.62);

  var travelled = 0.0;
  var hit = false;
  var eps = 0.0;
  for (var step = 0; step < 110; step++) {
    let p = ro + rd * travelled;
    let spinP = rotateZ(p, -spinAngle);
    let d = discDistance(spinP);
    eps = max(0.0006, 0.0006 * travelled);
    if (d < eps) {
      hit = true;
      break;
    }
    travelled += max(d * 0.6, eps * 0.5);
    if (travelled > 8.0) {
      break;
    }
  }

  if (!hit) {
    return vec4f(PAPER, 1.0);
  }

  let p = ro + rd * travelled;
  let spinP = rotateZ(p, -spinAngle);
  let spinNormal = normalAt(spinP, max(0.0015, eps));
  let n = rotateZ(spinNormal, spinAngle);

  let light = normalize(vec3f(-0.4, 0.6, 0.7));
  let diffuse = max(dot(n, light), 0.0);
  let ao = ambientOcclusion(spinP, spinNormal);
  let rim = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);

  let albedo = surfaceAlbedo(spinP, spinNormal);
  let color = albedo * (0.3 + 0.85 * diffuse) * ao + VIOLET * rim * 0.25;

  return vec4f(clamp(color, vec3f(0.0), vec3f(1.0)), 1.0);
}
