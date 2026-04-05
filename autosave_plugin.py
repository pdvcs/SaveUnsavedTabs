import os
import time
import traceback
import sublime
import sublime_plugin


AUTOSAVE_DIR = os.path.expanduser("~/.local/sublimetext/autosave-plugin")


def log(message):
    print("[autosave_plugin] {}".format(message))


def make_autosave_dir():
    os.makedirs(AUTOSAVE_DIR, exist_ok=True)
    log("Using autosave dir: {}".format(AUTOSAVE_DIR))


def next_autosave_path(timestamp_cache):
    base = time.strftime("%Y%m%d-%H%M%S")
    count = timestamp_cache.get(base, 0) + 1
    timestamp_cache[base] = count

    if count == 1:
        filename = "{}-autosave.txt".format(base)
    else:
        filename = "{}-autosave-{:04d}.txt".format(base, count)

    return os.path.join(AUTOSAVE_DIR, filename)


def view_label(view):
    file_name = view.file_name()
    if file_name:
        return file_name

    name = view.name()
    if name:
        return "<unnamed: {}>".format(name)

    return "<unnamed buffer>"


def save_unsaved_views(window):
    make_autosave_dir()

    views = [v for v in window.views() if v and v.window() == window]

    timestamp_cache = {}
    saved_views = []
    skipped_views = []
    failed_views = []

    log("Found {} views in current window".format(len(views)))

    for view in views:
        try:
            if view.is_loading():
                skipped_views.append((view, "still loading"))
                log("Skipping {}: still loading".format(view_label(view)))
                continue

            if view.settings().get("is_widget"):
                skipped_views.append((view, "widget"))
                log("Skipping {}: widget".format(view_label(view)))
                continue

            if view.element() is not None:
                skipped_views.append((view, "ui element"))
                log("Skipping {}: ui element".format(view_label(view)))
                continue

            if view.is_scratch():
                skipped_views.append((view, "scratch view"))
                log("Skipping {}: scratch view".format(view_label(view)))
                continue

            if not view.is_dirty():
                log("No action required for {}".format(view_label(view)))
                continue

            current_name = view.file_name()

            if current_name:
                log("Saving existing file: {}".format(current_name))
                window.focus_view(view)
                view.run_command("save")

                if view.is_dirty():
                    failed_views.append((view, "save command completed but buffer is still dirty"))
                    log("FAILED to save {}".format(current_name))
                else:
                    saved_views.append(view)
                    log("Saved {}".format(current_name))

                continue

            autosave_path = next_autosave_path(timestamp_cache)
            log("Autosaving unnamed buffer to {}".format(autosave_path))

            window.focus_view(view)
            view.retarget(autosave_path)
            view.run_command("save")

            if view.is_dirty():
                failed_views.append((view, "autosave command completed but buffer is still dirty"))
                log("FAILED to autosave unnamed buffer to {}".format(autosave_path))
            else:
                saved_views.append(view)
                log("Autosaved unnamed buffer to {}".format(autosave_path))

        except Exception as exc:
            failed_views.append((view, str(exc)))
            log("Exception while handling {}: {}".format(view_label(view), exc))
            log(traceback.format_exc())

    summary = {
        "saved_views": saved_views,
        "skipped_views": skipped_views,
        "failed_views": failed_views,
        "saved_count": len(saved_views),
        "skipped_count": len(skipped_views),
        "failed_count": len(failed_views),
    }

    log(
        "Summary: saved={}, skipped={}, failed={}".format(
            summary["saved_count"],
            summary["skipped_count"],
            summary["failed_count"],
        )
    )

    return summary


def close_views(window, views):
    for view in list(views):
        try:
            if view and view.window() == window:
                log("Closing {}".format(view_label(view)))
                window.focus_view(view)
                window.run_command("close")
        except Exception as exc:
            log("Exception while closing {}: {}".format(view_label(view), exc))
            log(traceback.format_exc())


def close_all_tabs(window):
    for view in list(window.views()):
        try:
            if view and view.window() == window:
                log("Closing {}".format(view_label(view)))
                window.focus_view(view)
                window.run_command("close")
        except Exception as exc:
            log("Exception while closing {}: {}".format(view_label(view), exc))
            log(traceback.format_exc())


def show_summary(window, action_label, summary):
    message = "{}: saved {}, skipped {}, failed {}".format(
        action_label,
        summary["saved_count"],
        summary["skipped_count"],
        summary["failed_count"],
    )

    if summary["failed_count"]:
        message += " — check console"

    window.status_message(message)
    log(message)


class SaveUnsavedAndCloseCommand(sublime_plugin.WindowCommand):
    def run(self):
        summary = save_unsaved_views(self.window)

        def finish():
            close_all_tabs(self.window)
            show_summary(self.window, "Save unsaved + close all tabs", summary)

        sublime.set_timeout(finish, 300)


class SaveUnsavedAndCloseSavedTabsCommand(sublime_plugin.WindowCommand):
    def run(self):
        summary = save_unsaved_views(self.window)

        def finish():
            close_views(self.window, summary["saved_views"])
            show_summary(self.window, "Save unsaved + close saved tabs", summary)

        sublime.set_timeout(finish, 300)
