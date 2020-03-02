# ============================================================================ #
# PlaybackTool
# ============================================================================ #
'''
README.md goes here
'''
# ---------------------------------------------------------------------------- #
# Imports
from maya import cmds, mel  # As always...

# My modules
from KlugTools.Utils import timeline_overlay

# Vendor import
from Qt import QtGui, QtCore, QtWidgets, QtCompat

# ---------------------------------------------------------------------------- #
# Globals

PBT = None
playbackFPS = 24  # Personal pref


# ============================================================================ #
# Event filter --------------------------------------------------------------- #

class UI_Event_Filter(QtCore.QObject):
    def __init__(self, parent):
        super(UI_Event_Filter, self).__init__()
        self._parent = parent
        self.clicks = [0, 0, 0]
    
    def check_clicks(self):
        check  = QtWidgets.QApplication.instance().mouseButtons()
        left   = bool(QtCore.Qt.LeftButton   & check)
        middle = bool(QtCore.Qt.MiddleButton & check)
        right  = bool(QtCore.Qt.RightButton  & check)
        self.clicks = [int(left), int(middle), int(right)]

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if self._parent.mouse_activation_state == False: # Prevent it from firing twice
                self._parent.mouse_activation_state = True
            
                if self._parent.is_active == True:
                    if self._parent.key_activation_state == True:
                        self.check_clicks()
                        if self.clicks == [1, 0, 0]: # Left click only
                            self._parent.scrub_frame_indicator()
                            if self._parent.did_scrub == False: # If not yet scrubbing
                                self._parent.start_scrub()
            
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if self._parent.mouse_activation_state == True: # Prevent it from firing twice
                self._parent.mouse_activation_state = False

                if self._parent.is_active == True:
                    if self._parent.key_activation_state == False:
                        print "Cleanup step"
                        self.check_clicks()
                        if self.clicks == [0, 0, 0]: # Mouse empty
                            self._parent.cleanup()
                        
            if event.type() == QtCore.QEvent.ApplicationStateChange:
                self._parent.cleanup()
                print 'Maya focus lost! Aborting!'

        return QtCore.QObject.eventFilter(self, obj, event)


# ---------------------------------------------------------------------------- #
# Classes

class PlaybackTool(QtWidgets.QWidget):
    """Docstring for PlaybackTool

    Don't run this directly. Use the interface methods.

    """

    def __init__(self):
        super(PlaybackTool, self).__init__()
        self.setObjectName('PlaybackTool')
        
        self.is_active = False
        self.key_activation_state = False
        self.is_playing    = cmds.play(q=True, state=True)
        self.did_scrub     = False
        self.mouse_activation_state = False
        self.panel_under_pointer = None
        
        self.filters_installed = False
        self.ui_event_filter = UI_Event_Filter(self)
        self.install_event_filters()

        self.previous_frame  = cmds.currentTime(q=True)
        self.indicator_frame = self.previous_frame
        self.timeline_indicator = timeline_overlay.Timeline_Overlay()
        self.timeline_indicator.show()
        
        self.timeline_indicator.set_color([255, 0, 120])
        self.timeline_indicator.set_alpha(100)
        self.timeline_indicator.set_frames(self.previous_frame)
        

    def install_event_filters(self):
        if not self.filters_installed:
            QtWidgets.QApplication.instance().installEventFilter(self.ui_event_filter)
        self.filters_installed = True

    def uninstall_event_filters(self):
        if self.filters_installed:
            QtWidgets.QApplication.instance().removeEventFilter(self.ui_event_filter)
        self.filters_installed = False

    def closeEvent(self, e):
        self.timeline_indicator.close()
        self.timeline_indicator.deleteLater()
        self.uninstall_event_filters()


    # -------------------------------------------------------------------------- #
    # Functions

    def start_scrub(self):
        print "Start scrub"
        self.did_scrub = True # Bounce out of playback after scrubbing.
        # Get into the timescrub
        self.panel_under_pointer = cmds.getPanel(underPointer=True)
        mel.eval('storeLastAction("restoreLastContext " + `currentCtx`)')
        cmds.setToolTo('TimeDragger')

    def stop_scrub(self):
        print "Stop scrub"
        self.is_active = False

        
        if self.panel_under_pointer:
            if cmds.getPanel(typeOf=self.panel_under_pointer) == 'modelPanel':
                cmds.evalDeferred("mel.eval('invokeLastAction')")
                return
        mel.eval('invokeLastAction') # For everything else not modelPanel

    def press(self):
        print "Press"
        self.is_active = True
        self.did_scrub = False
        self.key_activation_state = True
        self.is_playing = cmds.play(q=True, state=True)


    def release(self):
        print "Release"

        self.key_activation_state = False

        if self.did_scrub == False:
            self.is_active = False
            if self.is_playing:
                cmds.play(state=False) # Stop
                self.is_playing = False
            else:
                cmds.playbackOptions(edit=True, playbackSpeed=playbackFPS / 24.0)
                cmds.play(state=True) # Start
                self.is_playing = True
                self.scrub_frame_indicator()
        else: # Did scrub
            if self.mouse_activation_state == False:
                self.cleanup()

    def cleanup(self):
        self.stop_scrub()

    def toggle(self):
        if self.is_playing:
            cmds.play(state=False) # Stop
            cmds.currentTime(self.indicator_frame)
            cmds.play(state=True) # Start
            
        else:
            self.previous_frame = cmds.currentTime(q=True)
            cmds.currentTime(self.indicator_frame)
            self.timeline_indicator.set_frames(self.previous_frame)
            self.indicator_frame = self.previous_frame

    def scrub_frame_indicator(self):
        self.indicator_frame = cmds.currentTime(q=True)
        self.timeline_indicator.set_frames(self.indicator_frame)



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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def kill():
    global PBT
    PBT.close()
    PBT.deleteLater()
    PBT = None
    
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
Needs feedback for behavior

'''
