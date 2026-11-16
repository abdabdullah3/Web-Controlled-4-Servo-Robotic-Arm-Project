# SG90 Robotic Arm Controller

Local browser controller for four SG90 servos using an Arduino Uno R3 over USB.

## Pin mapping
- Base: D3
- Shoulder: D5
- Elbow: D6
- Gripper: D9

## Power and wiring
- Servo signal wires go to the pins above.
- Servo red wires go to a regulated external 5V supply.
- Servo brown/black wires go to the external supply GND.
- Connect external supply GND to Arduino GND.
- Do not power four SG90 servos from the Uno's 5V pin. A regulated 5V supply rated around 3A or more is a sensible starting point for four SG90s; actual current depends on load and servo versions.

## Windows setup
1. Open `arduino/robotic_arm.ino` in Arduino IDE, select Arduino Uno and the correct COM port, then upload.
2. Close Arduino Serial Monitor.
3. In this project folder, run:
   ```
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. If only one serial device is connected, the backend attempts to detect it automatically. Otherwise set the correct port, for example:
   ```
   $env:SERIAL_PORT="COM5"
   ```
5. Run `python app.py`.
6. Open `http://127.0.0.1:5000` in your browser.

## Linux/macOS
Create and activate a virtual environment, install requirements, then set `SERIAL_PORT` if needed (for example `/dev/ttyACM0`) and run `python app.py`.

## Operation
Four independent D-shaped controls send commands over USB:
- `S1:90` controls servo 1 to 90 degrees
- `S2:45` controls servo 2 to 45 degrees
- `S3:0` controls servo 3 to 0 degrees
- `S4:90` controls servo 4 to 90 degrees

The Paired hands card moves both hands together: L-Hand travels from 0° to 90° while R-Hand travels from 90° to 0°. The paired command sends both servo targets in one USB write. The individual hand controls remain available.

The dashboard also includes a range slider for each servo and a reset button that returns to the start positions: Base 90°, Shoulder 45°, L-Hand 0°, and R-Hand 90°. Controls are limited to Base 1–180°, Shoulder 0–90°, L-Hand 0–90°, and R-Hand 90°→0°.

## SG90 calibration and safety
Although the interface supports 0–180°, SG90 clones and mechanical linkages may not safely reach the full range. First test each servo with the arm linkage disconnected or unloaded. If a servo buzzes, strains, heats up, or hits a mechanical stop, stop and reduce its usable angle range or adjust the horn/linkage. Never force the servo by hand while powered.

The Flask app binds to localhost only; do not expose it directly to the public internet.
