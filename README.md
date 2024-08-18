# Pygame 3D Cube Renderer with PyOpenGL

This project is a 3D cube renderer built using Pygame and PyOpenGL. It allows for rendering 3D cubes with customizable positions, scales, and rotations, and includes a first-person camera for navigating the 3D space.

## Features

- Render 3D cubes with different positions, scales, and rotations.
- First-person camera controls for navigating the scene.
- Adjustable camera sensitivity and movement speed.
- Object properties loaded from a JSON file.

## Requirements

- Python 3.x

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/LostGameDev/Cube.git
    cd Cube
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Place your 3D object definitions in the `objects/objects.json` file. The file should follow this format:

    ```json
    {
        "ObjectName": 
        [
            {   
                "X": 0,
                "Y": 0,
                "Z": 0,
                "ScaleX": 1,
                "ScaleY": 1,
                "ScaleZ": 1,
                "RotationX": 0,
                "RotationY": 0,
                "RotationZ": 0,
                "Red": 0,
                "Green": 255,
                "Blue": 0,
                "Alpha": 255
            }
        ]
    }
    ```
This example will create a green opaque cube at 0, 0, 0 with default scale and with no rotation with the name ObjectName.

2. Run the `main.py` script:

    ```sh
    python main.py
    ```

3. Use the following controls to navigate the scene:

    - `W`: Move forward
    - `S`: Move backward
    - `A`: Move left
    - `D`: Move right
    - `SPACE`: Move up
    - `LSHIFT`: Move down
    - `Mouse`: Look around
    - `ESC`: Pause
    - `R`: Reset camera position and reload objects
    - `T`: Enable/disable wireframe mode
    - `B`: Enable/disable lighting

## Building

Simply run build.py to compile the program:
```sh
python build.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
