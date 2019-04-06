# ========================================================================== #
# PlaybackTool
# ========================================================================== #
'''
About:
Collaboration between Joe Holmark and Daniel Klug to mimic the playback
functionality of studio animation software.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

Usage:
PlaybackTool will play/pause playback with a quick tap. If you press and hold
the hotkey, you can also left click and drag to scrub the timeline.

If you tap the toggle key during playback, it will restart playback from the
start frame.

If you tap the toggle key any other time, it will flip between the start and
end frame of the last scrub or playback.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

Installation:
3 hotkeys need to be made - PRESS, RELEASE, and Toggle

# PRESS
from PlaybackTool import playbackTool
playbackTool.press()

# RELEASE
playbackTool.release()

# Toggle hotkey
from PlaybackTool import playbackTool
playbackTool.toggle()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

Current limitation:
PlaybackTool will not yet register manual clicks or scrubs in the timeline.
Will install callbacks in the next version.

'''
# -------------------------------------------------------------------------- #
# Imports

import maya.api.OpenMayaUI as apiUI
import maya.api.OpenMaya as api
from maya import cmds, mel
import time

# -------------------------------------------------------------------------- #
# Globals

playbackFPS = 24  # Personal pref

TIME_START = 0
isPlaying = False
isScrubbing = False
firstFrame, lastFrame = [0, 0]

# -------------------------------------------------------------------------- #
# Functions

def press():
    global TIME_START, isPlaying, firstFrame

    # Start the timer
    TIME_START = time.time()

    isPlaying = cmds.play(q=True, state=True)

    if isPlaying:
        cmds.play(state = False)
    else:
        firstFrame = cmds.currentTime(q=True)

    # The only annoying thing is the flashing in&out of the scrub context
    # whether or not we use it.
    # TODO: Investigate a workaround that doesn't use callbacks.
    mel.eval('storeLastAction( "restoreLastContext " + `currentCtx` )')
    cmds.setToolTo( 'TimeDragger' )

def release():
    global lastFrame

    lastFrame  = cmds.currentTime(q=True)

    mel.eval('invokeLastAction')

    if (time.time() - TIME_START) < 0.15:  # Quick button press
        if not isPlaying:
            cmds.playbackOptions(edit=True, playbackSpeed = playbackFPS / 24.0)
            cmds.play(state = True)

def toggle():
    global firstFrame, lastFrame, isPlaying

    isPlaying = cmds.play(q=True, state=True)

    if isPlaying:  # Or else Maya will ignore the playhead
        cmds.play(state=False)

    cmds.currentTime(firstFrame)

    if isPlaying:
        cmds.play(state=True)

    firstFrame, lastFrame = lastFrame, firstFrame

# ========================================================================== #
'''
from PlaybackTool import playbackTool
reload(playbackTool)
print playbackTool.firstFrame, playbackTool.lastFrame  # Fuck yes
'''
