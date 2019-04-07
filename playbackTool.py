# ========================================================================== #
# PlaybackTool2
# ========================================================================== #
'''
README.md goes here
'''
# -------------------------------------------------------------------------- #
# Imports

import maya.OpenMayaUI as mui  # Handling Maya QT widgets
import maya.api.OpenMaya as api  # Handling callbacks
from maya import cmds, mel  # As always...
import time  # Toggle key timing

# Vendor import
from Qt import QtGui, QtCore, QtWidgets, __binding__ 
if "PyQt" == __binding__:
    import sip
elif "PySide" == __binding__:
    import shiboken as shiboken  # Do Pyside
elif "PySide2" == __binding__:
    import shiboken2 as shiboken # You're on Maya 2018+


# -------------------------------------------------------------------------- #
# Globals

PBT = None
playbackFPS = 24  # Personal pref


# -------------------------------------------------------------------------- #
# Classes

class PlaybackTool(QtWidgets.QWidget):
    """Docstring for PlaybackTool
    
    Don't run this directly.

    """
    def __init__(self):
        super(PlaybackTool, self).__init__()
        self.setObjectName('TimelineGhost')

        self.initUI()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.start         = None
        self.end           = None
        self.total         = None
        self.brush_width   = None
        self.step          = None

        self.isPlaying     = cmds.play(q=True, state=True)
        self.isScrubbing   = False
        self.play_hold     = False

        time_init = cmds.currentTime(query=True)
        self.firstFrame    = time_init
        self.lastFrame     = time_init
        self.ghost_frame   = time_init
        self.current_frame = time_init

        self.callback_IDs = {}
        self._install_callbacks()

    def initUI(self):
        ptr = mui.MQtUtil.findControl(self._get_maya_timeline())
        timelineWidget = shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)

        internalWidget = timelineWidget.children()[0]
        try:
            lyt = internalWidget.children()[0]
        except:
            timelineWidget.layout().setContentsMargins(0, 0, 0, 0)
            lyt = QtWidgets.QVBoxLayout()
            lyt.setContentsMargins(0, 0, 0, 0)
            lyt.setSpacing(0)
            internalWidget.setLayout(lyt)
        lyt.addWidget(self)

    def closeEvent(self, e):
        for callback_ID in self.callback_IDs.values():
            api.MMessage.removeCallback(callback_ID)

    def _install_callbacks(self):
        self.callback_IDs['timechanged'] = \
            api.MEventMessage.addEventCallback(
                'timeChanged', self.on_time_changed)
        self.callback_IDs['playingBack'] = \
            api.MConditionMessage.addConditionCallback(
                'playingBack', self.playingBack)

    def playingBack(self, isPlaying, _):
        self.isPlaying = isPlaying
        if isPlaying:
            self.isScrubbing = not cmds.play(q=True, state=True)
            self.ghost_frame = cmds.currentTime(q=True)
        else:
            self.isScrubbing = False
            self.current_frame = cmds.currentTime(q=True)    
        self.update()

    def on_time_changed(self, *args):
        if self.isPlaying:
            return
        if self.isScrubbing:
            return
        frame = cmds.currentTime(q=True)
        self.ghost_frame = self.current_frame
        self.current_frame = frame
        self.update()


    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw(painter)
        painter.end()

    def draw(self, painter):
        self.start = cmds.playbackOptions(query=True, min=True)
        self.end   = cmds.playbackOptions(query=True, max=True)

        self.total = self.width()
        self.step = (self.total * 0.99) / (self.end-self.start+1)

        pen = QtGui.QPen()
        pen.setWidth(self.step)
        pen.setColor(QtGui.QColor(0, 150, 255, 100))  # I shouldn't hardcode the color...

        frame_pos = (self.ghost_frame - self.start) * self.step + (self.step / 2) + ((self.total * 0.01) * 0.5)
        line = QtCore.QLineF(
            QtCore.QPointF(frame_pos, 0),
            QtCore.QPointF(frame_pos, 200))

        painter.setPen(pen)
        painter.drawLine(line)

    def _get_timeline_range(self):
        time_range = cmds.timeControl(self._get_maya_timeline(), q=True, ra=True )
        return range(int(time_range[0]), int(time_range[1]))

    def _get_maya_timeline(self):
        return mel.eval("$tmpVar=$gPlayBackSlider")


    # -------------------------------------------------------------------------- #
    # Functions

    def press(self):
        # Start the timer
        self.TIME_START = time.time()

        self.isPlaying = cmds.play(q=True, state=True)

        if self.isPlaying:
            cmds.play(state = False)
            self.play_hold = True
        else:
            self.firstFrame = cmds.currentTime(q=True)

        # The only annoying thing is the flashing in&out of the scrub context
        # whether or not we use it.
        # TODO: Investigate a workaround that doesn't use callbacks.
        # I suppose we could be listening for left clicks while the spacebar
        # is held down...
        mel.eval('storeLastAction( "restoreLastContext " + `currentCtx` )')
        cmds.setToolTo( 'TimeDragger' )

    def release(self):

        mel.eval('invokeLastAction')

        if (time.time() - self.TIME_START) < 0.15:  # Quick button press
            if not self.isPlaying and not self.play_hold:
                cmds.playbackOptions(edit=True, playbackSpeed = playbackFPS / 24.0)
                cmds.play(state = True)
        
        self.play_hold = False

    def toggle(self):
        play_check = self.isPlaying
        if play_check:  # Or else Maya will ignore the playhead
            cmds.play(state=False)

        temp_frame = cmds.currentTime(q=True)
        cmds.currentTime(self.ghost_frame)

        if not play_check:
            self.ghost_frame = temp_frame
            self.update()
        else:
            self.update()
            cmds.play(state=True)

# ========================================================================== #
# The interface:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def press():
    global PBT
    if not PBT:
        PBT = PlaybackTool()
    PBT.press()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def release():
    PBT.release()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def toggle():
    PBT.toggle()


# ========================================================================== #
# Manual Override

if __name__ == "__main__":
    try:
        PBT.close()
        PBT.deleteLater()
    except:
        pass

    PBT = PlaybackTool()


# ========================================================================== #
# Notes
'''
Needs polish...
'''
