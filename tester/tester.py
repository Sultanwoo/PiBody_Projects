import time
from root_tools import display, ctrl_button

class Tester():
    def __init__(self, name, pins):
        display.clear()
        self.name = name
        self.pins = pins
        
    def start(self):
        alll = [0, 1, 2, 28, 5, 7, 17, 27]
        half = [4, 5, 6, 7, 16, 17, 26, 27]
        analog = [28, 27]
        servo = [8, 9]
        slot_name = ""
        if self.pins == alll:
            slot_name = "ANY GP"
        elif self.pins == half:
            slot_name = "any 4 pin GP on the right"
        elif self.pins == analog:
            slot_name = "GP28 or GP27"
        elif self.pins == servo:
            slot_name = "GP8 or GP9"
        elif type(self.pins) == list:
            slot_name = "GP" + str(self.pins[1])  
        else:
            slot_name = "GP" + str(self.pins) 

        display.clear()
        display.display_text("Hold down the button GP19 to move to the next test", 50, 20)
        display.display_text(f"Testing: {self.name}", 60, display.height - 35)
        display.display_text(f"Connect to: {slot_name}", 60, display.height - 15)
        time.sleep(0.5)

    def finish(self):
        display.clear()
        display.display_text(f"{self.name} Test completed", 60, 80)
        time.sleep(1)  # Delay for stability
        if ctrl_button.value():
            display.display_text(f"Pull the button up!", 50, 100)
        while ctrl_button.value():
            pass
        display.clear()
        



