from tester.led_tester import LedTester
from tester.led_tower_tester import LedTowerTester
from tester.light_tester import LightTester
from tester.servo_tester import ServoTester
from tester.motion_tester import MotionTester
from tester.touch_tester import TouchTester
from tester.potentiometer_tester import PotentiometerTester
from tester.light_sensor_tester import LightSensorTester
from tester.ultrasonic_tester import UltrasonicTester
from tester.encoder_tester import EncoderTester
from tester.joystick_tester import JoystickTester
from tester.sound_tester import SoundTester
from tester.climate_tester import ClimateTester
from tester.gyro_tester import GyroTester
from tester.gesture_tester import GestureTester
from tester.color_tester import ColorTester
from tester.button_tester import ButtonTester

full = [0, 1, 5, 7, 2, 28, 17, 27]
half = [4, 5, 6, 7, 16, 17, 26, 27] # 4 pins
led_tester = LedTester(full)
touch_tester = TouchTester(full) # touch, button and motion are one
button_tester = ButtonTester(full)
motion_tester = MotionTester(full)
led_tower_tester = LedTowerTester(22)
light_tester = LightTester(22)
servo_tester = ServoTester([8, 9])
potentiometer_tester = PotentiometerTester([28, 27]) # potentiometer and light sensor are one
light_sensor_tester = LightSensorTester([28, 27])
ultrasonic_tester = UltrasonicTester([6, 7]) # sad
encoder_tester = EncoderTester(half)
joystick_tester = JoystickTester([26, 27]) # sad
sound_tester = SoundTester([26, 27])
climate_tester = ClimateTester(half)
gyro_tester = GyroTester(half)
gesture_tester = GestureTester([6, 7]) # sad
color_tester = ColorTester([6, 7]) # sad


item_list = [led_tester, motion_tester, servo_tester, touch_tester, potentiometer_tester, encoder_tester, sound_tester, climate_tester, gyro_tester]


