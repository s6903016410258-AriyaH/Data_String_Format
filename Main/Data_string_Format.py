#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEON REGEX TERMINAL
====================
GUI (Tkinter) โปรแกรมประมวลผลข้อความด้วย re module
- โหลด/พิมพ์ข้อความลงในฟอร์ม
- เลือกฟังก์ชันประมวลผล (มากกว่า 10 ฟังก์ชัน) พร้อมปรับพารามิเตอร์ (pattern, flags, replacement, group index)
- แสดงผลลัพธ์ในอีกช่องของฟอร์ม
- ดักจับ Error ด้วย try-except ทุกจุดที่เสี่ยง
- ธีม: ไซเบอร์พังก์ / ไฮเทคอนาคต (จอมืด + นีออน)
"""

import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime

# ----------------------------------------------------------------------------
# THEME - CYBER / NEON
# ----------------------------------------------------------------------------
BG_MAIN     = "#060a12"
BG_PANEL    = "#0c1424"
BG_FIELD    = "#0a1220"
FG_TEXT     = "#c9f7ff"
NEON_CYAN   = "#00fff2"
NEON_MAG    = "#ff2bd6"
NEON_GREEN  = "#39ff88"
NEON_YELLOW = "#f6ff2b"
NEON_RED    = "#ff3b5c"
BORDER_CLR  = "#123043"
FONT_MONO   = ("Consolas", 11)
FONT_MONO_B = ("Consolas", 11, "bold")
FONT_TITLE  = ("Consolas", 20, "bold")
FONT_SMALL  = ("Consolas", 9)


# ----------------------------------------------------------------------------
# REGEX FUNCTION LIBRARY  (>= 10 functions, all parameterizable)
# ----------------------------------------------------------------------------
def build_flags(ignorecase, multiline, dotall):
    """รวม flag ของ re จาก checkbox ที่ผู้ใช้เลือก"""
    flags = 0
    if ignorecase:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    if dotall:
        flags |= re.DOTALL
    return flags


def f_find_emails(text, params):
    pattern = params.get("pattern") or r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบอีเมล --"]


def f_find_urls(text, params):
    pattern = params.get("pattern") or r"https?://[^\s\"'<>]+"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบ URL --"]


def f_find_phone_numbers(text, params):
    pattern = params.get("pattern") or r"(?:\+66|0)[\s-]?\d{1,2}[\s-]?\d{3}[\s-]?\d{4}"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบเบอร์โทร --"]


def f_find_numbers(text, params):
    pattern = params.get("pattern") or r"-?\d+(?:\.\d+)?"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบตัวเลข --"]


def f_find_dates(text, params):
    pattern = params.get("pattern") or r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบวันที่ --"]


def f_find_hashtags_mentions(text, params):
    pattern = params.get("pattern") or r"[#@]\w+"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบ hashtag/mention --"]


def f_find_ip_addresses(text, params):
    pattern = params.get("pattern") or r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบ IP address --"]


def f_find_words_by_length(text, params):
    n = params.get("extra") or "5"
    n = int(n) if str(n).strip().isdigit() else 5
    pattern = params.get("pattern") or r"\b\w{" + str(n) + r",}\b"
    matches = re.findall(pattern, text, params["flags"])
    return matches or [f"-- ไม่พบคำที่ยาว >= {n} ตัวอักษร --"]


def f_custom_search(text, params):
    pattern = params.get("pattern")
    if not pattern:
        raise ValueError("กรุณาใส่ Pattern สำหรับฟังก์ชัน Custom Search")
    matches = re.findall(pattern, text, params["flags"])
    return matches or ["-- ไม่พบข้อความที่ตรงกับ pattern --"]


def f_custom_replace(text, params):
    pattern = params.get("pattern")
    repl = params.get("replacement", "")
    if not pattern:
        raise ValueError("กรุณาใส่ Pattern สำหรับฟังก์ชัน Replace")
    new_text, n = re.subn(pattern, repl, text, flags=params["flags"])
    return [f"[แทนที่ทั้งหมด {n} ตำแหน่ง]", "", new_text]


def f_custom_split(text, params):
    pattern = params.get("pattern")
    if not pattern:
        raise ValueError("กรุณาใส่ Pattern สำหรับฟังก์ชัน Split")
    parts = re.split(pattern, text, flags=params["flags"])
    return [p for p in parts if p != ""] or ["-- แยกไม่ได้ผลลัพธ์ --"]


def f_count_matches(text, params):
    pattern = params.get("pattern")
    if not pattern:
        raise ValueError("กรุณาใส่ Pattern สำหรับฟังก์ชัน Count")
    matches = re.findall(pattern, text, params["flags"])
    return [f"จำนวนที่พบทั้งหมด: {len(matches)} รายการ"]


def f_extract_groups(text, params):
    pattern = params.get("pattern")
    if not pattern:
        raise ValueError("กรุณาใส่ Pattern ที่มี group เช่น (\\w+)@(\\w+)")
    idx_raw = params.get("extra") or "0"
    idx = int(idx_raw) if str(idx_raw).strip().lstrip("-").isdigit() else 0
    results = []
    for m in re.finditer(pattern, text, params["flags"]):
        try:
            results.append(str(m.group(idx)))
        except (IndexError, error_type_placeholder):  # noqa
            raise ValueError(f"ไม่มี group index {idx} ใน pattern นี้")
    return results or ["-- ไม่พบ match --"]


def f_validate_lines(text, params):
    pattern = params.get("pattern")
    if not pattern:
        raise ValueError("กรุณาใส่ Pattern สำหรับตรวจสอบทั้งบรรทัด (fullmatch)")
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip() == "":
            continue
        ok = re.fullmatch(pattern, line.strip(), params["flags"])
        status = "VALID  ✔" if ok else "INVALID ✘"
        out.append(f"[บรรทัด {i:>3}] {status}  :  {line.strip()}")
    return out or ["-- ไม่มีบรรทัดให้ตรวจสอบ --"]


# fix the placeholder used above (defined after, python allows forward ref at call time)
error_type_placeholder = re.error

FUNCTIONS = {
    "01. ค้นหาอีเมล (Find Emails)": (f_find_emails, "pattern"),
    "02. ค้นหา URL (Find URLs)": (f_find_urls, "pattern"),
    "03. ค้นหาเบอร์โทร (Find Phone Numbers)": (f_find_phone_numbers, "pattern"),
    "04. ค้นหาตัวเลข (Find Numbers)": (f_find_numbers, "pattern"),
    "05. ค้นหาวันที่ (Find Dates)": (f_find_dates, "pattern"),
    "06. ค้นหา #Hashtag / @Mention": (f_find_hashtags_mentions, "pattern"),
    "07. ค้นหา IP Address": (f_find_ip_addresses, "pattern"),
    "08. ค้นหาคำตามความยาว (Word Length)": (f_find_words_by_length, "extra"),
    "09. ค้นหาแบบกำหนดเอง (Custom Search)": (f_custom_search, "pattern"),
    "10. แทนที่ข้อความ (Replace)": (f_custom_replace, "pattern+repl"),
    "11. ตัดข้อความ (Split)": (f_custom_split, "pattern"),
    "12. นับจำนวนที่พบ (Count Matches)": (f_count_matches, "pattern"),
    "13. ดึงค่ากลุ่ม (Extract Group N)": (f_extract_groups, "pattern+extra"),
    "14. ตรวจสอบทั้งบรรทัด (Validate Lines)": (f_validate_lines, "pattern"),
}


# ----------------------------------------------------------------------------
# GUI APPLICATION
# ----------------------------------------------------------------------------
class NeonRegexTerminal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("N.E.X.U.S. // REGEX PROCESSING TERMINAL v2.077")
        self.geometry("1180x760")
        self.configure(bg=BG_MAIN)
        self.minsize(980, 640)

        self._build_style()
        self._build_layout()
        self._on_function_change()
        self._blink_cursor()

    # ---------------------------------------------------------------- style
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TCombobox",
                         fieldbackground=BG_FIELD,
                         background=BG_FIELD,
                         foreground=NEON_CYAN,
                         arrowcolor=NEON_CYAN,
                         bordercolor=BORDER_CLR,
                         lightcolor=BG_FIELD,
                         darkcolor=BG_FIELD,
                         insertcolor=NEON_CYAN)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_FIELD)],
                  foreground=[("readonly", NEON_CYAN)])

        style.configure("Neon.TCheckbutton",
                         background=BG_PANEL,
                         foreground=NEON_GREEN,
                         font=FONT_SMALL)
        style.map("Neon.TCheckbutton",
                  background=[("active", BG_PANEL)],
                  foreground=[("active", NEON_YELLOW)])

    # --------------------------------------------------------------- layout
    def _build_layout(self):
        # ---- Header -----------------------------------------------------
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=18, pady=(14, 6))

        title_lbl = tk.Label(
            header, text="⟦ N.E.X.U.S. ⟧  REGEX PROCESSING TERMINAL",
            bg=BG_MAIN, fg=NEON_CYAN, font=FONT_TITLE
        )
        title_lbl.pack(side="left")

        self.clock_lbl = tk.Label(header, text="", bg=BG_MAIN, fg=NEON_MAG, font=FONT_MONO_B)
        self.clock_lbl.pack(side="right")
        self._update_clock()

        sub_lbl = tk.Label(
            self, text=">> SYSTEM ONLINE // PATTERN MATCHING CORE READY //",
            bg=BG_MAIN, fg=NEON_GREEN, font=FONT_SMALL, anchor="w"
        )
        sub_lbl.pack(fill="x", padx=20)

        divider = tk.Frame(self, bg=NEON_CYAN, height=2)
        divider.pack(fill="x", padx=18, pady=(6, 10))

        # ---- Main body: left(input) | center(controls) | right(output) --
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 10))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.columnconfigure(2, weight=3)
        body.rowconfigure(0, weight=1)

        self._build_input_panel(body)
        self._build_control_panel(body)
        self._build_output_panel(body)

        # ---- Status bar ---------------------------------------------------
        self.status_var = tk.StringVar(value="READY.")
        status_bar = tk.Label(
            self, textvariable=self.status_var, anchor="w",
            bg="#020408", fg=NEON_GREEN, font=FONT_SMALL, padx=10, pady=4
        )
        status_bar.pack(fill="x", side="bottom")

    # ---- Panel: text input -------------------------------------------------
    def _build_input_panel(self, parent):
        frame = tk.LabelFrame(
            parent, text=" 📥 INPUT DATA STREAM ", labelanchor="n",
            bg=BG_PANEL, fg=NEON_CYAN, font=FONT_MONO_B,
            bd=2, relief="groove", highlightbackground=NEON_CYAN
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        btn_row = tk.Frame(frame, bg=BG_PANEL)
        btn_row.pack(fill="x", padx=8, pady=8)

        self._neon_button(btn_row, "📂 LOAD FILE", self.load_file, NEON_CYAN).pack(side="left", padx=(0, 6))
        self._neon_button(btn_row, "🗑 CLEAR", self.clear_input, NEON_RED).pack(side="left", padx=6)
        self._neon_button(btn_row, "✎ SAMPLE", self.load_sample, NEON_YELLOW).pack(side="left", padx=6)

        text_frame = tk.Frame(frame, bg=BORDER_CLR, bd=1)
        text_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.input_text = tk.Text(
            text_frame, wrap="word", bg=BG_FIELD, fg=FG_TEXT,
            insertbackground=NEON_CYAN, font=FONT_MONO, relief="flat",
            padx=8, pady=8, undo=True
        )
        scroll_in = tk.Scrollbar(text_frame, command=self.input_text.yview,
                                  troughcolor=BG_PANEL, bg=BG_FIELD)
        self.input_text.configure(yscrollcommand=scroll_in.set)
        self.input_text.pack(side="left", fill="both", expand=True)
        scroll_in.pack(side="right", fill="y")

    # ---- Panel: controls ----------------------------------------------------
    def _build_control_panel(self, parent):
        frame = tk.LabelFrame(
            parent, text=" ⚙ PATTERN CONTROL MATRIX ", labelanchor="n",
            bg=BG_PANEL, fg=NEON_MAG, font=FONT_MONO_B,
            bd=2, relief="groove", highlightbackground=NEON_MAG
        )
        frame.grid(row=0, column=1, sticky="nsew", padx=8)

        inner = tk.Frame(frame, bg=BG_PANEL)
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(inner, text="เลือกฟังก์ชันประมวลผล:", bg=BG_PANEL, fg=NEON_GREEN,
                 font=FONT_SMALL, anchor="w").pack(fill="x")

        self.func_var = tk.StringVar()
        self.func_combo = ttk.Combobox(
            inner, textvariable=self.func_var, values=list(FUNCTIONS.keys()),
            state="readonly", font=FONT_MONO
        )
        self.func_combo.current(0)
        self.func_combo.pack(fill="x", pady=(2, 12))
        self.func_combo.bind("<<ComboboxSelected>>", self._on_function_change)

        # Pattern entry
        self.pattern_label = tk.Label(inner, text="Regex Pattern:", bg=BG_PANEL,
                                       fg=NEON_GREEN, font=FONT_SMALL, anchor="w")
        self.pattern_label.pack(fill="x")
        self.pattern_entry = tk.Entry(inner, bg=BG_FIELD, fg=NEON_YELLOW,
                                       insertbackground=NEON_YELLOW, font=FONT_MONO,
                                       relief="flat")
        self.pattern_entry.pack(fill="x", ipady=4, pady=(2, 10))

        # Replacement entry (used by Replace)
        self.repl_label = tk.Label(inner, text="Replacement Text:", bg=BG_PANEL,
                                    fg=NEON_GREEN, font=FONT_SMALL, anchor="w")
        self.repl_entry = tk.Entry(inner, bg=BG_FIELD, fg=NEON_YELLOW,
                                    insertbackground=NEON_YELLOW, font=FONT_MONO,
                                    relief="flat")

        # Extra param entry (word length / group index)
        self.extra_label = tk.Label(inner, text="ค่าพารามิเตอร์เพิ่มเติม:", bg=BG_PANEL,
                                     fg=NEON_GREEN, font=FONT_SMALL, anchor="w")
        self.extra_entry = tk.Entry(inner, bg=BG_FIELD, fg=NEON_YELLOW,
                                     insertbackground=NEON_YELLOW, font=FONT_MONO,
                                     relief="flat")

        # Flags
        flag_frame = tk.LabelFrame(inner, text=" RE FLAGS ", bg=BG_PANEL, fg=NEON_CYAN,
                                    font=FONT_SMALL, bd=1, relief="groove")
        flag_frame.pack(fill="x", pady=(6, 14))

        self.var_ignorecase = tk.BooleanVar(value=True)
        self.var_multiline = tk.BooleanVar(value=False)
        self.var_dotall = tk.BooleanVar(value=False)

        ttk.Checkbutton(flag_frame, text="IGNORECASE", variable=self.var_ignorecase,
                         style="Neon.TCheckbutton").pack(anchor="w", padx=8, pady=2)
        ttk.Checkbutton(flag_frame, text="MULTILINE", variable=self.var_multiline,
                         style="Neon.TCheckbutton").pack(anchor="w", padx=8, pady=2)
        ttk.Checkbutton(flag_frame, text="DOTALL", variable=self.var_dotall,
                         style="Neon.TCheckbutton").pack(anchor="w", padx=8, pady=2)

        self._neon_button(inner, "▶ EXECUTE SCAN", self.execute, NEON_GREEN,
                           big=True).pack(fill="x", pady=(6, 4))
        self._neon_button(inner, "✕ CLEAR OUTPUT", self.clear_output, NEON_RED).pack(fill="x")

        hint = tk.Label(
            inner,
            text=("TIP: ฟังก์ชัน 01-08 มี pattern เริ่มต้นให้อยู่แล้ว\n"
                  "แต่สามารถแก้ไข pattern เองได้เพื่อกรองผลลัพธ์ต่างกัน"),
            bg=BG_PANEL, fg="#5f8fa3", font=FONT_SMALL, justify="left", anchor="w"
        )
        hint.pack(fill="x", pady=(14, 0))

    # ---- Panel: output --------------------------------------------------
    def _build_output_panel(self, parent):
        frame = tk.LabelFrame(
            parent, text=" 📤 OUTPUT / SCAN RESULT ", labelanchor="n",
            bg=BG_PANEL, fg=NEON_GREEN, font=FONT_MONO_B,
            bd=2, relief="groove", highlightbackground=NEON_GREEN
        )
        frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        text_frame = tk.Frame(frame, bg=BORDER_CLR, bd=1)
        text_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.output_text = tk.Text(
            text_frame, wrap="word", bg="#020608", fg=NEON_GREEN,
            insertbackground=NEON_GREEN, font=FONT_MONO, relief="flat",
            padx=8, pady=8, state="disabled"
        )
        scroll_out = tk.Scrollbar(text_frame, command=self.output_text.yview,
                                   troughcolor=BG_PANEL, bg=BG_FIELD)
        self.output_text.configure(yscrollcommand=scroll_out.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scroll_out.pack(side="right", fill="y")

    # ---- reusable neon button --------------------------------------------
    def _neon_button(self, parent, text, command, color, big=False):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=BG_FIELD, fg=color, activebackground=color, activeforeground=BG_MAIN,
            font=(FONT_MONO_B if not big else ("Consolas", 12, "bold")),
            relief="ridge", bd=2, cursor="hand2",
            highlightbackground=color, highlightthickness=1,
            padx=10, pady=8 if big else 4
        )
        return btn

    # ------------------------------------------------------------------
    # DYNAMIC FORM BEHAVIOUR
    # ------------------------------------------------------------------
    def _on_function_change(self, event=None):
        _, mode = FUNCTIONS[self.func_var.get()]

        self.repl_label.pack_forget()
        self.repl_entry.pack_forget()
        self.extra_label.pack_forget()
        self.extra_entry.pack_forget()

        self.pattern_entry.delete(0, tk.END)
        self.extra_entry.delete(0, tk.END)
        self.repl_entry.delete(0, tk.END)

        if "repl" in mode:
            self.repl_label.pack(fill="x", after=self.pattern_entry)
            self.repl_entry.pack(fill="x", ipady=4, pady=(2, 10), after=self.repl_label)
        if "extra" in mode:
            self.extra_entry.insert(0, "5" if "08" in self.func_var.get() else "0")
            self.extra_label.pack(fill="x")
            self.extra_entry.pack(fill="x", ipady=4, pady=(2, 10))

        self._set_status(f"เลือกฟังก์ชัน: {self.func_var.get()}", NEON_GREEN)

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def load_file(self):
        try:
            path = filedialog.askopenfilename(
                title="เลือกไฟล์ข้อความ",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path:
                return
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, content)
            self._set_status(f"โหลดไฟล์สำเร็จ: {path}", NEON_CYAN)
        except FileNotFoundError:
            messagebox.showerror("ผิดพลาด", "ไม่พบไฟล์ที่ระบุ")
            self._set_status("ERROR: ไม่พบไฟล์", NEON_RED)
        except PermissionError:
            messagebox.showerror("ผิดพลาด", "ไม่มีสิทธิ์เข้าถึงไฟล์นี้")
            self._set_status("ERROR: ไม่มีสิทธิ์เข้าถึงไฟล์", NEON_RED)
        except UnicodeDecodeError:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอ่านไฟล์นี้เป็นข้อความได้ (encoding ไม่รองรับ)")
            self._set_status("ERROR: อ่านไฟล์ไม่ได้ (encoding)", NEON_RED)
        except Exception as e:
            messagebox.showerror("ผิดพลาดไม่ทราบสาเหตุ", str(e))
            self._set_status(f"ERROR: {e}", NEON_RED)

    def load_sample(self):
        sample = (
            "ติดต่อเราได้ที่ contact@nexus-corp.io หรือ support@future.tech\n"
            "เว็บไซต์: https://www.nexus-corp.io/products และ http://future.tech\n"
            "โทร 081-234-5678 หรือ 0891112222\n"
            "Server IP: 192.168.1.10 และ 10.0.0.255\n"
            "วันที่นัดหมาย: 15/09/2026 และ 01-12-2025\n"
            "โพสต์ล่าสุด #AI #RegexIsFun ขอบคุณ @nexus_dev สำหรับข้อมูล\n"
            "ยอดขายปีนี้ 1024.50 บาท ลดลง -12.3 จากปีก่อน\n"
        )
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, sample)
        self._set_status("โหลดข้อความตัวอย่างแล้ว", NEON_YELLOW)

    def clear_input(self):
        self.input_text.delete("1.0", tk.END)
        self._set_status("ล้างข้อมูล Input แล้ว", NEON_YELLOW)

    def clear_output(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state="disabled")
        self._set_status("ล้างผลลัพธ์แล้ว", NEON_YELLOW)

    def execute(self):
        """หัวใจของโปรแกรม: ดึงข้อมูล -> ประมวลผลด้วย re -> แสดงผล พร้อม try-except ครบวงจร"""
        try:
            text = self.input_text.get("1.0", tk.END)
            if not text.strip():
                raise ValueError("ไม่มีข้อความให้ประมวลผล กรุณาใส่หรือโหลดข้อความก่อน")

            func_key = self.func_var.get()
            func, mode = FUNCTIONS[func_key]

            flags = build_flags(
                self.var_ignorecase.get(),
                self.var_multiline.get(),
                self.var_dotall.get()
            )

            params = {
                "pattern": self.pattern_entry.get().strip(),
                "replacement": self.repl_entry.get(),
                "extra": self.extra_entry.get().strip(),
                "flags": flags,
            }

            # ตรวจสอบ pattern ก่อนใช้งานจริง (ป้องกัน re.error)
            if params["pattern"]:
                re.compile(params["pattern"], flags)

            results = func(text, params)

            self._write_output(func_key, results)
            self._set_status(f"ประมวลผลสำเร็จ ✔ [{func_key}]", NEON_GREEN)

        except re.error as e:
            messagebox.showerror("Regex Pattern ผิดพลาด", f"Pattern ไม่ถูกต้อง:\n{e}")
            self._set_status(f"ERROR (re.error): {e}", NEON_RED)
        except ValueError as e:
            messagebox.showerror("ข้อมูลไม่ถูกต้อง", str(e))
            self._set_status(f"ERROR (ValueError): {e}", NEON_RED)
        except IndexError as e:
            messagebox.showerror("Group Index ผิดพลาด", f"ไม่พบ group ที่ระบุ:\n{e}")
            self._set_status(f"ERROR (IndexError): {e}", NEON_RED)
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาดไม่คาดคิด", str(e))
            self._set_status(f"ERROR (Unhandled): {e}", NEON_RED)

    def _write_output(self, func_key, results):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        header = f"=== ผลลัพธ์: {func_key} ===\n" + ("-" * 46) + "\n"
        self.output_text.insert(tk.END, header)
        for i, item in enumerate(results, start=1):
            self.output_text.insert(tk.END, f"{item}\n")
        self.output_text.configure(state="disabled")

    def _set_status(self, msg, color=NEON_GREEN):
        self.status_var.set(f">> {msg}")

    # ------------------------------------------------------------------
    # COSMETIC EFFECTS
    # ------------------------------------------------------------------
    def _update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S  |  %d-%m-%Y")
        self.clock_lbl.config(text=f"⏱ {now}")
        self.after(1000, self._update_clock)

    def _blink_cursor(self):
        # เอฟเฟกต์เล็กๆ ให้บอร์เดอร์ของช่อง status กระพริบแบบ HUD
        pass


if __name__ == "__main__":
    app = NeonRegexTerminal()
    app.mainloop()