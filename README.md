# Open World Simulation Game

An open-world simulation game built with Python and Raylib. This game features a dynamic ecosystem with various animal behaviors, plant growth mechanics, and environmental zones, providing a rich gameplay experience.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Gameplay](#gameplay)
- [Classes Overview](#classes-overview)
- [Contribution](#contributing)
- [License](#license)

## Features

- **Dynamic Weather System:** The environment changes between sunny, cloudy, and rainy conditions, affecting gameplay and ecosystem interactions.
- **Ecosystem Simulation:** Realistic interactions between animals and plants based on health, hunger, and environmental factors, creating a living ecosystem.
- **Animal Behaviors:** A variety of animal types, including herbivores and predators, each exhibiting unique movement, hunting, and social behaviors.
- **Plant Growth Mechanics:** Plants grow based on sunlight, humidity, and the presence of nearby plants, contributing to a realistic and responsive environment.
- **User Interaction:** Players can observe and interact with the ecosystem as animals hunt, reproduce, and compete for resources, enhancing the immersive experience.

## Installation

1. **Install Python:** Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Install Raylib:** Use pip to install the Raylib Python:
   pip install raylib-py
## Gameplay
**Starting the Game:** Upon launching the game, players are greeted with an introductory screen that explains the game mechanics.
**Exploring the Environment:** Players can navigate the open world, observing various animals and plants in their natural habitats.
**Animal Interactions:** Players will witness animals foraging for food, hunting, and engaging in social behaviors like mating and territory disputes.
**Environmental Effects:** Weather conditions can influence animal behavior and plant growth, creating dynamic gameplay scenarios.

## Classes Overview

**Plant Class:**
Represents a plant with properties such as health and growth patches.
Grows based on sunlight and humidity levels and can be consumed by animals.

**Animal Class:**
A base class for all animals, defining essential attributes and methods for movement, reproduction, and feeding.

**Predator Class:**
Inherits from the Animal class and implements specific hunting mechanics.
Can chase and catch prey based on their speed and agility.

**Human Class:**
Inherits from the Animal class and focuses on foraging behavior.
Aims to consume plants while avoiding predators.

and more classses...

## Contribution:
Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License
This project is free to use
