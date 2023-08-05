#! python

import serial


class berkeley500AError(Exception):
    """
    Berkeley 500A expection handle
    """
    def __init__(self, errCode):
        if '?1' == errCode:
            self.errStr = 'Invalid command'
        elif '?2' == errCode:
            self.errStr = 'Value out of range'
        else:
            self.errStr = 'Unkown error code'

    def __str__(self):
        return self.errStr


class berkeley500A(object):
    '''API for the Berkeley Nucleonics Corp Modell 500 A Digital Delay Generator

    This class provides an API for controll of the Berkeley Nucleonics Corp
    Modell 500 A Digital Delay Generator.
    The latest values of the device are stored in the class object to ease the
    control.

    :param comPort: address of serial port
    :type comPort: string

    Example::
        comPort = 'COM1'
        delayGen = berkeley500A(comPort)
        print(delayGen.gate)
        print(delayGen.getEcho())
    '''

    __version__ = '0.1.0'

    def __init__(self, comPort):
        self.comLink = serial.Serial(comPort, baudrate=9600,
                                     stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=5,
                                     parity=serial.PARITY_NONE)
        # Enable the echo
        try:
            _ = self.sendRcv('ECHO 1')
        except IndexError:
            try:
                self.echo = self.getEcho()
            except berkeley500AError:
                raise RuntimeError('Cannot connect to device.')

        self.setEcho(True)
        self.mode = self.getMode()
        self.gate = self.getGate()
        self.toPer = self.getToPer()
        self.DCOn = self.getDCOn()
        self.DCOff = self.getDCOff()
        self.trig = self.getTrig()
        self.cycles = self.getCycles()
        self.burst = self.getBurst()
        self.fmark = self.getFmark()
        self.T1 = {}
        self.T1['width'] = self.getWidth(1)
        self.T1['delay'] = self.getDelay(1)
        self.T1['polarity'] = self.getPolarity(1)
        self.T2 = {}
        self.T2['width'] = self.getWidth(2)
        self.T2['delay'] = self.getDelay(2)
        self.T2['polarity'] = self.getPolarity(2)
        self.T2['enable'] = self.getT2()
        self.T2['gate'] = self.getT2Gate()
        self.T2['relPeriod'] = self.getT2relPeriod()
        self.T2['wait'] = self.getT2waitPulses()
        self.T3 = {}
        self.T3['width'] = self.getWidth(3)
        self.T3['delay'] = self.getDelay(3)
        self.T3['polarity'] = self.getPolarity(3)
        self.T4 = {}
        self.T4['width'] = self.getWidth(4)
        self.T4['delay'] = self.getDelay(4)
        self.T4['polarity'] = self.getPolarity(4)

    def sendRcv(self, command):
        '''Takes a command and send it

        The string is converted to a compatible byte and send
        to the delay generator. The answer is analysed and in
        case a berkeley500AError raised.

        :param command: Command string
        :type: string
        :returns: answer
        :rtype: string
        '''
        commandByte = bytes(command, 'ASCII')
        sendByte = b'$' + commandByte + b'\r'
        try:
            if not self.comLink.isOpen():
                self.comLink.open()
            self.comLink.write(sendByte)
            answer = self.comLink.readline()
            self._checkErr(answer)
        finally:
            self.comLink.close()
        if answer.startswith(commandByte) or answer.startswith(b'ok'):
            return answer.decode('ASCII')
        else:
            raise RuntimeWarning('Answer is for different command.')

    def setEcho(self, enable=True):
        '''Enables or disables the echo

        Set the echo, should be set enabled, otherwise no communication with
        the computer. True enables to echo.

        :param enable: True by default
        :type: boolean
        '''
        answer = self.sendRcv('ECHO ' + str(int(enable)))
        self.echo = bool(answer[:-2].split()[1])

    def setMode(self, mode):
        '''Sets the mode

        Set the mode to
        0 = Continuous
        1 = Burst
        2 = Duty Cycle
        3 = Single Shot
        4 = External Trigger

        :param mode: Mode.
        :type: int
        '''
        if mode in range(5):
            answer = self.sendRcv('MODE ' + str(mode))
        else:
            raise ValueError('Mode out of range')
        self.mode = int(answer[:-2].split()[1])

    def setGate(self, gate):
        '''Sets the gate

        Enables the external trigger input to function as a gate controlling
        all outputs. Cannot be used with external trigger mode.

        Set the gate to
        0 = off
        1 = active low
        2 = active high

        :param gate: gate type
        :type: int
        '''
        answer = self.sendRcv('GATE ' + str(gate))
        self.gate = int(answer[:-2].split()[1])

    def setToPer(self, toPer):
        '''Sets to To internal sync period

        Sets the To internal sync period, in microseconds *10, used only in
        Continuous, Burst and Duty Cycle modes.
        Possible values for toPer: 1000 to 999999998

        :param toPer: internal sync period
        :type: int
        '''
        answer = self.sendRcv('ToPer ' + str(toPer))
        self.toPer = int(answer[:-2].split()[1])

    def setDCOn(self, dcOnTime):
        '''Sets the on time, in seconds, for the Duty Cycle Mode

        Possible values for dcOnTime: 1 - 10000

        :param dcOnTime: on time for Duty Cycle Mode
        :type: int
        '''
        answer = self.sendRcv('DC:On ' + str(dcOnTime))
        self.DCOn = int(answer[:-2].split()[1])

    def setDCOff(self, dcOffTime):
        '''Sets the off time, in seconds, for the Duty Cycle Mode

        Possible values for dcOffTime: 1 - 10000

        :param dcOffTime: off time for Duty Cycle Mode
        :type: int
        '''
        answer = self.sendRcv('DC:Off ' + str(dcOffTime))
        self.DCOff = int(answer[:-2].split()[1])

    def setTrig(self, edge):
        '''Sets the active edge of the Ext/Gate signal

        Sets the active edge of the Ext/Gate signal, when used as an external
        trigger.

        Possible values:
        0 = falling edge
        1 = raising edge

        :param edge: set edge type
        :type: int
        '''
        answer = self.sendRcv('TRIG ' + str(edge))
        self.trig = int(answer[:-2].split()[1])

    def setCycles(self, cycles):
        '''Sets the number of cycles for the Duty Cycle mode

        Possible values: 0 - 10000

        :param cycles: number of cycles
        :type: int
        '''
        answer = self.sendRcv('CYCLES ' + str(cycles))
        self.cycles = int(answer[:-2].split()[1])

    def setBurst(self, nPulses):
        '''Sets the number of pulses in the Burst Mode

        Possible values: 0 - 50000

        :param nPulses: number of pulses
        :type: int
        '''
        answer = self.sendRcv('#/BURST ' + str(nPulses))
        self.burst = int(answer[:-2].split()[1])

    def setWidth(self, channel, width):
        '''Sets pulse width in microseconds*10

        Sets the pulse width for channel in microseconds*10

        Possible values for width: 4 - 999999998

        :param channel: number of channel
        :type: int
        :param width: pulse width in microseconds*10
        :type: int
        '''
        answer = self.sendRcv('T' + str(channel) + ':Wid ' + str(width))
        if 1 == channel:
            self.T1['width'] = int(answer[:-2].split()[1])
        elif 2 == channel:
            self.T2['width'] = int(answer[:-2].split()[1])
        elif 3 == channel:
            self.T3['width'] = int(answer[:-2].split()[1])
        elif 4 == channel:
            self.T4['width'] = int(answer[:-2].split()[1])

    def setDelay(self, channel, delay):
        '''Sets the delay in in microseconds*10

        Sets the delay for channel in microseconds*10

        Possible values for delay: 4 - 999999998

        :param channel: number of channel
        :type: int
        :param delay: delay in microseconds*10
        :type: int
        '''
        answer = self.sendRcv('T' + str(channel) + ':Dly ' + str(delay))
        if 1 == channel:
            self.T1['delay'] = int(answer[:-2].split()[1])
        elif 2 == channel:
            self.T2['delay'] = int(answer[:-2].split()[1])
        elif 3 == channel:
            self.T3['delay'] = int(answer[:-2].split()[1])
        elif 4 == channel:
            self.T4['delay'] = int(answer[:-2].split()[1])

    def setPolarity(self, channel, pol):
        '''Sets the polarity of the output ofo channel

        Possible values for pol:
        0 = Negative (active low)
        1 = Positive (active high)

        :param channel: number of channel
        :type: int
        :param pol: polarity
        :type: int
        '''
        answer = self.sendRcv('T' + str(channel) + ':Pol ' + str(pol))
        if 1 == channel:
            self.T1['polarity'] = int(answer[:-2].split()[1])
        elif 2 == channel:
            self.T2['polarity'] = int(answer[:-2].split()[1])
        elif 3 == channel:
            self.T3['polarity'] = int(answer[:-2].split()[1])
        elif 4 == channel:
            self.T4['polarity'] = int(answer[:-2].split()[1])

    def setT2(self, enable):
        '''Turns the output of channel 2 on and off

        :param enable: enables or disables channel 2
        :type: boolean
        '''
        answer = self.sendRcv('T2:Enable ' + str(int(enable)))
        self.T2['enable'] = bool(answer[:-2].split()[1])

    def setT2Gate(self, gate):
        '''Enables the external unput to act as gate for T2's output

        Possible values for gate:
        0 = Off
        1 = Active Low
        2 = Active High

        :param gate: gate type
        :type: int
        '''
        answer = self.sendRcv('T2:Gate ' + str(gate))
        self.T2['gate'] = int(answer[:-2].split()[-1])

    def setT2waitPulses(self, nPulses):
        '''Set the number of pulses to wait after starting T1

        Set the number of pulses to wait after starting T1 before starting T2.
        Note: This is used to allow time for the laser to stabilize when T1 is
        used as a flashlamp trigger and T2 is the Q-switch trigger

        Possible values for nPulses: 0 - 10000

        :param nPulses: number of pulses
        :type: int
        '''
        answer = self.sendRcv('T2:Wait ' + str(nPulses))
        self.T2['wait'] = int(answer[:-2].split()[1])

    def setT2relPeriod(self, factor):
        '''Sets the period of T2 relative to T1

        Sets the period of T2 relative to T1. The period of T2 is the period
        of T1 multiplied by factor

        Possible values for factor: 0 - 10000

        :param factor: multiplication factor
        :type: int
        '''
        answer = self.sendRcv('T2*n ' + str(factor))
        self.T2['relPeriod'] = int(answer[:-2].split()[1])

    def beep(self, nBeep):
        '''Beeps the buzzer inside the 500A

        Possible values for nBeep: 1 - 1000

        :param nBeep: number of beeps
        :type: int
        '''
        _ = self.sendRcv('BEEP ' + str(nBeep))

    def run(self, enable):
        '''Enables / disables the pulse generator output

        :param enable:
        :type: boolean
        '''
        _ = self.sendRcv('RUN ' + str(int(enable)))

    def recall(self, slot):
        '''Recalls a stored configuration

        Possible values for slot: 1- 12

        :param slot: number of storage
        :type: int
        '''
        _ = self.sendRcv('RECALL ' + str(slot))

    def store(self, slot):
        '''Store a configuration

        Possible values for slot: 1- 12

        :param slot: number of storage
        :type: int
        '''
        _ = self.sendRcv('STORE ' + str(slot))

    def resetShotCounter(self):
        '''Resets shot counter
        '''
        _ = self.sendRcv('SHOTS 0')

    def setFmark(self, character):
        '''Sets the character used as a decimal point on the display

        Possible values for character:
        0 = , (comma)
        1 = . (period)

        :param character: character representation
        :type: int
        '''
        answer = self.sendRcv('Fmark, ' + str(character))
        self.fmark = int(answer[:-2].split()[1])

    def getEcho(self):
        '''Gets the current echo status

        :returns echo: echo enabled/disabled
        :rtype: boolean
        '''
        answer = self.sendRcv('ECHO ?')
        return bool(answer[:-2].split()[-1])

    def getMode(self):
        '''Gets the current mode

        :returns mode: generator mode
        :rtype: int
        '''
        answer = self.sendRcv('MODE ?')
        return int(answer[:-2].split()[-1])

    def getGate(self):
        '''Gets the current gate

        :returns gate: gate type
        :rtype: int
        '''
        answer = self.sendRcv('GATE ?')
        return int(answer[:-2].split()[-1])

    def getToPer(self):
        '''Gets the current To internal sync period

        :returns toPer: internal sync period
        :rtype: int
        '''
        answer = self.sendRcv('ToPer ?')
        return int(answer[:-2].split()[-1])

    def getDCOn(self):
        '''Gets the current on time for Duty Cycle Mode

        :returns DCOn: on time
        :rtype: int
        '''
        answer = self.sendRcv('DC:On ?')
        return int(answer[:-2].split()[-1])

    def getDCOff(self):
        '''Gets the current of time for Duty Cycle Mode

        :returns DCOff: off time
        :rtype: int
        '''
        answer = self.sendRcv('DC:Off ?')
        return int(answer[:-2].split()[-1])

    def getTrig(self):
        '''Gets the current trigger setting

        :returns trig: trigger setting
        :rtype: int
        '''
        answer = self.sendRcv('TRIG ?')
        return int(answer[:-2].split()[-1])

    def getCycles(self):
        '''Gets the current cycles in Duty Cycle Mode

        :returns cycles: number of cycles in Duty Cycle Mode
        :rtype: int
        '''
        answer = self.sendRcv('CYCLES ?')
        return int(answer[:-2].split()[-1])

    def getBurst(self):
        '''Gets the current number of cycles in Burst Mode

        :returns burst: number of cycles in Burst Mode
        :rtype: int
        '''
        answer = self.sendRcv('#/BURST ?')
        return int(answer[:-2].split()[-1])

    def getWidth(self, channel):
        '''Gets the current width of channel

        :param channel: channel number
        :type: int
        :returns width: width of channel
        :rtype: int
        '''
        answer = self.sendRcv('T' + str(channel) + ':Wid ?')
        return int(answer[:-2].split()[-1])

    def getDelay(self, channel):
        '''Gets the current delay of channel

        :param channel: channel number
        :type: int
        :returns delay: delay of channel
        :rtype: int
        '''
        answer = self.sendRcv('T' + str(channel) + ':Dly ?')
        return int(answer[:-2].split()[-1])

    def getPolarity(self, channel):
        '''Gets the current polarity of channel

        :param channel: channel number
        :type: int
        :returns polarity: polarity of channel
        :rtype: int
        '''
        answer = self.sendRcv('T' + str(channel) + ':Pol ?')
        return int(answer[:-2].split()[-1])

    def getT2(self):
        '''Gets the output status of T2

        :returns polarity: polarity of channel
        :rtype: boolean
        '''
        answer = self.sendRcv('T2:Enable ?')
        return bool(answer[:-2].split()[-1])

    def getT2Gate(self):
        '''Gets T2 external input status

        :returns T2Gate: gate input status
        :rtype: int
        '''
        answer = self.sendRcv('T2:Gate ?')
        return int(answer[:-2].split()[-1])

    def getT2waitPulses(self):
        '''Gets T2 number of wait pulses

        :returns nPulses: number of pulses
        :rtype: int
        '''
        answer = self.sendRcv('T2:Wait ?')
        return int(answer[:-2].split()[-1])

    def getT2relPeriod(self):
        '''Gets T2 relative period to T1

        :returns factor: multiplication factor
        :rtype: int
        '''
        answer = self.sendRcv('T2*n ?')
        return int(answer[:-2].split()[-1])

    def getFmark(self):
        '''Gets the current Fmark

        :returns factor: multiplication factor
        :rtype: int
        '''
        answer = self.sendRcv('Fmark, ?')
        return int(answer[:-2].split()[-1])

    def _checkErr(self, answer):
        '''Checks the answer for errors

        If the answer is a number, no error will be raised. If answer is
        unknown, a berkeley500AError is raised.

        :param answer: answer of device
        :type: byte
        '''
        answerCheck = answer[:-2].split()[-1]
        try:
            # Check wether answer is an integer
            _ = int(answerCheck)
            return
        except ValueError:
            errStr = answerCheck.decode('ASCII')
            if 'ok' == errStr:
                return
            else:
                raise berkeley500AError(errStr)

if __name__ == '__main__':
    comPort = 'COM1'
    delayGen = berkeley500A(comPort)
    print(delayGen.gate)
    print(delayGen.getEcho())
