import raylibpy as rl
import random
import math

# Define constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SUNNY = 1
CLOUDY = 2
RAINY = 3
RAINDROP_COUNT = 100
DESERT_COLOR = rl.Color(237, 201, 175, 255)
GRASSLAND_COLOR = rl.Color(124, 252, 0, 255)
FOREST_COLOR = rl.Color(34, 139, 34, 255)
TUNDRA_COLOR = rl.Color(200, 220, 240, 255)
MAX_PLANTS = 100

import random

class Plant:
    def __init__(self, x, y, game_map):
        self.x = x
        self.y = y
        self.size = 10  # Size of the plant patch (e.g., 10 pixels)
        self.health = 100
        self.growth_patches = [(self.x, self.y)]  # List to store the coordinates of all growth patches
        self.game_map = game_map
        self.update_zone()  # Determine the zone based on the plant's location

    def update_zone(self):
        # Update the zone for the current location of the plant
        cell_width = SCREEN_WIDTH // self.game_map.width
        cell_height = SCREEN_HEIGHT // self.game_map.height
        self.zone = self.game_map.get_zone(self.x // cell_width, self.y // cell_height)

    def grow(self, sunlight, humidity, nearby_plants=None):
        if len(self.growth_patches) >= MAX_PLANTS:
            return  # Stop growth if the maximum number of growth patches is reached

        # Grass growth depends on sunlight and humidity in Grassland or Forest zones
        if self.zone and self.zone.name in ["Grassland", "Forest"]:
            if sunlight > 20 and humidity > 50:
                if random.random() < self.growth_probability(sunlight, humidity):
                    # Grow by extending from the current plant's growth patches
                    self._extend_growth(nearby_plants)
            else:
                # Grass may die if conditions are too harsh
                self.health -= 1
                if self.health <= 0:
                    if nearby_plants is not None:
                        nearby_plants.remove(self)

    def _extend_growth(self, nearby_plants):
        new_patches = []
        for (px, py) in self.growth_patches:
            # Pick a random number of directions to grow (can grow in 1 to 4 directions)
            directions = random.sample([(-1, 0), (1, 0), (0, -1), (0, 1)], random.randint(1,2))

            for dx, dy in directions:  # Left, right, up, down
                cell_width = SCREEN_WIDTH // self.game_map.width
                cell_height = SCREEN_HEIGHT // self.game_map.height

                new_x = (px + dx * self.size * 2) // cell_width
                new_y = (py + dy * self.size * 2) // cell_height

                # Ensure new coordinates are within bounds
                new_x = min(max(new_x, 0), self.game_map.width - 1)
                new_y = min(max(new_y, 0), self.game_map.height - 1)

                # Check if the new location is already part of the plant
                if (new_x, new_y) not in self.growth_patches and (new_x, new_y) not in new_patches:
                    # Check for the zone and if there is already a plant at the new location
                    new_zone = self.game_map.get_zone(new_x, new_y)
                    if new_zone and not any(p.x == new_x and p.y == new_y for p in nearby_plants):
                        # Add the new patch to grow further
                        new_patches.append((px + dx * self.size * 2, py + dy * self.size * 2))

        # Add all newly grown patches to the plant
        self.growth_patches.extend(new_patches)

    def growth_probability(self, sunlight, humidity):
        # Customize growth probability based on environmental factors
        return (humidity * sunlight) * 0.000001

    def be_eaten(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.size = 0
            self.growth_patches = []  # Remove all patches if the plant dies
            return True
        return False

    def draw(self):
        # Draw each growth patch of the plant
        plant_size = self.size * 2
        for (px, py) in self.growth_patches:
            rl.draw_rectangle(px - plant_size // 2, py - plant_size // 2, plant_size, plant_size, rl.GREEN)

class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(1.0, 2.5)
        self.health = 100
        self.direction = random.uniform(0, 2 * math.pi)  # Direction in radians
        self.reproduction_range = 50  # Range within which animals can reproduce
        self.reproduction_chance = 0.1  # Chance to reproduce if another animal is nearby
        self.has_reproduced = False  # Track if this animal has already reproduced
        self.bravery = random.uniform(0, 1)  # 0 = fearful, 1 = brave
        self.size = random.uniform(1, 10)
        self.hunger = 100

    def move(self):
        # Move in the current direction
        if self.bravery < 0.5:
            # Avoidance behavior
            self.x += math.cos(self.direction) * self.speed * 0.5
            self.y += math.sin(self.direction) * self.speed * 0.5

            # Randomly change direction more frequently
            if random.random() < 0.05:
                self.direction += random.uniform(-0.5, 0.5)
        else:
            # Normal movement
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed

            # Randomly change direction
            if random.random() < 0.02:  # 2% chance to change direction each frame
                self.direction += random.uniform(-0.5, 0.5)

        # Check for boundary collision and adjust direction
        if self.x <= 0 or self.x >= SCREEN_WIDTH:
            self.direction = math.pi - self.direction
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            self.direction = -self.direction

        # Ensure the animal stays within screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH))
        self.y = max(0, min(self.y, SCREEN_HEIGHT))

        self.hunger-=0.05

    def distance_to(self, entity):
        return math.hypot(self.x - entity.x, self.y - entity.y)

    def reproduce(self, animals):
        if self.has_reproduced:
            return  # Skip reproduction if this animal has already reproduced

        for animal in animals:
            if isinstance(animal, type(self)) and animal != self:
                distance = self.distance_to(animal)
                if distance < self.reproduction_range and not animal.has_reproduced:
                    # Create a new animal at a random position nearby
                    new_x = self.x + random.uniform(-10, 10)
                    new_y = self.y + random.uniform(-10, 10)
                    new_animal = type(self)(new_x, new_y)  # Create the same type of animal
                    animals.append(new_animal)
                    self.has_reproduced = True
                    animal.has_reproduced = True
                    break  # Only reproduce once

    def eat_plants(self, plants):
        if self.hunger < 30:
            if not plants:
                return  # No plants to eat, exit the function

            # Find the nearest plant
            nearest_plant = min(plants, key=lambda plant: self.distance_to(plant))

            # Move towards the nearest plant if not within eating range
            if self.distance_to(nearest_plant) > 15:
                self.move_towards(nearest_plant, step_size=2)  # Move towards the plant
            else:
                # Eat the plant if within range
                if nearest_plant.size < 5:  # Small plants are completely eaten
                    nearest_plant.health -= 100
                    if nearest_plant.health <= 0:
                        plants.remove(nearest_plant)
                else:  # Large plants are partially eaten
                    nearest_plant.be_eaten(2)
                self.health = min(self.health + 50, 100)  # Gain health from eating
                self.hunger = min(self.hunger + 70, 100)  # Satisfy hunger

    def move_towards(self, target, step_size=1):
        # Calculate the direction vector towards the target
        direction_x = target.x - self.x
        direction_y = target.y - self.y
        
        # Normalize the direction vector
        distance = (direction_x**2 + direction_y**2) ** 0.5
        if distance == 0:  # Prevent division by zero
            return

        direction_x /= distance
        direction_y /= distance
        
        # Move by step_size towards the target
        self.x += direction_x * step_size
        self.y += direction_y * step_size

    def draw(self):
        rl.draw_circle(self.x, self.y, 6, rl.BROWN)

class Predator(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(2.0, 4.0)
        self.hunger = 100  # Initial hunger level

    def hunt(self, animals, predators, rabbits):
        if self.hunger >= 50:
            return  # Only hunt if hunger is less than threshold

        # Find the closest prey
        closest_prey = None
        min_distance = float('inf')

        for prey in animals + rabbits:
            distance = self.distance_to(prey)
            if distance < min_distance:
                min_distance = distance
                closest_prey = prey

        if closest_prey and min_distance < 20:  # Within hunting range
            closest_prey.health -= 100
            if closest_prey.health <= 0:
                if isinstance(closest_prey, Rabbit):
                    rabbits.remove(closest_prey)
                else:
                    animals.remove(closest_prey)
            self.hunger = 100  # Reset hunger after a successful hunt
        elif closest_prey:  # Move towards the closest prey
            angle = math.atan2(closest_prey.y - self.y, closest_prey.x - self.x)
            self.direction = angle

    def move(self, animals, humans, rabbits):
        if self.hunger < 60:
            super().move()
            self.hunger -= 0.1  # Decrease hunger over time
            self.hunt(animals, None, rabbits)  # Hunt if hungry
        else:
            # Stop moving if hunger is above or equal to threshold
            self.hunger -= 0.1
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed

            # Check for boundary collision and adjust direction
            if self.x <= 0 or self.x >= SCREEN_WIDTH:
                self.direction = math.pi - self.direction
            if self.y <= 0 or self.y >= SCREEN_HEIGHT:
                self.direction = -self.direction

            # Randomly change direction
            if random.random() < 0.02:  # 2% chance to change direction each frame
                self.direction += random.uniform(-0.5, 0.5)

            # Ensure the animal stays within screen bounds
            self.x = max(0, min(self.x, SCREEN_WIDTH))
            self.y = max(0, min(self.y, SCREEN_HEIGHT))
        for human in humans:
            if self.distance_to(human) < 20:  # Within attack range
                human.health -= 45
                if human.health <= 0:
                    humans.remove(human)
                # Retaliate by attacking the human
                self.hunger = min(self.hunger + 55, 100)

    def draw(self):
        rl.draw_circle(self.x, self.y, 7, rl.RED)

class Lion(Predator):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(3.0, 4.0)  # Faster than base predator
        self.hunger = 100

    def hunt(self, animals,predators, rabbits):
        if self.hunger >= 60:
            return  # Only hunt if hunger is less than 60

        # Lion behavior: prioritize larger animals
        largest_prey = None
        max_size = 0

        for prey in animals + rabbits:
            if prey.size >= max_size:  # Assuming animals have a `size` attribute
                max_size = prey.size
                largest_prey = prey

        if largest_prey and self.distance_to(largest_prey) < 20:  # Within hunting range
            largest_prey.health -= 100
            if largest_prey.health <= 0:
                if isinstance(largest_prey, Rabbit):
                    rabbits.remove(largest_prey)
                else:
                    animals.remove(largest_prey)
            self.hunger = 100  # Reset hunger after a successful hunt
        elif largest_prey:
            angle = math.atan2(largest_prey.y - self.y, largest_prey.x - self.x)
            self.direction = angle

    def move_as_group(lions, animals, humans, rabbits, group_size=3, proximity_threshold=20):
        # Ensure lions move as a group
        if len(lions) >= group_size:
            # Calculate the group's average position
            avg_x = sum(lion.x for lion in lions) / len(lions)
            avg_y = sum(lion.y for lion in lions) / len(lions)

            # Move each lion towards the average position to stay as a group
            for lion in lions:
                if lion.distance_to(avg_x, avg_y) > proximity_threshold:
                    lion.move_towards_position(avg_x, avg_y, step_size=2)

                # Proceed with regular movement and hunger check
                lion.move(animals, humans, rabbits)
                if lion.hunger <= 0:
                    lions.remove(lion)

    def move_towards_position(self, target_x, target_y, step_size=1):
        # Calculate the direction vector towards the target position
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        
        # Normalize the direction vector
        distance = (direction_x**2 + direction_y**2) ** 0.5
        if distance == 0:  # Prevent division by zero
            return

        direction_x /= distance
        direction_y /= distance
        
        # Move by step_size towards the target position
        self.x += direction_x * step_size
        self.y += direction_y * step_size

    def draw(self):
        rl.draw_circle(self.x, self.y, 8, rl.DARKBROWN)  # Distinct color for Lion

class Tiger(Predator):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(2.5, 4.5)  # Faster and more aggressive
        self.hunger = 100

    def hunt(self, animals,predators, rabbits):
        if self.hunger >= 60:
            return  # Only hunt if hunger is less than 60

        # Tiger behavior: aggressive hunting
        closest_prey = None
        min_distance = float('inf')

        for prey in animals + rabbits:
            distance = self.distance_to(prey)
            if distance < min_distance:
                min_distance = distance
                closest_prey = prey

        if closest_prey and min_distance < 20:  # Within hunting range
            closest_prey.health -= 80  # More damage compared to Lion
            if closest_prey.health <= 0:
                if isinstance(closest_prey, Rabbit):
                    rabbits.remove(closest_prey)
                else:
                    animals.remove(closest_prey)
            self.hunger = 100  # Reset hunger after a successful hunt
        elif closest_prey:
            angle = math.atan2(closest_prey.y - self.y, closest_prey.x - self.x)
            self.direction = angle

    def draw(self):
        rl.draw_circle(self.x, self.y, 8, rl.ORANGE)  # Distinct color for Tiger

class Human(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 1.5
        self.hunger = 100  # Initial hunger level
        self.emotion = random.choice(['happy', 'sad', 'angry', 'fearful'])  # Random initial emotion
        self.greedy = random.choice([True, False])  # Whether the human is greedy

    def hunt(self, animals, predators,rabbits):
        if self.hunger <= 0:
            return

        # Change behavior based on emotion
        if self.emotion == 'fearful':
            self.run_from_predators(predators)
            self.hunt_animals(animals,rabbits)
        elif self.emotion == 'angry':
            self.hunt_predators(predators)
            self.hunt_everything(animals,rabbits,predators)
        elif self.emotion == 'happy' or self.emotion == 'sad':
            self.hunt_animals(animals,rabbits)
    
    def run_from_predators(self, predators):
        for predator in predators:
            if self.distance_to(predator) < 20:  # Within predator range
                # Increase speed to escape
                self.speed = 3.0
                angle = math.atan2(self.y - predator.y, self.x - predator.x)
                self.direction = angle
                self.move()  # Move away from the predator
                return  # Stop running after escaping

    def hunt_predators(self, predators):
        for predator in predators:
            if self.distance_to(predator) < 20:  # Within predator range
                # Hunt the predator
                predator.health -= 50
                if predator.health <= 0:
                    predators.remove(predator)
                self.hunger = min(self.hunger + 50, 100)
                return  # Stop searching after a successful hunt

    def hunt_animals(self, animals,rabbits):
        if self.hunger < 50:
            # Find the closest prey
            closest_prey = None
            min_distance = float('inf')

            for prey in animals + rabbits:
                distance = self.distance_to(prey)
                if distance < min_distance:
                    min_distance = distance
                    closest_prey = prey

            if closest_prey and min_distance < 20:  # Within hunting range
                closest_prey.health -= 100
                if closest_prey.health <= 0:
                    if isinstance(closest_prey, Rabbit):
                        rabbits.remove(closest_prey)
                    else:
                        animals.remove(closest_prey)
                self.hunger = 100  # Reset hunger after a successful hunt
            elif closest_prey:  # Move towards the closest prey
                angle = math.atan2(closest_prey.y - self.y, closest_prey.x - self.x)
                self.direction = angle   

    def hunt_everything(self, animals,rabbits,predators):
        if self.hunger < 50:
            # Find the closest prey
            closest_prey = None
            min_distance = float('inf')

            for prey in animals + rabbits + predators:
                distance = self.distance_to(prey)
                if distance < min_distance:
                    min_distance = distance
                    closest_prey = prey

            if closest_prey and min_distance < 20:  # Within hunting range
                closest_prey.health -= 100
                if closest_prey.health <= 0:
                    if isinstance(closest_prey, Rabbit):
                        rabbits.remove(closest_prey)
                    elif isinstance(closest_prey, Predator):
                        predators.remove(closest_prey)
                    else:
                        animals.remove(closest_prey)
                self.hunger = 100  # Reset hunger after a successful hunt
            elif closest_prey:  # Move towards the closest prey
                angle = math.atan2(closest_prey.y - self.y, closest_prey.x - self.x)
                self.direction = angle

    def move(self):
        # Adjust speed based on emotion
        if self.emotion == 'happy':
            self.speed = 1.5
        elif self.emotion == 'sad':
            self.speed = 1.0
        elif self.emotion == 'angry':
            self.speed = 2.0
        elif self.emotion == 'fearful':
            self.speed = 1.0
            # Avoid dangerous areas
            if random.random() < 0.05:
                self.direction += random.uniform(-math.pi / 4, math.pi / 4)

        # Increase speed if greedy or very hungry
        if self.greedy or self.hunger < 55:
            self.speed = max(self.speed, 3)  # Ensure greedy humans move faster

        super().move()
        self.hunger -= 0.05  # Decrease hunger over time

    def draw(self):
        color = rl.BLUE
        if self.emotion == 'happy':
            color = (173, 216, 230, 255) 
        elif self.emotion == 'angry':
            color = rl.DARKBLUE
        elif self.emotion == 'fearful':
            color = (106, 90, 205, 255)
        elif self.emotion == 'sad':
            color = rl.BLUE
        rl.draw_circle(self.x, self.y, 9, color)

# Define new animal types
class Rabbit(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(1.5, 3.0)
        self.reproduction_chance = 0.2

    def draw(self):
        rl.draw_circle(self.x, self.y, 4, rl.GRAY)

class Bird(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(2.0, 4.0)
        self.reproduction_chance = 0.3

    def move(self, humans, predators):
        # Avoid collisions with predators and humans
        for predator in predators:
            if self.distance_to(predator) < 70:
                angle = math.atan2(self.y - predator.y, self.x - predator.x)
                self.direction = angle 

        for human in humans:
            if self.distance_to(human) < 70:
                angle = math.atan2(self.y - human.y, self.x - human.x)
                self.direction = angle 

        # Move in the current direction
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

        # Check for boundary collision and adjust direction
        if self.x <= 0 or self.x >= SCREEN_WIDTH:
            self.direction = math.pi - self.direction
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            self.direction = -self.direction

        # Randomly change direction
        if random.random() < 0.60:  
            self.direction += random.uniform(-0.5, 0.5)

        # Ensure the bird stays within screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH))
        self.y = max(0, min(self.y, SCREEN_HEIGHT))

        self.hunger-=0.05

    def draw(self):
        rl.draw_circle(self.x, self.y, 4, rl.YELLOW)

class Raindrop:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT)
        self.speed = random.uniform(2, 5)
        self.length = random.uniform(5, 15)
        self.color = rl.BLUE

    def move(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-SCREEN_HEIGHT, -1)
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self):
        rl.draw_line(int(self.x), int(self.y), int(self.x), int(self.y + self.length), self.color)

class Zone:
    def __init__(self, name, temperature_range, humidity_range,color):
        self.name = name
        self.temperature_range = temperature_range
        self.humidity_range = humidity_range
        self.color = color
    
    def get_color(self):
        return self.color

    def get_temperature(self):
        return random.uniform(self.temperature_range[0], self.temperature_range[1])

    def get_humidity(self):
        return random.uniform(self.humidity_range[0], self.humidity_range[1])

    def get_weather(self):
        # Simple weather effects based on the zone
        weather = "clear"
        if self.name == "Desert":
            if random.random() < 0.05:
                weather = "rain"
        elif self.name == "Grassland":
            if random.random() < 0.2:
                weather = "rain"
        elif self.name == "Forest":
            if random.random() < 0.3:
                weather = "rain"
        elif self.name == "Tundra":
            if random.random() < 0.2:
                weather = "snow"
        return weather
    
class Map:
    def __init__(self, width, height, zone_size):
        self.width = width
        self.height = height
        self.zone_size = zone_size
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.assign_zones()
        self.smooth_zones()

    def assign_zones(self):
        # Define zone types and their attributes
        zones = [
            Zone("Desert", (30, 50), (0, 20), DESERT_COLOR),
            Zone("Grassland", (15, 30), (20, 60), GRASSLAND_COLOR),
            Zone("Forest", (5, 15), (60, 100), FOREST_COLOR),
            Zone("Tundra", (-10, 5), (20, 50), TUNDRA_COLOR)
        ]
        
        # Initial random assignment of zones
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.choice(zones)

    def smooth_zones(self):
        # Smooth the map to ensure contiguous zones
        for _ in range(5):  # Number of smoothing iterations
            new_grid = [[None for _ in range(self.width)] for _ in range(self.height)]
            for y in range(self.height):
                for x in range(self.width):
                    # Count the occurrences of each zone in the surrounding cells
                    zone_counts = {}
                    for dy in range(-1, 5):
                        for dx in range(-1, 5):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                zone = self.grid[ny][nx]
                                if zone not in zone_counts:
                                    zone_counts[zone] = 0
                                zone_counts[zone] += 1
                    # Choose the most common zone in the surrounding cells
                    most_common_zone = max(zone_counts, key=zone_counts.get)
                    new_grid[y][x] = most_common_zone
            self.grid = new_grid

    def get_zone(self, x, y):
        return self.grid[y][x]
    
    def get_sunlight_and_humidity(self, x, y):
        zone = self.get_zone(x, y)
        sunlight = zone.get_temperature() 
        humidity = zone.get_humidity()  
        return sunlight, humidity

def draw_map(game_map):
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    cell_width = screen_width // game_map.width
    cell_height = screen_height // game_map.height

    for y in range(game_map.height):
        for x in range(game_map.width):
            zone = game_map.get_zone(x, y)
            color = zone.get_color() if zone else rl.DARKGRAY
            rl.draw_rectangle(x * cell_width, y * cell_height, cell_width, cell_height, color)

# Initialize the simulation
def main():
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, b"Open World Simulation")
    rl.set_target_fps(60)

    plants = []
    animals = []
    predators = []
    tigers=[]
    lions=[]
    humans = []
    rabbits = []
    birds = []

    sunlight = 50
    humidity = 50
    weather = SUNNY

    raindrops = [Raindrop() for _ in range(RAINDROP_COUNT)]

    desert = Zone("Desert", (30, 50), (5, 15),DESERT_COLOR)
    grassland = Zone("Grassland", (15, 30), (30, 60),GRASSLAND_COLOR)
    forest = Zone("Forest", (5, 20), (60, 90),FOREST_COLOR)
    tundra = Zone("Tundra", (-30, 5), (10, 30),TUNDRA_COLOR)

    game_map = Map(100, 100,1)  # Example map size 10x10

    while not rl.window_should_close():
        # Input handling to place entities
        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            cell_width = SCREEN_WIDTH // game_map.width
            cell_height = SCREEN_HEIGHT // game_map.height
            
            cell_x = mouse_x // cell_width
            cell_y = mouse_y // cell_height
            
            # Ensure cell_x and cell_y are within bounds
            cell_x = min(max(cell_x, 0), game_map.width - 1)
            cell_y = min(max(cell_y, 0), game_map.height - 1)
            
            # Get the zone for the clicked cell
            zone = game_map.get_zone(cell_x, cell_y)
            plants.append(Plant(mouse_x, mouse_y,game_map))

        # Check for key presses to spawn specific animal types
        if rl.is_key_pressed(rl.KEY_A):  # Example: 'A' key spawns an Animal
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            animals.append(Animal(mouse_x, mouse_y))
        elif rl.is_key_pressed(rl.KEY_P):  # Example: 'P' key spawns a Predator
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            predators.append(Predator(mouse_x, mouse_y))
        elif rl.is_key_pressed(rl.KEY_H):  # Example: 'H' key spawns a Human
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            humans.append(Human(mouse_x, mouse_y))
        elif rl.is_key_pressed(rl.KEY_R):  # Example: 'R' key spawns a Rabbit
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            rabbits.append(Rabbit(mouse_x, mouse_y))
        elif rl.is_key_pressed(rl.KEY_B):  # Example: 'B' key spawns a Bird
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            birds.append(Bird(mouse_x, mouse_y))
        elif rl.is_key_pressed(rl.KEY_L):  # Example: 'L' key spawns a Lion
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            lions.append(Lion(mouse_x, mouse_y))
        elif rl.is_key_pressed(rl.KEY_T):  # Example: 'T' key spawns a Tiger
            mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
            tigers.append(Tiger(mouse_x, mouse_y))

        if rl.is_key_pressed(rl.KEY_W):  # Example: 'W' key changes weather
            weather = (weather % 3) + 1

        if weather == SUNNY:
            pass
            '''if(sunlight<70):
                sunlight+=30'''
        elif weather == CLOUDY:
            pass
            '''if(sunlight>50):
                sunlight-=25'''
        elif weather == RAINY:
            pass
            '''if(humidity<60):
                humidity+=12
            if(humidity>90):
                humidity-=4'''

        # Edit parameters with keyboard input
        if rl.is_key_pressed(rl.KEY_UP):
            sunlight = min(sunlight + 5, 100)
        elif rl.is_key_pressed(rl.KEY_DOWN):
            sunlight = max(sunlight - 5, 0)
        elif rl.is_key_pressed(rl.KEY_LEFT):
            humidity = max(humidity - 5, 0)
        elif rl.is_key_pressed(rl.KEY_RIGHT):
            humidity = min(humidity + 5, 100)

        # Update entities
        for plant in plants:
            plant.grow(sunlight, humidity,plants)

        for predator in predators:
            predator.move(animals, humans, rabbits)  # Pass predator list to move method
            if predator.hunger <= 0:
                predators.remove(predator)

        for tiger in tigers:
            tiger.move(animals,humans, rabbits)  # Pass tiger list to move method
            if tiger.hunger <= 0:
                tigers.remove(tiger)

        for lion in lions:
            lion.move(animals,humans,rabbits)  # Pass lion list to move method
            if lion.hunger <= 0:
                lions.remove(lion)

        for human in humans:
            human.move()
            human.hunt(animals, predators,rabbits)
            if human.hunger <= 0:
                humans.remove(human)

        for animal in animals:
            animal.move()
            animal.eat_plants(plants)  # Eat plants
            animal.reproduce(animals)  # Reproduce

            if animal.hunger <= 0:
                animals.remove(animal)

            # Animals flee from predators and humans
            for predator in predators:
                if animal.distance_to(predator) < 30:
                    angle = math.atan2(animal.y - predator.y, animal.x - predator.x)
                    animal.direction = angle
            for human in humans:
                if animal.distance_to(human) < 30:
                    angle = math.atan2(animal.y - human.y, animal.x - human.x)
                    animal.direction = angle

        for rabbit in rabbits:
            rabbit.move()
            rabbit.eat_plants(plants)  # Eat plants
            rabbit.reproduce(rabbits)  # Reproduce

            if rabbit.hunger <= 0:
                rabbits.remove(rabbit)

            # Rabbits flee from predators and humans
            for predator in predators:
                if rabbit.distance_to(predator) < 30:
                    angle = math.atan2(rabbit.y - predator.y, rabbit.x - predator.x)
                    rabbit.direction = angle
            for human in humans:
                if rabbit.distance_to(human) < 30:
                    angle = math.atan2(rabbit.y - human.y, rabbit.x - human.x)
                    rabbit.direction = angle

        for bird in birds:
            bird.move(humans, predators)
            bird.eat_plants(plants)  # Eat plants
            bird.reproduce(birds)  # Reproduce

            if bird.hunger <= 0:
                birds.remove(bird)


        if weather == RAINY:
            for raindrop in raindrops:
                raindrop.move()

        # Draw entities
        rl.begin_drawing()
        draw_map(game_map)

        if weather == RAINY:
            for raindrop in raindrops:
                raindrop.draw()

        for plant in plants:
            plant.draw()

        for animal in animals:
            animal.draw()

        for predator in predators:
            predator.draw()

        for human in humans:
            human.draw()

        for rabbit in rabbits:
            rabbit.draw()

        for bird in birds:
            bird.draw()

        for tiger in tigers:
            tiger.draw()
        
        for lion in lions:
            lion.draw()

        # Draw parameters
        rl.draw_text(f"Sunlight: {sunlight}", 10, 10, 20, rl.DARKGRAY)
        rl.draw_text(f"Humidity: {humidity}", 10, 40, 20, rl.DARKGRAY)  
        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
