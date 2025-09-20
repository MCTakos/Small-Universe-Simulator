from vpython import sphere, vector, color, rate, scene, local_light
import math
import random

# --- Scene Setup ---
scene.title = "Ultimate Universe Simulator"
scene.background = color.black
scene.width = 1200
scene.height = 800
scene.forward = vector(0,-0.3,-1)

# --- Constants ---
AU = 1.496e8        # km scaled for visualization
LY = 9.461e12       # km scaled for visualization
NUM_STARS = 30
NUM_PLANETS = 60
NUM_BLACKHOLES = 15
NUM_GALAXIES = 5
GALAXY_STARS = 80

# --- Utility Functions ---
def random_vector(scale):
    return vector(random.uniform(-scale,scale),
                  random.uniform(-scale,scale),
                  random.uniform(-scale,scale))

# --- Stars and Lights ---
stars = []
star_lights = []
for i in range(NUM_STARS):
    pos = random_vector(200*LY)
    star = sphere(pos=pos, radius=1*LY/1e6, color=color.yellow, emissive=True)
    stars.append(star)
    star_lights.append(local_light(pos=pos, color=color.white))  # illuminate planets

# --- Planets and Moons ---
planets = []
moons = []
for i in range(NUM_PLANETS):
    star_index = i % NUM_STARS
    star_pos = stars[star_index].pos
    orbit_radius = random.uniform(0.5,5)*AU
    orbit_speed = random.uniform(0.01,0.05)
    angle = random.uniform(0,2*math.pi)
    planet = sphere(pos=star_pos + vector(orbit_radius,0,0),
                    radius=0.5*AU/1e6, color=color.blue, emissive=True)
    planets.append({
        "obj": planet,
        "star_index": star_index,
        "orbit_radius": orbit_radius,
        "angle": angle,
        "orbit_speed": orbit_speed,
        "rotation_speed": random.uniform(0.01,0.03)
    })
    # Add 0-2 moons per planet
    for m in range(random.randint(0,2)):
        moon_orbit = random.uniform(0.1,0.5)*AU
        moon_speed = random.uniform(0.05,0.1)
        moon_angle = random.uniform(0,2*math.pi)
        moon = sphere(pos=planet.pos + vector(moon_orbit,0,0),
                      radius=0.1*AU/1e6, color=color.white, emissive=True)
        moons.append({
            "obj": moon,
            "planet_index": i,
            "orbit_radius": moon_orbit,
            "angle": moon_angle,
            "orbit_speed": moon_speed,
            "rotation_speed": random.uniform(0.05,0.1)
        })

# --- Black Holes ---
black_holes = []
for i in range(NUM_BLACKHOLES):
    pos = random_vector(300*LY)
    bh = sphere(pos=pos, radius=1.5*LY/1e6, color=color.black, emissive=True)
    black_holes.append(bh)

# --- Procedural Galaxies ---
galaxy_stars = []
for g in range(NUM_GALAXIES):
    center = random_vector(500*LY)
    stars_in_galaxy = []
    for s in range(GALAXY_STARS):
        # Spiral arm using polar coordinates
        angle = random.uniform(0,4*math.pi)
        radius = random.uniform(50,150)
        x = radius*math.cos(angle) + center.x
        y = random.uniform(-20,20) + center.y
        z = radius*math.sin(angle) + center.z
        star = sphere(pos=vector(x,y,z), radius=0.5*LY/1e6, color=color.yellow, emissive=True)
        stars_in_galaxy.append(star)
    galaxy_stars.append(stars_in_galaxy)

# --- Interstellar Events ---
comets = []
neutron_stars = []

def spawn_comet():
    pos = random_vector(500*LY)
    return {"obj": sphere(pos=pos, radius=0.3*AU/1e6, color=color.white, emissive=True),
            "velocity": random_vector(2)}

def spawn_neutron_star():
    pos = random_vector(400*LY)
    return sphere(pos=pos, radius=0.7*LY/1e6, color=color.cyan, emissive=True)

# --- Animation Loop ---
while True:
    rate(50)
    
    # Rotate galaxies slowly
    for galaxy in galaxy_stars:
        for star in galaxy:
            star.rotate(angle=0.0002, axis=vector(0,1,0))
    
    # Rotate stars and black holes slowly
    for obj in stars + black_holes:
        obj.rotate(angle=0.0005, axis=vector(0,1,0))
    
    # Update planet orbits and rotation
    for planet in planets:
        p = planet["obj"]
        star_pos = stars[planet["star_index"]].pos
        planet["angle"] += planet["orbit_speed"]
        x = star_pos.x + planet["orbit_radius"]*math.cos(planet["angle"])
        z = star_pos.z + planet["orbit_radius"]*math.sin(planet["angle"])
        y = star_pos.y
        p.pos = vector(x,y,z)
        p.rotate(angle=planet["rotation_speed"], axis=vector(0,1,0))
    
    # Update moon orbits and rotation
    for moon in moons:
        m = moon["obj"]
        planet_pos = planets[moon["planet_index"]]["obj"].pos
        moon["angle"] += moon["orbit_speed"]
        x = planet_pos.x + moon["orbit_radius"]*math.cos(moon["angle"])
        z = planet_pos.z + moon["orbit_radius"]*math.sin(moon["angle"])
        y = planet_pos.y
        m.pos = vector(x,y,z)
        m.rotate(angle=moon["rotation_speed"], axis=vector(0,1,0))
    
    # Cosmic events
    if random.random() < 0.001:
        star = random.choice(stars)
        star.color = color.red  # supernova
    if random.random() < 0.0005:
        bh = random.choice(black_holes)
        bh.color = color.white  # BH activity
    if random.random() < 0.002:
        comets.append(spawn_comet())
    if random.random() < 0.001:
        neutron_stars.append(spawn_neutron_star())
    
    # Move comets
    for comet in comets:
        comet["obj"].pos += comet["velocity"]
    
    # Intergalactic collisions / BH mergers (simplified)
    if random.random() < 0.0003 and len(black_holes) > 1:
        bh1, bh2 = random.sample(black_holes, 2)
        mid = (bh1.pos + bh2.pos)/2
        bh1.pos = mid
        bh2.pos = mid
        # Flash effect for merger
        bh1.color = color.white
        bh2.color = color.white
