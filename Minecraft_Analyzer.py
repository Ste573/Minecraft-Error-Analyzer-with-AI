import time
import requests
import os
import psutil
import threading
import json
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from tkinter import ttk

LOG_FILE = "C:/Users/ПК/AppData/Roaming/PrismLauncher/instances/1.21.1/minecraft/logs/latest.log"
CHECK_INTERVAL = 1
WAIT_AFTER_CRASH = 3
CONFIG_FILE = "minecraft_analyzer_config.json"

AI_SERVICES = {
    "ollama": {
        "name": "🖥️ Ollama (Local)",
        "url": "http://localhost:11434/api/generate",
        "models": ["gemma3:4b", "gemma2:2b", "mistral:latest", "llama3:latest"],
        "requires_key": False
    },
    "openai": {
        "name": "🔴 OpenAI (ChatGPT)",
        "url": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-4", "gpt-3.5-turbo"],
        "requires_key": True
    },
}

TRANSLATIONS = {
    "ru": {
        "title": "🎮 Анализатор ошибок Minecraft с ИИ",
        "version": "v4.3",
        "settings": "⚙️ Настройки",
        "log_path": "📂 Путь к логу:",
        "select": "Выбрать",
        "ai_service": "🤖 AI Сервис:",
        "language": "🌍 Язык:",
        "start": "▶️ Запустить",
        "stop": "⏹️ Остановить",
        "quick": "⚡ Короткое решение",
        "clear": "🗑️ Очистить",
        "settings_btn": "⚙️ Параметры",
        "stopped": "⏹️ Остановлено",
        "running": "▶️ Запущено",
        "logging": "📋 Логирование",
        "minecraft_not_running": "🎮 Minecraft: Не запущен",
        "minecraft_running": "🎮 Minecraft: Запущен",
        "minecraft_crashed": "🎮 Minecraft: Вылетел",
        "minecraft_unknown": "🎮 Minecraft: Неизвестно",
        "checking_ai": "🔍 Проверяю AI...",
        "ai_connected": "✅ AI подключен",
        "ai_not_found": "❌ Ошибка AI",
        "file_not_found": "❌ ФАЙЛ НЕ НАЙДЕН!",
        "path_updated": "✅ Путь обновлен:",
        "minecraft_started": "✅ Minecraft запущен",
        "minecraft_crashed_msg": "❌ Minecraft вылетел!",
        "waiting": "⏳ Жду 3 сек...",
        "collecting": "🔍 Собираю лог...",
        "found_errors": "✅ Найдены",
        "symbols": "символов в логе",
        "sending": "📤 Отправляю на анализ...",
        "no_errors": "ℹ️ Ошибок не найдено",
        "ready": "🎮 Готов к запуску...",
        "full_analysis": "🚨 ПОЛНЫЙ АНАЛИЗ",
        "quick_analysis": "⚡ БЫСТРЫЙ АНАЛИЗ",
        "monitoring_started": "▶️ МОНИТОРИНГ ЗАПУЩЕН",
        "monitoring_stopped": "⏹️ МОНИТОРИНГ ОСТАНОВЛЕН",
        "analyzing": "⏳ Анализирую...",
        "quick_analyzing": "⏳ Быстрый анализ...",
        "ai_analysis": "🤖 АНАЛИЗ ОТ ИИ:",
        "error_response": "⚠️ Пустой ответ",
        "error": "❌ Ошибка:",
        "timeout": "⏱️ Таймаут",
        "connection_lost": "❌ Потеряно соединение",
        "no_saved_log": "Нет логов!",
        "warning": "⚠️ Внимание",
        "instruction": "Инструкция:\n1. Нажмите \"Параметры\"\n2. Нажмите \"Запустить\"\n3. Запустите Minecraft\n4. При вылете - анализ автоматический",
        "waiting_minecraft": "🎮 Ожидаю Minecraft...",
        "minecraft_working": "💤 Minecraft работает...",
        "settings_title": "⚙️ Параметры",
        "language_label": "Язык:",
        "service_label": "AI Сервис:",
        "model_label": "Модель:",
        "custom_label": "Своя модель:",
        "api_key_label": "API Ключ:",
        "user_level": "Уровень:",
        "beginner": "👤 Обычный",
        "professional": "👨‍💼 Профессионал",
        "beginner_desc": "Простые ответы",
        "professional_desc": "Подробный анализ",
        "save": "💾 Сохранить",
        "cancel": "❌ Отмена",
        "settings_saved": "✅ Сохранено!",
    },
    "en": {
        "title": "🎮 Minecraft Error Analyzer",
        "version": "v4.3",
        "settings": "⚙️ Settings",
        "log_path": "📂 Log path:",
        "select": "Select",
        "ai_service": "🤖 AI Service:",
        "language": "🌍 Language:",
        "start": "▶️ Start",
        "stop": "⏹️ Stop",
        "quick": "⚡ Quick",
        "clear": "🗑️ Clear",
        "settings_btn": "⚙️ Settings",
        "stopped": "⏹️ Stopped",
        "running": "▶️ Running",
        "logging": "📋 Logging",
        "minecraft_not_running": "🎮 Minecraft: Stopped",
        "minecraft_running": "🎮 Minecraft: Running",
        "minecraft_crashed": "🎮 Minecraft: Crashed",
        "minecraft_unknown": "🎮 Minecraft: Unknown",
        "checking_ai": "🔍 Checking AI...",
        "ai_connected": "✅ AI connected",
        "ai_not_found": "❌ AI error",
        "file_not_found": "❌ FILE NOT FOUND!",
        "path_updated": "✅ Path updated:",
        "minecraft_started": "✅ Minecraft started",
        "minecraft_crashed_msg": "❌ Minecraft crashed!",
        "waiting": "⏳ Waiting 3 sec...",
        "collecting": "🔍 Collecting log...",
        "found_errors": "✅ Found",
        "symbols": "symbols in log",
        "sending": "📤 Sending...",
        "no_errors": "ℹ️ No errors",
        "ready": "🎮 Ready...",
        "full_analysis": "🚨 FULL ANALYSIS",
        "quick_analysis": "⚡ QUICK ANALYSIS",
        "monitoring_started": "▶️ MONITORING STARTED",
        "monitoring_stopped": "⏹️ MONITORING STOPPED",
        "analyzing": "⏳ Analyzing...",
        "quick_analyzing": "⏳ Quick analysis...",
        "ai_analysis": "🤖 AI ANALYSIS:",
        "error_response": "⚠️ Empty response",
        "error": "❌ Error:",
        "timeout": "⏱️ Timeout",
        "connection_lost": "❌ Connection lost",
        "no_saved_log": "No logs!",
        "warning": "⚠️ Warning",
        "instruction": "Instructions:\n1. Click \"Settings\"\n2. Click \"Start\"\n3. Launch Minecraft\n4. On crash - auto analysis",
        "waiting_minecraft": "🎮 Waiting...",
        "minecraft_working": "💤 Running...",
        "settings_title": "⚙️ Settings",
        "language_label": "Language:",
        "service_label": "AI Service:",
        "model_label": "Model:",
        "custom_label": "Custom model:",
        "api_key_label": "API Key:",
        "user_level": "Level:",
        "beginner": "👤 Regular",
        "professional": "👨‍💼 Professional",
        "beginner_desc": "Simple answers",
        "professional_desc": "Detailed analysis",
        "save": "💾 Save",
        "cancel": "❌ Cancel",
        "settings_saved": "✅ Saved!",
    }
}

class SettingsWindow:
    def __init__(self, parent, current_settings, translations):
        self.result = None
        self.current_settings = current_settings
        self.t = translations
        
        self.window = tk.Toplevel(parent)
        self.window.title(self.t["settings_title"])
        self.window.geometry("550x650")
        self.window.configure(bg="#0a0a0a")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
        self.window.update_idletasks()
        x = parent.winfo_x() + 200
        y = parent.winfo_y() + 50
        self.window.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=self.t["language_label"]).pack(anchor=tk.W, pady=(10, 5))
        self.lang_var = tk.StringVar(value=self.current_settings["language"])
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Radiobutton(lang_frame, text="🇷🇺 Русский", variable=self.lang_var, value="ru").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(lang_frame, text="🇬🇧 English", variable=self.lang_var, value="en").pack(side=tk.LEFT, padx=10)
        
        ttk.Label(main_frame, text=self.t["service_label"]).pack(anchor=tk.W, pady=(10, 5))
        self.service_var = tk.StringVar(value=self.current_settings["service"])
        service_combo = ttk.Combobox(main_frame, textvariable=self.service_var,
                                     values=[AI_SERVICES[s]["name"] for s in AI_SERVICES.keys()],
                                     state="readonly", width=45)
        service_combo.pack(fill=tk.X, pady=(0, 15))
        service_combo.bind("<<ComboboxSelected>>", self.on_service_change)
        
        ttk.Label(main_frame, text=self.t["model_label"]).pack(anchor=tk.W, pady=(10, 5))
        self.model_var = tk.StringVar(value=self.current_settings["model"])
        self.model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, state="readonly", width=45)
        self.model_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text=self.t["custom_label"]).pack(anchor=tk.W, pady=(5, 5))
        self.custom_model = tk.StringVar(value=self.current_settings.get("custom_model", ""))
        ttk.Entry(main_frame, textvariable=self.custom_model, width=45).pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(main_frame, text=self.t["api_key_label"]).pack(anchor=tk.W, pady=(5, 5))
        self.api_key = tk.StringVar(value=self.current_settings.get("api_key", ""))
        ttk.Entry(main_frame, textvariable=self.api_key, width=45, show="*").pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(main_frame, text=self.t["user_level"]).pack(anchor=tk.W, pady=(10, 10))
        self.user_var = tk.StringVar(value=self.current_settings.get("user_level", "beginner"))
        
        ttk.Radiobutton(main_frame, text=self.t["beginner"], variable=self.user_var, value="beginner").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(main_frame, text=f"   {self.t['beginner_desc']}", foreground="#888888").pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        ttk.Radiobutton(main_frame, text=self.t["professional"], variable=self.user_var, value="professional").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(main_frame, text=f"   {self.t['professional_desc']}", foreground="#888888").pack(anchor=tk.W, padx=10, pady=(0, 20))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        ttk.Button(button_frame, text=self.t["save"], command=self.save_settings, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.t["cancel"], command=self.window.destroy, width=20).pack(side=tk.LEFT, padx=5)
        
        self.on_service_change()
    
    def on_service_change(self, event=None):
        service_name = self.service_var.get()
        try:
            service_key = [k for k, v in AI_SERVICES.items() if v["name"] == service_name][0]
            models = AI_SERVICES[service_key]["models"]
            self.model_combo["values"] = models
            if models:
                self.model_combo.set(models[0])
        except:
            pass
    
    def save_settings(self):
        service_name = self.service_var.get()
        try:
            service_key = [k for k, v in AI_SERVICES.items() if v["name"] == service_name][0]
        except:
            service_key = "ollama"
        
        self.result = {
            "language": self.lang_var.get(),
            "service": service_key,
            "model": self.model_var.get(),
            "custom_model": self.custom_model.get(),
            "api_key": self.api_key.get(),
            "user_level": self.user_var.get()
        }
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.result, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        messagebox.showinfo("✅", "Сохранено!" if self.lang_var.get() == "ru" else "Saved!")
        self.window.destroy()

class LanguageSelectWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🎮 Minecraft")
        self.window.geometry("500x350")
        self.window.configure(bg="#0a0a0a")
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 250
        y = (self.window.winfo_screenheight() // 2) - 175
        self.window.geometry(f'+{x}+{y}')
        self.selected_language = None
        self.setup_ui()
    
    def setup_ui(self):
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill=tk.X, padx=20, pady=30)
        ttk.Label(title_frame, text="🎮 Choose / Выберите").pack()
        
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ru_btn = tk.Button(button_frame, text="🇷🇺 РУССКИЙ", bg="#1e5f74", fg="#00ff00",
                          activebackground="#2a8fa0", height=3, cursor="hand2",
                          command=lambda: self.select_language("ru"))
        ru_btn.pack(fill=tk.BOTH, expand=True, pady=10)
        
        en_btn = tk.Button(button_frame, text="🇬🇧 ENGLISH", bg="#5f1e74", fg="#00aaff",
                          activebackground="#8a2aa0", height=3, cursor="hand2",
                          command=lambda: self.select_language("en"))
        en_btn.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def select_language(self, lang):
        self.selected_language = lang
        self.window.quit()
        self.window.destroy()
    
    def get_language(self):
        self.window.mainloop()
        return self.selected_language

class MinecraftAnalyzerGUI:
    def __init__(self, root, language="en"):
        self.root = root
        self.language = language
        self.t = TRANSLATIONS[language]
        self.root.title(self.t['title'])
        self.root.geometry("1100x750")
        self.root.configure(bg="#0a0a0a")
        
        self.log_file = tk.StringVar(value=LOG_FILE)
        self.is_running = False
        self.minecraft_was_running = False
        self.last_position = 0
        self.monitor_thread = None
        self.last_crash_log = None
        
        self.service = "ollama"
        self.model = "gemma3:4b"
        self.custom_model = ""
        self.api_key = ""
        self.user_level = "beginner"
        
        self.load_settings()
        self.setup_style()
        self.setup_ui()
        self.check_ai_connection()
    
    def load_settings(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.language = config.get("language", self.language)
                    self.service = config.get("service", "ollama")
                    self.model = config.get("model", "gemma3:4b")
                    self.custom_model = config.get("custom_model", "")
                    self.api_key = config.get("api_key", "")
                    self.user_level = config.get("user_level", "beginner")
                    self.t = TRANSLATIONS[self.language]
        except:
            pass
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        bg_color = "#0a0a0a"
        fg_color = "#00ff00"
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
    
    def setup_ui(self):
        top_frame = ttk.LabelFrame(self.root, text=self.t["settings"], padding=15)
        top_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(top_frame, text=self.t["log_path"]).grid(row=0, column=0, sticky=tk.W, padx=10, pady=8)
        ttk.Entry(top_frame, textvariable=self.log_file, width=40).grid(row=0, column=1, padx=10, pady=8, sticky=tk.EW)
        ttk.Button(top_frame, text=self.t["select"], width=10, command=self.select_log_file).grid(row=0, column=2, padx=5)
        
        ttk.Label(top_frame, text=self.t["ai_service"]).grid(row=1, column=0, sticky=tk.W, padx=10, pady=8)
        service_name = AI_SERVICES[self.service]["name"]
        ttk.Label(top_frame, text=f"{service_name}", foreground="#00aaff").grid(row=1, column=1, sticky=tk.W, padx=10)
        ttk.Button(top_frame, text=self.t["settings_btn"], width=15, command=self.open_settings).grid(row=1, column=2, padx=5)
        
        self.ai_status = ttk.Label(top_frame, text=self.t["checking_ai"], foreground="#ffaa00")
        self.ai_status.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)
        
        control_frame = ttk.Frame(self.root, padding=15)
        control_frame.pack(fill=tk.X, padx=15)
        
        self.start_btn = ttk.Button(control_frame, text=self.t["start"], command=self.start_monitoring, width=18)
        self.start_btn.pack(side=tk.LEFT, padx=8)
        self.stop_btn = ttk.Button(control_frame, text=self.t["stop"], command=self.stop_monitoring, state=tk.DISABLED, width=18)
        self.stop_btn.pack(side=tk.LEFT, padx=8)
        self.quick_btn = ttk.Button(control_frame, text=self.t["quick"], command=self.quick_analyze, state=tk.DISABLED, width=18)
        self.quick_btn.pack(side=tk.LEFT, padx=8)
        self.clear_btn = ttk.Button(control_frame, text=self.t["clear"], command=self.clear_output, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=8)
        self.status_label = ttk.Label(control_frame, text=self.t["stopped"], foreground="#ff0000")
        self.status_label.pack(side=tk.LEFT, padx=30)
        
        log_frame = ttk.LabelFrame(self.root, text=self.t["logging"], padding=12)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.output_text = scrolledtext.ScrolledText(log_frame, height=22, width=130, bg="#1a1a1a", fg="#00ff00", font=("Courier", 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        self.output_text.tag_config("info", foreground="#00ff00")
        self.output_text.tag_config("success", foreground="#00ff00", font=("Courier", 9, "bold"))
        self.output_text.tag_config("warning", foreground="#ffaa00")
        self.output_text.tag_config("error", foreground="#ff3333", font=("Courier", 9, "bold"))
        self.output_text.tag_config("ai", foreground="#00aaff")
        self.output_text.tag_config("quick", foreground="#ff00ff")
        self.output_text.tag_config("title", foreground="#ffff00", font=("Courier", 11, "bold"))
        
        info_frame = ttk.Frame(self.root, padding=10)
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        self.minecraft_status = ttk.Label(info_frame, text=self.t["minecraft_not_running"], foreground="#ff0000")
        self.minecraft_status.pack(side=tk.LEFT, padx=15)
        level_text = self.t["professional"] if self.user_level == "professional" else self.t["beginner"]
        self.level_label = ttk.Label(info_frame, text=f"👤 {level_text}", foreground="#888888")
        self.level_label.pack(side=tk.LEFT, padx=15)
        self.time_label = ttk.Label(info_frame, text="", foreground="#888888")
        self.time_label.pack(side=tk.RIGHT, padx=15)
        
        self.display_welcome()
    
    def display_welcome(self):
        service_name = AI_SERVICES[self.service]["name"]
        level_text = self.t["professional"] if self.user_level == "professional" else self.t["beginner"]
        welcome_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         🎮 {self.t['title']}                                               ║
║         {level_text}                                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

{self.t['instruction']}
        """
        self.log(welcome_text, "title")
    
    def open_settings(self):
        current_settings = {
            "language": self.language,
            "service": self.service,
            "model": self.model,
            "custom_model": self.custom_model,
            "api_key": self.api_key,
            "user_level": self.user_level
        }
        settings_window = SettingsWindow(self.root, current_settings, self.t)
        self.root.wait_window(settings_window.window)
        if settings_window.result:
            if settings_window.result["language"] != self.language:
                self.language = settings_window.result["language"]
                self.t = TRANSLATIONS[self.language]
            self.service = settings_window.result["service"]
            self.model = settings_window.result["model"]
            self.custom_model = settings_window.result["custom_model"]
            self.api_key = settings_window.result["api_key"]
            self.user_level = settings_window.result["user_level"]
            level_text = self.t["professional"] if self.user_level == "professional" else self.t["beginner"]
            self.level_label.config(text=f"👤 {level_text}")
            self.display_welcome()
            self.log(f"✅ {self.t['settings_saved']}", "success")
            self.check_ai_connection()
    
    def log(self, message, tag="info"):
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        self.root.update()
    
    def select_log_file(self):
        file = filedialog.askopenfilename(title="Select latest.log", filetypes=[("Log files", "*.log"), ("All files", "*.*")])
        if file:
            self.log_file.set(file)
            self.log(f"{self.t['path_updated']} {file}", "success")
    
    def check_ai_connection(self):
        self.log(self.t["checking_ai"], "warning")
        service_name = AI_SERVICES[self.service]["name"]
        try:
            if self.service == "ollama":
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    self.ai_status.config(text=self.t["ai_connected"], foreground="#00ff00")
                    self.log(f"✅ {service_name} OK", "success")
                else:
                    raise Exception()
            else:
                if not self.api_key:
                    raise Exception()
                self.ai_status.config(text=self.t["ai_connected"], foreground="#00ff00")
                self.log(f"✅ {service_name} OK", "success")
        except:
            self.ai_status.config(text=self.t["ai_not_found"], foreground="#ff0000")
            self.log(self.t["ai_not_found"], "error")
    
    def is_minecraft_running(self):
        try:
            for proc in psutil.process_iter(['name']):
                if 'javaw.exe' in proc.name() or 'java.exe' in proc.name():
                    return True
        except:
            pass
        return False
    
    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        if self.is_running:
            self.root.after(1000, self.update_time)
    
    def start_monitoring(self):
        log_path = self.log_file.get()
        if not os.path.exists(log_path):
            messagebox.showerror("Error", f"{self.t['file_not_found']}\n{log_path}")
            return
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text=self.t["running"], foreground="#00ff00")
        self.log("\n" + "="*90, "title")
        self.log(self.t["monitoring_started"], "title")
        self.log("="*90, "title")
        self.log(f"📂 {log_path}\n", "info")
        self.last_position = os.path.getsize(log_path)
        self.monitor_thread = threading.Thread(target=self.monitor_loop, args=(log_path,), daemon=True)
        self.monitor_thread.start()
        self.update_time()
    
    def stop_monitoring(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.quick_btn.config(state=tk.DISABLED)
        self.status_label.config(text=self.t["stopped"], foreground="#ff0000")
        self.minecraft_status.config(text=self.t["minecraft_unknown"], foreground="#888888")
        self.log("\n" + "="*90, "title")
        self.log(self.t["monitoring_stopped"], "title")
        self.log("="*90 + "\n", "title")
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.log("🗑️ Cleared\n", "info")
    
    def quick_analyze(self):
        if not self.last_crash_log:
            messagebox.showwarning(self.t["warning"], self.t["no_saved_log"])
            return
        self.log("\n" + "="*90, "title")
        self.log(self.t["quick_analysis"], "quick")
        self.log("="*90, "title")
        thread = threading.Thread(target=self.analyze_errors_quick, daemon=True)
        thread.start()
    
    def send_to_ai(self, prompt, is_quick=False):
        try:
            if self.service == "ollama":
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=60 if is_quick else 180
                )
                if response.status_code == 200:
                    return response.json().get('response', '')
            elif self.service == "openai":
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000},
                    timeout=60 if is_quick else 180
                )
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
        except:
            pass
        return None
    
    def analyze_errors_quick(self):
        # ПРАВИЛЬНО ВЫБИРАЕМ ЯЗЫК
        if self.language == "ru":
            lang_instruction = "Ответь на РУССКОМ языке"
        else:
            lang_instruction = "Answer in ENGLISH"
        
        if self.user_level == "professional":
            prompt = f"""Ты эксперт Minecraft/Java разработчик.
{lang_instruction}

КРАТКИЙ ТЕХНИЧЕСКИЙ АНАЛИЗ лога краша:

{self.last_crash_log}

Дай краткий ответ:
⚡ ПРИЧИНА:
✅ РЕШЕНИЕ:"""
        else:
            prompt = f"""Ты эксперт Minecraft.
{lang_instruction}

ПРОСТОЕ ОБЪЯСНЕНИЕ лога краша:

{self.last_crash_log}

Дай простой ответ:
⚡ ЧТО СЛУЧИЛОСЬ:
✅ КАК ИСПРАВИТЬ:"""
        
        try:
            self.log(f"{self.t['quick_analyzing']}\n", "warning")
            result = self.send_to_ai(prompt, is_quick=True)
            if result:
                self.log(result + "\n", "quick")
            else:
                self.log(self.t["error_response"], "warning")
        except Exception as e:
            self.log(f"{self.t['error']} {e}", "error")
        self.log("="*90 + "\n", "title")
    
    def monitor_loop(self, log_path):
        check_count = 0
        while self.is_running:
            try:
                check_count += 1
                minecraft_running = self.is_minecraft_running()
                if minecraft_running and not self.minecraft_was_running:
                    self.minecraft_status.config(text=self.t["minecraft_running"], foreground="#00ff00")
                    self.log(self.t["minecraft_started"], "success")
                    self.minecraft_was_running = True
                    try:
                        self.last_position = os.path.getsize(log_path)
                    except:
                        pass
                elif not minecraft_running and self.minecraft_was_running:
                    self.minecraft_status.config(text=self.t["minecraft_crashed"], foreground="#ff0000")
                    self.log(f"\n{self.t['minecraft_crashed_msg']}", "error")
                    self.minecraft_was_running = False
                    self.log(self.t["waiting"], "warning")
                    for i in range(WAIT_AFTER_CRASH):
                        time.sleep(1)
                    self.log(self.t["collecting"], "warning")
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            all_lines = f.readlines()
                        start_index = max(0, len(all_lines) - 500)
                        crash_log = ''.join(all_lines[start_index:])
                        self.last_crash_log = crash_log
                        if any(keyword in crash_log.upper() for keyword in ['ERROR', 'FATAL', 'EXCEPTION', 'CRASH']):
                            self.log(f"{self.t['found_errors']} ошибок", "success")
                            self.log(f"{self.t['sending']}\n", "info")
                            self.quick_btn.config(state=tk.NORMAL)
                            self.analyze_errors(crash_log)
                        else:
                            self.log(self.t["no_errors"], "info")
                            self.quick_btn.config(state=tk.DISABLED)
                    except:
                        pass
                    self.log(f"\n{self.t['ready']}\n", "info")
                if minecraft_running and check_count % 30 == 0:
                    self.log(self.t["minecraft_working"], "info")
                time.sleep(CHECK_INTERVAL)
            except:
                time.sleep(CHECK_INTERVAL)
    
    def analyze_errors(self, error_log):
        self.log("="*90, "title")
        self.log(self.t["full_analysis"], "title")
        self.log("="*90, "title")
        
        # ПРАВИЛЬНО ВЫБИРАЕМ ЯЗЫК
        if self.language == "ru":
            lang_instruction = "Ответь на РУССКОМ языке"
        else:
            lang_instruction = "Answer in ENGLISH"
        
        if self.user_level == "professional":
            prompt = f"""Ты старший разработчик Java и эксперт Minecraft.
{lang_instruction}

ПОЛНЫЙ ТЕХНИЧЕСКИЙ АНАЛИЗ лога краша:

{error_log}

Дай подробный ответ с техническими деталями:
🔴 ОСНОВНАЯ ПРИЧИНА:
📋 ВСЕ ОШИБКИ:
🔍 ТЕХНИЧЕСКАЯ ПРИЧИНА:
✅ РЕШЕНИЕ:
💡 СОВЕТЫ:"""
        else:
            prompt = f"""Ты эксперт Minecraft.
{lang_instruction}

ПРОСТОЕ ОБЪЯСНЕНИЕ лога краша:

{error_log}

Дай простой понятный ответ:
🔴 ЧТО СЛУЧИЛОСЬ:
✅ ПОЧЕМУ ЭТО ПРОИЗОШЛО:
💡 КАК ИСПРАВИТЬ:"""
        
        try:
            self.log(f"{self.t['analyzing']}\n", "warning")
            result = self.send_to_ai(prompt, is_quick=False)
            if result:
                self.log(f"{self.t['ai_analysis']}\n", "ai")
                self.log(result + "\n", "ai")
            else:
                self.log(self.t["error_response"], "warning")
        except Exception as e:
            self.log(f"{self.t['error']} {e}", "error")
        self.log("="*90 + "\n", "title")

if __name__ == "__main__":
    try:
        import psutil
    except:
        print("pip install psutil requests")
        exit()
    
    lang_window = LanguageSelectWindow()
    language = lang_window.get_language()
    
    if language:
        root = tk.Tk()
        app = MinecraftAnalyzerGUI(root, language)
        root.mainloop()
