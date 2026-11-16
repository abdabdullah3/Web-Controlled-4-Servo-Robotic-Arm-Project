from flask import Flask, render_template, request, jsonify
from serial import Serial, SerialException
from serial.tools import list_ports
import os
import threading
import time

app = Flask(__name__)

# Set SERIAL_PORT to your Arduino port, e.g. COM5 on Windows.
# If omitted, the app auto-selects only when exactly one serial port is detected.
SERIAL_PORT = os.getenv("SERIAL_PORT", "").strip()
BAUD_RATE = 9600
SERVO_LIMITS = {
    1: (1, 180),
    2: (0, 90),
    3: (0, 90),
    4: (0, 90),
}
arduino = None
active_port = None
serial_lock = threading.Lock()


def available_ports():
    return [p.device for p in list_ports.comports()]


def choose_port():
    ports = available_ports()
    if SERIAL_PORT:
        return SERIAL_PORT
    if len(ports) == 1:
        return ports[0]
    return None


def connect_arduino():
    global arduino, active_port

    if arduino and arduino.is_open:
        return True

    port = choose_port()
    if not port:
        return False

    try:
        arduino = Serial(port, BAUD_RATE, timeout=1, write_timeout=1)
        active_port = port
        # Arduino Uno resets when the serial connection opens.
        time.sleep(2)
        return True
    except (SerialException, OSError):
        arduino = None
        active_port = None
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/status")
def status():
    ports = available_ports()
    connected = bool(arduino and arduino.is_open)
    return jsonify({
        "connected": connected,
        "port": active_port or SERIAL_PORT or (ports[0] if len(ports) == 1 else None),
        "available_ports": ports,
        "needs_port_selection": not SERIAL_PORT and len(ports) > 1
    })


@app.post("/api/servo")
def set_servo():
    data = request.get_json(silent=True) or {}

    try:
        servo = int(data["servo"])
        angle = int(data["angle"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Send integer values for servo and angle."), 400

    if servo not in (1, 2, 3, 4):
        return jsonify(error="Servo number must be between 1 and 4."), 400
    minimum, maximum = SERVO_LIMITS[servo]
    if not minimum <= angle <= maximum:
        return jsonify(
            error=f"Servo {servo} angle must be between {minimum} and {maximum} degrees."
        ), 400

    with serial_lock:
        if not connect_arduino():
            ports = available_ports()
            hint = (
                "More than one serial port found. Set SERIAL_PORT to your Arduino port."
                if len(ports) > 1 and not SERIAL_PORT
                else "Check the USB cable, Arduino port, and SERIAL_PORT setting."
            )
            return jsonify(error=f"Arduino connection unavailable. {hint}", available_ports=ports), 503

        try:
            arduino.write(f"S{servo}:{angle}\n".encode("ascii"))
            arduino.flush()
        except (SerialException, OSError) as exc:
            return jsonify(error=f"Serial communication failed: {exc}"), 503

    return jsonify(ok=True, servo=servo, angle=angle)


@app.post("/api/servo-pair")
def set_servo_pair():
    data = request.get_json(silent=True) or {}

    try:
        left_angle = int(data["left_angle"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Send an integer left_angle value."), 400

    if not 0 <= left_angle <= 90:
        return jsonify(error="L-Hand angle must be between 0 and 90 degrees."), 400

    right_angle = 90 - left_angle
    with serial_lock:
        if not connect_arduino():
            ports = available_ports()
            hint = (
                "More than one serial port found. Set SERIAL_PORT to your Arduino port."
                if len(ports) > 1 and not SERIAL_PORT
                else "Check the USB cable, Arduino port, and SERIAL_PORT setting."
            )
            return jsonify(error=f"Arduino connection unavailable. {hint}", available_ports=ports), 503

        try:
            arduino.write(f"S3:{left_angle}\nS4:{right_angle}\n".encode("ascii"))
            arduino.flush()
        except (SerialException, OSError) as exc:
            return jsonify(error=f"Serial communication failed: {exc}"), 503

    return jsonify(ok=True, left_angle=left_angle, right_angle=right_angle)


if __name__ == "__main__":
    # Local PC control only. Do not expose the development server publicly.
    app.run(host="127.0.0.1", port=5000, debug=False)
