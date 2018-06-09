## vsClipboard
vsClipboard is an attempt at creating a non-intrusive clipboard tool that re-uses all the well known hotkeys responsible for cutting, copying and pasting - *Ctl + X*, *Ctrl + C* and *Ctrl + V*.

It is available for **Windows only**, not because I am a Microsoft fan (*trust me, I'm not*), but because, unfortunately, that is the OS I am currently stuck with and I believe other OSs probably have much better available tools.

<img src="file:///C:/users/vasko/documents/sharex/screenshots/2018-05/test_2.gif">

### Why?
I thought most available clipboard tools were a bit clunky and not well integrated, meaning you would usually use other hotkeys than the classic ones. 

Additionally, they seem to have expanded into much bigger tools than just a simple clipboard, so I thought I would try writing something small sitting in the background myself.

### Running instructions
The only dependency that is not part of the standard Python install on Windows is PySide (*I've been using PySide 1.2.4*), which can be installed following the instructions [here](https://pypi.org/project/PySide/).

*EDIT: It has come to my attention that some people don't have the `pywin` library available on a fresh install, so you might need to get that as well - [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32)*

After that, all you need to do to run the application is execute the `run.py` file, and that should show the config window, which can be minimized to let the app run in the background.

```
python run.py
```

### Config
The main window contains all the preferences the tool has. They are also going to be stored in a `config.json` file after the first execution of the tool, so they can be modified through a text editor as well.

The following options are available

- `history_length` - how many entries should be available for pasting
- `hold_before_showing` - the amount of time (*in seconds*) before the window is shown when pressing *Ctrl + V*. If the hotkey is released before that time, normal pasting functionality is performed. The default is `0.15`
- `poll_clipboard_interval` - how often (*in seconds*) to poll the clipboard for changes

### Building an executable
For freezing to an executable I have been using [cxfreeze](https://anthony-tuininga.github.io/cx_Freeze/), as it's [recommended by Qt](https://wiki.qt.io/Packaging_PySide_applications_on_Windows).

```
cxfreeze run.py --target-dir dist --base-name Win32GUI --include-modules atexit,PySide.QtNetwork --target-name vsClipboard.exe && ^
cd dist && ^
mkdir vsClipboard && ^
cd vsClipboard && ^
mkdir ui && ^
cd .. && ^
cd .. && ^
cp vsClipboard/ui/styles.css dist/vsClipboard/ui/ && ^
cp icon.png dist/
```

*Please forgive the horrible batch scripting skills.*

This will freeze the python code to an `.exe` and a bunch of libraries, and once that is done, it will copy the needed stylesheets and icons to the `dist` folder, leaving you with a portable version of the app.

### Known limitations
Pasting is slightly slower than usual, because the tool performs the pasting function on release of the *Ctrl + V* hotkey instead of doing it on press as usual.

The reason for this is that the tool waits for the specified `hold_before_showing` amount of time before being shown, in order to retain normal pasting functionality if a clipboard history is not required.

Lowering that setting results in a snappier performance, but also the tool gets triggered much quicker, so pasting without it getting shown might become trickier.

That being said, in my experience of working with the tool, the difference has been negligible.