import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import subprocess
import sys
from datetime import datetime
import threading
import queue

class AppProgramWriter:
    def __init__(self, root):
        self.root = root
        self.root.title("App Program Writer - Professional Code Editor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Treeview', background='#3c3f41', foreground='white', fieldbackground='#3c3f41')
        self.style.configure('Treeview.Heading', background='#4c5052', foreground='white')
        
        # Variables
        self.current_file = None
        self.current_project = None
        self.projects = {}
        self.recent_files = []
        self.auto_save = tk.BooleanVar(value=True)
        self.line_numbers = tk.BooleanVar(value=True)
        
        # Create main containers
        self.create_menu()
        self.create_toolbar()
        self.create_main_panels()
        self.create_status_bar()
        
        # Load settings
        self.load_settings()
        
        # Auto-save timer
        self.auto_save_timer = None
        if self.auto_save.get():
            self.start_auto_save()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+Shift+N")
        file_menu.add_command(label="Open File", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.editor.event_generate("<<Undo>>"), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.editor.event_generate("<<Redo>>"), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Line Numbers", variable=self.line_numbers, command=self.toggle_line_numbers)
        view_menu.add_checkbutton(label="Auto Save", variable=self.auto_save, command=self.toggle_auto_save)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Run Code", command=self.run_code, accelerator="F5")
        tools_menu.add_command(label="Format Code", command=self.format_code)
        tools_menu.add_command(label="Search & Replace", command=self.show_search_replace)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=2)
        
        # Toolbar buttons
        ttk.Button(toolbar, text="New Project", command=self.new_project).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side='left', padx=2)
        ttk.Separator(toolbar, orient='vertical').pack(side='left', padx=5, fill='y')
        ttk.Button(toolbar, text="Run", command=self.run_code).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Format", command=self.format_code).pack(side='left', padx=2)
        
        # Language selector
        ttk.Label(toolbar, text="Language:").pack(side='right', padx=5)
        self.language_var = tk.StringVar(value="Python")
        language_combo = ttk.Combobox(toolbar, textvariable=self.language_var, 
                                    values=["Python", "JavaScript", "Java", "C++", "C#", "HTML", "CSS", "SQL"], 
                                    width=10, state="readonly")
        language_combo.pack(side='right', padx=2)
        language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
    
    def create_main_panels(self):
        # Main container
        main_container = ttk.PanedWindow(self.root, orient='horizontal')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Project explorer
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)
        
        # Project explorer
        project_label = ttk.Label(left_frame, text="Project Explorer", font=('Arial', 10, 'bold'))
        project_label.pack(pady=5)
        
        self.project_tree = ttk.Treeview(left_frame, show='tree')
        self.project_tree.pack(fill='both', expand=True, padx=5)
        self.project_tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Right panel - Editor and output
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=3)
        
        # Editor notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create default editor tab
        self.create_editor_tab()
        
        # Output panel
        output_frame = ttk.Frame(right_frame)
        output_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_frame, text="Output", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, bg='#1e1e1e', fg='#ffffff')
        self.output_text.pack(fill='x', padx=5)
    
    def create_editor_tab(self, filename="Untitled", content=""):
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text=filename)
        
        # Line numbers
        if self.line_numbers.get():
            self.line_numbers_text = tk.Text(editor_frame, width=4, padx=3, takefocus=0, 
                                           border=0, background='#2b2b2b', foreground='#858585',
                                           state='disabled', font=('Consolas', 10))
            self.line_numbers_text.pack(side='left', fill='y')
        
        # Main editor
        self.editor = scrolledtext.ScrolledText(editor_frame, bg='#1e1e1e', fg='#ffffff', 
                                              insertbackground='#ffffff', font=('Consolas', 11),
                                              undo=True, wrap='none')
        self.editor.pack(side='right', fill='both', expand=True)
        
        # Bind events
        self.editor.bind('<KeyRelease>', self.on_editor_change)
        self.editor.bind('<Control-s>', lambda e: self.save_file())
        self.editor.bind('<Control-n>', lambda e: self.new_file())
        self.editor.bind('<Control-o>', lambda e: self.open_file())
        self.editor.bind('<F5>', lambda e: self.run_code())
        
        # Insert content
        if content:
            self.editor.insert('1.0', content)
        
        # Update line numbers
        self.update_line_numbers()
        
        return editor_frame
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief='sunken')
        self.status_label.pack(side='left', fill='x')
        
        # Cursor position
        self.cursor_label = ttk.Label(status_frame, text="Line: 1, Col: 1", relief='sunken')
        self.cursor_label.pack(side='right')
        
        # Bind cursor movement
        self.editor.bind('<KeyRelease>', self.update_cursor_position)
        self.editor.bind('<ButtonRelease-1>', self.update_cursor_position)
    
    def new_project(self):
        project_name = tk.simpledialog.askstring("New Project", "Enter project name:")
        if project_name:
            project_path = filedialog.askdirectory(title="Select project directory")
            if project_path:
                self.create_project(project_name, project_path)
    
    def create_project(self, name, path):
        project = {
            'name': name,
            'path': path,
            'files': [],
            'created': datetime.now().isoformat()
        }
        
        self.projects[name] = project
        self.current_project = name
        self.update_project_tree()
        self.save_settings()
        
        # Create project structure
        os.makedirs(path, exist_ok=True)
        project_file = os.path.join(path, f"{name}.proj")
        with open(project_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        self.status_label.config(text=f"Project '{name}' created successfully")
    
    def open_project(self):
        project_file = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("Project files", "*.proj"), ("All files", "*.*")]
        )
        if project_file:
            try:
                with open(project_file, 'r') as f:
                    project = json.load(f)
                
                self.projects[project['name']] = project
                self.current_project = project['name']
                self.update_project_tree()
                self.save_settings()
                
                self.status_label.config(text=f"Project '{project['name']}' opened successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open project: {str(e)}")
    
    def new_file(self):
        filename = f"Untitled_{len(self.notebook.tabs()) + 1}"
        self.create_editor_tab(filename)
        self.notebook.select(self.notebook.tabs()[-1])
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Java files", "*.java"),
                ("C++ files", "*.cpp;*.hpp"),
                ("C# files", "*.cs"),
                ("HTML files", "*.html;*.htm"),
                ("CSS files", "*.css"),
                ("SQL files", "*.sql"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                self.create_editor_tab(filename, content)
                self.current_file = file_path
                
                # Add to recent files
                if file_path not in self.recent_files:
                    self.recent_files.insert(0, file_path)
                    self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
                
                self.status_label.config(text=f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        
        try:
            current_tab = self.notebook.select()
            editor = self.get_current_editor()
            content = editor.get('1.0', 'end-1c')
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.status_label.config(text=f"Saved: {os.path.basename(self.current_file)}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            return False
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Java files", "*.java"),
                ("C++ files", "*.cpp"),
                ("C# files", "*.cs"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("SQL files", "*.sql"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            return self.save_file()
        return False
    
    def run_code(self):
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save the file first")
            return
        
        try:
            # Get current editor content
            editor = self.get_current_editor()
            content = editor.get('1.0', 'end-1c')
            
            # Save content to temp file
            temp_file = self.current_file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Run based on file extension
            ext = os.path.splitext(temp_file)[1].lower()
            
            if ext == '.py':
                result = subprocess.run([sys.executable, temp_file], 
                                     capture_output=True, text=True, timeout=30)
            elif ext == '.js':
                result = subprocess.run(['node', temp_file], 
                                     capture_output=True, text=True, timeout=30)
            elif ext == '.java':
                # Compile and run Java
                class_name = os.path.splitext(os.path.basename(temp_file))[0]
                compile_result = subprocess.run(['javac', temp_file], 
                                             capture_output=True, text=True)
                if compile_result.returncode == 0:
                    result = subprocess.run(['java', class_name], 
                                         capture_output=True, text=True, timeout=30)
                else:
                    result = compile_result
            else:
                messagebox.showinfo("Info", f"Running {ext} files is not supported yet")
                return
            
            # Display output
            self.output_text.delete('1.0', 'end')
            if result.stdout:
                self.output_text.insert('end', "STDOUT:\n" + result.stdout)
            if result.stderr:
                self.output_text.insert('end', "STDERR:\n" + result.stderr)
            if result.returncode != 0:
                self.output_text.insert('end', f"\nExit code: {result.returncode}")
            
            self.status_label.config(text="Code execution completed")
            
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Code execution timed out")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run code: {str(e)}")
    
    def format_code(self):
        # Basic code formatting (can be enhanced with external formatters)
        editor = self.get_current_editor()
        content = editor.get('1.0', 'end-1c')
        
        # Simple Python formatting
        if self.current_file and self.current_file.endswith('.py'):
            try:
                import autopep8
                formatted = autopep8.fix_code(content)
                editor.delete('1.0', 'end')
                editor.insert('1.0', formatted)
                self.status_label.config(text="Code formatted successfully")
            except ImportError:
                messagebox.showinfo("Info", "Install autopep8 for Python formatting: pip install autopep8")
        else:
            messagebox.showinfo("Info", "Code formatting not available for this file type")
    
    def show_search_replace(self):
        # Create search and replace dialog
        search_window = tk.Toplevel(self.root)
        search_window.title("Search & Replace")
        search_window.geometry("400x200")
        search_window.transient(self.root)
        search_window.grab_set()
        
        ttk.Label(search_window, text="Find:").pack(pady=5)
        find_entry = ttk.Entry(search_window, width=40)
        find_entry.pack(pady=5)
        
        ttk.Label(search_window, text="Replace with:").pack(pady=5)
        replace_entry = ttk.Entry(search_window, width=40)
        replace_entry.pack(pady=5)
        
        button_frame = ttk.Frame(search_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Find", 
                  command=lambda: self.find_text(find_entry.get())).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Replace", 
                  command=lambda: self.replace_text(find_entry.get(), replace_entry.get())).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Replace All", 
                  command=lambda: self.replace_all_text(find_entry.get(), replace_entry.get())).pack(side='left', padx=5)
    
    def find_text(self, search_text):
        if not search_text:
            return
        
        editor = self.get_current_editor()
        editor.tag_remove('search', '1.0', 'end')
        
        start_pos = '1.0'
        while True:
            pos = editor.search(search_text, start_pos, 'end')
            if not pos:
                break
            
            end_pos = f"{pos}+{len(search_text)}c"
            editor.tag_add('search', pos, end_pos)
            start_pos = end_pos
        
        editor.tag_config('search', background='yellow', foreground='black')
    
    def replace_text(self, search_text, replace_text):
        if not search_text:
            return
        
        editor = self.get_current_editor()
        try:
            editor.replace('sel.first', 'sel.last', replace_text)
        except tk.TclError:
            messagebox.showinfo("Info", "Please select text to replace")
    
    def replace_all_text(self, search_text, replace_text):
        if not search_text:
            return
        
        editor = self.get_current_editor()
        content = editor.get('1.0', 'end-1c')
        new_content = content.replace(search_text, replace_text)
        editor.delete('1.0', 'end')
        editor.insert('1.0', new_content)
        
        self.status_label.config(text=f"Replaced {content.count(search_text)} occurrences")
    
    def get_current_editor(self):
        current_tab = self.notebook.select()
        for child in self.notebook.children[current_tab].winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                return child
        return None
    
    def update_project_tree(self):
        self.project_tree.delete(*self.project_tree.get_children())
        
        if self.current_project and self.current_project in self.projects:
            project = self.projects[self.current_project]
            project_node = self.project_tree.insert('', 'end', text=project['name'], values=[project['path']])
            
            # Add files to tree
            for file_path in project.get('files', []):
                filename = os.path.basename(file_path)
                self.project_tree.insert(project_node, 'end', text=filename, values=[file_path])
    
    def on_tree_double_click(self, event):
        item = self.project_tree.selection()[0]
        values = self.project_tree.item(item, 'values')
        if values and os.path.isfile(values[0]):
            self.open_file_from_path(values[0])
    
    def open_file_from_path(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            self.create_editor_tab(filename, content)
            self.current_file = file_path
            self.status_label.config(text=f"Opened: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def on_editor_change(self, event=None):
        if self.auto_save.get():
            self.schedule_auto_save()
    
    def schedule_auto_save(self):
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.auto_save_timer = self.root.after(5000, self.auto_save_file)  # 5 seconds delay
    
    def auto_save_file(self):
        if self.current_file and self.auto_save.get():
            self.save_file()
    
    def start_auto_save(self):
        if self.auto_save.get():
            self.auto_save_timer = self.root.after(5000, self.auto_save_file)
    
    def toggle_auto_save(self):
        if self.auto_save.get():
            self.start_auto_save()
        else:
            if self.auto_save_timer:
                self.root.after_cancel(self.auto_save_timer)
    
    def toggle_line_numbers(self):
        # Implementation for toggling line numbers
        pass
    
    def update_line_numbers(self):
        if hasattr(self, 'line_numbers_text') and self.line_numbers.get():
            content = self.editor.get('1.0', 'end-1c')
            lines = content.count('\n') + 1
            
            line_numbers_content = '\n'.join(str(i) for i in range(1, lines + 1))
            self.line_numbers_text.config(state='normal')
            self.line_numbers_text.delete('1.0', 'end')
            self.line_numbers_text.insert('1.0', line_numbers_content)
            self.line_numbers_text.config(state='disabled')
    
    def update_cursor_position(self, event=None):
        try:
            cursor_pos = self.editor.index('insert')
            line, col = cursor_pos.split('.')
            self.cursor_label.config(text=f"Line: {int(line)}, Col: {int(col) + 1}")
        except:
            pass
    
    def on_language_change(self, event=None):
        # Update syntax highlighting based on language
        language = self.language_var.get()
        self.status_label.config(text=f"Language changed to: {language}")
    
    def show_about(self):
        about_text = """App Program Writer v1.0
        
A professional code editor and project manager
for developers and programmers.

Features:
• Multi-language support
• Project management
• Code execution
• Auto-save functionality
• Search and replace
• Modern dark theme UI

Created with Python and Tkinter"""
        
        messagebox.showinfo("About", about_text)
    
    def load_settings(self):
        try:
            if os.path.exists('app_writer_settings.json'):
                with open('app_writer_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.recent_files = settings.get('recent_files', [])
                    self.projects = settings.get('projects', {})
        except:
            pass
    
    def save_settings(self):
        try:
            settings = {
                'recent_files': self.recent_files,
                'projects': self.projects
            }
            with open('app_writer_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
        except:
            pass

def main():
    root = tk.Tk()
    app = AppProgramWriter(root)
    
    # Bind keyboard shortcuts
    root.bind('<Control-n>', lambda e: app.new_project())
    root.bind('<Control-o>', lambda e: app.open_file())
    root.bind('<Control-s>', lambda e: app.save_file())
    root.bind('<Control-Shift-S>', lambda e: app.save_file_as())
    root.bind('<F5>', lambda e: app.run_code())
    
    root.mainloop()

if __name__ == "__main__":
    main()
