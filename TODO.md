## TO DO:
- [] Languages support
- [] Rewrite the UI classes so they behave in the way I want them and look the way i want them
- [] Investigate occasional delay

## DONE:
- [x] Watch out for the paste window getting left behind which means we are stuck in the _hold function loop between funcPress and funcRelease
    + **UPDATE**: Seems like the issue is caused when pressing other buttons together with the hotkey combination. Essentially, if I press Ctrl + A + V I get a hotkey trigger. When I release A, though, I get another hotkey trigger even though Ctrl + V is still pressed.
- [x] Config file. Store preferences
- [x] Move the __init__.py of the ***vsClipboard*** package to an app.py file- - [x] Make sure database connections are managed properly, which means do some research on it. Things to look out for
    + do i need to create a new connection on read and write or can I just initialize once and carry on using it during the lifetime of the application
