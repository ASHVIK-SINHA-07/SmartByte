# Changelog

All notable changes to Smart Study Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-02

### 🎉 Major Release - Complete UI Overhaul & AI Integration

### Added
- ✨ **AI-Powered Quiz Generation** using Google Gemini AI
  - Intelligent question generation from notes
  - Comprehension-testing questions
  - Multiple question types
- 🎨 **Custom Logo & Branding**
  - Professional 128x128 logo design
  - 64x64 window icon
  - Graduation cap and book symbolism
- 📁 **Organized Project Structure**
  - Created `assets/` folder for images
  - Created `utils/` folder for utility scripts
  - Created `docs/` folder for documentation
  - Separated concerns for better maintainability
- ⏰ **Redesigned Reminders Tab**
  - Dropdown date/time selection (no manual typing)
  - Quick time buttons (1 Hour, 3 Hours, Tomorrow, 1 Week)
  - Message suggestions
  - Active reminder counter badge
  - Two-column layout
- 📝 **Comprehensive Documentation**
  - PROJECT_STRUCTURE.md - Complete project layout
  - REORGANIZATION_SUMMARY.md - Migration details
  - LOGO_INTEGRATION.md - Logo feature documentation
  - AI_QUIZ_FEATURE.md - Quiz system documentation

### Changed
- 🔤 **Font Size Enhancements**
  - Increased all fonts by 3pt for better readability
  - Tab labels: 13pt → 16pt
  - Headers: 14-18pt → 17-21pt
  - Body text: 12pt → 15pt
  - Timer display: 56pt → 59pt
  - Adjusted spacing proportionally
- 🎨 **UI Improvements**
  - Better visual hierarchy
  - Enhanced padding and margins
  - Improved button spacing
  - More polished appearance
- 📦 **Asset Paths**
  - Updated logo.png path to assets/logo.png
  - Updated icon.png path to assets/icon.png
  - Maintained backward compatibility with fallbacks

### Fixed
- 🐛 **Delete Functionality**
  - Fixed notes reappearing after deletion
  - Implemented proper note tracking with `current_note_id`
  - Added `update_note()` function for proper editing
  - Resolved autosave timer conflicts
- 🔄 **Duplicate Notes Prevention**
  - Autosave no longer creates duplicates
  - Proper create vs update logic
  - Note modification tracking
- ⚠️ **Pandas FutureWarning**
  - Fixed dtype incompatibility in storage.py
  - Added proper type handling for CSV columns
  - Ensured string columns stay as strings
- 🔧 **Reminders Module**
  - Added missing `schedule_reminder()` function
  - Added missing `remove_job()` function
  - Added missing `stop_scheduler()` function
  - Fixed AttributeError issues

### Technical
- 🔧 Added Pillow dependency for image processing
- 🔧 Updated import statements for PIL/ImageTk
- 🔧 Improved error handling for asset loading
- 🔧 Enhanced logging throughout application
- 🔧 Better code organization and modularity

---

## [1.5.0] - 2025-11-XX

### Added
- 📊 Dashboard with XP tracking
- 🏆 Badge system for achievements
- 📈 Statistics tracking (notes, quizzes, study time)
- 🎯 Flashcard mode for quizzes
- 🔍 Live search filtering for notes

### Changed
- Improved UI with ttkbootstrap themes
- Enhanced note editor with auto-save
- Better error messages and user feedback

### Fixed
- Various UI glitches
- Search performance issues
- Timer accuracy improvements

---

## [1.0.0] - 2025-10-XX

### 🎉 Initial Release

### Added
- 📝 Basic note-taking functionality
- ⏰ Reminder system with manual time entry
- 🎯 Simple quiz generation
- ⏱️ Study timer with Pomodoro support
- 📊 Basic dashboard
- 🎨 Light/Dark theme support
- 💾 CSV-based data storage
- 📋 Tag system for notes
- 🔍 Search functionality
- ⌨️ Keyboard shortcuts

### Features
- Create, read, update, delete notes
- Set reminders with date/time
- Generate quizzes from notes
- Track study sessions
- View activity history
- Organize with tags
- Theme customization

---

## Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

### Version History
- **2.0.0** - Major UI overhaul, AI integration, project reorganization
- **1.5.0** - Dashboard enhancements, flashcards, statistics
- **1.0.0** - Initial release with core features

---

## Upgrade Guide

### From 1.x to 2.0

#### Data Migration
Your existing data is automatically compatible:
- Notes stored in `data/notes.csv` - no changes needed
- Stats in `data/stats.json` - automatically updated

#### New Features to Explore
1. Try the new AI quiz generation (Quiz tab)
2. Check out the redesigned Reminders tab
3. Notice the new logo in the header
4. Enjoy larger, more readable fonts

#### Breaking Changes
None! Version 2.0 is fully backward compatible.

---

## Upcoming Features

### Version 2.1 (Q1 2026)
- [ ] Cloud sync integration
- [ ] PDF export for notes
- [ ] Voice-to-text notes
- [ ] Calendar view
- [ ] Advanced statistics
- [ ] Custom themes editor

### Version 3.0 (Q2 2026)
- [ ] Multi-language support
- [ ] Plugin system
- [ ] Web version
- [ ] Mobile app
- [ ] Collaborative features
- [ ] Advanced AI capabilities

---

## Deprecation Notices

### None Currently
All features from version 1.x are maintained in 2.0.

---

## Contributors

Thanks to everyone who has contributed to this project!

- **Ashvik Sinha** - Creator and maintainer
- **GitHub Copilot** - AI pair programmer
- **Open Source Community** - Inspiration and support

---

## Support

For questions, issues, or feature requests:
- 📫 [Open an Issue](https://github.com/ASHVIK-SINHA-07/my-first-repo/issues)
- 💬 [Start a Discussion](https://github.com/ASHVIK-SINHA-07/my-first-repo/discussions)

---

**[⬆ Back to Top](#changelog)**
