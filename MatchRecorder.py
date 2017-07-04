
from TekkenGameState import TekkenGameState
from ButtonCommandEnum import Command
from MoveInfoEnums import InputDirectionCodes
from MoveInfoEnums import InputAttackCodes

class MatchRecorder:
    NOTATION = {
        Command.HoldForward : 'F',
        Command.HoldBack: 'B',
        Command.HoldDown: 'D',
        Command.HoldUp: 'U',

        Command.Hold1: '+1*',
        Command.Hold2: '+2*',
        Command.Hold3: '+3*',
        Command.Hold4: '+4*',

        Command.ReleaseForward: '-F',
        Command.ReleaseBack: '-B',
        Command.ReleaseDown: '-D',
        Command.ReleaseUp: '-U',

        Command.Release1: '+1-',
        Command.Release2: '+2-',
        Command.Release3: '+3-',
        Command.Release4: '+4-'
    }

    def __init__(self):
        self.input_log = []


    def Update(self, gameState:TekkenGameState):
        bot_input = gameState.GetBotInputState()
        opp_input = gameState.GetOppInputState()
        #self.input_log.append(bot_input[0].name + "," + bot_input[1].name + "|" + opp_input[0].name + "," + opp_input[1].name)
        self.input_log.append((bot_input, opp_input))

    def GetInputAsCommands(self):
        commands = []
        previous_input = None
        for input in self.input_log:
            if previous_input != None:
                commands += self.TransitionToCommandFromCommand(input[1], previous_input[1])
            previous_input = input
        #print(self.CompressCommands(commands))
        return self.CompressCommands(commands)

    def CompressCommands(self, commands):
        compressed_commands = []
        wait_frames = 0
        for command in commands:
            if command[0] == Command.Wait:
                wait_frames += 1
            else:
                if wait_frames > 0:
                    compressed_commands.append((Command.Wait, wait_frames))
                    wait_frames = 0
                compressed_commands.append(command)
        compressed_commands.append((Command.Wait, wait_frames))

        return compressed_commands



    def GetInputAsNotation(self):
        commands = self.GetInputAsCommands()
        notation = self.GetCommandsAsNotation(commands)
        return notation


    def GetCommandsAsNotation(self, commands):
        notation = ""
        for command in commands:
            if command[0] == Command.Wait:
                notation += str(command[1]) + ', '
            else:
                notation += MatchRecorder.NOTATION[command[0]] + ', '
        return notation


    def TransitionToCommandFromCommand(self, input, prev_input):
        command = []
        new_dir = input[0].name
        prev_dir = prev_input[0].name

        command += self.CheckForString('u', prev_dir, new_dir, Command.HoldUp, Command.ReleaseUp)
        command += self.CheckForString('d', prev_dir, new_dir, Command.HoldDown, Command.ReleaseDown)
        command += self.CheckForString('b', prev_dir, new_dir, Command.HoldBack, Command.ReleaseBack)
        command += self.CheckForString('f', prev_dir, new_dir, Command.HoldForward, Command.ReleaseForward)


        new_att = input[1].name
        prev_att = prev_input[1].name

        command += self.CheckForString('1', prev_att, new_att, Command.Hold1, Command.Release1)
        command += self.CheckForString('2', prev_att, new_att, Command.Hold2, Command.Release2)
        command += self.CheckForString('3', prev_att, new_att, Command.Hold3, Command.Release3)
        command += self.CheckForString('4', prev_att, new_att, Command.Hold4, Command.Release4)

        command.append((Command.Wait, 1))

        return command

    def CheckForString(self, string, old, new, on_add, on_remove):
        command = []
        if string in old and not string in new:
            command.append((on_remove, 0))
        if string in new and not string in old:
            command.append((on_add, 0))
        return command



    def PrintInputLog(self, filename):
        print("Recording match...")
        with open(filename, 'w') as fw:
            for input in self.input_log:
                fw.write(input + "\n")
        print("...match recorded")


