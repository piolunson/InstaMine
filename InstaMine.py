
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import hashlib
import shutil
import ctypes
import sys

# ── Sprawdź czy admin ──────────────────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return os.getuid() == 0  # Linux/macOS fallback

# ── Kolory i styl ──────────────────────────────────────────────────────────────
BG        = "#0d0f14"
SURFACE   = "#161922"
BORDER    = "#1e2230"
ACCENT    = "#00d4aa"
ACCENT2   = "#0099ff"
TEXT      = "#e8eaf0"
SUBTEXT   = "#6b7280"
BTN_START = "#00d4aa"
BTN_HOVER = "#00b894"
DANGER    = "#ff4757"

FONT_TITLE  = ("Courier New", 13, "bold")
FONT_LABEL  = ("Courier New", 9)
FONT_BTN    = ("Courier New", 10, "bold")
FONT_SMALL  = ("Courier New", 8)
FONT_PATH   = ("Courier New", 8)

# ── Główna aplikacja ────────────────────────────────────────────────────────────
class InstaMine(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InstaMine")
        self.geometry("300x480")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.selected_path = tk.StringVar(value="")
        self.mode = tk.StringVar(value="replace_zero")
        self.admin = is_admin()

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w, h = 300, 480
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", pady=(16, 4), padx=16)

        tk.Label(hdr, text="\u26cf INSTA", font=("Courier New", 18, "bold"),
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(hdr, text="MINE", font=("Courier New", 18, "bold"),
                 fg=ACCENT2, bg=BG).pack(side="left")

        admin_txt  = "● ADMIN"  if self.admin else "○ USER"
        admin_col  = ACCENT     if self.admin else DANGER
        tk.Label(hdr, text=admin_txt, font=FONT_SMALL,
                 fg=admin_col, bg=BG).pack(side="right", pady=4)

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # ── SELECT FILE / FOLDER ──────────────────────────────────────────────
        sel_frame = tk.Frame(self, bg=SURFACE, bd=0, relief="flat")
        sel_frame.pack(fill="x", padx=12, pady=(12, 6))

        def _on_enter(e): sel_btn.config(bg="#1a2e40")
        def _on_leave(e): sel_btn.config(bg=SURFACE)

        sel_btn = tk.Button(
            sel_frame, text="[>]  SELECT FILE / FOLDER",
            font=FONT_BTN, fg=ACCENT2, bg=SURFACE,
            activebackground="#1a2e40", activeforeground=ACCENT2,
            bd=1, relief="solid", highlightbackground=ACCENT2,
            highlightthickness=1, cursor="hand2",
            command=self._select_path
        )
        sel_btn.pack(fill="x", ipady=10, padx=1, pady=1)
        sel_btn.bind("<Enter>", _on_enter)
        sel_btn.bind("<Leave>", _on_leave)

        # Path label
        path_frame = tk.Frame(self, bg=BORDER, bd=0)
        path_frame.pack(fill="x", padx=12, pady=(0, 10))
        self.path_lbl = tk.Label(
            path_frame, textvariable=self.selected_path,
            font=FONT_PATH, fg=SUBTEXT, bg=BORDER,
            anchor="w", wraplength=270, justify="left"
        )
        self.path_lbl.pack(fill="x", padx=6, pady=4)

        # ── CHOOSE MODE label ─────────────────────────────────────────────────
        tk.Label(self, text="CHOOSE MODE", font=("Courier New", 9, "bold"),
                 fg=SUBTEXT, bg=BG).pack(anchor="w", padx=14, pady=(2, 5))

        # ── 2×2 MODE GRID ─────────────────────────────────────────────────────
        grid_outer = tk.Frame(self, bg=BG)
        grid_outer.pack(fill="x", padx=12, pady=(0, 12))

        modes = [
            ("replace_zero", "[0] Replace\nwith 0"),
            ("move_trash",   "[X] Move to\nTrash"),
            ("hash_replace", "[#] Hash\nReplace"),
            ("replace_ns",   "[!] Replace\nwith NS"),
        ]

        self.mode_btns = {}
        for i, (key, label) in enumerate(modes):
            r, c = divmod(i, 2)
            btn = tk.Button(
                grid_outer, text=label,
                font=FONT_LABEL, fg=TEXT, bg=SURFACE,
                activebackground=ACCENT, activeforeground=BG,
                bd=1, relief="solid", highlightbackground=BORDER,
                highlightthickness=1, cursor="hand2", wraplength=110,
                command=lambda k=key: self._select_mode(k)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, ipadx=6, ipady=10, sticky="nsew")
            self.mode_btns[key] = btn
            grid_outer.columnconfigure(c, weight=1)

        self._select_mode("replace_zero")  # default highlight

        # ── START ─────────────────────────────────────────────────────────────
        start_frame = tk.Frame(self, bg=BG)
        start_frame.pack(fill="x", padx=12, pady=(4, 0))

        def _st_enter(e): start_btn.config(bg=BTN_HOVER)
        def _st_leave(e): start_btn.config(bg=BTN_START)

        start_btn = tk.Button(
            start_frame, text=">> START",
            font=("Courier New", 13, "bold"), fg=BG, bg=BTN_START,
            activebackground=BTN_HOVER, activeforeground=BG,
            bd=0, relief="flat", cursor="hand2",
            command=self._start
        )
        start_btn.pack(fill="x", ipady=14)
        start_btn.bind("<Enter>", _st_enter)
        start_btn.bind("<Leave>", _st_leave)

        # Status bar
        self.status = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self.status, font=FONT_SMALL,
                 fg=SUBTEXT, bg=BG).pack(pady=(8, 4))

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _select_mode(self, key):
        self.mode.set(key)
        for k, btn in self.mode_btns.items():
            if k == key:
                btn.config(bg=ACCENT, fg=BG,
                           highlightbackground=ACCENT, relief="flat")
            else:
                btn.config(bg=SURFACE, fg=TEXT,
                           highlightbackground=BORDER, relief="solid")

    def _select_path(self):
        choice = filedialog.askopenfilename(title="Select file") or \
                 filedialog.askdirectory(title="Or select folder")
        if choice:
            self.selected_path.set(choice)
            self.status.set("Path selected.")

    # ── Core operations ────────────────────────────────────────────────────────
    def _get_files(self, path):
        if os.path.isfile(path):
            return [path]
        files = []
        for root, _, fnames in os.walk(path):
            for f in fnames:
                files.append(os.path.join(root, f))
        return files

    def _replace_with_zeros(self, files):
        for fp in files:
            try:
                size = os.path.getsize(fp)
                with open(fp, "wb") as f:
                    f.write(b"\x00" * size)
            except Exception as e:
                self.status.set(f"Err: {e}")

    def _move_to_trash(self, path):
        trash = os.path.join(os.path.expanduser("~"), ".Trash") \
                if sys.platform != "win32" else \
                os.path.join(os.environ.get("USERPROFILE", "C:/"), "Desktop/Trash_InstaMine")
        os.makedirs(trash, exist_ok=True)
        try:
            shutil.move(path, trash)
        except Exception as e:
            self.status.set(f"Err: {e}")

    def _hash_replace(self, files):
        for fp in files:
            try:
                with open(fp, "rb") as f:
                    data = f.read()
                h = hashlib.sha256(data).hexdigest().encode()
                with open(fp, "wb") as f:
                    f.write(h)
            except Exception as e:
                self.status.set(f"Err: {e}")

    def _replace_with_ns(self, files):
        for fp in files:
            try:
                size = os.path.getsize(fp)
                if size == 0:
                    continue
                pattern = (b"NS" * (size // 2 + 1))[:size]
                with open(fp, "wb") as f:
                    f.write(pattern)
            except Exception as e:
                self.status.set(f"Err: {e}")

    def _start(self):
        path = self.selected_path.get()
        if not path:
            messagebox.showwarning("InstaMine", "Wybierz plik lub folder!")
            return
        if not os.path.exists(path):
            messagebox.showerror("InstaMine", "Ścieżka nie istnieje.")
            return

        mode = self.mode.get()
        files = self._get_files(path)
        count = len(files)

        confirm = messagebox.askyesno(
            "InstaMine",
            f"Tryb: {mode}\n{count} plik(ów)\n\nCzy na pewno chcesz kontynuować?"
        )
        if not confirm:
            return

        self.status.set("Pracuje...")
        self.update()

        if mode == "replace_zero":
            self._replace_with_zeros(files)
        elif mode == "move_trash":
            self._move_to_trash(path)
        elif mode == "hash_replace":
            self._hash_replace(files)
        elif mode == "replace_ns":
            self._replace_with_ns(files)

        self.status.set(f"[OK] Gotowe! ({count} plik(ow))")
        messagebox.showinfo("InstaMine", f"Operacja zakończona!\n{count} plik(ów) przetworzono.")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = InstaMine()
    app.mainloop()
