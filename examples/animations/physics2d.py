from coldtype import *
from coldtype.fx.skia import phototype
from coldtype.physics.pymunk import segments

# pip install pymunk

import pymunk
from pymunk import Vec2d
import random as rnd

r = Rect(1080, 1080)
ri = r.inset(-4, 0)

txt = (StSt("C", Font.ColdObvi(), 1200, wdth=1)
    .align(r, ty=1)
    .fssw(-1, 1, 1))

space = pymunk.Space()
space.gravity = (0.0, -900.0)

# def begin(arbiter, space, data):
#     print("Collision started!")
#     return True  # Allow the collision to occur

# def pre_solve(arbiter, space, data):
#     print("Collision is being solved!")
#     return True  # Continue processing the collision

# def post_solve(arbiter, space, data):
#     print("Collision solved!")
#     # Use arbiter.total_impulse to get collision force if needed

# def separate(arbiter, space, data):
#     print("Collision ended!")

# Define the collision handler
#handler = space.add_collision_handler(0, 0)

# Attach callbacks to the handler
#handler.begin = begin
# handler.pre_solve = pre_solve
# handler.post_solve = post_solve
# handler.separate = separate

static_body = space.static_body
floor = pymunk.Segment(static_body, *ri.es.splat(), 0.0)
static_lines = [
    pymunk.Segment(static_body, *ri.ew.splat(), 0.0),
    pymunk.Segment(static_body, *ri.ee.splat(), 0.0),
    floor
]

letter_lines = txt.ch(segments(static_body))
static_lines.extend(letter_lines)

for line in static_lines:
    line.elasticity = 1
    line.friction = 0.1

space.add(*static_lines)

particles = []

@animation(tl=450, bg=0, render_bg=1, reset_to_zero=1)
def scratch(f):
    if f.i == 275:
        space.remove(floor)
        for idx, s in enumerate(letter_lines):
            if idx%10 != 0:
                space.remove(s)

    if f.i <= 275:
        for _ in range(0, 10):
            mass = 0.1
            radius = rnd.randint(7, 13)
            inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            body = pymunk.Body(mass, inertia)
            x = rnd.randint(10, f.a.r.w-10)
            body.position = x, rnd.randint(1150, 1300)
            shape = pymunk.Circle(body, radius, Vec2d(0, 0))
            space.add(body, shape)
            particles.append(shape)

    particles_to_remove = []

    for particle in particles:
        if particle.body.position.y < 0:
            particles_to_remove.append(particle)
    
    for particle in particles_to_remove:
        space.remove(particle, particle.body)
        particles.remove(particle)

    ### Update physics
    # Running in a range since that smaller increments repeated
    # seems to get better results
    for x in range(3):
        space.step(1 / 100.0)

    out = P()
    for particle in particles:
        p = Point(particle.body.position.x, particle.body.position.y)
        out += P().rect(Rect.FromCenter(p, particle.radius)).f(1)
    
    return out.ch(phototype(f.a.r.inset(0, 0), blur=1, cut=100, cutw=10))