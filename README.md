# PlaybackTool

A simple hotkey setup to mimic the playback and scrub functionality of proprietary animation software from the big studios.


Originally written by Joe Holmark then ~~expanded~~ messed with by Daniel Klug.

![Demo](https://i.imgur.com/k7HgUfm.gif)

## Usage:
PlaybackTool will play/pause playback with a **quick tap**. If you **press and hold**
the hotkey, you can also **left click and drag** to scrub the timeline.

If you **tap the toggle** key during playback, it will restart playback from the
start frame.

If you **tap the toggle** key any other time, it will flip between the start and
end frame of the last scrub or playback.



## Installation:
Place the **playbackTool.py** file in your _~/maya/scripts_ folder.

3 hotkeys need to be made - PRESS, RELEASE, and Toggle.

The preferred hotkey for PRESS and RELEASE is Space. 
For the toggle, use shift-space.


```python
#PRESS
import playbackTool
playbackTool.press()
```

```python
#RELEASE
playbackTool.release()
```
```python
#Toggle
import playbackTool
playbackTool.toggle()
```


## Current limitation:
- PlaybackTool flashes in&out of the scrub context when quick-tapping.
