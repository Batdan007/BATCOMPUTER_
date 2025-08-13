# App Program Writer - Professional Code Editor

A modern, feature-rich code editor and project manager built with Python and Tkinter, designed for developers and programmers.

## 🚀 Features

### Core Features
- **Multi-language Support**: Python, JavaScript, Java, C++, C#, HTML, CSS, SQL
- **Project Management**: Create, open, and manage coding projects
- **Code Editor**: Syntax-aware editing with line numbers
- **Code Execution**: Run code directly from the editor (F5)
- **Auto-save**: Automatic file saving with configurable intervals
- **Search & Replace**: Find and replace text with highlighting

### User Interface
- **Modern Dark Theme**: Professional dark color scheme
- **Tabbed Interface**: Multiple files open simultaneously
- **Project Explorer**: Tree view of project structure
- **Toolbar**: Quick access to common functions
- **Status Bar**: File information and cursor position
- **Output Panel**: View program execution results

### Developer Tools
- **Code Formatting**: Automatic code formatting (Python with autopep8)
- **Keyboard Shortcuts**: Standard editor shortcuts (Ctrl+S, Ctrl+O, F5)
- **Recent Files**: Quick access to recently opened files
- **Settings Persistence**: Remembers your preferences

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: Python 3.7 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 100MB free space

### Python Dependencies
Most dependencies are built-in with Python. For enhanced features, install:

```bash
pip install -r app_writer_requirements.txt
```

**Core dependencies (built-in):**
- `tkinter` - GUI framework
- `json` - JSON handling
- `os`, `sys` - System utilities
- `subprocess` - Process execution
- `datetime` - Date/time handling
- `threading`, `queue` - Threading support

**Optional dependencies:**
- `autopep8` - Python code formatting
- `black` - Alternative Python formatter
- `pygments` - Syntax highlighting

## 🛠️ Installation

### Method 1: Direct Download
1. Download `app_program_writer.py`
2. Ensure Python 3.7+ is installed
3. Run: `python app_program_writer.py`

### Method 2: From Source
1. Clone or download the project
2. Navigate to the project directory
3. Install dependencies: `pip install -r app_writer_requirements.txt`
4. Run: `python app_program_writer.py`

### Method 3: Create Executable (Windows)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed app_program_writer.py
```

## 🎯 Quick Start

### 1. Launch the Application
```bash
python app_program_writer.py
```

### 2. Create Your First Project
- Click **File → New Project** or use **Ctrl+N**
- Enter project name
- Select project directory
- Click **Create**

### 3. Create Your First File
- Click **File → New File** or use **Ctrl+Shift+N**
- Start coding in the editor
- Save with **Ctrl+S**

### 4. Run Your Code
- Press **F5** or click **Tools → Run Code**
- View output in the bottom panel

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New Project | Ctrl+N |
| Open File | Ctrl+O |
| New File | Ctrl+Shift+N |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Run Code | F5 |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Cut | Ctrl+X |
| Copy | Ctrl+C |
| Paste | Ctrl+V |

## 🗂️ Project Management

### Creating Projects
1. **File → New Project** (Ctrl+N)
2. Enter project name
3. Select directory location
4. Project file (.proj) is created automatically

### Project Structure
```
ProjectName/
├── ProjectName.proj          # Project configuration
├── src/                      # Source code files
├── docs/                     # Documentation
├── tests/                    # Test files
└── README.md                 # Project documentation
```

### Opening Projects
- **File → Open Project**
- Navigate to .proj file
- All project files appear in explorer

## 🔧 Configuration

### Settings File
The application creates `app_writer_settings.json` to store:
- Recent files list
- Project information
- User preferences

### Customization
- **View → Line Numbers**: Toggle line number display
- **View → Auto Save**: Enable/disable automatic saving
- **Language Selector**: Choose programming language for syntax hints

## 🐛 Troubleshooting

### Common Issues

**"tkinter module not found"**
- Install Python with tkinter: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- Windows/macOS: tkinter comes with Python installation

**Code execution fails**
- Ensure file is saved first
- Check file extension matches language
- Verify required interpreters are installed (Python, Node.js, Java)

**Performance issues**
- Close unnecessary tabs
- Reduce auto-save frequency
- Restart application

### Getting Help
1. Check the output panel for error messages
2. Verify file permissions
3. Ensure dependencies are installed
4. Check Python version compatibility

## 🚀 Advanced Features

### Code Formatting
- **Python**: Uses autopep8 for automatic formatting
- **Other languages**: Basic formatting available
- **Tools → Format Code** or right-click context menu

### Search and Replace
- **Tools → Search & Replace**
- Find text with highlighting
- Replace single or all occurrences
- Regular expression support (planned)

### Multi-language Support
- **Python**: Full execution and formatting
- **JavaScript**: Node.js execution
- **Java**: Compilation and execution
- **HTML/CSS**: Preview functionality (planned)

## 🔮 Future Enhancements

### Planned Features
- **Syntax Highlighting**: Color-coded code for all languages
- **Code Completion**: Intelligent code suggestions
- **Git Integration**: Version control within the editor
- **Debugging**: Integrated debugger support
- **Extensions**: Plugin system for custom functionality
- **Themes**: Multiple color schemes
- **Terminal**: Integrated terminal for command execution

### Contributing
Contributions are welcome! Areas for improvement:
- Additional language support
- Enhanced syntax highlighting
- Performance optimizations
- UI/UX improvements
- Testing and documentation

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Support

### Reporting Issues
- Create an issue with detailed description
- Include system information and error messages
- Provide steps to reproduce the problem

### Feature Requests
- Submit feature requests through issues
- Describe the desired functionality
- Explain the use case and benefits

---

**App Program Writer** - Empowering developers with a professional, feature-rich code editing experience.

*Built with ❤️ using Python and Tkinter*
