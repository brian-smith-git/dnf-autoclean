#!/usr/bin/env python3
"""
dnf-autoclean-gui.py

A GTK3 PyGObject GUI frontend for dnf-autoclean.py

Features:
- Slider to choose how many kernels to keep (1..10)
- Toggle for Dry Run (checkbox)
- Schedule selector (informational — edits /etc/dnf-autoclean.conf if user saves)
- Run Now (Dry Run) and Run Now (Execute) buttons
- Shows command output in a scrollable text view
- Uses pkexec to elevate when running destructive actions (if available)
- Loads/saves simple config at ~/.config/dnf-autoclean.conf

Dependencies:
- Python 3
- PyGObject (python3-gi and gir1.2-gtk-3.0)

Save this file in your repo as `dnf-autoclean-gui.py` and run with:
  python3 dnf-autoclean-gui.py

"""

import gi
import os
import shlex
import subprocess
import configparser
from gi.repository import Gtk, Gdk, GLib

APP_NAME = "DNF Auto Cleaner"
CONFIG_PATH = os.path.expanduser("~/.config/dnf-autoclean.conf")
SYSTEM_SCRIPT = "/opt/dnf-autoclean/dnf-autoclean.py"

DEFAULTS = {
    'keep': '5',
    'dry_run': 'true',
    'schedule': 'weekly',
}

class DnfAutoCleanGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title=APP_NAME)
        self.set_default_size(640, 480)
        self.set_border_width(12)

        self.cfg = configparser.ConfigParser()
        self.load_local_config()

        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(vbox)

        # Row: Keep slider and label
        keep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vbox.pack_start(keep_box, False, False, 0)

        keep_label = Gtk.Label(label="Kernels to keep:")
        keep_box.pack_start(keep_label, False, False, 0)

        self.keep_adjustment = Gtk.Adjustment(int(self.cfg['dnf-autoclean'].get('keep', DEFAULTS['keep'])), 1, 10, 1, 10, 0)
        self.keep_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.keep_adjustment)
        self.keep_scale.set_draw_value(True)
        self.keep_scale.set_value_pos(Gtk.PositionType.RIGHT)
        keep_box.pack_start(self.keep_scale, True, True, 0)

        # Row: Dry run checkbox and schedule combo
        opts_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vbox.pack_start(opts_box, False, False, 0)

        self.dry_check = Gtk.CheckButton(label="Dry run (no removal)")
        self.dry_check.set_active(self.cfg['dnf-autoclean'].get('dry_run', DEFAULTS['dry_run']) == 'true')
        opts_box.pack_start(self.dry_check, False, False, 0)

        schedule_label = Gtk.Label(label="Schedule:")
        opts_box.pack_start(schedule_label, False, False, 0)

        self.schedule_combo = Gtk.ComboBoxText()
        for s in ["daily", "weekly", "monthly"]:
            self.schedule_combo.append_text(s)
        self.schedule_combo.set_active(1 if self.cfg['dnf-autoclean'].get('schedule', DEFAULTS['schedule']) == 'weekly' else 0)
        opts_box.pack_start(self.schedule_combo, False, False, 0)

        # Buttons: Run (dry-run) and Run (do it)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vbox.pack_start(btn_box, False, False, 0)

        self.btn_dry = Gtk.Button(label="Run (Dry Run)")
        self.btn_dry.connect("clicked", self.on_run_clicked, True)
        btn_box.pack_start(self.btn_dry, False, False, 0)

        self.btn_run = Gtk.Button(label="Run (Execute)")
        self.btn_run.connect("clicked", self.on_run_clicked, False)
        btn_box.pack_start(self.btn_run, False, False, 0)

        self.btn_save = Gtk.Button(label="Save Config")
        self.btn_save.connect("clicked", self.on_save_config)
        btn_box.pack_start(self.btn_save, False, False, 0)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep, False, True, 6)

        # Status / Output view
        self.output_buffer = Gtk.TextBuffer()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)

        self.output_view = Gtk.TextView(buffer=self.output_buffer)
        self.output_view.set_editable(False)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled.add(self.output_view)

        # Footer: help & version
        footer = Gtk.Label(label="Note: any destructive run requires admin privileges; pkexec will be used to elevate.")
        vbox.pack_start(footer, False, False, 0)

        self.show_all()

    def load_local_config(self):
        # Ensure section exists
        if os.path.exists(CONFIG_PATH):
            try:
                self.cfg.read(CONFIG_PATH)
            except Exception:
                self.cfg['dnf-autoclean'] = DEFAULTS
        else:
            self.cfg['dnf-autoclean'] = DEFAULTS

    def on_save_config(self, widget):
        self.cfg['dnf-autoclean']['keep'] = str(int(self.keep_scale.get_value()))
        self.cfg['dnf-autoclean']['dry_run'] = 'true' if self.dry_check.get_active() else 'false'
        self.cfg['dnf-autoclean']['schedule'] = self.schedule_combo.get_active_text()
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            self.cfg.write(f)
        self.append_output(f"Saved config to {CONFIG_PATH}\n")

    def append_output(self, text):
        end_iter = self.output_buffer.get_end_iter()
        self.output_buffer.insert(end_iter, text)

    def run_command_capture(self, cmd, use_pkexec=False):
        """Run a command and stream output to the text buffer. If use_pkexec, prefix command with pkexec."""
        if use_pkexec:
            # Wrap in sh -c so that complex args are handled
            cmd = ["pkexec", "sh", "-c", cmd]
        else:
            cmd = ["sh", "-c", cmd]

        self.append_output(f"$ {cmd if not use_pkexec else 'pkexec ...'}\n")

        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except FileNotFoundError as e:
            self.append_output(f"Failed to run command: {e}\n")
            return

        # Read lines as they come and append to buffer
        for line in iter(p.stdout.readline, ""):
            GLib.idle_add(self.append_output, line)
        p.stdout.close()
        p.wait()
        GLib.idle_add(self.append_output, f"Command exited: {p.returncode}\n")

    def on_run_clicked(self, widget, dry_force):
        keep = int(self.keep_scale.get_value())
        dry = self.dry_check.get_active()
        is_dry_run = dry_force or dry

        # Build command
        cmd = f"{shlex.quote(SYSTEM_SCRIPT)} --keep {keep}"
        if is_dry_run:
            cmd += " --dry-run"

        # If executing (not dry), we must elevate
        if not is_dry_run:
            # Ask for confirmation
            dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.OK_CANCEL, text="Confirm destructive action")
            dialog.format_secondary_text("This will remove packages from the system. Continue?")
            resp = dialog.run()
            dialog.destroy()
            if resp != Gtk.ResponseType.OK:
                self.append_output("User canceled the destructive run.\n")
                return

            # Use pkexec if available
            if shutil_which("pkexec"):
                self.append_output("Using pkexec to elevate...\n")
                self.run_command_capture(cmd, use_pkexec=True)
            else:
                # If no pkexec, warn and run (may fail)
                self.append_output("Warning: pkexec not available — attempting to run command directly (may fail).\n")
                self.run_command_capture(cmd, use_pkexec=False)
        else:
            # dry-run can run unprivileged
            self.append_output("Starting dry-run...\n")
            self.run_command_capture(cmd, use_pkexec=False)


def shutil_which(name):
    """Simple which replacement to avoid importing shutil into the global scope earlier."""
    for path in os.environ.get("PATH", "").split(os.pathsep):
        f = os.path.join(path, name)
        if os.path.isfile(f) and os.access(f, os.X_OK):
            return f
    return None


def main():
    # Check system script exists
    if not os.path.exists(SYSTEM_SCRIPT):
        dialog = Gtk.MessageDialog(flags=0, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text="DNF AutoClean not installed")
        dialog.format_secondary_text(f"Expected system script at {SYSTEM_SCRIPT}.\nInstall the core tool first or adjust the path in this GUI.")
        dialog.run()
        dialog.destroy()

    win = DnfAutoCleanGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
