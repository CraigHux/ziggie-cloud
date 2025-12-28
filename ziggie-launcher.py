#!/usr/bin/env python3
"""
Ziggie Control Center - Launcher
A GUI application to choose between VS Code or Cursor and open the Ziggie workspace.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import shutil
from pathlib import Path


class ZiggieLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Ziggie Control Center - Launcher")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Set window icon (if available)
        self.set_window_icon()

        # Configure style
        self.configure_style()

        # Session preference
        self.session_var = tk.StringVar(value="new")

        # Create UI
        self.create_ui()

    def set_window_icon(self):
        """Set a custom window icon if available."""
        try:
            # Try to find an icon in common locations
            icon_paths = [
                r"C:\Ziggie\icon.ico",
                r"C:\Ziggie\ziggie.ico",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
            ]

            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    return
        except Exception:
            pass  # Use default icon if custom icon not found

    def configure_style(self):
        """Configure the visual style of the application."""
        # Color scheme: Professional with tech/cat theme
        self.bg_color = "#1a1a1a"  # Dark background
        self.fg_color = "#e8e8e8"  # Light text
        self.accent_color = "#4a9eff"  # Tech blue
        self.success_color = "#4caf50"  # Green
        self.warning_color = "#ff9800"  # Orange

        self.root.configure(bg=self.bg_color)

        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')

        # Button styling
        style.configure('Accent.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       relief='flat')

        style.map('Accent.TButton',
                 foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
                 background=[('pressed', '#0d5aa7'), ('active', '#1a7fd4')])

    def create_ui(self):
        """Create the user interface."""
        # Header frame
        header_frame = tk.Frame(self.root, bg=self.accent_color, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text="Ziggie Control Center",
            font=('Segoe UI', 18, 'bold'),
            fg='white',
            bg=self.accent_color
        )
        title_label.pack(pady=(15, 5))

        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Launcher",
            font=('Segoe UI', 10),
            fg='#b3d9ff',
            bg=self.accent_color
        )
        subtitle_label.pack(pady=(0, 15))

        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Welcome message
        welcome_label = tk.Label(
            content_frame,
            text="Welcome to Ziggie!\n\nChoose your preferred code editor to open the workspace.",
            font=('Segoe UI', 11),
            fg=self.fg_color,
            bg=self.bg_color,
            justify=tk.CENTER,
            wraplength=400
        )
        welcome_label.pack(pady=(0, 25))

        # Editor selection buttons frame
        buttons_frame = tk.Frame(content_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=(0, 25))

        # VS Code button
        vscode_btn = tk.Button(
            buttons_frame,
            text="🔵 VS Code",
            command=lambda: self.launch_editor("code"),
            font=('Segoe UI', 12, 'bold'),
            bg=self.accent_color,
            fg='white',
            activebackground='#0d5aa7',
            activeforeground='white',
            padx=20,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            width=20
        )
        vscode_btn.pack(pady=8)

        # Cursor button
        cursor_btn = tk.Button(
            buttons_frame,
            text="⚡ Cursor",
            command=lambda: self.launch_editor("cursor"),
            font=('Segoe UI', 12, 'bold'),
            bg=self.success_color,
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            padx=20,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            width=20
        )
        cursor_btn.pack(pady=8)

        # Session preference frame
        session_frame = tk.LabelFrame(
            content_frame,
            text="Session Type",
            font=('Segoe UI', 10, 'bold'),
            fg=self.fg_color,
            bg=self.bg_color,
            relief=tk.FLAT,
            padx=15,
            pady=12
        )
        session_frame.pack(fill=tk.X, pady=(0, 20))

        # Radio buttons for session preference
        radio_frame = tk.Frame(session_frame, bg=self.bg_color)
        radio_frame.pack(fill=tk.X)

        new_session_radio = tk.Radiobutton(
            radio_frame,
            text="New Session",
            variable=self.session_var,
            value="new",
            font=('Segoe UI', 10),
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            cursor="hand2"
        )
        new_session_radio.pack(anchor=tk.W, pady=3)

        continue_radio = tk.Radiobutton(
            radio_frame,
            text="Continue Previous Session",
            variable=self.session_var,
            value="continue",
            font=('Segoe UI', 10),
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            cursor="hand2"
        )
        continue_radio.pack(anchor=tk.W, pady=3)

        # Footer info
        info_label = tk.Label(
            content_frame,
            text="Workspace: C:\\Ziggie",
            font=('Segoe UI', 9),
            fg='#888888',
            bg=self.bg_color
        )
        info_label.pack(side=tk.BOTTOM, anchor=tk.W)

    def find_editor_executable(self, editor):
        """
        Find the editor executable path with robust checking.

        Checks in order:
        1. PATH using shutil.which()
        2. Common Windows installation locations

        Args:
            editor: Either "code" (VS Code) or "cursor"

        Returns:
            Full path to the editor executable if found, None otherwise
        """
        # First, try to find in PATH
        if editor == "code":
            path_result = shutil.which("code")
            if path_result:
                return path_result

            # Check common VS Code installation locations
            vscode_paths = [
                r"C:\Users\minin\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            ]
            for path in vscode_paths:
                if os.path.exists(path):
                    return path

        elif editor == "cursor":
            path_result = shutil.which("cursor")
            if path_result:
                return path_result

            # Check common Cursor installation locations
            cursor_paths = [
                r"C:\Program Files\cursor\Cursor.exe",
                r"C:\Program Files (x86)\cursor\Cursor.exe",
                r"C:\Users\minin\AppData\Local\Programs\cursor\Cursor.exe",
            ]
            for path in cursor_paths:
                if os.path.exists(path):
                    return path

        return None

    def is_editor_installed(self, editor):
        """Check if the specified editor is installed and accessible."""
        editor_path = self.find_editor_executable(editor)

        if not editor_path:
            return False

        try:
            result = subprocess.run(
                [editor_path, "--version"],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def launch_editor(self, editor):
        """Launch the chosen editor with the Ziggie workspace."""
        # Find the editor executable with robust checking
        editor_path = self.find_editor_executable(editor)

        if not editor_path:
            editor_name = "VS Code" if editor == "code" else "Cursor"
            messagebox.showerror(
                "Editor Not Found",
                f"{editor_name} is not installed or not accessible.\n\n"
                f"Please install {editor_name}.\n\n"
                f"Installation links:\n"
                f"- VS Code: https://code.visualstudio.com\n"
                f"- Cursor: https://cursor.sh"
            )
            return

        workspace_path = r"C:\Ziggie"

        # Get session preference
        session_type = self.session_var.get()

        try:
            # Build command with full path to editor executable
            if session_type == "continue":
                # Try to reuse the window if available
                cmd = [editor_path, workspace_path, "--reuse-window"]
            else:
                # Open in new window
                cmd = [editor_path, workspace_path]

            # Launch the editor
            subprocess.Popen(
                cmd,
                cwd=workspace_path,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )

            # Show success message
            editor_name = "VS Code" if editor == "code" else "Cursor"
            session_msg = "continuing previous session" if session_type == "continue" else "new session"
            messagebox.showinfo(
                "Launching Editor",
                f"Opening {editor_name} with Ziggie workspace ({session_msg})..."
            )

            # Close launcher after successful launch
            self.root.after(1000, self.root.quit)

        except Exception as e:
            messagebox.showerror(
                "Launch Failed",
                f"Failed to launch editor:\n\n{str(e)}"
            )

    def run(self):
        """Start the launcher application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    root = tk.Tk()
    launcher = ZiggieLauncher(root)
    launcher.run()


if __name__ == "__main__":
    main()
