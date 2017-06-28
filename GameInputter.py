"""
A layer of abstraction over ArtificialKeyboard, GameInputter.py takes basic Tekken commands (forward, tap light punch,
hold back) and turns them into the actual keypresses.

"""

from ArtificialKeyboard import ArtificalKeyboard

#directinput scan codes
class Keys:
    UP = 0xc8
    DOWN = 0xd0
    LEFT = 0xCB
    RIGHT = 0xCD
    A = 0x4b
    B = 0x4c
    X = 0x47
    Y = 0x48
    START =  0xc7
    SELECT = 0xd2
    LB = 0x49
    RB = 0x4d
    LT = 0x4a
    RT = 0x4e

class GameControllerInputter:
    BUTTON_1 = Keys.X
    BUTTON_2 = Keys.Y
    BUTTON_3 = Keys.RB
    BUTTON_4 = Keys.B
    BUTTON_LEFT = Keys.LEFT
    BUTTON_RIGHT = Keys.RIGHT
    BUTTON_UP = Keys.UP
    BUTTON_DOWN = Keys.DOWN
    BUTTON_RB = Keys.RB
    BUTTON_ACCEPT = Keys.A



    def __init__(self):
        self.heldKeys = []
        self.tappedKeys = []
        self.releasedKeys = []
        self.heldKeys = []
        self.performedInitialKeyRelease = False
        self.wasOnLeft = True
        self.isOnLeft = True
        self.releasedKeyJailTime = 0
        self.isTekkenActiveWindow = False
        self.SetControlsOnLeft()


    def checkFacing(self):
        isBotOnLeft = self.isOnLeft
        if(self.wasOnLeft != isBotOnLeft):
            if isBotOnLeft:
               self.SetControlsOnLeft()
            else:       #bot is on the right
                self.SetControlsOnRight()
            self.Release()
        self.wasOnLeft = isBotOnLeft

    def SetControlsOnLeft(self):
        self.back = GameControllerInputter.BUTTON_LEFT
        self.forward = GameControllerInputter.BUTTON_RIGHT
        self.right = GameControllerInputter.BUTTON_DOWN
        self.left = GameControllerInputter.BUTTON_UP

    def SetControlsOnRight(self):
        self.back = GameControllerInputter.BUTTON_RIGHT
        self.forward = GameControllerInputter.BUTTON_LEFT
        self.right = GameControllerInputter.BUTTON_UP
        self.left = GameControllerInputter.BUTTON_DOWN

    def TapBack(self):
        self.TapButton(self.back)

    def TapForward(self):
        self.TapButton(self.forward)

    def TapDown(self):
        self.TapButton(GameControllerInputter.BUTTON_DOWN)

    def TapUp(self):
        self.TapButton(GameControllerInputter.BUTTON_UP)

    def TapRight(self):
        self.TapButton(self.right)

    def TapLeft(self):
        self.TapButton(self.left)

    def Tap1(self):
        self.TapButton(GameControllerInputter.BUTTON_1)

    def Tap2(self):
        self.TapButton(GameControllerInputter.BUTTON_2)

    def Tap3(self):
        self.TapButton(GameControllerInputter.BUTTON_3)

    def Tap4(self):
        self.TapButton(GameControllerInputter.BUTTON_4)

    def TapAccept(self):
        self.TapButton(GameControllerInputter.BUTTON_ACCEPT)

    def TapRageArt(self):
        self.TapButton(GameControllerInputter.BUTTON_RB)

    def HoldBack(self):
        self.HoldButton(self.back)

    def HoldDown(self):
        self.HoldButton(GameControllerInputter.BUTTON_DOWN)

    def HoldUp(self):
        self.HoldButton(GameControllerInputter.BUTTON_UP)

    def HoldForward(self):
        self.HoldButton(self.forward)

    def ReleaseForward(self):
        self.ReleaseKeyIfActive(self.forward)
        if self.forward in self.heldKeys:
            self.heldKeys.remove(self.forward)

    def ReleaseUp(self):
        self.ReleaseKeyIfActive(GameControllerInputter.BUTTON_UP)
        if GameControllerInputter.BUTTON_UP in self.heldKeys:
            self.heldKeys.remove(GameControllerInputter.BUTTON_UP)

    def ReleaseBack(self):
        self.ReleaseKeyIfActive(self.back)
        if self.back in self.heldKeys:
            self.heldKeys.remove(self.back)

    def ReleaseDown(self):
        self.ReleaseKeyIfActive(GameControllerInputter.BUTTON_DOWN)
        if GameControllerInputter.BUTTON_DOWN in self.heldKeys:
            self.heldKeys.remove(GameControllerInputter.BUTTON_DOWN )

    def TapButton(self, button):
        if not button in self.releasedKeys:
            self.PressKeyIfActive(button)
            self.tappedKeys.append(button)
            self.releasedKeyJailTime = 0

    def HoldButton(self, button):
        if not button in self.heldKeys:
            self.PressKeyIfActive(button)
            self.heldKeys.append(button)

    def Update(self, isTekkenActiveWindow, isOnLeft):
        self.isTekkenActiveWindow = isTekkenActiveWindow
        self.isOnLeft = isOnLeft
        self.checkFacing()

        if isTekkenActiveWindow and not self.performedInitialKeyRelease:
            self.Release()
            self.performedInitialKeyRelease = True

        else:
            self.releasedKeyJailTime -= 1
            if self.releasedKeyJailTime <= 0:
                self.releasedKeys = []
                for button in self.tappedKeys:
                    self.ReleaseKeyIfActive(button)
                    self.releasedKeys.append(button)
                    if button in self.heldKeys:
                        self.heldKeys.remove(button)
                self.tappedKeys = []

    def Release(self):
        if (self.isTekkenActiveWindow):
            self.heldKeys = []
            GameControllerInputter.ReleaseAllButtons()

    def PressKeyIfActive(self, hexKeyCode):
        if (self.isTekkenActiveWindow):
            ArtificalKeyboard.PressKey(hexKeyCode)

    def ReleaseKeyIfActive(self, hexKeyCode):
        if (self.isTekkenActiveWindow):
            ArtificalKeyboard.ReleaseKey(hexKeyCode)

    def ReleaseAllButtons():
        #print("releasing all buttons")
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_1)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_2)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_3)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_4)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_UP)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_DOWN)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_LEFT)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_RIGHT)
        ArtificalKeyboard.ReleaseKey(GameControllerInputter.BUTTON_RB)


