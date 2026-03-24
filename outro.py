"""
RUST & RUIN — CINEMATIC OUTRO  ✦  Director's Cut
══════════════════════════════════════════════════
A child and their droid cross a battlefield.
The droid sacrifices itself to become a weapon.
A giant robot falls. A cow emerges. A UFO descends.
Nothing makes sense. Everything is beautiful.

SPACE / ESC to skip
"""

import pygame, math, random, sys, struct, colorsys
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

W, H = 1280, 720
FPS = 60
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("RUST & RUIN — CINEMATIC OUTRO")
clock = pygame.time.Clock()

# ── Maths ────────────────────────────────────────────────────────────────────
τ = math.tau
PI = math.pi
def lerp(a, b, t):     return a + (b - a) * t
def clamp(v, lo, hi):  return max(lo, min(hi, v))
def ease_out(t):        return 1 - (1 - clamp(t, 0, 1)) ** 3
def ease_out5(t):       return 1 - (1 - clamp(t, 0, 1)) ** 5
def ease_in(t):         return clamp(t, 0, 1) ** 3
def ease_io(t):         t = clamp(t, 0, 1); return t * t * (3 - 2 * t)
def ease_elastic(t):
    t = clamp(t, 0, 1)
    if t == 0 or t == 1: return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * τ / 3) + 1
def ease_bounce(t):
    t = clamp(t, 0, 1)
    if t < 1/2.75: return 7.5625*t*t
    elif t < 2/2.75: t -= 1.5/2.75; return 7.5625*t*t+0.75
    elif t < 2.5/2.75: t -= 2.25/2.75; return 7.5625*t*t+0.9375
    else: t -= 2.625/2.75; return 7.5625*t*t+0.984375
def lc(a, b, t):       return tuple(int(lerp(a[i], b[i], clamp(t, 0, 1))) for i in range(3))
def dist2(a, b):       return math.hypot(a[0]-b[0], a[1]-b[1])

# ── Procedural Audio ────────────────────────────────────────────────────────
SR = 44100
def make_pcm(samples):
    data = bytearray()
    for s in samples:
        data += struct.pack('<h', int(clamp(s, -1, 1) * 32767))
    return bytes(data)

def sine(f, t, amp=1.0): return amp * math.sin(τ * f * t)
def noise(): return random.uniform(-1, 1)

def gen_sfx(name, dur):
    n = int(SR * dur); buf = []
    for i in range(n):
        t = i / SR
        if name == 'footstep':
            env = math.exp(-t * 25)
            buf.append((noise() * 0.5 + sine(120, t, 0.3) + sine(60, t, 0.2)) * env)
        elif name == 'wind':
            env = math.sin(PI * t / dur) ** 0.5
            buf.append(noise() * env * 0.35 + sine(55 + 35 * math.sin(τ * 0.15 * t), t, 0.08) * env)
        elif name == 'droid_hum':
            env = min(1, t * 3) * max(0, 1 - (t - dur + 0.3) / 0.3)
            f1 = 350 + 60 * math.sin(τ * 0.9 * t)
            buf.append(env * (sine(f1, t, 0.3) + sine(f1 * 1.5, t, 0.15) + noise() * 0.02))
        elif name == 'alert':
            env = (math.sin(PI * t / dur)) * math.exp(-t * 2)
            buf.append(env * (sine(800 + 400 * math.sin(τ * 6 * t), t, 0.4) + noise() * 0.05))
        elif name == 'transform':
            env = min(1, t * 5) * max(0, 1 - (t - dur + 0.2) / 0.2)
            f1 = 200 + 2000 * (t / dur)
            buf.append(env * (sine(f1, t, 0.3) + sine(f1 * 0.5, t, 0.2) + noise() * 0.15 * math.exp(-t * 3)))
        elif name == 'charge':
            env = min(1, t / dur * 2) ** 2
            f1 = 100 + 900 * (t / dur) ** 2
            buf.append(env * (sine(f1, t, 0.4) + sine(f1 * 2, t, 0.15) + noise() * 0.05 * env))
        elif name == 'laser':
            env = math.exp(-t * 4) * (1 - math.exp(-t * 40))
            f1 = 3000 - 2000 * (t / dur)
            buf.append(env * (sine(f1, t, 0.5) + sine(f1 * 0.5, t, 0.25) + noise() * 0.08))
        elif name == 'explosion':
            env = math.exp(-t * 2.0) * (1 - math.exp(-t * 30))
            buf.append(clamp((noise() * 0.7 + sine(50 + t * 15, t, 0.35) + sine(25, t, 0.5) * math.exp(-t * 3)) * env, -.99, .99))
        elif name == 'explosion_big':
            env = math.exp(-t * 1.2) * (1 - math.exp(-t * 25))
            sub = sine(22, t, 0.7) * math.exp(-t * 2)
            buf.append(clamp((noise() * 0.65 + sine(40, t, 0.3) + sub) * env, -.99, .99))
        elif name == 'debris':
            env = math.exp(-t * 4)
            buf.append(noise() * env * 0.65 + sine(280 - 200 * t / dur, t, 0.12) * env)
        elif name == 'whoosh':
            env = math.sin(PI * t / dur) * math.exp(-t * 1.2)
            buf.append(env * (noise() * 0.55 + sine(180 + 1600 * (t / dur), t, 0.18)))
        elif name == 'moo':
            env = math.sin(PI * t / dur) ** 0.35
            f1 = 170 + 55 * math.sin(τ * 0.45 * t) + 18 * math.sin(τ * 2.2 * t)
            buf.append((sine(f1, t, 0.45) + sine(f1 * 2, t, 0.12) + sine(f1 * 3, t, 0.05)) * env * 0.8)
        elif name == 'moo_confused':
            env = math.sin(PI * t / dur) ** 0.35
            f1 = 200 + 80 * math.sin(τ * 0.8 * t) + 30 * (t / dur)
            buf.append((sine(f1, t, 0.4) + sine(f1 * 1.5, t, 0.15)) * env * 0.7)
        elif name == 'ufo':
            env = min(1, t * 2) * max(0, 1 - (t - dur + 0.5) / 0.5)
            f1 = 300 + 70 * math.sin(τ * 0.7 * t)
            f2 = 450 + 55 * math.sin(τ * 1.05 * t + 1)
            buf.append(env * (sine(f1, t, 0.3) + sine(f2, t, 0.22) + noise() * 0.025))
        elif name == 'beam':
            env = min(1, t * 3) * max(0, 1 - (t - dur + 0.3) / 0.3)
            buf.append(env * (sine(210, t, 0.28) + sine(420, t, 0.14) + sine(630, t, 0.07) + noise() * 0.035))
        elif name == 'abduction':
            env = min(1, t * 2) * max(0, 1 - (t - dur + 0.4) / 0.4)
            f1 = 550 + 350 * math.sin(τ * 0.25 * t) + 180 * math.sin(τ * 0.6 * t)
            buf.append(env * (sine(f1, t, 0.35) + sine(f1 * 1.5, t, 0.18) + noise() * 0.04))
        elif name == 'thunder':
            env = math.exp(-t * 3.5) * (1 - math.exp(-t * 45))
            buf.append(clamp((noise() * 0.85 + sine(35, t, 0.25) + sine(22, t, 0.18)) * env, -.99, .99))
        elif name == 'impact':
            env = math.exp(-t * 16)
            buf.append((noise() * 0.75 + sine(70, t, 0.35)) * env)
        elif name == 'sad_tone':
            env = math.sin(PI * t / dur) ** 0.6
            buf.append(env * (sine(440, t, 0.2) + sine(554, t, 0.15) + sine(659, t, 0.1)) * 0.5)
        elif name == 'sparkle':
            env = math.exp(-t * 5) * (1 - math.exp(-t * 30))
            buf.append(env * (sine(2000 + 500 * math.sin(τ * 8 * t), t, 0.3) + noise() * 0.05))
        elif name == 'cow_walk':
            env = math.exp(-t * 30)
            buf.append((noise() * 0.3 + sine(200, t, 0.2)) * env * 0.5)
        else:
            buf.append(0)
    return make_pcm(buf)

print("Generating audio...")
sfx_defs = {
    'footstep': 0.15, 'wind': 3.0, 'droid_hum': 2.5, 'alert': 0.8,
    'transform': 1.5, 'charge': 2.0, 'laser': 0.6, 'explosion': 2.0,
    'explosion_big': 3.0, 'debris': 0.7, 'whoosh': 0.5, 'moo': 1.5,
    'moo_confused': 1.0, 'ufo': 3.5, 'beam': 2.5, 'abduction': 2.5,
    'thunder': 1.2, 'impact': 0.3, 'sad_tone': 2.0, 'sparkle': 0.4,
    'cow_walk': 0.1,
}
SFX = {}
for name, dur in sfx_defs.items():
    SFX[name] = pygame.mixer.Sound(buffer=gen_sfx(name, dur))

vol_map = {
    'footstep': 0.4, 'wind': 0.25, 'droid_hum': 0.4, 'alert': 0.6,
    'transform': 0.7, 'charge': 0.6, 'laser': 0.85, 'explosion': 0.9,
    'explosion_big': 1.0, 'debris': 0.5, 'whoosh': 0.5, 'moo': 0.8,
    'moo_confused': 0.7, 'ufo': 0.5, 'beam': 0.35, 'abduction': 0.5,
    'thunder': 0.6, 'impact': 0.7, 'sad_tone': 0.3, 'sparkle': 0.4,
    'cow_walk': 0.3,
}
for k, v in vol_map.items():
    SFX[k].set_volume(v)
print("Audio ready.")

# ── Sound scheduler ─────────────────────────────────────────────────────────
class SoundScheduler:
    def __init__(self):
        self.events = []
        self.fired = set()
    def at(self, t, key, vol=None):
        self.events.append((t, key, vol))
    def update(self, t):
        for i, (et, key, vol) in enumerate(self.events):
            if i not in self.fired and t >= et:
                if vol is not None:
                    SFX[key].set_volume(vol)
                SFX[key].play()
                self.fired.add(i)

SCHED = SoundScheduler()

# ── Fonts ────────────────────────────────────────────────────────────────────
def get_font(size, bold=False):
    for name in ["consolas", "dejavusansmono", "couriernew", "arial"]:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f: return f
    return pygame.font.SysFont(None, size, bold=bold)

F_title  = get_font(52, True)
F_sub    = get_font(28, True)
F_chat   = get_font(17)
F_chat_b = get_font(17, True)
F_name   = get_font(14, True)
F_hint   = get_font(13)
F_big    = get_font(72, True)

# ── Camera System ────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.x = 0; self.y = 0
        self.target_x = 0; self.target_y = 0
        self.zoom = 1.0; self.target_zoom = 1.0
        self.shake_amt = 0; self.shake_decay = 5
        self.shake_ox = 0; self.shake_oy = 0
        self.smooth = 3.0
        self.zoom_smooth = 2.5
        self.moves = []
        self.active_move = None

    def shake(self, intensity, decay=5):
        self.shake_amt = intensity
        self.shake_decay = decay

    def pan_to(self, x, y, zoom=None, dur=2.0):
        self.target_x = x; self.target_y = y
        if zoom is not None: self.target_zoom = zoom
        self.smooth = max(0.5, 2.0 / dur)

    def cut_to(self, x, y, zoom=None):
        self.x = self.target_x = x
        self.y = self.target_y = y
        if zoom is not None:
            self.zoom = self.target_zoom = zoom

    def add_move(self, start_t, dur, fx, fy, tx, ty, fz, tz, ease_fn=ease_io):
        self.moves.append((start_t, dur, fx, fy, tx, ty, fz, tz, ease_fn))

    def update(self, dt, t):
        for move in self.moves:
            st, dur, fx, fy, tx, ty, fz, tz, efn = move
            if st <= t < st + dur:
                prog = efn((t - st) / dur)
                self.x = lerp(fx, tx, prog)
                self.y = lerp(fy, ty, prog)
                self.zoom = lerp(fz, tz, prog)
                self.target_x = self.x; self.target_y = self.y
                self.target_zoom = self.zoom
                self.active_move = move
                break
        else:
            self.active_move = None
            self.x += (self.target_x - self.x) * min(1, self.smooth * dt)
            self.y += (self.target_y - self.y) * min(1, self.smooth * dt)
            self.zoom += (self.target_zoom - self.zoom) * min(1, self.zoom_smooth * dt)

        if self.shake_amt > 0.5:
            self.shake_ox = random.uniform(-self.shake_amt, self.shake_amt)
            self.shake_oy = random.uniform(-self.shake_amt, self.shake_amt)
            self.shake_amt *= max(0, 1 - self.shake_decay * dt)
        else:
            self.shake_ox = self.shake_oy = 0
            self.shake_amt = 0

    def world_to_screen(self, wx, wy):
        sx = (wx - self.x) * self.zoom + W / 2 + self.shake_ox
        sy = (wy - self.y) * self.zoom + H / 2 + self.shake_oy
        return int(sx), int(sy)

cam = Camera()

# ── Cinematic Director ────────────────────────────────────────────────────────
def ease_in_out_sine(t): return -(math.cos(math.pi * t) - 1) / 2

class CinematicDirector:
    def __init__(self, cam):
        self.cam = cam
        self.tracks  = []
        self.cuts    = []
        self.pulses  = []
        self.lookahead  = 0.12
        self.max_speed  = 650.0

    def add_track(self, start, dur, target_fn, offset_fn=None, zoom_fn=None,
                  easing=None, weight=1.0):
        if easing is None: easing = ease_in_out_sine
        self.tracks.append((start, dur, target_fn, offset_fn, zoom_fn, easing, weight))

    def add_cut(self, time, x, y, z):
        self.cuts.append((time, x, y, z))

    def add_pulse(self, start, dur=0.6, amp=0.18, freq=8.0, decay=3.0):
        self.pulses.append((start, dur, amp, freq, decay))

    def _active(self, t):
        out = []
        for st, dur, tf, of, zf, e, w in self.tracks:
            if st <= t <= st + dur:
                p = clamp((t - st) / dur, 0, 1)
                out.append((p, tf, of, zf, e, w))
        return out

    def update(self, t, dt):
        for ct, cx, cy, cz in self.cuts:
            if abs(t - ct) < dt * 1.5:
                self.cam.cut_to(cx, cy, cz)
        acts = self._active(t)
        if acts:
            sum_w = tx = ty = tz = 0.0
            for p, tf, of, zf, e, w in acts:
                pe = e(p)
                px, py = tf(t + self.lookahead)
                if of:
                    ox2, oy2 = of(p); px += ox2; py += oy2
                z = zf(pe) if zf else self.cam.target_zoom
                tx += px * w; ty += py * w; tz += z * w; sum_w += w
            tx /= sum_w; ty /= sum_w; tz /= sum_w
            dx = tx - self.cam.target_x; dy = ty - self.cam.target_y
            dist = math.hypot(dx, dy)
            max_step = self.max_speed * dt
            if dist > max_step > 0:
                s = max_step / dist
                tx = self.cam.target_x + dx * s
                ty = self.cam.target_y + dy * s
            self.cam.target_x = tx
            self.cam.target_y = ty
            self.cam.target_zoom = clamp(tz, 0.52, 1.55)
        for st, dur, amp, freq, decay in self.pulses:
            if st <= t <= st + dur:
                u = (t - st) / dur
                wave = math.sin(2 * math.pi * freq * u)
                env  = math.exp(-decay * u)
                self.cam.target_zoom *= (1.0 + amp * wave * env)

director = CinematicDirector(cam)

# ── Particles ────────────────────────────────────────────────────────────────
class Particle:
    __slots__ = ('x','y','vx','vy','life','ml','sz','col','grav','glow','trail','spin')
    def __init__(self, x, y, vx, vy, life, sz, col, grav=120, glow=False, trail=False, spin=0):
        self.x=float(x); self.y=float(y); self.vx=float(vx); self.vy=float(vy)
        self.life=self.ml=float(life); self.sz=float(sz)
        self.col=col[:3]; self.grav=grav; self.glow=glow; self.trail=trail; self.spin=spin

class ParticleSystem:
    def __init__(self):
        self.particles = []
    def add(self, x, y, vx, vy, life, sz, col, grav=120, glow=False, trail=False, spin=0):
        if len(self.particles) < 2000:
            self.particles.append(Particle(x, y, vx, vy, life, sz, col, grav, glow, trail, spin))
    def burst(self, x, y, n, spd, col, life=0.8, sz=4, grav=200, glow=True, spread=τ):
        for _ in range(n):
            a = random.uniform(0, spread); s = random.uniform(spd*0.3, spd)
            dc = tuple(min(255, c + random.randint(-25, 25)) for c in col[:3])
            self.add(x+random.uniform(-6,6), y+random.uniform(-6,6),
                     math.cos(a)*s, math.sin(a)*s,
                     life*random.uniform(0.5,1.4), sz*random.uniform(0.4,1.5), dc, grav, glow)
    def sparks(self, x, y, n=25, spd=400):
        cols = [(255,220,80),(255,140,20),(255,80,10),(200,240,255)]
        for _ in range(n):
            a = random.uniform(0, τ); s = random.uniform(80, spd)
            self.add(x, y, math.cos(a)*s, math.sin(a)*s,
                     random.uniform(0.3,1.0), random.uniform(2,6), random.choice(cols), 400, True, True)
    def fire(self, x, y, n=8):
        for _ in range(n):
            c = random.choice([(255,60,0),(255,140,20),(255,220,60),(255,100,30)])
            self.add(x+random.uniform(-15,15), y, random.uniform(-18,18),
                     random.uniform(-140,-50), random.uniform(0.2,0.6),
                     random.uniform(5,14), c, -40, True)
    def smoke(self, x, y, n=3, col=(60,55,70), sz=20):
        for _ in range(n):
            self.add(x+random.uniform(-18,18), y+random.uniform(-4,4),
                     random.uniform(-20,20), random.uniform(-60,-18),
                     random.uniform(2,4), sz*random.uniform(0.6,1.3), col, -12)
    def embers(self, x, y, n=8):
        for _ in range(n):
            a = random.uniform(-PI, 0.3); s = random.uniform(50, 300)
            self.add(x, y, math.cos(a)*s, math.sin(a)*s,
                     random.uniform(1.5,3.5), random.uniform(3,8),
                     random.choice([(255,180,40),(255,100,20),(200,60,10)]), 250, True, True)
    def debris(self, x, y, n=14):
        for _ in range(n):
            a = random.uniform(-PI, 0.3); s = random.uniform(80, 500)
            c = random.choice([(85,80,90),(65,58,62),(105,98,88),(45,45,55)])
            self.add(x, y, math.cos(a)*s, math.sin(a)*s,
                     random.uniform(1,3), random.uniform(5,16), c, 320, False, False,
                     random.uniform(-6,6))
    def dust_puff(self, x, y, n=6):
        for _ in range(n):
            self.add(x+random.uniform(-10,10), y, random.uniform(-40,40),
                     random.uniform(-30,-10), random.uniform(0.8,1.8),
                     random.uniform(8,18), (120,110,100), -8)
    def stardust(self, x, y, n=5):
        for _ in range(n):
            a = random.uniform(0, τ); s = random.uniform(4, 35)
            c = random.choice([(220,200,255),(180,220,255),(255,240,200),(200,255,240)])
            self.add(x+random.uniform(-50,50), y+random.uniform(-35,35),
                     math.cos(a)*s, math.sin(a)*s - random.uniform(8,25),
                     random.uniform(2,4.5), random.uniform(2,5), c, -4, True)
    def energy_gather(self, cx, cy, n=12, radius=120):
        for _ in range(n):
            a = random.uniform(0, τ)
            r = random.uniform(radius*0.6, radius)
            px = cx + math.cos(a) * r; py = cy + math.sin(a) * r
            spd = random.uniform(80, 200)
            dx = cx - px; dy = cy - py; d = max(1, math.hypot(dx, dy))
            c = random.choice([(100,180,255),(60,220,255),(200,220,255),(150,255,200)])
            self.add(px, py, dx/d*spd, dy/d*spd,
                     random.uniform(0.3,0.8), random.uniform(2,5), c, 0, True)
    def shockwave_ring(self, x, y, n=35):
        for i in range(n):
            a = τ * i / n
            self.add(x, y, math.cos(a)*random.uniform(250,550),
                     math.sin(a)*random.uniform(250,550),
                     random.uniform(0.3,0.9), random.uniform(2,6), (255,200,100), 140, True)
    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0: continue
            p.vy += p.grav * dt; p.x += p.vx * dt; p.y += p.vy * dt
            p.vx *= max(0, 1 - dt * (1.2 if not p.trail else 0.6))
            alive.append(p)
        self.particles = alive
    def draw(self, surf, cam_obj=None):
        for p in self.particles:
            t2 = p.life / p.ml; a = int(200 * min(t2, 0.8))
            if a < 5: continue
            if cam_obj:
                sx, sy = cam_obj.world_to_screen(p.x, p.y)
                sz = max(1, int(p.sz * (0.3 + 0.7 * t2) * cam_obj.zoom))
            else:
                sx, sy = int(p.x), int(p.y)
                sz = max(1, int(p.sz * (0.3 + 0.7 * t2)))
            if sx < -50 or sx > W+50 or sy < -50 or sy > H+50: continue
            r, g, b = p.col
            if p.glow and sz >= 2:
                gs = pygame.Surface((sz*6, sz*6), pygame.SRCALPHA)
                pygame.draw.circle(gs, (r, g, b, max(1, a//5)), (sz*3, sz*3), sz*3)
                pygame.draw.circle(gs, (r, g, b, max(1, a//2)), (sz*3, sz*3), sz*2)
                pygame.draw.circle(gs, (min(255,r+40), min(255,g+40), min(255,b+40), max(1,a)),
                                   (sz*3, sz*3), sz)
                surf.blit(gs, (sx-sz*3, sy-sz*3), special_flags=pygame.BLEND_RGBA_ADD)
            else:
                if sz >= 2:
                    s2 = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
                    pygame.draw.circle(s2, (r, g, b, a), (sz, sz), sz)
                    surf.blit(s2, (sx-sz, sy-sz))
                else:
                    if 0 <= sx < W and 0 <= sy < H:
                        pygame.draw.circle(surf, (r, g, b), (sx, sy), 1)

parts = ParticleSystem()

# ── Rain System ──────────────────────────────────────────────────────────────
class Rain:
    def __init__(self, n=600):
        self.drops = []
        for _ in range(n):
            self.drops.append([random.uniform(-100, W+200), random.uniform(-H, H),
                              random.uniform(0.4, 2.0)])
    def update(self, dt, wind=2.5):
        for d in self.drops:
            d[1] += d[2] * 520 * dt
            d[0] += wind * d[2] * 30 * dt
            if d[1] > H + 20:
                d[1] = random.uniform(-80, -5)
                d[0] = random.uniform(-100, W + 200)
    def draw(self, surf, alpha=80, wind=2.5):
        rl = pygame.Surface((W, H), pygame.SRCALPHA)
        for x, y, spd in self.drops:
            a = int(alpha * spd * 0.5); l = int(20 * spd)
            if a < 3: continue
            pygame.draw.line(rl, (155, 190, 235, min(255, a)),
                            (int(x), int(y)), (int(x - wind*l*0.06), int(y+l)), 1)
        surf.blit(rl, (0, 0))

rain = Rain()

# ── Glow / Visual Helpers ───────────────────────────────────────────────────
def glow(surf, x, y, r, col, alpha=140, add=True):
    if r < 2 or alpha < 3: return
    r = int(r)
    gs = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    cr, cg, cb = col[:3]
    steps = max(2, r // 6)
    for i in range(r, 0, -max(1, r // steps)):
        t2 = i / r; a = int(alpha * (1 - t2) ** 1.6)
        pygame.draw.circle(gs, (cr, cg, cb, max(0, min(255, a))), (r+1, r+1), i)
    flag = pygame.BLEND_RGBA_ADD if add else 0
    surf.blit(gs, (int(x)-r-1, int(y)-r-1), special_flags=flag)

def glowing_line(surf, p1, p2, col, w=3, gr=24, alpha=200):
    cr, cg, cb = col[:3]
    for gw, ga in [(gr, alpha//5), (gr//2, alpha//2), (w*2, alpha), (w, 255)]:
        if gw < 1: continue
        gs = pygame.Surface((W, H), pygame.SRCALPHA)
        bright = (gw == w)
        dc = (min(255, cr+60) if bright else cr,
              min(255, cg+60) if bright else cg,
              min(255, cb+60) if bright else cb,
              max(1, min(255, int(ga))))
        pygame.draw.line(gs, dc, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), gw)
        surf.blit(gs, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

def lens_flare(surf, cx, cy, intensity=1.0, col=(255,200,120)):
    if intensity < 0.05: return
    r, g, b = col[:3]; a_base = int(255 * intensity)
    sw = int(350 * intensity); sh = int(4 * intensity) + 1
    streak = pygame.Surface((sw*2, sh*4+2), pygame.SRCALPHA)
    for i in range(sh*2, 0, -1):
        t2 = i / (sh * 2)
        pygame.draw.rect(streak, (r, g, b, int(a_base*t2**2*0.5)),
                         (0, sh*2-i, sw*2, i*2))
    surf.blit(streak, (cx-sw, cy-sh*2), special_flags=pygame.BLEND_RGBA_ADD)
    glow(surf, cx, cy, int(25*intensity), (255,255,255), a_base, True)
    glow(surf, cx, cy, int(55*intensity), col, int(a_base*0.6), True)
    for dist_f, sz, am in [(0.15, 12, 0.35), (0.25, 8, 0.25), (0.4, 6, 0.2)]:
        fx = cx + int((cx - W//2) * dist_f); fy = cy
        gs2 = pygame.Surface((sz*4, sz*4), pygame.SRCALPHA)
        a2 = int(a_base * am)
        pygame.draw.circle(gs2, (r, g, min(255, b+50), min(255, a2)), (sz*2, sz*2), sz*2)
        surf.blit(gs2, (fx-sz*2, fy-sz*2), special_flags=pygame.BLEND_RGBA_ADD)

def draw_god_rays(surf, cx, cy, n_rays=6, alpha=20, col=(255,240,200), length=800):
    rs = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(n_rays):
        base_a = math.radians(-90 + (i - n_rays/2) * (50/n_rays))
        w2 = random.randint(5, 20)
        pts = [(cx-w2, cy), (cx+w2, cy),
               (int(cx+math.cos(base_a+0.06)*length), int(cy+math.sin(base_a+0.06)*length)),
               (int(cx+math.cos(base_a-0.06)*length), int(cy+math.sin(base_a-0.06)*length))]
        pygame.draw.polygon(rs, (*col, min(255, alpha)), pts)
    surf.blit(rs, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

def vignette(surf, strength=100):
    v = pygame.Surface((W, H), pygame.SRCALPHA)
    max_r = max(W, H) // 2
    for r in range(max_r, 0, -6):
        t2 = 1 - r / max_r
        a = int(strength * t2 ** 2.5)
        if a > 0:
            pygame.draw.ellipse(v, (0, 0, 0, min(255, a)),
                               (W//2-r, H//2-r, r*2, r*2), 6)
    surf.blit(v, (0, 0))

def letterbox(surf, h=70, alpha=255):
    lb = pygame.Surface((W, h)); lb.fill((0, 0, 0)); lb.set_alpha(min(255, alpha))
    surf.blit(lb, (0, 0)); surf.blit(lb, (0, H - h))

def flash_screen(surf, col, alpha):
    if alpha < 4: return
    fs = pygame.Surface((W, H)); fs.fill(col[:3]); fs.set_alpha(min(255, int(alpha)))
    surf.blit(fs, (0, 0))

def fade_black(surf, alpha):
    if alpha < 4: return
    fs = pygame.Surface((W, H)); fs.fill((0, 0, 0)); fs.set_alpha(min(255, int(alpha)))
    surf.blit(fs, (0, 0))

# ── Sky / Environment ───────────────────────────────────────────────────────
def draw_sky(surf, top, bot, mid=None, mid_pos=0.45):
    h = int(H * 0.7)
    for y in range(h):
        f = y / h
        if mid and f < mid_pos:
            c = lc(top, mid, f / mid_pos)
        elif mid:
            c = lc(mid, bot, (f - mid_pos) / (1 - mid_pos))
        else:
            c = lc(top, bot, f)
        pygame.draw.line(surf, c, (0, y), (W, y))

def draw_stars(surf, t, count=120, alpha_mult=1.0):
    for i in range(count):
        sx = (i * 347 + 13) % W; sy = (i * 211 + 7) % int(H * 0.55)
        sa = int(alpha_mult * 80 * (0.5 + 0.5 * math.sin(t * 0.4 + i * 0.7)))
        if sa > 5:
            sz = 1 if i % 7 != 0 else 2
            pygame.draw.circle(surf, (200, 210, 240), (sx, sy), sz)

def draw_moon(surf, x, y, r, t):
    pygame.draw.circle(surf, (210, 220, 235), (x, y), r)
    pygame.draw.circle(surf, (190, 200, 218), (x + r//4, y - r//5), int(r * 0.8))
    glow(surf, x, y, r + 35, (200, 220, 255), 20, True)

def draw_ground(surf, gy, col=(20, 16, 28), wet=True):
    pygame.draw.rect(surf, col, (0, gy, W, H - gy))
    if wet:
        for y in range(gy, min(H, gy + 50)):
            a = int(60 * (1 - (y - gy) / 50))
            sh = int(6 * math.sin(y * 0.3) * a // max(1, 60))
            pygame.draw.line(surf, (30+sh, 26+sh, 44+sh), (0, y), (W, y))

def draw_city_silhouette(surf, gy, scroll=0):
    buildings = [
        (60,200),(110,160),(150,220),(190,140),(240,180),(290,130),(340,190),
        (390,160),(440,210),(500,140),(550,180),(610,200),(660,150),(720,170),
        (780,210),(840,155),(900,190),(960,170),(1020,220),(1080,160),(1140,200),
        (1200,180),(1260,150),(1320,210),(1400,190),
    ]
    for bx, bh in buildings:
        sx = int(bx - scroll * 0.12)
        if sx < -50 or sx > W + 50: continue
        depth = min(1.0, bh / 220)
        fog = int(22 + 18 * depth)
        bc = (12 + fog//3, 10 + fog//4, 18 + fog//2)
        pygame.draw.rect(surf, bc, (sx, gy - bh, 40, bh))
        pygame.draw.rect(surf, (min(255,bc[0]+8), min(255,bc[1]+8), min(255,bc[2]+8)),
                        (sx, gy - bh, 40, 4))
        for wy in range(gy - bh + 12, gy - 10, 16):
            for wx in range(sx + 6, sx + 34, 10):
                if (wx * 7 + wy * 13 + int(scroll)) % 19 < 4:
                    wc = [(255,210,140),(200,220,255),(255,180,80)][(wx+wy)%3]
                    wl = pygame.Surface((5, 7), pygame.SRCALPHA)
                    pygame.draw.rect(wl, (*wc, 100), (0, 0, 5, 7))
                    surf.blit(wl, (wx, wy), special_flags=pygame.BLEND_RGBA_ADD)

# ── Cloud System ─────────────────────────────────────────────────────────────
class CloudSystem:
    def __init__(self):
        self.layers = []
        for layer in range(3):
            cl = []
            for _ in range(6 + layer * 3):
                cl.append({
                    'x': random.uniform(-200, W + 200),
                    'y': random.uniform(50 + layer * 35, 180 + layer * 55),
                    'rx': random.uniform(100, 280),
                    'ry': random.uniform(25, 75),
                    'alpha': random.uniform(0.25, 0.7),
                    'drift': random.uniform(-10, 10),
                    'phase': random.uniform(0, τ),
                })
            self.layers.append(cl)

    def draw(self, surf, t, flash_amt=0.0):
        for li, layer in enumerate(self.layers):
            for cloud in layer:
                cx = cloud['x'] + math.sin(t * 0.025 + cloud['phase']) * cloud['drift']
                cy = cloud['y']
                rx, ry = int(cloud['rx']), int(cloud['ry'])
                a = int(cloud['alpha'] * 140 * (1 + flash_amt * 0.4))
                a = min(255, a)
                col_data = [
                    ((35,30,55), 0.4), ((70,62,100), 0.7), ((130,120,170), 1.0)
                ]
                for (pc, pa_m), pr in zip(col_data, [1.0, 0.8, 0.6]):
                    w2 = max(1, int(rx*2*pr)); h2 = max(1, int(ry*2*pr))
                    cs = pygame.Surface((w2+4, h2+4), pygame.SRCALPHA)
                    pygame.draw.ellipse(cs, (*pc, int(a*pa_m)), (0, 0, w2, h2))
                    surf.blit(cs, (int(cx-rx*pr), int(cy-ry*pr)), special_flags=pygame.BLEND_RGBA_ADD)
                if flash_amt > 0.1:
                    w3 = max(1, rx*2); h3 = max(1, ry*2)
                    lg = pygame.Surface((w3+4, h3+4), pygame.SRCALPHA)
                    pygame.draw.ellipse(lg, (190,195,255, int(flash_amt*180*cloud['alpha'])),
                                       (0, 0, w3, h3))
                    surf.blit(lg, (int(cx-rx), int(cy-ry)), special_flags=pygame.BLEND_RGBA_ADD)

clouds = CloudSystem()

# ── Shockwave System ────────────────────────────────────────────────────────
shockwaves = []
def add_shockwave(x, y, col=(255,200,100), speed=800):
    shockwaves.append({'x':x,'y':y,'r':0,'life':0.8,'ml':0.8,'col':col,'spd':speed})

def update_shockwaves(dt):
    dead = []
    for s in shockwaves:
        s['r'] += s['spd'] * dt; s['life'] -= dt
        if s['life'] <= 0: dead.append(s)
    for d in dead: shockwaves.remove(d)

def draw_shockwaves(surf, cam_obj=None):
    for s in shockwaves:
        t2 = s['life'] / s['ml']; a = int(200 * t2**2)
        if a < 4 or s['r'] < 2: continue
        if cam_obj:
            sx, sy = cam_obj.world_to_screen(s['x'], s['y'])
            r = int(s['r'] * cam_obj.zoom)
        else:
            sx, sy = int(s['x']), int(s['y']); r = int(s['r'])
        if r < 2: continue
        cr, cg, cb = s['col']
        w2 = r*2+4; h2 = max(1, r//2+4)
        rs2 = pygame.Surface((w2, h2), pygame.SRCALPHA)
        ew = max(1, r*2+2); eh = max(1, r//3+2)
        pygame.draw.ellipse(rs2, (cr, cg, cb, min(255, a)), (0, 0, ew, eh), max(1, 3-int(t2*3)))
        surf.blit(rs2, (sx-r-1, sy-r//6), special_flags=pygame.BLEND_RGBA_ADD)

# ── Lightning ────────────────────────────────────────────────────────────────
lightning_bolts = []
thunder_flash = 0.0

def trigger_lightning(x, y_start, y_end):
    segs = []; x_ = x
    steps = random.randint(7, 13)
    for i in range(steps):
        nx = x_ + random.randint(-35, 35)
        ny = int(lerp(y_start, y_end, i / steps))
        segs.append((int(x_), ny, nx, int(lerp(y_start, y_end, (i+1)/steps))))
        x_ = nx
    lightning_bolts.append({'segs': segs, 'life': 0.16, 'ml': 0.16})

def draw_lightning_bolts(surf):
    dead = []
    for b in lightning_bolts:
        t2 = b['life'] / b['ml']; a = int(200 * t2**0.5)
        for x1, y1, x2, y2 in b['segs']:
            glowing_line(surf, (x1, y1), (x2, y2), (175, 195, 255), 2, 25, a)
        b['life'] -= 0.016
        if b['life'] <= 0: dead.append(b)
    for d in dead: lightning_bolts.remove(d)


# ══════════════════════════════════════════════════════════════════════════════
# ── CHARACTER DRAWING ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def draw_kid(surf, cx, cy, sc=1.0, facing=1, pose='walk', t=0, alpha=255, walk_phase=0):
    TW, TH = 120, 160
    s = pygame.Surface((TW, TH), pygame.SRCALPHA)
    ox, oy = 60, TH - 8

    bob = math.sin(walk_phase * 4.5) * 3 if pose == 'walk' else (math.sin(t*1.8)*1.5 if pose == 'stand' else 0)
    breathe = math.sin(t * 1.4) * 1

    # Shadow
    pygame.draw.ellipse(s, (0,0,0,40), (ox-18, oy-4, 36, 8))

    # Legs
    leg_col = (50, 45, 60); boot_col = (25, 22, 35)
    if pose == 'walk':
        l_off = math.sin(walk_phase * 4.5) * 8
        r_off = math.sin(walk_phase * 4.5 + PI) * 8
        for lx, lo in [(-8, l_off), (4, r_off)]:
            pygame.draw.rect(s, leg_col, (ox+lx, oy-38+int(lo*0.3), 8, 38-int(abs(lo)*0.2)))
            pygame.draw.rect(s, boot_col, (ox+lx-2, oy-8, 12, 10))
    elif pose == 'aim':
        pygame.draw.rect(s, leg_col, (ox-14, oy-38, 8, 38))
        pygame.draw.rect(s, boot_col, (ox-16, oy-8, 12, 10))
        pygame.draw.rect(s, leg_col, (ox+6, oy-38, 8, 38))
        pygame.draw.rect(s, boot_col, (ox+4, oy-8, 12, 10))
    else:
        for lx in [-8, 4]:
            pygame.draw.rect(s, leg_col, (ox+lx, oy-38, 8, 38))
            pygame.draw.rect(s, boot_col, (ox+lx-2, oy-8, 12, 10))

    # Body
    by = oy - 70 + int(bob) + int(breathe)
    jacket = (45, 75, 140); jacket_hi = (65, 100, 180)
    pygame.draw.rect(s, jacket, (ox-14, by, 28, 38))
    pygame.draw.rect(s, jacket_hi, (ox-14, by, 28, 8))
    # Belt
    pygame.draw.rect(s, (40, 35, 25), (ox-14, by+30, 28, 5))
    pygame.draw.rect(s, (180, 150, 30), (ox-3, by+30, 6, 5))

    # Scarf
    scarf = (200, 40, 40); scarf_hi = (240, 70, 60)
    flutter = math.sin(t * 3.5 + walk_phase) * 5 * facing
    pygame.draw.rect(s, scarf, (ox-16, by-3, 32, 10))
    pygame.draw.rect(s, scarf_hi, (ox-16, by-3, 32, 4))
    pygame.draw.polygon(s, scarf, [
        (ox-4, by+8), (ox-14+int(flutter), by+28),
        (ox-6+int(flutter), by+32), (ox+2, by+12)])
    pygame.draw.polygon(s, scarf, [
        (ox+2, by+6), (ox+16+int(flutter*1.2), by+24),
        (ox+8+int(flutter*1.2), by+30), (ox+6, by+10)])

    # Arms
    arm_col = (48, 78, 145); glove_col = (22, 22, 38)
    if pose == 'aim' and facing >= 0:
        pygame.draw.polygon(s, arm_col, [(ox+8, by+10), (ox+28, by+16), (ox+28, by+24), (ox+8, by+22)])
        pygame.draw.rect(s, glove_col, (ox+24, by+14, 8, 12))
        pygame.draw.polygon(s, arm_col, [(ox-6, by+12), (ox+20, by+18), (ox+20, by+26), (ox-6, by+24)])
        pygame.draw.rect(s, glove_col, (ox+16, by+16, 8, 12))
    elif pose == 'aim':
        pygame.draw.polygon(s, arm_col, [(ox-8, by+10), (ox-28, by+16), (ox-28, by+24), (ox-8, by+22)])
        pygame.draw.rect(s, glove_col, (ox-32, by+14, 8, 12))
        pygame.draw.polygon(s, arm_col, [(ox+6, by+12), (ox-20, by+18), (ox-20, by+26), (ox+6, by+24)])
        pygame.draw.rect(s, glove_col, (ox-24, by+16, 8, 12))
    elif pose == 'sad':
        pygame.draw.polygon(s, arm_col, [(ox-14, by+8), (ox-16, by+32), (ox-10, by+32), (ox-8, by+8)])
        pygame.draw.rect(s, glove_col, (ox-18, by+28, 10, 8))
        pygame.draw.polygon(s, arm_col, [(ox+8, by+8), (ox+10, by+32), (ox+16, by+32), (ox+14, by+8)])
        pygame.draw.rect(s, glove_col, (ox+8, by+28, 10, 8))
    else:
        sw = math.sin(walk_phase * 4.5) * 6 if pose == 'walk' else 0
        pygame.draw.polygon(s, arm_col, [(ox-14, by+8), (ox-18+int(sw), by+28),
                                         (ox-12+int(sw), by+30), (ox-8, by+12)])
        pygame.draw.rect(s, glove_col, (ox-20+int(sw), by+26, 8, 8))
        pygame.draw.polygon(s, arm_col, [(ox+8, by+8), (ox+12-int(sw), by+28),
                                         (ox+18-int(sw), by+30), (ox+14, by+12)])
        pygame.draw.rect(s, glove_col, (ox+10-int(sw), by+26, 8, 8))

    # Head
    hy = by - 36
    pygame.draw.rect(s, (200, 162, 125), (ox-3, hy+32, 6, 8))
    pygame.draw.ellipse(s, (218, 175, 132), (ox-16, hy, 32, 36))
    pygame.draw.polygon(s, (218, 175, 132), [(ox-8, hy+32), (ox+8, hy+32), (ox, hy+38)])

    # Hair
    hair = (38, 28, 18)
    pygame.draw.ellipse(s, hair, (ox-18, hy-5, 36, 20))
    spikes = [-14, -7, 0, 7, 14]
    for i, sx2 in enumerate(spikes):
        h2 = 14 + abs(i - 2) * 5 + int(math.sin(t + i) * 2)
        pygame.draw.polygon(s, hair, [(ox+sx2-4, hy+3), (ox+sx2+4, hy+3), (ox+sx2, hy - h2)])
    pygame.draw.rect(s, hair, (ox + (-20 if facing >= 0 else 12), hy + 4, 8, 22))

    # Eyes
    ew, eh = 11, 10
    if pose == 'sad':
        for ex in [ox - 8, ox + 4]:
            ey = hy + 14
            pygame.draw.ellipse(s, (240, 248, 255), (ex-ew//2, ey-eh//2+2, ew, eh-3))
            pygame.draw.ellipse(s, (50, 90, 200), (ex-4, ey-2, 8, 8))
            pygame.draw.circle(s, (15, 12, 40), (ex, ey+1), 3)
            pygame.draw.circle(s, (255, 255, 255), (ex-2, ey-1), 2)
            pygame.draw.arc(s, hair, pygame.Rect(ex-ew//2, ey-eh//2, ew, eh), 0.2, PI-0.2, 3)
    else:
        for ex in [ox - 8, ox + 4]:
            ey = hy + 14
            pygame.draw.ellipse(s, (240, 248, 255), (ex-ew//2, ey-eh//2, ew, eh))
            iris = (55, 110, 220) if pose != 'aim' else (80, 150, 255)
            pygame.draw.ellipse(s, iris, (ex-4, ey-eh//2+1, 8, eh-2))
            pygame.draw.circle(s, (18, 15, 45), (ex, ey+1), 3)
            pygame.draw.circle(s, (255, 255, 255), (ex-2, ey-1), 2)
            pygame.draw.circle(s, (255, 255, 255), (ex+2, ey+2), 1)
            brow_y = ey - eh//2 - 3
            if pose == 'aim':
                pygame.draw.line(s, hair, (ex-5, brow_y-1), (ex+5, brow_y+1), 2)
            else:
                pygame.draw.line(s, hair, (ex-5, brow_y), (ex+5, brow_y), 2)

    # Mouth
    if pose == 'sad':
        pygame.draw.arc(s, (170, 110, 90), pygame.Rect(ox-5, hy+26, 10, 6), 0, PI, 2)
    elif pose == 'aim':
        pygame.draw.line(s, (170, 110, 90), (ox-4, hy+28), (ox+4, hy+28), 2)
    else:
        pygame.draw.arc(s, (170, 110, 90), pygame.Rect(ox-4, hy+24, 8, 5), PI, τ, 2)

    # Ear
    ear_x = ox + (14 if facing >= 0 else -16)
    pygame.draw.ellipse(s, (208, 165, 122), (ear_x, hy+10, 6, 10))

    if sc != 1.0:
        nw, nh = max(1, int(TW * sc)), max(1, int(TH * sc))
        s = pygame.transform.smoothscale(s, (nw, nh))
    if facing < 0:
        s = pygame.transform.flip(s, True, False)
    s.set_alpha(min(255, alpha))
    surf.blit(s, (int(cx - TW*sc//2), int(cy - TH*sc + 8*sc)))


def draw_droid(surf, cx, cy, sc=1.0, t=0, alpha=255, state='normal', transform_t=0):
    TW, TH = 90, 110
    s = pygame.Surface((TW, TH), pygame.SRCALPHA)
    ox, oy = 45, 75

    hover = math.sin(t * 2.5) * 5
    morph = clamp(transform_t, 0, 1)

    if morph < 0.5:
        m = morph * 2

        # Thrust glow
        ta = int((100 + 60*math.sin(t*5)) * (1 - m))
        te = pygame.Surface((36, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(te, (0, 160, 255, min(255, ta)), (0, 0, 36, 16))
        s.blit(te, (ox-18, oy-8+int(hover)), special_flags=pygame.BLEND_RGBA_ADD)

        body_col = (50, 90, 148)
        body_hi = (78, 130, 205)

        body_w = max(1, int(lerp(36, 50, m)))
        body_h = max(1, int(lerp(32, 16, m)))
        pygame.draw.ellipse(s, body_col, (ox-body_w//2, oy-55+int(hover), body_w, body_h))
        pygame.draw.ellipse(s, body_hi, (ox-body_w//2, oy-55+int(hover), body_w, max(1, body_h//3)))

        # Core light
        core_pulse = int(180 + 75 * math.sin(t * 3.2))
        core_r = max(1, int(6*(1-m)))
        pygame.draw.circle(s, (0, core_pulse, 255), (ox, oy-40+int(hover)), core_r)
        small_r = max(1, int(3*(1-m)))
        pygame.draw.circle(s, (150, 220, 255), (ox, oy-40+int(hover)), small_r)

        # Core glow
        cg = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(cg, (0, 180, 255, int(60*(1-m))), (15, 15), 15)
        s.blit(cg, (ox-15, oy-55+int(hover)), special_flags=pygame.BLEND_RGBA_ADD)

        # Arms
        for sign in [-1, 1]:
            ax = ox + sign * int(lerp(20, 25, m))
            arm_r = max(1, int(5*(1-m)))
            pygame.draw.circle(s, (58, 100, 162), (ax, oy-42+int(hover)), arm_r)
            arm_h = max(1, int(14*(1-m)))
            pygame.draw.rect(s, (46, 84, 140), (ax-3, oy-40+int(hover), 6, arm_h))

        # Head
        head_h = max(1, int(lerp(30, 15, m)))
        pygame.draw.ellipse(s, (42, 78, 132), (ox-14, oy-80+int(hover), 28, head_h))
        pygame.draw.ellipse(s, (66, 112, 180), (ox-14, oy-80+int(hover), 28, max(1, head_h//3)))

        # Eyes
        if m < 0.3:
            blink = 1 if math.sin(t*2.0) > 0.94 else 0
            for ex in [ox-8, ox+8]:
                ey = oy-68+int(hover)
                r_eye = 5
                if state == 'sad':
                    pygame.draw.circle(s, (0, 180, 220), (ex, ey), r_eye)
                    pygame.draw.circle(s, (80, 210, 240), (ex, ey), r_eye-2)
                    cover = pygame.Surface((r_eye*2+2, r_eye+2), pygame.SRCALPHA)
                    pygame.draw.rect(cover, (42, 78, 132, 200), (0, 0, r_eye*2+2, r_eye))
                    s.blit(cover, (ex-r_eye-1, ey-r_eye-1))
                elif not blink:
                    pygame.draw.circle(s, (0, 210, 255), (ex, ey), r_eye)
                    pygame.draw.circle(s, (100, 235, 255), (ex, ey), r_eye-2)
                    pygame.draw.circle(s, (255, 255, 255), (ex-2, ey-2), 2)
                    eg = pygame.Surface((r_eye*4, r_eye*4), pygame.SRCALPHA)
                    pygame.draw.circle(eg, (0, 190, 255, 45), (r_eye*2, r_eye*2), r_eye*2)
                    s.blit(eg, (ex-r_eye*2, ey-r_eye*2), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    pygame.draw.line(s, (0, 170, 210), (ex-r_eye, ey), (ex+r_eye, ey), 2)

            # Antenna
            pygame.draw.line(s, (66, 110, 180), (ox, oy-80+int(hover)), (ox, oy-95+int(hover)), 2)
            ant_p = int(180 + 75*math.sin(t*5))
            pygame.draw.circle(s, (0, ant_p, 255), (ox, oy-97+int(hover)), 4)

    else:
        m = (morph - 0.5) * 2
        gun_w = max(1, int(lerp(30, 80, m)))
        gun_h = max(1, int(lerp(20, 18, m)))

        gc_dark = (24, 28, 42); gc_mid = (40, 48, 68); gc_hi = (60, 78, 110)
        energy = (80, 200, 255) if m < 0.8 else (int(lerp(80,180,m)), int(lerp(200,240,m)), 255)

        # Main barrel
        pygame.draw.rect(s, gc_dark, (ox-gun_w//2, oy-50+int(hover*0.3), gun_w, gun_h))
        pygame.draw.rect(s, gc_mid, (ox-gun_w//2, oy-50+int(hover*0.3), gun_w, max(1, gun_h//3)))

        # Extended barrel
        if m > 0.3:
            ext = max(1, int(40 * (m - 0.3) / 0.7))
            pygame.draw.rect(s, gc_dark, (ox+gun_w//2, oy-46+int(hover*0.3), ext, 10))
            pygame.draw.rect(s, gc_mid, (ox+gun_w//2, oy-46+int(hover*0.3), ext, 4))
            glow_r = max(1, int(8 * m))
            eg2 = pygame.Surface((glow_r*4, glow_r*4), pygame.SRCALPHA)
            pygame.draw.circle(eg2, (*energy, int(150*m)), (glow_r*2, glow_r*2), glow_r*2)
            s.blit(eg2, (ox+gun_w//2+ext-glow_r*2, oy-42+int(hover*0.3)-glow_r*2),
                   special_flags=pygame.BLEND_RGBA_ADD)

        # Scope
        pygame.draw.rect(s, gc_hi, (ox-gun_w//4, oy-56+int(hover*0.3), max(1, gun_w//2), 6))
        # Energy cell
        cell_a = int(200 * m)
        pygame.draw.rect(s, (*energy, min(255, cell_a)), (ox-8, oy-48+int(hover*0.3), 16, max(1, gun_h-4)))

        # Core eye remnant
        eye_sz = max(1, int(lerp(5, 3, m)))
        core_col = (0, int(lerp(210, 255, m)), 255)
        pygame.draw.circle(s, core_col, (ox-gun_w//4, oy-42+int(hover*0.3)), eye_sz)
        pygame.draw.circle(s, (200, 240, 255), (ox-gun_w//4, oy-42+int(hover*0.3)), max(1, eye_sz-2))

    if sc != 1.0:
        nw, nh = max(1, int(TW * sc)), max(1, int(TH * sc))
        s = pygame.transform.smoothscale(s, (nw, nh))
    s.set_alpha(min(255, alpha))
    surf.blit(s, (int(cx - TW*sc//2), int(cy - TH*sc + 8*sc)))


def draw_giant_robot(surf, cx, cy, sc=1.0, damage=0.0, t=0.0, panel_open=0.0):
    TW, TH = 480, 860
    s = pygame.Surface((TW + 80, TH + 60), pygame.SRCALPHA)
    ox, oy = TW // 2 + 40, TH + 30
    wob   = math.sin(t * 0.65) * 4 * (1 - damage)
    pulse = math.sin(t * 2.8)
    hpulse = math.sin(t * 1.4)

    # ── Palette (Optimus Prime / heavy Autobot) ───────────────────────────
    R1  = (195, 28, 18)    # primary red
    R2  = (240, 58, 38)    # red highlight
    R3  = (108, 14, 8)     # red shadow
    B1  = (24,  48, 112)   # primary blue
    B2  = (48,  85, 175)   # blue highlight
    B3  = (12,  24,  62)   # blue shadow
    CH  = (158, 168, 188)  # chrome
    CHL = (218, 226, 240)  # chrome light
    DK  = (22,  26,  38)   # dark metal
    MD  = (42,  48,  66)   # mid metal
    SLV = (110, 118, 135)  # silver
    XST = (48,  52,  68)   # exhaust
    WGL = (28,  58, 118)   # windshield glass
    WGH = (55, 105, 190)   # windshield highlight
    EYE = (30, 175, 255)   # Autobot blue eyes
    EYG = (80, 210, 255)   # eye glow

    def sr(x, y, w, h, col=MD):
        if w < 1 or h < 1: return
        px = int(ox + x * sc); py = int(oy - y * sc)
        pw = max(1, int(w * sc)); ph = max(1, int(h * sc))
        pygame.draw.rect(s, col, (px, py, pw, ph))
        hi = (min(255, col[0]+30), min(255, col[1]+30), min(255, col[2]+30))
        sh = (max(0,   col[0]-28), max(0,   col[1]-28), max(0,   col[2]-28))
        pygame.draw.rect(s, hi, (px, py, pw, max(1, ph // 5)))
        pygame.draw.rect(s, sh, (px, py + ph - max(1, ph // 6), pw, max(1, ph // 6)))

    def sc2(x, y, r, col):
        if r < 1: return
        pygame.draw.circle(s, col, (int(ox + x*sc), int(oy - y*sc)), max(1, int(r*sc)))

    def poly(pts, col):
        sp = [(int(ox + x*sc), int(oy - y*sc)) for x, y in pts]
        if len(sp) >= 3:
            pygame.draw.polygon(s, col, sp)

    def line(x1, y1, x2, y2, col, w=1):
        pygame.draw.line(s, col,
            (int(ox + x1*sc), int(oy - y1*sc)),
            (int(ox + x2*sc), int(oy - y2*sc)),
            max(1, int(w*sc)))

    # ════════════════════════════════════════════════════════════════════
    # FEET — massive armored boots
    # ════════════════════════════════════════════════════════════════════
    for sign in [-1, 1]:
        fx = sign * 92
        # Boot base plate (wide, flat)
        sr(fx - 46, 0, 92, 18, DK)
        sr(fx - 50 + sign*4, 0, 100, 28, MD)
        sr(fx - 44, 5, 88, 10, CH)        # chrome toe strip
        # Main boot body
        sr(fx - 38, 18, 76, 62, DK)
        sr(fx - 34, 22, 68, 54, B1)
        sr(fx - 32, 24, 64, 20, B2)       # upper highlight
        # Ankle armour fin
        poly([(fx + sign*36, 80), (fx + sign*52, 55), (fx + sign*52, 80)], R1)
        poly([(fx + sign*36, 80), (fx + sign*50, 58), (fx + sign*50, 80)], R2)
        # Boot rivets
        for rx2 in [-22, -8, 8, 22]:
            sc2(fx + rx2, 14, 3, CH)

    # ════════════════════════════════════════════════════════════════════
    # LOWER LEGS — thick, panelled shins
    # ════════════════════════════════════════════════════════════════════
    for sign in [-1, 1]:
        lx = sign * 88
        wo = wob * sign * 0.18
        # Shin core
        sr(lx - 32, 78 + wo, 64, 168, DK)
        sr(lx - 28, 82 + wo, 56, 160, B1)
        # Front shin plate (red stripe)
        sr(lx - 20, 95 + wo, 40, 120, R1)
        sr(lx - 18, 97 + wo, 36, 40,  R2)  # upper shine
        # Side armor panels
        sr(lx + sign*22, 88 + wo, 22, 130, B3)
        sr(lx + sign*22, 88 + wo, 22, 24,  B2)
        # Horizontal ribbing
        for ry in range(110, 230, 22):
            sr(lx - 30, ry + wo, 60, 7, CH)
        # Exhaust vents (back side)
        for ev in range(3):
            sr(lx - sign*28 - 4, 100 + ev*28 + wo, 12, 16, XST)
            line(lx - sign*24, 104 + ev*28 + wo,
                 lx - sign*24, 112 + ev*28 + wo, DK, 1)

    # ════════════════════════════════════════════════════════════════════
    # KNEES — large armored knee caps
    # ════════════════════════════════════════════════════════════════════
    for sign in [-1, 1]:
        kx = sign * 88
        wo = wob * sign * 0.18
        sc2(kx, 248 + wo, 36, R3)
        sc2(kx, 248 + wo, 28, R1)
        sc2(kx, 248 + wo, 18, R2)
        sc2(kx, 248 + wo, 7,  CH)
        # Knee side guards
        poly([(kx - sign*14, 218 + wo), (kx - sign*44, 230 + wo),
              (kx - sign*44, 270 + wo), (kx - sign*14, 278 + wo)], DK)
        poly([(kx - sign*16, 220 + wo), (kx - sign*42, 232 + wo),
              (kx - sign*42, 268 + wo), (kx - sign*16, 276 + wo)], MD)
        # Knee hydraulic pins
        for kp in [-12, 12]:
            sc2(kx + kp*sign*0, 260 + wo, 4, CHL)

    # ════════════════════════════════════════════════════════════════════
    # UPPER LEGS / THIGHS
    # ════════════════════════════════════════════════════════════════════
    for sign in [-1, 1]:
        ux = sign * 82
        wo = wob * sign * 0.14
        # Thigh main
        sr(ux - 34, 270 + wo, 68, 138, B3)
        sr(ux - 30, 274 + wo, 60, 130, B1)
        sr(ux - 26, 278 + wo, 52, 46,  B2)  # top shine
        # Front thigh plate
        sr(ux - 22, 280 + wo, 44, 90, R1)
        sr(ux - 20, 282 + wo, 40, 28, R2)
        # Hydraulic pistons
        line(ux + sign*22, 290 + wo, ux + sign*22, 365 + wo, SLV, 3)
        sc2(ux + sign*22, 290 + wo, 7, CH)
        sc2(ux + sign*22, 365 + wo, 7, CH)
        sc2(ux + sign*22, 330 + wo, 5, CHL)  # mid bearing
        # Thigh ribs
        for ty in range(310, 390, 20):
            sr(ux - 28, ty + wo, 56, 5, MD)

    # ════════════════════════════════════════════════════════════════════
    # HIP / PELVIS
    # ════════════════════════════════════════════════════════════════════
    sr(-105, 408, 210, 68, DK)
    sr(-98,  413, 196, 58, R3)
    sr(-90,  416, 180, 50, R1)
    sr(-86,  418, 172, 22, R2)   # top highlight
    # Center crotch plate
    sr(-26, 412, 52, 58, B3)
    sr(-22, 416, 44, 50, B1)
    sr(-18, 418, 36, 18, B2)
    # Hip flares / side spikes
    for sign in [-1, 1]:
        poly([(sign*88, 408), (sign*110, 388), (sign*106, 408)], CH)
        poly([(sign*80, 412), (sign*110, 392), (sign*88,  412)], SLV)
        # Hip vent slots
        for hv in range(3):
            sr(sign*68 - (6 if sign==1 else 0), 420 + hv*12, 14, 7, DK)

    # ════════════════════════════════════════════════════════════════════
    # TORSO — Optimus truck-cab chest
    # ════════════════════════════════════════════════════════════════════
    # Rear torso base
    sr(-108, 476, 216, 292, DK)
    sr(-100, 480, 200, 284, R3)
    sr( -92, 484, 184, 276, R1)
    sr( -88, 486, 176, 36,  R2)  # top chest shine

    # Side blue torso panels
    for sign in [-1, 1]:
        sr(sign*62, 492, 38, 252, B3)
        sr(sign*64, 496, 30, 244, B1)
        sr(sign*64, 496, 30, 28,  B2)
        # Side panel vent slots
        for sv in range(7):
            sr(sign*66, 536 + sv*26, 24, 12, DK)

    # ── Chest grill (lower cab section) ─────────────────────────────────
    sr(-82, 484, 164, 62, DK)
    # Grill bars
    for gx in range(-78, 82, 14):
        sr(gx, 488, 9, 54, MD)
    sr(-82, 484, 164, 9,  CH)   # top bar
    sr(-82, 540, 164, 6,  CH)   # bottom bar
    # Bumper chrome strip
    sr(-88, 476, 176, 10, CH)
    sr(-84, 478, 168, 4,  CHL)

    # ── Windshield / truck glass (iconic Optimus chest windows) ──────────
    # Left glass pane
    poly([(-88, 552), (-18, 572), (-18, 648), (-88, 628)], WGH)
    poly([(-86, 554), (-20, 573), (-20, 646), (-86, 626)], WGL)
    poly([(-82, 558), (-50, 565), (-50, 610), (-82, 602)], (65, 118, 202))  # glare
    # Right glass pane
    poly([(88, 552), (18, 572), (18, 648), (88, 628)], WGH)
    poly([(86, 554), (20, 573), (20, 646), (86, 626)], WGL)
    poly([(82, 558), (50, 565), (50, 610), (82, 602)], (65, 118, 202))
    # Center windshield divider pillar
    sr(-11, 550, 22, 106, DK)
    sr( -8, 553, 16,  98, CH)
    sr( -5, 555, 10,  6,  CHL)

    # ── Matrix of Leadership / energy core ──────────────────────────────
    core_a = int((160 + 55*pulse) * (1 - damage * 0.85))
    if core_a > 8:
        csurf = pygame.Surface((140, 140), pygame.SRCALPHA)
        for cr in range(60, 0, -5):
            ca = int(core_a * (1 - cr/60) ** 1.3)
            rc = (min(255, EYE[0] + int((255-EYE[0])*(1-cr/60))),
                  min(255, EYE[1] + int((255-EYE[1])*(1-cr/60))),
                  255)
            pygame.draw.circle(csurf, (*rc, min(255, ca)), (70, 70), cr)
        s.blit(csurf, (int(ox - 70), int(oy - 620*sc - 70)),
               special_flags=pygame.BLEND_RGBA_ADD)
    # Octagonal matrix frame
    poly([(-18, 596), (-8, 587), (8, 587), (18, 596),
          (18, 610), (8, 619), (-8, 619), (-18, 610)], CH)
    poly([(-14, 598), (-6, 591), (6, 591), (14, 598),
          (14, 608), (6, 615), (-6, 615), (-14, 608)], DK)
    sc2(0, 603, 7, EYE)
    sc2(0, 603, 4, CHL)

    # ── Cockpit panel (cow reveal) ───────────────────────────────────────
    if panel_open > 0:
        hx2 = int(ox - 32*sc); hy2 = int(oy - 696*sc)
        hw  = max(1, int(64*sc)); hh  = max(1, int(72*sc))
        open_h = max(1, int(hh * (1 - panel_open)))
        pygame.draw.rect(s, (28, 34, 52),  (hx2, hy2, hw, open_h))
        pygame.draw.rect(s, (50, 80, 135), (hx2, hy2, hw, open_h), max(1, int(2*sc)))
        if panel_open > 0.3:
            ig = pygame.Surface((hw + 12, hh + 12), pygame.SRCALPHA)
            pygame.draw.rect(ig, (255, 220, 140, int(138 * panel_open)), (0, 0, hw+12, hh+12))
            s.blit(ig, (hx2 - 6, hy2), special_flags=pygame.BLEND_RGBA_ADD)
    else:
        pygame.draw.rect(s, (14, 18, 32),
            (int(ox-32*sc), int(oy-696*sc), max(1,int(64*sc)), max(1,int(72*sc))))
        pygame.draw.rect(s, (50, 80, 135),
            (int(ox-32*sc), int(oy-696*sc), max(1,int(64*sc)), max(1,int(72*sc))),
            max(1, int(2*sc)))

    # ════════════════════════════════════════════════════════════════════
    # SHOULDER PAULDRONS — massive Optimus-style
    # ════════════════════════════════════════════════════════════════════
    for sign in [-1, 1]:
        spx = sign * 150
        wo = wob * sign * 0.32
        # Pauldron base
        poly([(sign*98, 700+wo), (spx+sign*46, 720+wo),
              (spx+sign*46, 640+wo), (sign*98, 630+wo)], DK)
        # Main shoulder block
        sr(spx - 28, 642 + wo, 76, 96,  R3)
        sr(spx - 24, 645 + wo, 68, 90,  R1)
        sr(spx - 22, 647 + wo, 64, 30,  R2)  # shine
        # Chrome ridge lines
        sr(spx - 26, 726 + wo, 72, 10,  CH)
        sr(spx - 24, 728 + wo, 68, 4,   CHL)
        # Shoulder vent bars
        for sv in range(4):
            sr(spx - 14 + sv*12, 660 + wo, 8, 42, DK)
        # Side exhaust stacks
        poly([(spx + sign*18, 725 + wo), (spx + sign*30, 760 + wo),
              (spx + sign*36, 756 + wo), (spx + sign*24, 723 + wo)], CH)
        sr(spx + sign*20, 725 + wo, 12, 36, XST)
        sc2(spx + sign*26, 759 + wo, 6, DK)
        sc2(spx + sign*26, 759 + wo, 3, MD)
        # Shoulder spike
        poly([(spx - sign*18, 738 + wo), (spx - sign*28, 762 + wo),
              (spx - sign*22, 764 + wo), (spx - sign*12, 740 + wo)], R1)
        poly([(spx - sign*19, 739 + wo), (spx - sign*26, 760 + wo),
              (spx - sign*22, 762 + wo), (spx - sign*15, 741 + wo)], R2)
        # Shoulder rivet ring
        for ri in range(6):
            ang = math.radians(ri * 60 + t * 8 * (1 - damage))
            sc2(spx + math.cos(ang)*16, 690 + math.sin(ang)*10 + wo, 3, CH)

    # ════════════════════════════════════════════════════════════════════
    # ARMS — detailed, powered
    # ════════════════════════════════════════════════════════════════════
    for sign in [-1, 1]:
        ax = sign * 158
        wo = wob * sign * 0.38

        # Upper arm
        sr(ax - 26, 548 + wo, 52, 118, DK)
        sr(ax - 22, 552 + wo, 44, 110, B1)
        sr(ax - 20, 554 + wo, 40, 36,  B2)
        # Upper arm red stripe
        sr(ax - 16, 572 + wo, 32, 58, R1)
        sr(ax - 14, 574 + wo, 28, 18, R2)
        # Upper arm ribs
        for ub in range(4):
            sr(ax - 23, 580 + ub*16 + wo, 46, 5, CH)

        # Elbow joint (large ball)
        sc2(ax, 542 + wo, 26, DK)
        sc2(ax, 542 + wo, 20, MD)
        sc2(ax, 542 + wo, 12, CH)
        sc2(ax, 542 + wo, 5,  CHL)
        # Elbow blade fins
        poly([(ax + sign*14, 548 + wo), (ax + sign*32, 525 + wo),
              (ax + sign*30, 522 + wo), (ax + sign*12, 545 + wo)], CH)
        poly([(ax + sign*14, 558 + wo), (ax + sign*32, 535 + wo),
              (ax + sign*30, 532 + wo), (ax + sign*12, 555 + wo)], SLV)

        # Forearm
        sr(ax - 24, 428 + wo, 48, 118, R3)
        sr(ax - 20, 432 + wo, 40, 110, R1)
        sr(ax - 18, 434 + wo, 36, 30,  R2)
        # Forearm detail ribs
        for fr in range(5):
            sr(ax - 21, 446 + fr*16 + wo, 42, 5, R3)
        # Forearm side panel
        sr(ax + sign*16, 440 + wo, 14, 80, DK)
        sr(ax + sign*16, 440 + wo, 14, 22, MD)

        # Wrist guard (chrome)
        sr(ax - 26, 420 + wo, 52, 18, DK)
        sr(ax - 24, 422 + wo, 48, 12, CH)
        sr(ax - 20, 423 + wo, 40, 5,  CHL)

        # Fist / hand
        sr(ax - 25, 372 + wo, 50, 54, DK)
        sr(ax - 22, 375 + wo, 44, 48, MD)
        sr(ax - 20, 377 + wo, 40, 16, SLV)
        # Knuckle ridge
        for ki in range(4):
            sc2(ax - 14 + ki*9, 420 + wo, 6, CH)
            sc2(ax - 14 + ki*9, 420 + wo, 3, CHL)
        # Finger groove lines
        for fl in range(3):
            line(ax - 22, 394 + fl*10 + wo, ax + 22, 394 + fl*10 + wo, DK, 1)

        # Ion blaster on left arm (Optimus has a gun)
        if sign == -1:
            sr(ax - 10, 340 + wo, 20, 36, DK)
            sr(ax -  7, 343 + wo, 14, 32, XST)
            sr(ax -  8, 340 + wo, 16,  8, CH)
            sc2(ax, 337 + wo, 9, DK)
            sc2(ax, 337 + wo, 6, XST)
            # Barrel glow
            blast_a = int((100 + 45*pulse) * (1 - damage))
            if blast_a > 6:
                bg = pygame.Surface((34, 34), pygame.SRCALPHA)
                pygame.draw.circle(bg, (*EYG, min(255, blast_a)), (17, 17), 17)
                s.blit(bg, (int(ox + (ax-17)*sc), int(oy - (350)*sc - 17)),
                       special_flags=pygame.BLEND_RGBA_ADD)
        else:
            # Right arm shield flap
            poly([(ax+16, 480+wo), (ax+36, 460+wo),
                  (ax+40, 390+wo), (ax+16, 410+wo)], B3)
            poly([(ax+16, 478+wo), (ax+34, 461+wo),
                  (ax+38, 394+wo), (ax+16, 412+wo)], B1)
            sr(ax+16, 446 + wo, 22, 8, CH)
            sr(ax+16, 422 + wo, 22, 8, CH)

    # ════════════════════════════════════════════════════════════════════
    # NECK
    # ════════════════════════════════════════════════════════════════════
    sr(-18, 724, 36, 38, DK)
    sr(-14, 726, 28, 34, MD)
    # Collar ring
    sr(-24, 758, 48, 14, CH)
    sr(-20, 760, 40,  6, CHL)
    sc2(-20, 765, 4, CH)
    sc2( 20, 765, 4, CH)

    # ════════════════════════════════════════════════════════════════════
    # HEAD — Optimus Prime iconic helmet
    # ════════════════════════════════════════════════════════════════════
    # Helmet shell
    sr(-56, 772, 112, 116, DK)
    sr(-52, 775, 104, 110, R3)
    sr(-48, 778, 96,  106, R1)
    sr(-44, 780, 88,  30,  R2)   # top dome shine

    # Iconic square cheek guards (side panels)
    for sign in [-1, 1]:
        sr(sign*46, 792, 24, 78, DK)
        sr(sign*48, 795, 20, 72, B1)
        sr(sign*48, 795, 20, 24, B2)
        # Cheek vent slots
        for cv in range(3):
            sr(sign*50, 824 + cv*14, 14, 8, DK)
        # Cheek chrome edge
        line(sign*46, 792, sign*46, 870, CH, 1)

    # Face plate (Optimus silver chin/face)
    sr(-40, 772, 80, 62, DK)
    sr(-37, 775, 74, 58, CH)
    sr(-34, 777, 68, 24, CHL)   # face highlight
    # Face line details (mouthplate grooves)
    for fl in range(4):
        line(-36, 810 + fl*7, 36, 810 + fl*7, MD, 1)
    # Nose bridge
    sr(-5, 798, 10, 14, SLV)
    sc2(0, 806, 4, CH)

    # ── Eyes (glowing Autobot blue) ──────────────────────────────────────
    eye_a = int((210 + 45*pulse) * (1 - damage * 0.72))
    for ex in [-22, 22]:
        # Eye housing
        sr(ex - 13, 800, 26, 17, DK)
        # Eye glow (multi-layer)
        for er in range(10, 0, -2):
            ea = int(eye_a * (1 - er/10)**1.1)
            pygame.draw.ellipse(s,
                (*EYE, min(255, ea)),
                (int(ox + (ex-er*0.9)*sc), int(oy - (813)*sc - int(er*0.5*sc)),
                 max(1, int(er*1.8*sc)), max(1, int(er*sc))))
        # Hard eye rect
        sr(ex - 9, 804, 18, 11, EYE)
        # Iris center
        sc2(ex, 809, 4, CHL)
        sc2(ex, 809, 2, (255, 255, 255))
        # Brow plate
        sr(ex - 12, 798, 24, 5, DK)
        sr(ex - 10, 799, 20, 3, MD)

    # ── Helmet crest (prime fin) ─────────────────────────────────────────
    sr(-50, 885, 100, 26, R1)
    sr(-46, 888, 92,  10, R2)
    # Center crest fin
    poly([(-8, 885), (-4, 914), (4, 914), (8, 885)], CH)
    poly([(-6, 887), (-3, 912), (3, 912), (6, 887)], CHL)
    # Crest side tabs
    for sign in [-1, 1]:
        poly([(sign*50, 885), (sign*62, 874), (sign*62, 885)], R2)
        poly([(sign*52, 885), (sign*62, 876), (sign*62, 885)], R1)

    # ── Helmet top flat brow ─────────────────────────────────────────────
    sr(-52, 883, 104, 4, CH)

    # ══════════════════════════════════════════════════════════════════════
    # ENERGY / POWER LINES (glowing veins in the torso)
    # ══════════════════════════════════════════════════════════════════════
    if damage < 0.9:
        vein_a = int((50 + 22*hpulse) * (1 - damage))
        for vy, vx1, vx2 in [(534, -70, 70), (574, -65, 65), (614, -58, 58)]:
            vl = pygame.Surface((TW + 80, 3), pygame.SRCALPHA)
            pygame.draw.line(vl, (*EYE, max(1, min(255, vein_a))), (0, 1), (TW+80, 1), 1)
            s.blit(vl, (0, int(oy - vy*sc - 1)), special_flags=pygame.BLEND_RGBA_ADD)

    # ══════════════════════════════════════════════════════════════════════
    # DAMAGE SYSTEM
    # ══════════════════════════════════════════════════════════════════════
    if damage > 0.1:
        ds = pygame.Surface((TW + 80, TH + 60), pygame.SRCALPHA)
        for _ in range(int(damage * 32)):
            x1 = random.randint(int(ox - 105*sc), int(ox + 105*sc))
            y1 = random.randint(int(oy - 840*sc), int(oy - 140*sc))
            x2, y2 = x1, y1
            for _ in range(random.randint(2, 5)):
                x2 += random.randint(-int(28*sc), int(28*sc))
                y2 += random.randint(-int(18*sc), int(18*sc))
                pygame.draw.line(ds, (255, 115, 22, int(230*damage)),
                                 (x1, y1), (x2, y2), max(1, int(2*sc)))
                x1, y1 = x2, y2
        s.blit(ds, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Damage sparks
        if damage > 0.35:
            for _ in range(int(damage * 10)):
                spx = random.randint(int(ox-100*sc), int(ox+100*sc))
                spy = random.randint(int(oy-700*sc), int(oy-200*sc))
                sk = pygame.Surface((22, 22), pygame.SRCALPHA)
                sa = int(200 * (damage - 0.35) / 0.65)
                pygame.draw.circle(sk, (255, 195, 40, min(255, sa)),
                                   (11, 11), random.randint(2, 7))
                s.blit(sk, (spx - 11, spy - 11), special_flags=pygame.BLEND_RGBA_ADD)

    surf.blit(s, (int(cx - TW//2 - 40), int(cy - TH - 10)))

def draw_cow(surf, cx, cy, sc=1.0, t=0, alpha=255, lift=0.0, walk_phase=0):
    # ── Realistic Zebu / Brahman cow (white coat, hump, dewlap) ──────────────
    TW, TH = 340, 230
    s = pygame.Surface((TW, TH), pygame.SRCALPHA)

    # Cow faces RIGHT.  ox/oy = body horizontal centre / ground line.
    ox, oy = 130, TH - 8
    breathe  = math.sin(t * 1.6) * 1.8

    # ── Palette ──────────────────────────────────────────────────────────────
    coat     = (236, 230, 218)   # main white-cream
    coat_sh  = (200, 194, 182)   # shadow on coat
    coat_hi  = (252, 250, 246)   # highlight
    muz_col  = (215, 188, 168)   # muzzle / nose bridge (pinkish-tan)
    nostril  = (110, 72, 58)
    eye_wh   = (238, 244, 250)
    eye_iris = (52, 34, 16)
    hoof_c   = (32, 25, 16)
    horn_c   = (195, 180, 130)
    tuft_c   = (28, 20, 12)      # dark tail tuft

    # ── Shadow ───────────────────────────────────────────────────────────────
    sa = int(85 * (1 - lift))
    if sa > 4:
        sh_surf = pygame.Surface((200, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(sh_surf, (0, 0, 0, sa), (0, 0, 200, 22))
        s.blit(sh_surf, (ox - 90, oy - 10))

    # ── Walk animation ───────────────────────────────────────────────────────
    bl = int(math.sin(walk_phase * 3.0      ) * 10 * (1 - lift))  # back-leg phase
    fl = int(math.sin(walk_phase * 3.0 + PI ) * 10 * (1 - lift))  # front-leg phase

    # ── Helper: draw one leg (upper+lower segment, knee bump, hoof) ─────────
    def leg(lx, top_y, lo, fwd_lean=0):
        knee_y = top_y + 44
        foot_y = oy - 8 + lo
        pygame.draw.line(s, coat_sh, (lx, top_y), (lx + fwd_lean, knee_y + lo), 8)
        pygame.draw.line(s, coat,    (lx + fwd_lean, knee_y + lo), (lx + fwd_lean//2, foot_y), 7)
        pygame.draw.circle(s, coat_sh, (lx + fwd_lean, knee_y + lo), 7)   # knee
        pygame.draw.ellipse(s, hoof_c, (lx + fwd_lean//2 - 7, foot_y, 14, 10))

    # Back inner leg (drawn first so outer overlaps)
    leg(ox - 68, oy - 98 + int(breathe*0.3),  bl,  3)
    leg(ox + 56, oy - 103 + int(breathe*0.3), fl, -3)

    # ── Main body ─────────────────────────────────────────────────────────────
    bcx = ox - 5;  bcy = oy - 112 + int(breathe)
    bw, bh = 200, 70
    pygame.draw.ellipse(s, coat,    (bcx - bw//2, bcy - bh//2, bw, bh))
    pygame.draw.ellipse(s, coat_hi, (bcx - bw//2 + 12, bcy - bh//2, bw - 24, bh//3))
    pygame.draw.ellipse(s, coat_sh, (bcx - bw//2 + 18, bcy + bh//4, bw - 36, bh//3))

    # ── Hump (Zebu withers hump — over front-centre of back) ─────────────────
    hpx = ox + 28;  hpy = oy - 158 + int(breathe)
    pygame.draw.ellipse(s, coat,    (hpx - 48, hpy - 24, 96, 54))
    pygame.draw.ellipse(s, coat_hi, (hpx - 38, hpy - 22, 76, 24))
    pygame.draw.ellipse(s, coat_sh, (hpx - 42, hpy + 8,  84, 18))

    # ── Neck ─────────────────────────────────────────────────────────────────
    ncx_top  = bcx + bw//2 - 18;  ncy_top  = bcy - bh//2 + 6
    ncx_bot  = bcx + bw//2 + 12;  ncy_bot  = bcy + 5
    head_root_top = ox + 115;     head_root_y_top = oy - 148 + int(breathe)
    head_root_bot = ox + 118;     head_root_y_bot = oy - 105 + int(breathe)
    neck_poly = [
        (ncx_top,        ncy_top),
        (ncx_bot,        ncy_bot),
        (head_root_bot,  head_root_y_bot),
        (head_root_top,  head_root_y_top),
    ]
    pygame.draw.polygon(s, coat,    neck_poly)
    pygame.draw.polygon(s, coat_sh, neck_poly, 2)
    # neck highlight
    pygame.draw.line(s, coat_hi, (ncx_top + 4, ncy_top), (head_root_top - 4, head_root_y_top), 4)

    # ── Dewlap (hanging skin under the throat — very Zebu) ───────────────────
    dwx = ox + 100;  dwy_top = oy - 128 + int(breathe)
    sway_d = math.sin(t * 1.4) * 3
    dewlap = [
        (dwx - 8,  dwy_top),
        (dwx + 10, dwy_top),
        (dwx + 7 + int(sway_d), dwy_top + 55),
        (dwx - 5 + int(sway_d), dwy_top + 58),
    ]
    pygame.draw.polygon(s, coat_sh, dewlap)
    pygame.draw.line(s, (185, 178, 164), (dwx + 1, dwy_top + 2),
                     (dwx + 1 + int(sway_d), dwy_top + 54), 3)

    # ── Udder ────────────────────────────────────────────────────────────────
    udx = ox - 38;  udy = oy - 62 + int(breathe)
    pygame.draw.ellipse(s, (225, 192, 182), (udx - 20, udy, 40, 24))
    for tx2 in [udx - 8, udx + 8]:
        pygame.draw.line(s, (200, 160, 148), (tx2, udy + 20), (tx2, udy + 30), 4)

    # ── Outer legs (drawn after body so they appear in front) ────────────────
    leg(ox - 52, oy - 96 + int(breathe*0.3), -bl,  3)
    leg(ox + 72, oy - 100 + int(breathe*0.3),-fl, -3)

    # ── Head ─────────────────────────────────────────────────────────────────
    hcx = ox + 148;  hcy = oy - 122 + int(breathe)
    # Skull (elongated ellipse, slightly downward-angled snout line)
    pygame.draw.ellipse(s, coat,    (hcx - 40, hcy - 24, 76, 44))
    pygame.draw.ellipse(s, coat_hi, (hcx - 32, hcy - 22, 58, 20))
    # Forehead ridge (slightly raised)
    pygame.draw.ellipse(s, coat_hi, (hcx - 28, hcy - 26, 40, 14))

    # ── Muzzle / snout (wide, fleshy, drooping slightly) ─────────────────────
    mux = hcx + 36;  muy = hcy + 4
    pygame.draw.ellipse(s, muz_col, (mux - 22, muy - 16, 44, 30))
    pygame.draw.ellipse(s, coat_sh, (mux - 20, muy - 16, 42, 14))  # top shading
    # Nostrils
    pygame.draw.ellipse(s, nostril, (mux - 12, muy - 2, 8, 6))
    pygame.draw.ellipse(s, nostril, (mux + 3,  muy - 2, 8, 6))
    # Highlight on muzzle
    pygame.draw.ellipse(s, (230, 208, 192), (mux - 10, muy + 6, 22, 8))

    # ── Eye ──────────────────────────────────────────────────────────────────
    ex = hcx + 4;  ey = hcy - 10
    pygame.draw.ellipse(s, eye_wh,  (ex - 11, ey - 8,  22, 16))
    pygame.draw.ellipse(s, eye_iris,(ex -  7, ey - 6,  14, 13))
    pygame.draw.circle(s, (4, 2, 1),  (ex, ey + 1), 5)
    pygame.draw.circle(s, (255,255,255), (ex - 3, ey - 3), 2)  # catchlight
    pygame.draw.circle(s, (255,255,255), (ex + 2, ey + 2), 1)
    # Eyelashes
    for la in range(-2, 3):
        pygame.draw.line(s, (35,25,14), (ex + la*3, ey - 8), (ex + la*3 - 1, ey - 13), 1)
    # Lower eyelid fold
    pygame.draw.arc(s, coat_sh, pygame.Rect(ex-10, ey-6, 20, 14), 0, PI, 1)

    # ── Ears (large, droopy — Zebu characteristic) ───────────────────────────
    # Far ear (right side of head, partially visible)
    pygame.draw.ellipse(s, coat_sh, (hcx - 26, hcy - 38, 16, 26))
    pygame.draw.ellipse(s, (200, 152, 140), (hcx - 24, hcy - 36, 12, 22))
    # Near ear (large, floppy, hanging outward-down)
    ear_poly = [
        (hcx - 10, hcy - 24),
        (hcx - 14, hcy - 18),
        (hcx - 46, hcy -  8),
        (hcx - 50, hcy - 24),
    ]
    pygame.draw.polygon(s, coat,    ear_poly)
    inner_ear = [
        (hcx - 12, hcy - 22),
        (hcx - 15, hcy - 19),
        (hcx - 44, hcy -  9),
        (hcx - 47, hcy - 22),
    ]
    pygame.draw.polygon(s, (208, 155, 143), inner_ear)
    pygame.draw.line(s, coat_sh, (hcx-14, hcy-19), (hcx-44, hcy-10), 2)

    # ── Horns (short, spreading outward-upward like the photo) ───────────────
    hbx = hcx - 18;  hby = hcy - 22
    # Near horn
    pts_n = [(hbx, hby), (hbx - 6, hby - 4), (hbx - 16, hby - 26), (hbx - 12, hby - 28)]
    pygame.draw.polygon(s, horn_c, pts_n)
    pygame.draw.line(s, (170,155,108), (hbx-14, hby-27), (hbx-16, hby-26), 1)
    # Far horn (lighter, partially behind head)
    pts_f = [(hbx+10, hby-2), (hbx+14, hby-6), (hbx+22, hby-26), (hbx+18, hby-27)]
    pygame.draw.polygon(s, coat_sh, pts_f)

    # ── Tail (long, thin, swinging with dark tuft) ────────────────────────────
    t_ox = bcx - bw//2 + 6;  t_oy = bcy - 12 + int(breathe)
    sway_t = math.sin(t * 2.0 + 1.0) * 16
    tpts = [
        (t_ox,              t_oy),
        (t_ox - 10,         t_oy + 30 + int(sway_t * 0.2)),
        (t_ox - 14,         t_oy + 62 + int(sway_t * 0.5)),
        (t_ox - 8 + int(sway_t), t_oy + 90 + int(sway_t * 0.3)),
    ]
    for i in range(len(tpts) - 1):
        pygame.draw.line(s, coat_sh, tpts[i], tpts[i+1], max(1, 4 - i))
    tuft_x, tuft_y = int(tpts[-1][0]), int(tpts[-1][1])
    for ti in range(9):
        ang2 = math.radians(185 + ti * 19 + sway_t * 0.4)
        tx3 = int(tuft_x + math.cos(ang2) * 9)
        ty3 = int(tuft_y + math.sin(ang2) * 11)
        pygame.draw.line(s, tuft_c, (tuft_x, tuft_y), (tx3, ty3), 2)
    pygame.draw.circle(s, tuft_c, (tuft_x, tuft_y), 5)

    # ── UFO abduction lift glow ───────────────────────────────────────────────
    if lift > 0.1:
        eg = pygame.Surface((TW, TH), pygame.SRCALPHA)
        pygame.draw.ellipse(eg, (175, 125, 255, int(65*lift)),
                            (ox - 90, hcy - 30, 260, TH - (hcy - 30)))
        s.blit(eg, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        for i in range(12):
            ang = τ * i / 12 + t * 0.7
            rad = 60 + 22 * math.sin(t + i)
            dpx = int(bcx + rad * math.cos(ang))
            dpy = int(bcy + rad * math.sin(ang) * 0.4)
            ds2 = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(ds2, (215, 175, 255, int(140*lift)), (4, 4), 4)
            s.blit(ds2, (dpx - 4, dpy - 4), special_flags=pygame.BLEND_RGBA_ADD)

    if sc != 1.0:
        nw, nh = max(1, int(TW * sc)), max(1, int(TH * sc))
        s = pygame.transform.smoothscale(s, (nw, nh))
    s.set_alpha(min(255, alpha))
    surf.blit(s, (int(cx - TW*sc//2), int(cy - TH*sc + 6*sc)))


def draw_ufo(surf, cx, cy, sc=1.0, t=0, alpha=255):
    TW, TH = 300, 150
    s = pygame.Surface((TW, TH), pygame.SRCALPHA)
    ox, oy = 150, 100
    hov = math.sin(t * 1.4) * 4

    # Ambient halo
    for r, a in [(120, 10), (100, 18), (80, 25)]:
        halo = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.ellipse(halo, (95,55,210, min(255, a)), (0, r//4, r*2, r))
        s.blit(halo, (ox-r, oy-r//2+int(hov)))

    # Saucer body
    pygame.draw.ellipse(s, (88,92,120), (ox-100, oy-18+int(hov), 200, 38))
    pygame.draw.ellipse(s, (115,122,158), (ox-98, oy-18+int(hov), 196, 10))
    pygame.draw.ellipse(s, (64,68,94), (ox-98, oy-2+int(hov), 196, 18))
    pygame.draw.ellipse(s, (155,162,195), (ox-100, oy-20+int(hov), 200, 5))
    pygame.draw.ellipse(s, (76,82,112), (ox-100, oy+14+int(hov), 200, 5))

    # Dome
    pygame.draw.ellipse(s, (68,76,115), (ox-55, oy-58+int(hov), 110, 55))
    pygame.draw.ellipse(s, (90,102,148), (ox-53, oy-58+int(hov), 106, 22))
    # Window
    pygame.draw.ellipse(s, (38,46,94), (ox-38, oy-52+int(hov), 76, 42))
    pygame.draw.ellipse(s, (75,125,215), (ox-38, oy-52+int(hov), 76, 42), 2)
    wg = pygame.Surface((70, 38), pygame.SRCALPHA)
    pygame.draw.ellipse(wg, (95,170,255,80), (0, 0, 70, 38))
    s.blit(wg, (ox-35, oy-50+int(hov)), special_flags=pygame.BLEND_RGBA_ADD)

    # Rotating lights
    n_lights = 10
    for i in range(n_lights):
        angle = t * 1.8 + i * τ / n_lights
        lx = int(ox + 82 * math.cos(angle))
        ly = int(oy + 6 * math.sin(angle) + int(hov))
        hue = i / n_lights
        light_col = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.7, 1.0))
        la = int(clamp(180 + 75*math.sin(t*3.5+i), 0, 255))
        ls = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(ls, (*light_col, max(1, la//3)), (8, 8), 8)
        pygame.draw.circle(ls, (*light_col, min(255, la)), (8, 8), 3)
        s.blit(ls, (lx-8, ly-8), special_flags=pygame.BLEND_RGBA_ADD)

    # Bottom glow
    tg = pygame.Surface((TW, 40), pygame.SRCALPHA)
    tga = int(70 + 35*math.sin(t*2.8))
    pygame.draw.ellipse(tg, (75,45,210, min(255, tga)), (ox-45, 0, 90, 40))
    s.blit(tg, (0, oy-2+int(hov)), special_flags=pygame.BLEND_RGBA_ADD)

    if sc != 1.0:
        nw, nh = max(1, int(TW*sc)), max(1, int(TH*sc))
        s = pygame.transform.smoothscale(s, (nw, nh))
    s.set_alpha(min(255, alpha))
    surf.blit(s, (int(cx - TW*sc//2), int(cy - oy*sc)))


def draw_tractor_beam(surf, ux, uy, ground_y, strength, t):
    if strength < 0.02: return
    bw = int(lerp(18, 130, strength))
    bl = ground_y - uy - 18
    if bl < 10: return
    bs = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(bs, (75,28,195, int(30*strength)),
        [(ux-bw*2, uy+18), (ux+bw*2, uy+18), (ux+bw*3, ground_y), (ux-bw*3, ground_y)])
    pygame.draw.polygon(bs, (135,55,255, int(70*strength)),
        [(ux-bw, uy+18), (ux+bw, uy+18), (ux+bw*2, ground_y), (ux-bw*2, ground_y)])
    pygame.draw.polygon(bs, (195,135,255, int(120*strength)),
        [(ux-bw//2, uy+18), (ux+bw//2, uy+18), (ux+bw, ground_y), (ux-bw, ground_y)])
    surf.blit(bs, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    for i in range(0, bl, int(max(1, 12 - strength * 6))):
        y = uy + 18 + i; t2 = i / bl; sw = int(bw * (1 + t2))
        sa = int(50*strength*(0.5+0.5*math.sin(t*12+i*0.25)))
        if sa > 4:
            ls = pygame.Surface((W, 2), pygame.SRCALPHA)
            pygame.draw.line(ls, (195,135,255, min(255, sa)), (ux-sw, 1), (ux+sw, 1), 1)
            surf.blit(ls, (0, y))


# ══════════════════════════════════════════════════════════════════════════════
# ── CHAT BUBBLE SYSTEM ───────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

class ChatBubble:
    def __init__(self, speaker, text, portrait, side='left', life=3.5, emphasis=False):
        self.speaker = speaker; self.text = text; self.portrait = portrait
        self.side = side; self.life = self.ml = life
        self.alpha = 0; self.y_off = 30; self.emphasis = emphasis
        self.char_reveal = 0; self.char_timer = 0

    def update(self, dt):
        self.life -= dt
        fade_in = 0.25; fade_out = 0.4
        if self.life > self.ml - fade_in:
            self.alpha = int(255 * (1 - (self.life - self.ml + fade_in) / fade_in))
        elif self.life < fade_out:
            self.alpha = int(255 * (self.life / fade_out))
        else:
            self.alpha = 255
        self.y_off = int(lerp(0, 25, ease_out(1 - min(1, (self.ml - self.life) / 0.25))))
        self.char_timer += dt
        self.char_reveal = min(len(self.text), int(self.char_timer * 28))

    def draw(self, surf):
        if self.alpha < 5: return
        BW = 420; BH = 80; PAD = 10; PW = 50
        bx = 22 if self.side == 'left' else W - BW - 22
        by = H - 70 - BH - 12 + self.y_off

        bg = pygame.Surface((BW, BH), pygame.SRCALPHA)
        pygame.draw.rect(bg, (4, 6, 18, int(self.alpha * 0.88)), (0, 0, BW, BH))
        accent = {
            'kid': (80, 150, 255), 'droid': (0, 210, 255), 'cow': (180, 220, 80),
            'boss': (200, 40, 40), 'ufo': (160, 80, 255), 'narrator': (180, 180, 200),
        }.get(self.portrait, (100, 170, 255))
        pygame.draw.rect(bg, (*accent, min(255, self.alpha)), (0, 0, BW, BH), 2)
        pygame.draw.rect(bg, (*accent, min(255, self.alpha)), (0, 0, BW, 3))
        surf.blit(bg, (bx, by))

        ps = pygame.Surface((PW, PW), pygame.SRCALPHA)
        pygame.draw.circle(ps, (18, 22, 40, min(255, self.alpha)), (PW//2, PW//2), PW//2)
        pygame.draw.circle(ps, (*accent, min(255, self.alpha)), (PW//2, PW//2), PW//2, 2)
        _draw_portrait(ps, PW//2, PW//2, PW//2-3, self.portrait)
        ps.set_alpha(min(255, self.alpha))
        surf.blit(ps, (bx+PAD, by+BH//2-PW//2))

        ns = F_name.render(self.speaker, True, accent)
        ns.set_alpha(min(255, self.alpha))
        surf.blit(ns, (bx+PAD+PW+8, by+7))

        visible_text = self.text[:self.char_reveal]
        words = visible_text.split(); line = ""; lines = []
        mx = BW - PW - PAD*3 - 8
        for w in words:
            test = line + w + " "
            if F_chat.size(test)[0] > mx:
                lines.append(line.rstrip()); line = w + " "
            else:
                line = test
        if line: lines.append(line.rstrip())

        col = (255, 230, 100) if self.emphasis else (222, 225, 245)
        for i, ln in enumerate(lines[:2]):
            ts = F_chat.render(ln, True, col)
            ts.set_alpha(min(255, self.alpha))
            surf.blit(ts, (bx+PAD+PW+8, by+22+i*20))

def _draw_portrait(s, cx, cy, r, kind):
    if kind == 'kid':
        pygame.draw.circle(s, (218,175,132), (cx, cy), r)
        pygame.draw.ellipse(s, (38,28,18), (cx-r, cy-r, r*2, int(r*0.7)))
        for i, sx in enumerate([-r//3, 0, r//3]):
            h = r//3 + abs(i-1)*r//5
            pygame.draw.polygon(s, (38,28,18), [(cx+sx-3, cy-r//3), (cx+sx+3, cy-r//3), (cx+sx, cy-r//3-h)])
        for ex in [cx-r//4, cx+r//4]:
            pygame.draw.ellipse(s, (240,248,255), (ex-4, cy-2, 8, 7))
            pygame.draw.circle(s, (50,100,220), (ex, cy), 2)
    elif kind == 'droid':
        pygame.draw.circle(s, (50,90,148), (cx, cy), r)
        for ex in [cx-r//4, cx+r//4]:
            pygame.draw.circle(s, (0,210,255), (ex, cy-1), max(1, r//5))
            pygame.draw.circle(s, (180,240,255), (ex, cy-1), max(1, r//8))
    elif kind == 'cow':
        pygame.draw.circle(s, (222,214,204), (cx, cy), r)
        pygame.draw.ellipse(s, (198,190,180), (cx-r//3, cy+r//5, r*2//3, r//3))
        for ex in [cx-r//4, cx+r//4]:
            pygame.draw.ellipse(s, (238,245,255), (ex-3, cy-4, 6, 6))
            pygame.draw.circle(s, (10,6,3), (ex, cy-1), 2)
    elif kind == 'boss':
        pygame.draw.circle(s, (58,62,80), (cx, cy), r)
        pygame.draw.rect(s, (175,16,6), (cx-r+4, cy-2, r*2-8, max(1, r//3)))
    elif kind == 'ufo':
        pygame.draw.circle(s, (50,40,80), (cx, cy), r)
        pygame.draw.ellipse(s, (88,92,120), (cx-r+4, cy-r//4, r*2-8, r//2))
        pygame.draw.ellipse(s, (75,125,215), (cx-r//2, cy-r//3, r, r//2), 1)
    elif kind == 'narrator':
        pygame.draw.circle(s, (30,30,40), (cx, cy), r)
        pygame.draw.circle(s, (160,160,180), (cx, cy), r, 1)
        ts = F_hint.render("?", True, (160,160,180))
        s.blit(ts, (cx-ts.get_width()//2, cy-ts.get_height()//2))


bubbles = []

# ══════════════════════════════════════════════════════════════════════════════
# ── SCENE TIMELINE ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
SCENES = [0.0, 15.0, 24.0, 32.0, 44.0, 56.5, 75.0, 83.0]
GROUND_Y = 540

# Sound scheduling
SCHED.at(0.3,  'wind')
SCHED.at(0.75, 'footstep'); SCHED.at(1.95, 'footstep'); SCHED.at(3.15, 'footstep')
SCHED.at(4.5,  'footstep'); SCHED.at(5.7,  'footstep')
SCHED.at(6.75, 'footstep'); SCHED.at(7.95, 'footstep')
SCHED.at(9.0,  'droid_hum')
SCHED.at(10.5, 'footstep'); SCHED.at(12.0, 'footstep')
SCHED.at(13.5, 'wind', 0.3)
SCHED.at(15.3, 'impact'); SCHED.at(15.75, 'thunder')
SCHED.at(16.5, 'impact'); SCHED.at(19.5,  'alert')
SCHED.at(24.75,'sad_tone'); SCHED.at(26.25,'transform')
SCHED.at(28.5, 'sparkle'); SCHED.at(29.7,  'charge')
SCHED.at(32.2, 'laser');   SCHED.at(32.6,  'impact')
SCHED.at(33.0, 'explosion'); SCHED.at(33.6, 'explosion_big')
SCHED.at(34.2, 'debris'); SCHED.at(35.25, 'debris'); SCHED.at(36.0, 'wind')
SCHED.at(44.75,'wind', 0.2); SCHED.at(46.5, 'impact', 0.3)
SCHED.at(48.25,'moo');   SCHED.at(49.75,  'cow_walk')
SCHED.at(50.5, 'cow_walk'); SCHED.at(51.25, 'cow_walk')
SCHED.at(57.25,'ufo');   SCHED.at(60.75,  'beam')
SCHED.at(63.5, 'abduction'); SCHED.at(65.0, 'moo_confused'); SCHED.at(70.0, 'whoosh')

# Bubble queue
    bubble_q = [
        (1.5,  "KAI", "The battlefield stretches forever...", "kid", "left", 3.5, False),
        (6.75, "AXIOM", "just shutup till we get there. Also, I'm hungry.", "droid", "right", 3.5, False),
        (12.0, "KAI", "Droids don't eat, Axiom.", "kid", "left", 2.5, False),
        (12.75,"AXIOM", "I eat lil kids....", "droid", "right", 2.5, False),
        (15.75,"KAI", "what the.. what is that.", "kid", "left", 3.0, True),
        (18.0, "BOSS", "FOOLISH CHILD. YOU DARE APPROACH ME?", "boss", "right", 3.5, True),
        (21.0, "KAI", "Axiom... what do we do?", "kid", "left", 2.5, False),
        (22.2, "AXIOM", "why u gotta be asking a lotta questions..", "droid", "right", 2.5, False),
        (24.75,"AXIOM", "you expect me to turn myself into a gun or smthng-.", "droid", "right", 3.0, False),
        (27.0, "KAI", "i mean.. can you--", "kid", "left", 2.0, True),
        (28.2, "AXIOM", "might as well .", "droid", "right", 3.0, False),
        (30.0, "KAI", "wow.", "kid", "left", 2.0, False),
        (32.0, "KAI", "is the grass green.. SHOOT", "kid", "left", 2.0, True),
        (35.25,"KAI", "...Did we get him?", "kid", "left", 2.5, False),
        (37.5, "AXIOM", "*static* ...yes... direct hit... *crackle*", "droid", "right", 3.0, False),
        (44.5, "KAI", "Wait... what is THAT in the cockpit?", "kid", "left", 3.0, False),
        (46.5, "???", "...moo.", "cow", "right", 3.0, False),
        (49.5, "KAI", "A COW!? The final boss was a COW inside a giant transformer terminator robot!?", "kid", "left", 3.0, True),
        (51.75,"AXIOM", "*static* ...I sacrificed myself... for a cow...", "droid", "right", 3.5, False),
        (53.25,"COW", "*chews grass judgmentally*", "cow", "right", 3.0, False),
        (57.5, "KAI", "...Do you hear that sound?", "kid", "left", 2.5, False),
        (60.75,"KAI", "IS THAT A UFO!?", "kid", "left", 2.5, True),
        (63.75,"COW", "moo. (finally, my ride has arrived)", "cow", "right", 3.0, False),
        (66.0, "KAI", "The cow... is being ABDUCTED??.", "kid", "left", 3.0, False),
        (69.0, "AXIOM", "*crackle* ...none of this is in my database.. who made this goofy aah-game", "droid", "right", 3.0, False),
        (72.0, "COW", "moo~ (i will be back)", "cow", "right", 3.0, False),
        (75.0, "KAI", "grass cannot be that high.. right? ", "kid", "left", 3.0, False),

    ]
bq_idx = 0

# ── Cinematic Director Timeline ───────────────────────────────────────────────
# Target fns use live world-space coords so camera actually follows characters
def _kid_t(t_):   return kid_world_x, GROUND_Y - 80
def _boss_t(t_):  return boss_world_x, GROUND_Y - 260
def _droid_t(t_): return droid_world_x, droid_world_y - 25
def _mid_t(t_):   return (kid_world_x + boss_world_x) * 0.5, GROUND_Y - 150
def _cow_t(t_):   return cow_world_x, cow_world_y - 55
def _ufo_t(t_):
    mid = lerp(float(GROUND_Y), float(ufo_y), 0.45) - 30
    return 640.0, mid

# Zoom curves  (pe = eased scene progress 0-1)
def _zw(pe): return lerp(0.78, 0.88, pe)   # wide
def _zm(pe): return lerp(0.95, 1.08, pe)   # medium
def _zc(pe): return lerp(1.08, 1.28, pe)   # close
def _zt(pe): return lerp(1.22, 1.45, pe)   # tight
def _zu(pe): return lerp(0.55, 0.63, pe)   # ultra-wide (UFO)

# Seed the camera on a correct ground-level position
# (kid_world_x starts at -50 per scene 0 logic; use literal so this runs before the main loop)
cam.cut_to(-50, GROUND_Y - 80, 1.0)

# Scene 0 (0-15s): Follow kid marching toward the boss
director.add_track(0, 15, _kid_t, None, _zm, ease_in_out_sine, 1.0)

# Scene 1 (15-24s): Boss reveal — pull wide then drift to kid's reaction
director.add_cut(15.0, 640, GROUND_Y - 180, 0.80)
director.add_track(15,  5, _mid_t,  None, _zw, ease_in_out_sine, 1.1)
director.add_pulse(15.1, 0.55, 0.11, 6.0, 2.5)
director.add_track(20,  4, _kid_t,  None, _zc, ease_in_out_sine, 1.0)

# Scene 2 (24-32s): Droid sacrifice — push tight on the droid
director.add_cut(24.0, 380, GROUND_Y - 100, 1.18)
director.add_track(24, 8, _droid_t, None, _zt, ease_in_out_sine, 1.0)

# Scene 3 (32-44s): Laser blast — snap wide for the shot, track explosion
director.add_cut(32.0, 580, GROUND_Y - 210, 0.85)
director.add_track(32, 4, _boss_t,  None, _zm, ease_in_out_sine, 1.1)
director.add_pulse(33.1, 0.75, 0.24, 9.0, 3.5)
director.add_track(36, 8, _mid_t,   None, _zw, ease_in_out_sine, 1.0)

# Scene 4 (44-56.5s): Boss cockpit opens, cow walks free
director.add_cut(44.0, 900, GROUND_Y - 280, 0.88)
director.add_track(44, 7, _boss_t,  None, _zm, ease_in_out_sine, 1.0)
director.add_track(51, 6, _cow_t,   None, _zc, ease_in_out_sine, 1.0)

# Scene 5 (56.5-75s): UFO descends; frame both saucer and ground
director.add_cut(56.5, 640, GROUND_Y - 220, 0.62)
director.add_track(56.5, 18, _ufo_t, None, _zu, ease_in_out_sine, 1.0)
director.add_pulse(56.7, 0.65, 0.14, 7.0, 2.5)

# ══════════════════════════════════════════════════════════════════════════════
# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

t = 0.0
running = True
cur_scene = 0
giant_damage = 0.0
cow_lift = 0.0
beam_strength = 0.0
droid_transform = 0.0
panel_open = 0.0
next_lightning = random.uniform(2, 5)
cow_walk_phase = 0.0
cow_world_x = 700.0
cow_world_y = float(GROUND_Y)
kid_world_x = 0.0
kid_world_y = float(GROUND_Y)
boss_world_x = 900.0
boss_world_y = float(GROUND_Y + 4)
droid_world_x = 80.0
droid_world_y = float(GROUND_Y - 80)
kid_walk_phase = 0.0
cow_emerge = 0.0
ufo_y = -150.0

# Pre-compute grain frames
print("Baking grain...")
_GRAIN_N = 6
_grain_pool = []
for _ in range(_GRAIN_N):
    gs = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(8000):
        gx = random.randint(0, W-1); gy = random.randint(0, H-1)
        gv = random.randint(55, 255); ga = random.randint(3, 12)
        gs.set_at((gx, gy), (gv, gv, gv, ga))
    _grain_pool.append(gs)
_grain_idx = 0
print("Ready. Starting cinematic...")

while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)
    t += dt

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_ESCAPE, pygame.K_SPACE): running = False

    if t > SCENES[-1] + 1.0: running = False

    # Determine current scene
    new_scene = 0
    for i in range(len(SCENES) - 1):
        if t >= SCENES[i]:
            new_scene = i
    cur_scene = new_scene
    st = t - SCENES[cur_scene]

    # Update systems
    SCHED.update(t)
    cam.update(dt, t)
    parts.update(dt)
    update_shockwaves(dt)

    # Bubbles
    while bq_idx < len(bubble_q) and t >= bubble_q[bq_idx][0]:
        bt, spk, txt, por, side, life, emph = bubble_q[bq_idx]
        bubbles.append(ChatBubble(spk, txt, por, side, life, emph))
        bq_idx += 1
    for b in bubbles: b.update(dt)
    bubbles[:] = [b for b in bubbles if b.life > 0]

    # Lightning
    if cur_scene <= 1:
        next_lightning -= dt
        if next_lightning <= 0:
            trigger_lightning(random.randint(200, W-200), 50, random.randint(160, 280))
            thunder_flash = 0.35 + random.uniform(0, 0.25)
            next_lightning = random.uniform(4, 8)
    thunder_flash = max(0, thunder_flash - dt * 2.8)

    # ── Per-scene logic ──────────────────────────────────────────────────────

    if cur_scene == 0:
        kid_world_x = lerp(-50, 400, ease_io(clamp(st / 14.0, 0, 1)))
        kid_world_y = GROUND_Y
        kid_walk_phase = st * 2.2
        droid_world_x = kid_world_x + 60 + math.sin(t * 1.5) * 8
        droid_world_y = GROUND_Y - 75 + math.sin(t * 2.5) * 5
        rain.update(dt, 2.5)
        if random.random() < 0.15:
            parts.smoke(random.randint(int(kid_world_x - 200), int(kid_world_x + 400)),
                       GROUND_Y - 8, 1, (50, 46, 58), 18)
        if random.random() < 0.08:
            parts.stardust(random.randint(0, 1400), random.randint(80, 250), 2)

    elif cur_scene == 1:
        kid_world_x = lerp(400, 380, ease_io(min(1, st / 2)))
        kid_walk_phase = 0
        droid_world_x = kid_world_x + 55 + math.sin(t * 1.5) * 6
        droid_world_y = GROUND_Y - 75 + math.sin(t * 2.5) * 5
        boss_world_x = 900
        boss_world_y = GROUND_Y + 4
        if st < 1.0:
            rain.update(dt, 2.5)
        if 0.1 < st < 0.5: cam.shake(12, 4)
        if 0.9 < st < 1.3: cam.shake(8, 4)

    elif cur_scene == 2:
        kid_world_x = 380
        droid_transform = clamp((st - 1.0) / 3.0, 0, 1)
        droid_world_x = lerp(kid_world_x + 55, kid_world_x + 30, ease_io(min(1, st / 1.5)))
        droid_world_y = lerp(GROUND_Y - 75, GROUND_Y - 55, ease_io(min(1, st / 1.5)))
        if 1.5 < st < 4.0 and random.random() < 0.3:
            parts.energy_gather(droid_world_x, droid_world_y, 4, 80 + 60 * droid_transform)
        if 3.5 < st < 5.0 and random.random() < 0.2:
            parts.stardust(droid_world_x, droid_world_y, 3)

    elif cur_scene == 3:
        kid_world_x = 380
        droid_transform = 1.0
        if st > 0.5:
            giant_damage = min(1.0, (st - 0.5) / 3.0)
        if 0.5 < st < 0.6:
            add_shockwave(boss_world_x, boss_world_y - 200, (255, 200, 100), 900)
            add_shockwave(boss_world_x, boss_world_y - 200, (255, 100, 30), 600)
            parts.shockwave_ring(boss_world_x, boss_world_y - 200)
            cam.shake(30, 3)
        if 0.5 < st < 3.0 and random.random() < 0.4:
            parts.fire(boss_world_x + random.randint(-80, 80), boss_world_y - random.randint(60, 300), 8)
            parts.smoke(boss_world_x + random.randint(-90, 90), boss_world_y - random.randint(80, 320), 2, (52, 48, 62))
            parts.embers(boss_world_x, boss_world_y - 160, 4)
        if 0.5 < st < 2.0 and random.random() < 0.3:
            parts.debris(boss_world_x, boss_world_y - 180, 3)
        if st > 5.0:
            panel_open = min(1.0, (st - 5.0) / 2.0)

    elif cur_scene == 4:
        kid_world_x = 380
        giant_damage = 1.0
        panel_open = 1.0
        droid_transform = 1.0
        cow_emerge = ease_out5(clamp((st - 1.5) / 2.5, 0, 1))
        cow_world_x = lerp(boss_world_x, boss_world_x - 80, cow_emerge)
        cow_world_y = lerp(boss_world_y - 220, GROUND_Y, cow_emerge)
        if st > 4.5:
            cow_walk_phase += dt * 3
            walk_dist = (st - 4.5) * 15
            cow_world_x = boss_world_x - 80 - walk_dist
        if random.random() < 0.08:
            parts.smoke(boss_world_x + random.randint(-60, 60), boss_world_y - random.randint(20, 200),
                       1, (45, 42, 55), 20)

    elif cur_scene == 5:
        kid_world_x = 380
        giant_damage = 1.0; panel_open = 1.0; droid_transform = 1.0
        cow_world_x = lerp(cow_world_x, 640, min(1, st * 0.3))
        ufo_y = lerp(-150, 80, ease_out(min(1, st / 3.0)))
        beam_strength = clamp((st - 3.0) / 2.0, 0, 1)
        cow_lift = clamp((st - 5.5) / 5.0, 0, 1)
        cow_world_y = lerp(GROUND_Y, ufo_y + 30, cow_lift ** 1.2)
        if beam_strength > 0.1 and random.random() < 0.3:
            bx2 = 640 + random.uniform(-80, 80) * beam_strength
            parts.add(bx2, GROUND_Y - 5, random.uniform(-30, 30), -random.uniform(40, 130),
                     random.uniform(0.5, 1.0), random.uniform(3, 8), (155, 95, 255), -18, True)
        if cow_lift > 0.1 and random.random() < 0.2:
            parts.stardust(640, int(cow_world_y), 3)

    # Cinematic director: set camera targets from live world positions
    director.update(t, dt)

    # ══════════════════════════════════════════════════════════════════════════
    # ── RENDER ────────────────────────────────────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════════

    screen.fill((2, 3, 10))

    if cur_scene <= 5:
        # Sky
        sky_shift = clamp(t / 50, 0, 1)
        if cur_scene < 3:
            draw_sky(screen, lc((6,4,18), (10,6,22), sky_shift),
                     lc((20,15,38), (28,18,45), sky_shift),
                     lc((14,22,42), (18,26,48), sky_shift), 0.48)
        elif cur_scene == 3:
            fire_t = clamp(st / 2.0, 0, 1)
            draw_sky(screen, lc((6,4,18), (32,10,6), fire_t),
                     lc((20,15,38), (50,16,8), fire_t),
                     lc((14,22,42), (44,22,8), fire_t), 0.45)
        elif cur_scene == 4:
            clear_t = clamp(st / 4, 0, 1)
            draw_sky(screen, lc((32,10,6), (18,6,35), clear_t),
                     lc((50,16,8), (32,12,52), clear_t),
                     lc((44,22,8), (26,16,48), clear_t), 0.45)
        else:
            draw_sky(screen, (16,5,30), (30,10,50), (24,8,42), 0.45)

        # Stars
        star_alpha = 0.3 if cur_scene < 3 else (0.5 if cur_scene == 4 else 0.8)
        if cur_scene == 3: star_alpha = max(0, 0.3 - st * 0.2)
        draw_stars(screen, t, 140, star_alpha)

        # Moon
        if cur_scene < 3:
            draw_moon(screen, W - 180, 85, 40, t)

        # Clouds
        clouds.draw(screen, t, thunder_flash)

        # Lightning
        draw_lightning_bolts(screen)
        if thunder_flash > 0.05:
            flash_screen(screen, (175, 195, 255), int(thunder_flash * 30))

        # City
        scroll = cam.x * 0.15
        draw_city_silhouette(screen, GROUND_Y, scroll)

        # Fire accents
        if cur_scene >= 3:
            fire_int = min(1.0, giant_damage)
            for fx2, fph in [(boss_world_x - 100, 0), (boss_world_x + 80, 1.5), (boss_world_x, 3)]:
                sx2, sy2 = cam.world_to_screen(fx2, GROUND_Y)
                fl = 0.6 + 0.4 * math.sin(t * 7 + fph)
                glow(screen, sx2, sy2, int(18 * fire_int * fl), (255, 75, 0), int(35 * fire_int * fl), True)

        # Ground
        _, gy_screen = cam.world_to_screen(0, GROUND_Y)
        draw_ground(screen, gy_screen, (18, 14, 24), wet=(cur_scene < 3))

        # God rays from explosion
        if cur_scene == 3 and st > 0.5:
            bsx, bsy = cam.world_to_screen(boss_world_x, boss_world_y - 200)
            draw_god_rays(screen, bsx, bsy, 8, int(18 * min(1, (st-0.5)/2)), (255, 145, 35), 600)

        # Boss robot
        if cur_scene >= 1:
            bsx2, bsy2 = cam.world_to_screen(boss_world_x, boss_world_y)
            boss_sc = 0.55 * cam.zoom
            glow(screen, bsx2, bsy2 - int(200 * cam.zoom), int(70 * cam.zoom),
                 (180, 18, 8) if giant_damage < 0.5 else (100, 50, 20),
                 int(50 * (1 - giant_damage * 0.7)), True)
            draw_giant_robot(screen, bsx2, bsy2, boss_sc, giant_damage, t, panel_open)

        # Wreckage
        if cur_scene >= 4:
            for i in range(16):
                ang = i * τ / 16 + 0.3
                d = 40 + i * 15
                wx = boss_world_x + d * math.cos(ang)
                wy = GROUND_Y + d * math.sin(ang) * 0.25
                sx3, sy3 = cam.world_to_screen(wx, wy)
                mc = [(50, 54, 68), (66, 70, 86), (36, 40, 54)][i % 3]
                sz = max(1, int((8 + i * 4) * cam.zoom))
                pygame.draw.rect(screen, mc, (sx3, sy3, sz, max(1, sz // 3)))

        # Cow
        if cur_scene >= 4:
            if cur_scene == 4:
                cow_alpha = int(255 * cow_emerge) if st < 4 else 255
            else:
                cow_alpha = int(255 * max(0, 1 - max(0, cow_lift - 0.9) / 0.1))
            if cow_alpha > 5:
                csx, csy = cam.world_to_screen(cow_world_x, cow_world_y)
                cow_sc = max(0.05, lerp(0.8, 0.25, cow_lift) * cam.zoom)
                draw_cow(screen, csx, csy, cow_sc, t, min(255, cow_alpha), cow_lift, cow_walk_phase)
                if cur_scene == 4 and cow_emerge > 0.5:
                    glow(screen, csx, csy - int(60 * cow_sc), int(50 * cow_sc),
                         (200, 150, 255), int(40 * cow_emerge), True)

        # UFO
        if cur_scene >= 5:
            usx, usy = cam.world_to_screen(640, ufo_y)
            ufo_alpha = int(255 * ease_out(min(1, st / 2)))
            if ufo_alpha > 5:
                ufo_sc = max(0.05, 0.95 * cam.zoom)
                draw_ufo(screen, usx, usy, ufo_sc, t, min(255, ufo_alpha))
                glow(screen, usx, usy, int(220 * cam.zoom), (55, 18, 170), int(22 * ufo_alpha / 255), True)
                glow(screen, usx, usy, int(120 * cam.zoom), (95, 35, 215), int(35 * ufo_alpha / 255), True)
                lens_flare(screen, usx, usy, min(1, ufo_alpha / 255) * 0.5, (115, 75, 255))
                draw_god_rays(screen, usx, usy + int(35 * cam.zoom), 10,
                             int(12 * ufo_alpha / 255), (135, 75, 255), int(H * 1.2))

            gy_s = cam.world_to_screen(0, GROUND_Y - 15)[1]
            draw_tractor_beam(screen, usx, usy + int(40 * cam.zoom), gy_s, beam_strength, t)

        # Droid / Gun
        if cur_scene <= 3:
            dsx, dsy = cam.world_to_screen(droid_world_x, droid_world_y)
            d_sc = max(0.05, 0.75 * cam.zoom)
            d_state = 'sad' if (cur_scene == 2 and st < 1.5) else 'normal'
            draw_droid(screen, dsx, dsy, d_sc, t, 255, d_state, droid_transform)
            if droid_transform < 0.5:
                glow(screen, dsx, dsy - int(30 * d_sc), int(35 * d_sc), (0, 170, 255), 30, True)

        # Kid
        kid_pose = 'walk' if cur_scene == 0 else ('aim' if (cur_scene == 3 and st < 3) else ('sad' if cur_scene == 2 and st < 1.5 else 'stand'))
        kid_facing = 1
        ksx, ksy = cam.world_to_screen(kid_world_x, kid_world_y)
        k_sc = max(0.05, 0.85 * cam.zoom)
        draw_kid(screen, ksx, ksy, k_sc, kid_facing, kid_pose, t, 255, kid_walk_phase)

        # Laser beam (Scene 3)
        if cur_scene == 3 and 0.1 < st < 2.5:
            la = int(255 * min(1, (st - 0.1) / 0.15) * max(0, 1 - max(0, st - 1.5) / 1.0))
            if la > 10:
                tip_sx, tip_sy = cam.world_to_screen(kid_world_x + 80, GROUND_Y - 52)
                hit_sx, hit_sy = cam.world_to_screen(boss_world_x - 20, boss_world_y - 200)
                for bw2, ba, bc2 in [
                    (80, la//8, (55,130,255)), (50, la//5, (90,180,255)),
                    (30, la//3, (140,210,255)), (14, la//2, (210,235,255)),
                    (6, la, (255,255,255)), (2, 255, (255,255,255))
                ]:
                    glowing_line(screen, (tip_sx, tip_sy), (hit_sx, hit_sy), bc2, bw2, bw2*2, ba)
                mf_r = int((25 + 12*math.sin(t*28)) * cam.zoom)
                glow(screen, tip_sx, tip_sy, mf_r, (80, 200, 255), la, True)
                glow(screen, tip_sx, tip_sy, mf_r//2, (255, 255, 255), la, True)
                lens_flare(screen, tip_sx, tip_sy, min(1, la/255) * 0.7, (95, 175, 255))
                glow(screen, hit_sx, hit_sy, int(55 * cam.zoom), (255, 130, 18), la, True)
                glow(screen, hit_sx, hit_sy, int(25 * cam.zoom), (255, 235, 95), la, True)

        # Flash effects
        if cur_scene == 3 and 0.1 < st < 0.6:
            fv = int(200 * (1 - abs(st - 0.3) / 0.3))
            flash_screen(screen, (255, 242, 225), max(0, fv))
        if cur_scene == 3 and 0.5 < st < 2.0:
            bloom = int(55 * (1 - abs(st - 1.2) / 0.8) * giant_damage)
            flash_screen(screen, (255, 95, 18), max(0, bloom))

        # Rain
        if cur_scene < 2:
            rain.draw(screen, int(75 * max(0, 1 - t / 16)), 2.5)
        elif cur_scene == 2 and st < 2:
            rain.draw(screen, int(75 * (1 - st / 2)), 2.5)

        # Particles
        parts.draw(screen, cam)

        # Shockwaves
        draw_shockwaves(screen, cam)

        # Fog
        for y_fog, density, speed in [(GROUND_Y - 25, 28, 0.35), (GROUND_Y - 55, 14, 0.2)]:
            _, fy = cam.world_to_screen(0, y_fog)
            fog = pygame.Surface((W, 35), pygame.SRCALPHA)
            for fx in range(0, W, 75):
                ox2 = int(fx + math.sin(t * speed + fx * 0.004) * 18)
                pygame.draw.ellipse(fog, (45, 40, 58, density), (ox2-55, 0, 110, 35))
            screen.blit(fog, (0, fy))

        # Vignette
        vig_str = 90 if cur_scene < 3 else (70 if cur_scene == 3 else 110)
        vignette(screen, vig_str)

        # Color tint
        if cur_scene < 3:
            tint = pygame.Surface((W, H)); tint.fill((0, 8, 22)); tint.set_alpha(18)
            screen.blit(tint, (0, 0))
        elif cur_scene == 4:
            tint = pygame.Surface((W, H)); tint.fill((18, 4, 30)); tint.set_alpha(22)
            screen.blit(tint, (0, 0))
        elif cur_scene >= 5:
            tint = pygame.Surface((W, H)); tint.fill((12, 4, 30)); tint.set_alpha(28)
            screen.blit(tint, (0, 0))

        # Scene fade in
        if cur_scene > 0:
            fade_dur = 0.6
            if st < fade_dur:
                fade_black(screen, int(255 * (1 - st / fade_dur)))

        # Final fade out
        if t > SCENES[6] - 3.0:
            fa = int(255 * ease_io((t - (SCENES[6] - 3.0)) / 3.0))
            fade_black(screen, fa)

    # Title card (Scene 6)
    if cur_scene >= 6:
        screen.fill((2, 3, 8))
        tc_t = st
        if tc_t < 4:
            title_a = int(255 * ease_io(min(2, tc_t / 2.5)))
            ts = F_title.render("RUST  &  RUIN", True, (200, 210, 240))
            ts.set_alpha(min(255, title_a))
            screen.blit(ts, (W//2 - ts.get_width()//3, H//2 - 60))
            if tc_t > 1.0:
                sub_a = int(255 * ease_io(min(1, (tc_t - 1.0) / 1.0)))
                ss = F_sub.render("And the cow....", True, (140, 150, 180))
                ss.set_alpha(min(255, sub_a))
                screen.blit(ss, (W//2 - ss.get_width()//2, H//2 + 10))
            if tc_t > 2.5:
                cr_a = int(200 * ease_io(min(3, (tc_t - 2.5) / 1.0)))
                cs = F_hint.render("Thank you for playing.", True, (100, 105, 130))
                cs.set_alpha(min(255, cr_a))
                screen.blit(cs, (W//2 - cs.get_width()//2, H//2 + 55))
        else:
            fade_black(screen, int(255 * min(1, (tc_t - 4) / 2)))

    # Film grain
    _grain_idx = (_grain_idx + 1) % _GRAIN_N
    screen.blit(_grain_pool[_grain_idx], (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Letterbox
    lb_alpha = 255
    if cur_scene >= 6 and st > 3:
        lb_alpha = int(255 * max(0, 1 - (st - 3) / 2))
    letterbox(screen, 68, lb_alpha)

    # Chat bubbles
    for b in bubbles:
        b.draw(screen)

    # Skip hint
    if t < SCENES[-1] - 2:
        hs = F_hint.render("SPACE / ESC  skip", True, (40, 40, 50))
        screen.blit(hs, (W - hs.get_width() - 12, H - 15))

    pygame.display.flip()

pygame.quit()
sys.exit()
