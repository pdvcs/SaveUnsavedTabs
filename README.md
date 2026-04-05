# A Sublime Text Plugin to Save Unsaved Work

A small Sublime Text 4 plugin for cleaning up a window without losing work.

It adds two Command Palette actions:

- save every dirty tab in the current window, including unnamed buffers
- optionally close either all tabs or only the tabs that were successfully saved

Unnamed buffers are written to timestamped text files so you do not have to name them manually before closing the window.

## What It Does

The plugin scans every view in the current window and:

- saves dirty files that already have a filename
- autosaves dirty unnamed buffers into a local autosave directory
- skips scratch views, widgets, loading views, and UI elements
- reports a summary in the status bar and logs details to the Sublime console

Autosaved unnamed buffers use filenames like:

- `20260405-013603-autosave.txt`
- `20260405-013603-autosave-0002.txt`
- `20260405-013603-autosave-0003.txt`

## Commands

### Save Unsaved And Close All Tabs

- Saves all dirty named files in the current window.
- Autosaves all dirty unnamed buffers.
- Closes all tabs in the current window afterward.

Use this when you want to clear the whole window after preserving everything that can be saved.

### Save Unsaved And Close Saved Tabs

- Saves all dirty named files in the current window.
- Autosaves all dirty unnamed buffers.
- Closes only the tabs that were successfully saved or autosaved.
- Leaves untouched tabs open if they were skipped or failed.

Use this when you want to keep problem tabs visible instead of closing everything.

## Installation

### Manual install

1. Open your Sublime Text `Packages` directory.
2. Create a folder named `st4-autosave-plugin` or clone this repository there.
3. Put these files in that folder:
   - `autosave_plugin.py`
   - `Default.sublime-commands`
4. Restart Sublime Text or reload the plugin host.

Typical package locations:

- macOS: `~/Library/Application Support/Sublime Text/Packages/`
- Linux: `~/.config/sublime-text/Packages/`
- Windows: `%APPDATA%\\Sublime Text\\Packages\\`

## How To Use It

1. Open the Command Palette in Sublime Text.
2. Run `Save Unsaved And Close All Tabs` or `Save Unsaved And Close Saved Tabs`.
3. Watch the status bar for the summary.
4. If anything fails, open the Sublime console for details.

## Where Autosaved Files Go

Unnamed buffers are saved into:

`~/.local/sublimetext/autosave-plugin`

The plugin creates that directory automatically if it does not already exist.

## Important Behavior

- The plugin operates on the current window only.
- Only dirty tabs are processed.
- Named files are saved in place.
- Unnamed buffers are retargeted to autosave files and then saved.
- If a save fails and the buffer stays dirty, the failure is reported and the tab is not treated as safely saved.

## Limitations

- There is no settings file yet for changing the autosave directory or filename format.
- Autosaved unnamed buffers are written with a `.txt` extension.
- The autosave path is currently hardcoded in the plugin.

## Troubleshooting

If the command does not behave as expected:

- open the Sublime console to inspect log messages from `autosave_plugin`
- check whether the tab is a scratch view, widget, or still loading
- confirm the autosave directory is writable
- confirm the buffer is actually dirty before running the command

## Development

Quick syntax check:

```bash
python3 -m py_compile autosave_plugin.py
```
