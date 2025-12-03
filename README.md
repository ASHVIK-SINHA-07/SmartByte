# 🎓 Smart Study Assistant

> Your AI-powered learning companion for enhanced productivity and effective studying

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/ASHVIK-SINHA-07)

<div align="center">
  <img src="assets/logo.png" alt="Smart Study Assistant Logo" width="150">
</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Technologies](#-technologies)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

**Smart Study Assistant** is a comprehensive desktop application designed to revolutionize your study experience. Built with Python and powered by Google's Gemini AI, it combines note-taking, reminder scheduling, AI-powered quiz generation, and productivity tracking into one seamless platform.

### Why Smart Study Assistant?

- 📝 **Intelligent Note-Taking** - Create, organize, and search notes with ease
- ⏰ **Smart Reminders** - Never miss a study session with intelligent scheduling
- 🎯 **AI-Generated Quizzes** - Test your knowledge with AI-powered questions
- ⏱️ **Study Timer** - Track your study sessions with Pomodoro technique
- 📊 **Progress Dashboard** - Visualize your learning journey with XP and badges
- 🎨 **Modern UI** - Beautiful, responsive interface with light/dark themes

---

## ✨ Features

### 📝 Notes Management
- **Rich Text Editor** - Write and format notes with ease
- **Auto-Save** - Never lose your work with automatic saving
- **Tags & Search** - Organize and quickly find your notes
- **Live Filtering** - Real-time search across all notes
- **Export Options** - Save notes in multiple formats

### ⏰ Smart Reminders
- **Dropdown Date/Time Selection** - Easy-to-use date and time pickers
- **Quick Time Buttons** - Set reminders for 1 hour, 3 hours, tomorrow, or 1 week
- **Message Suggestions** - Pre-built reminder messages
- **Active Reminder List** - View and manage all scheduled reminders
- **APScheduler Integration** - Reliable reminder notifications

### 🎯 AI-Powered Quiz Generator
- **Gemini AI Integration** - Intelligent question generation from your notes
- **Comprehension Testing** - Questions designed to test understanding
- **Interactive Flashcards** - Study with flip-card style learning
- **Progress Tracking** - Monitor your quiz performance

### ⏱️ Study Timer
- **Pomodoro Technique** - Built-in 25-minute focus sessions
- **Custom Durations** - Set your own study time
- **Quick Actions** - Pomodoro, short break, long break presets
- **Session History** - Track all your study sessions
- **XP Rewards** - Earn points for completed sessions

### 📊 Dashboard & Analytics
- **XP System** - Gamified learning experience
- **Badge Collection** - Unlock achievements as you study
- **Activity Timeline** - Recent study activity overview
- **Statistics** - Notes created, quizzes taken, study time
- **Visual Cards** - Clean, modern data presentation

### 🎨 Customization
- **Light/Dark Themes** - Easy theme switching
- **Modern UI** - Built with ttkbootstrap for a polished look
- **Responsive Design** - Adapts to different screen sizes
- **Custom Logo** - Professional branding with custom icon

---

## 🎬 Demo

### Main Interface
```
<img width="1710" height="1112" alt="Screenshot 2025-12-03 at 1 49 47 PM" src="https://github.com/user-attachments/assets/2df94cd6-2ce6-4aae-93c2-85d97becf7e5" />


```

### Key Screenshots
- **Notes Tab**: Rich text editor with search and tags
- **Reminders Tab**: Dropdown-based date/time selection with quick buttons
- **Quiz Tab**: AI-generated questions from your notes
- **Timer Tab**: Pomodoro timer with session tracking
- **Dashboard**: XP, badges, and activity overview

---

## 🚀 Installation

### Prerequisites
- **Python 3.8+** installed on your system
- **pip** (Python package manager)
- **Gemini API Key** (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Step 1: Clone the Repository
```bash
git clone https://github.com/ASHVIK-SINHA-07/my-first-repo.git
cd my-first-repo/Smart_byte
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Required Packages:
```
ttkbootstrap>=1.10.1     # Modern UI styling
pandas>=2.0.0            # Data handling
python-dotenv>=1.0.0     # Environment variables
google-generativeai>=0.3.0  # Gemini AI
apscheduler>=3.10.0      # Reminder scheduling
pyttsx3>=2.90            # Text-to-speech
pillow>=10.0.0           # Image processing
```

### Step 3: Configure Environment
Create a `.env` file in the Smart_byte directory:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

### Step 4: Run the Application
```bash
python3 main.py
```

---

## 💻 Usage

### Basic Workflow

#### 1. **Create a Note**
```
1. Go to the Notes tab
2. Click "➕ New"
3. Enter title, content, and tags
4. Auto-saves every 3 seconds
```

#### 2. **Set a Reminder**
```
1. Go to the Reminders tab
2. Select date using dropdowns
3. Select time (hour:minute)
4. Or use Quick Select buttons (1 Hour, Tomorrow, etc.)
5. Enter reminder message or pick a suggestion
6. Click "Add Reminder"
```

#### 3. **Generate a Quiz**
```
1. Create some notes first
2. Go to the Quiz tab
3. Click "✨ Generate 5 Questions"
4. AI will analyze your notes and create questions
5. Click "📝 Take Quiz" to start
6. Use flashcards for interactive learning
```

#### 4. **Use Study Timer**
```
1. Go to the Timer tab
2. Click "🍅 Pomodoro (25 min)" for quick start
3. Or enter custom duration
4. Click "▶️ Start"
5. Complete session to earn XP
```

#### 5. **Track Progress**
```
1. Go to the Dashboard tab
2. View your XP, notes count, and badges
3. Check recent activity
4. See upcoming reminders
```

### Keyboard Shortcuts
- **Ctrl/Cmd + S** - Save note manually
- **Ctrl/Cmd + N** - New note
- **Ctrl/Cmd + T** - Toggle theme (light/dark)
- **Ctrl/Cmd + Z** - Undo
- **Ctrl/Cmd + Y** - Redo

---

## 📁 Project Structure

```
Smart_byte/
│
├── 📄 Core Application Files
│   ├── main.py                 # Main application entry point
│   ├── config.py               # Configuration settings
│   ├── logger.py               # Logging system
│   ├── ui_components.py        # Custom UI widgets
│   ├── ai_utils.py             # AI/Gemini integration
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (not in repo)
│   ├── .env.example            # Template for .env
│   └── README.md               # This file
│
├── 📁 modules/                 # Core functionality modules
│   ├── storage.py              # Data persistence (CSV/JSON)
│   ├── reminders.py            # Reminder scheduling system
│   ├── quizgen.py              # Quiz generation logic
│   ├── speech_notes.py         # Speech-to-text features
│   ├── notes_manager.py        # Notes management
│   └── tts.py                  # Text-to-speech features
│
├── 📁 assets/                  # Visual assets
│   ├── logo.png                # App logo (128x128)
│   └── icon.png                # Window icon (64x64)
│
├── 📁 utils/                   # Utility scripts
│   ├── cleanup_database.py     # Remove duplicate notes
│   ├── sync_stats.py           # Synchronize statistics
│   ├── verify_notes_section.py # Verify notes system
│   └── create_logo.py          # Logo generation script
│
├── 📁 scripts/                 # Maintenance scripts
│   └── migrate_notes.py        # Database migration utilities
│
├── 📁 data/                    # User data (not in repo)
│   ├── notes.csv               # Stored notes
│   └── stats.json              # User statistics
│
└── 📁 logs/                    # Application logs (not in repo)
    └── app.log                 # Runtime logs
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)
```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Model Selection
GEMINI_MODEL=gemini-2.0-flash-exp  # or gemini-1.5-flash
```

### Config File (`config.py`)
Customize appearance and behavior:
```python
# Font Settings
FONT_FAMILY = "Segoe UI"
FONT_SIZES = {
    "title": 21,
    "header": 17,
    "body": 15,
    "small": 12
}

# Color Schemes
LIGHT_COLORS = {...}
DARK_COLORS = {...}

# File Paths
DATA_DIR = "data"
LOGS_DIR = "logs"
```

---

## 🛠️ Technologies

### Core Technologies
- **Python 3.8+** - Programming language
- **Tkinter** - GUI framework
- **ttkbootstrap** - Modern UI styling
- **Google Gemini AI** - Intelligent quiz generation

### Key Libraries
|   Library    |  Purpose  | Version |
|--------------|---------|---------|
| ttkbootstrap | Modern UI components | 1.10.1+ |
| pandas | Data handling & CSV operations | 2.0.0+ |
| google-generativeai | AI quiz generation | 0.3.0+ |
| apscheduler | Reminder scheduling | 3.10.0+ |
| pyttsx3 | Text-to-speech | 2.90+ |
| pillow | Image processing | 10.0.0+ |
| python-dotenv | Environment management | 1.0.0+ |

### Architecture
- **MVC Pattern** - Model-View-Controller architecture
- **Modular Design** - Separated concerns in modules/
- **Event-Driven** - Tkinter event loop
- **Async Scheduling** - APScheduler for reminders

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### 1. Fork the Repository
```bash
git clone https://github.com/ASHVIK-SINHA-07/my-first-repo.git
cd my-first-repo
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/AmazingFeature
```

### 3. Make Your Changes
- Follow PEP 8 style guidelines
- Add comments for complex logic
- Update documentation as needed

### 4. Commit Your Changes
```bash
git commit -m "Add: Amazing new feature"
```

### 5. Push to Your Fork
```bash
git push origin feature/AmazingFeature
```

### 6. Open a Pull Request
Go to the repository and click "New Pull Request"

### Contribution Guidelines
- Write clear commit messages
- Add tests for new features
- Update README.md if needed
- Respect existing code style

---

## 📝 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Linting
pylint *.py modules/*.py

# Formatting
black *.py modules/*.py

# Type checking
mypy *.py
```

### Building Executable
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

---

## 🐛 Troubleshooting

### Common Issues

#### Logo not appearing
```bash
# Verify assets folder
ls assets/
# Should show: icon.png, logo.png

# Regenerate logo
python utils/create_logo.py
```

#### Gemini API errors
```bash
# Check API key in .env
cat .env | grep GEMINI_API_KEY

# Test API connection
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('✓ API Connected')"
```

#### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

#### Database issues
```bash
# Clean duplicates
python utils/cleanup_database.py

# Verify data integrity
python utils/verify_notes_section.py
```

---

## 🗺️ Roadmap

### Version 2.0 (Current)
- [x] AI-powered quiz generation
- [x] Dropdown-based reminder scheduling
- [x] Custom logo integration
- [x] Organized project structure
- [x] Comprehensive documentation

### Version 2.1 (Planned)
- [ ] Cloud sync (Google Drive/Dropbox)
- [ ] PDF export for notes
- [ ] Voice-to-text note creation
- [ ] Mobile companion app
- [ ] Collaborative study groups
- [ ] Calendar integration
- [ ] Statistics graphs/charts
- [ ] Custom themes editor

### Version 3.0 (Future)
- [ ] Multi-language support
- [ ] Plugin system
- [ ] Web version
- [ ] Browser extension
- [ ] Advanced AI features
- [ ] Spaced repetition algorithm

---

## 📊 Statistics

- **Lines of Code**: ~2,500+
- **Modules**: 6 core modules
- **Features**: 25+ features
- **UI Components**: 15+ custom widgets
- **Supported Themes**: 2 (Light/Dark)

---

## 🎓 Learning Resources

### Documentation
- [Project Structure Guide](PROJECT_STRUCTURE.md)
- [Reorganization Summary](REORGANIZATION_SUMMARY.md)
- [API Documentation](docs/)

### External Resources
- [Gemini AI Documentation](https://ai.google.dev/docs)
- [ttkbootstrap Documentation](https://ttkbootstrap.readthedocs.io/)
- [Python Tkinter Guide](https://docs.python.org/3/library/tkinter.html)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 ASHVIK SINHA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👨‍💻 Author

**Ashvik Sinha**

- GitHub: [@ASHVIK-SINHA-07](https://github.com/ASHVIK-SINHA-07)
- Email: [Contact via GitHub]
- Project Link: [Smart Study Assistant](https://github.com/ASHVIK-SINHA-07/my-first-repo)

---

## 🙏 Acknowledgments

- **Google Gemini AI** - For powerful AI capabilities
- **ttkbootstrap** - For beautiful UI components
- **Python Community** - For excellent libraries
- **Open Source Contributors** - For inspiration and tools

---

## 💬 Support

### Get Help
- 📫 Open an [Issue](https://github.com/ASHVIK-SINHA-07/my-first-repo/issues)
- 💬 Start a [Discussion](https://github.com/ASHVIK-SINHA-07/my-first-repo/discussions)
- 📖 Check the [Wiki](https://github.com/ASHVIK-SINHA-07/my-first-repo/wiki)

### Star History
If you find this project helpful, please consider giving it a ⭐!

[![Star History](https://img.shields.io/github/stars/ASHVIK-SINHA-07/my-first-repo?style=social)](https://github.com/ASHVIK-SINHA-07/my-first-repo/stargazers)

---

## 📸 Screenshots

<details>
<summary>Click to view screenshots</summary>

### Notes Tab
![Notes Tab](docs/screenshots/notes_tab.png)
*Rich text editor with search, tags, and auto-save*

### Reminders Tab
![Reminders Tab](docs/screenshots/reminders_tab.png)
*Dropdown date/time selection with quick buttons*

### Quiz Tab
![Quiz Tab](docs/screenshots/quiz_tab.png)
*AI-generated questions from your notes*

### Timer Tab
![Timer Tab](docs/screenshots/timer_tab.png)
*Pomodoro timer with session history*

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*XP tracking, badges, and activity overview*

</details>

---

## 🔐 Security

- API keys stored in `.env` (not tracked by git)
- Local data storage only
- No data sent to external servers (except Gemini API for quiz generation)
- Secure handling of user notes

### Reporting Security Issues
Please report security vulnerabilities via email rather than public issues.

---

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Latest Updates (v2.0)
- ✨ Added AI-powered quiz generation
- 🎨 Redesigned reminders tab with dropdowns
- 🖼️ Custom logo and icon integration
- 📁 Reorganized project structure
- 📝 Comprehensive documentation
- ➕ Font size enhancements (+3pt)

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

**Made with ❤️ and ☕ by Ashvik Sinha and team**

[⬆ Back to Top](#-smart-study-assistant)

</div>

---

**Last Updated:** December 2, 2025  
**Version:** 2.0  
**Status:** 🟢 Active Development
