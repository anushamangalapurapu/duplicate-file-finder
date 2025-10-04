# 🔎 Duplicate File Finder - Multi-Folder Edition

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

A powerful, intelligent Python script to find and manage duplicate files across multiple folders with support for regex patterns, parallel processing, and safe backup options.

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Folder Scanning**: Scan multiple folders simultaneously
- **Regex Pattern Support**: Use wildcards and patterns to match folders (e.g., `C:\Users\*\Documents`)
- **Smart Duplicate Detection**: Identifies duplicates based on normalized filename and file size
- **Copy Detection**: Recognizes files with "copy", "(1)", "(2)" patterns as duplicates
- **Cross-Folder Duplicates**: Finds duplicates across different folders and drives

### ⚡ Performance
- **Parallel Processing**: Uses concurrent threads (up to 10) for faster file operations
- **Progress Tracking**: Real-time progress updates during operations
- **Optimized Scanning**: Efficient file traversal and grouping algorithms

### 🛡️ Safety Features
- **Multi-Stage Confirmation**: Multiple prompts before any destructive operation
- **Backup System**: Option to move files to backup before deletion
- **Folder Structure Preservation**: Maintains original directory structure in backups
- **Timestamped Backups**: Each backup includes a timestamp for easy tracking
- **Error Handling**: Comprehensive error reporting and recovery

### 📊 Reporting
- **Interactive Table Display**: Clear visual representation of all files
- **Detailed Statistics**: Shows space savings, duplicate counts, and file groups
- **CSV Export**: Export complete results to CSV for external analysis
- **Backup Reports**: Automatic CSV generation for backed-up files

### 🚫 Ignore Capabilities
- **File Pattern Ignoring**: Ignore specific file patterns (e.g., `*.tmp`, `*.log`)
- **System Files**: Skip common system files (Thumbs.db, .DS_Store)
- **Folder Exclusion**: Exclude entire folders from scanning
- **Flexible Patterns**: Support for wildcards and exact matches

## 📋 Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## 🚀 Installation

### Option 1: Clone Repository
```bash
git clone https://github.com/yourusername/duplicate-file-finder.git
cd duplicate-file-finder
```

### Option 2: Download Script
Download `find_duplicates.py` directly and run it.

## 💻 Usage

### Basic Usage
```bash
python find_duplicates.py
```

### Step-by-Step Guide

#### 1. **Folder Selection**
The script will prompt you to enter folder paths. You have multiple options:

**Single Folder:**
```
Enter folder path(s): C:\Users\John\Documents
```

**Multiple Folders (comma-separated):**
```
Enter folder path(s): C:\Users\John\Documents, D:\Backup, E:\Projects
```

**Regex Patterns:**
```
Enter folder path(s): C:\Users\*\Documents
```
This scans the Documents folder for ALL users.

**Mixed Input:**
```
Enter folder path(s): C:\Folder1, D:\Projects\*, E:\Backup\2024*
```

#### 2. **File Ignore Settings**
Choose whether to ignore specific files:

```
Do you want to ignore any files or folders? yes
Enter files/patterns to ignore: *.tmp, *.log, Thumbs.db, .DS_Store
```

**Ignore Options:**
- `*.tmp` - Ignore all .tmp files
- `*.log` - Ignore all .log files
- `Thumbs.db` - Ignore specific filename
- `C:\Temp` - Ignore entire folder
- Mix multiple patterns: `*.tmp, *.log, C:\Temp, ~*`

#### 3. **View Results**
The script displays:
- Table of all files with duplicate status
- Summary statistics
- Detailed duplicate groups
- Space savings calculation

#### 4. **Export to CSV** (Optional)
```
Would you like to export results to CSV? yes
```
Creates `duplicate_files_report.csv` with complete analysis.

#### 5. **Remove Duplicates** (Optional)
```
Would you like to remove duplicate files? yes
```

**Backup Option:**
```
Do you want to create a backup before removing? yes
Enter the backup folder path: C:\Backup\Duplicates_2024
```

**Final Confirmation:**
```
Type 'CONFIRM' to proceed: CONFIRM
```

## 📖 Examples

### Example 1: Scan Single Folder
```
Enter folder path(s): C:\Users\John\Documents

Do you want to ignore any files? no

Scanning folder: C:\Users\John\Documents
Found 150 files
Duplicates found: 25 files in 10 groups
Space to be saved: 125.50 MB
```

### Example 2: Scan Multiple Folders with Pattern
```
Enter folder path(s): C:\Users\*\Desktop, D:\Backup

Do you want to ignore any files? yes
Enter files/patterns to ignore: *.tmp, Thumbs.db

Expanding pattern: C:\Users\*\Desktop
  ✓ Found: C:\Users\John\Desktop
  ✓ Found: C:\Users\Jane\Desktop
✓ Added: D:\Backup

Scanning 3 folders...
Found 450 files
Ignored 23 files based on ignore patterns
Duplicates found: 78 files in 32 groups
Space to be saved: 2.35 GB
```

### Example 3: Remove Duplicates with Backup
```
Would you like to remove duplicate files? yes

Files to be removed: 45
Space to be freed: 890.25 MB

Do you want to proceed? yes

Do you want to create a backup? yes
Enter backup folder: C:\Backup\Duplicates_20241003

Type 'CONFIRM' to proceed: CONFIRM

Processing 45 duplicate files using parallel threads...
✓ [1/45] Moved to backup: documents\report.pdf
✓ [2/45] Moved to backup: photos\image.jpg
...
✓ [45/45] Moved to backup: videos\clip.mp4

Operation Summary:
✅ Files successfully processed: 45
📦 Files moved to backup: 45
💾 Space freed from source: 890.25 MB
🎉 All duplicate files processed successfully!

✓ Backup CSV report created: C:\Backup\Duplicates_20241003\backup_report_20241003_143022.csv
```

### Example 4: Ignore System and Temp Files
```
Enter folder path(s): C:\, D:\

Do you want to ignore any files? yes
Enter files/patterns to ignore: *.tmp, *.log, *.cache, Thumbs.db, .DS_Store, desktop.ini, C:\Windows, C:\Program Files

🚫 Will ignore 7 pattern(s):
  • *.tmp
  • *.log
  • *.cache
  • Thumbs.db
  • .DS_Store
  • desktop.ini
  • C:\Windows
  • C:\Program Files
```

## 📊 Output Files

### 1. duplicate_files_report.csv
Generated when you choose to export results.

**Columns:**
- Full Path
- File Name
- Base Folder
- Relative Path
- Size (Bytes)
- Size (Readable)
- Status (DUPLICATE/UNIQUE)
- Duplicate Count
- Normalized Name

### 2. backup_report_YYYYMMDD_HHMMSS.csv
Generated when you create a backup.

**Columns:**
- Original Path
- Backup Path
- Relative Path
- Filename
- Size (Bytes)
- Size (Readable)
- Normalized Name
- Backup Date

## 🔧 How It Works

### Duplicate Detection Algorithm

1. **File Normalization**: Removes copy indicators from filenames
   - `document (1).pdf` → `document.pdf`
   - `photo copy.jpg` → `photo.jpg`
   - `report - Copy.docx` → `report.docx`

2. **Grouping**: Files are grouped by (normalized_name, file_size)
   - Same normalized name + same size = potential duplicate

3. **Duplicate Marking**: Groups with 2+ files are marked as duplicates

4. **Preservation**: First file in each group is kept, others are marked for removal

### Parallel Processing

The script uses Python's `concurrent.futures.ThreadPoolExecutor` for:
- Parallel file moving/deletion (up to 10 threads)
- Faster processing of large duplicate sets
- Real-time progress tracking across threads

### Safety Mechanisms

1. **Preview Mode**: Shows what will be kept/removed before action
2. **Multi-Confirmation**: Requires explicit "yes" and "CONFIRM" inputs
3. **Backup Option**: Non-destructive removal via file moving
4. **Error Isolation**: Individual file errors don't stop the entire process
5. **Detailed Logging**: Complete error reporting with file paths

## 🎨 Sample Output

```
===============================================================================================
🔎 DUPLICATE FILE FINDER - MULTI-FOLDER EDITION
===============================================================================================

📁 FOLDER SELECTION
You can specify folders in multiple ways:
  1. Single folder path: C:\Users\Documents
  2. Multiple folders (comma-separated): C:\Folder1, D:\Folder2
  3. Regex pattern: C:\Users\*\Documents
  4. Mix of above: C:\Folder1, D:\Projects\*, E:\Backup

Enter folder path(s): C:\Users\John\Documents, D:\Backup

✓ Added: C:\Users\John\Documents
✓ Added: D:\Backup
📊 Total folders to scan: 2

🚫 FILE IGNORE SETTINGS
Do you want to ignore any files? yes
Enter files/patterns to ignore: *.tmp, Thumbs.db

✓ Will ignore 2 pattern(s):
  • *.tmp
  • Thumbs.db

🔍 Starting scan of 2 folder(s)...

  Scanning: C:\Users\John\Documents
    ✓ Found 125 files
  Scanning: D:\Backup
    ✓ Found 87 files

🚫 Ignored 5 files based on ignore patterns
✓ Scan complete! Found 207 files.

===============================================================================================
📋 FILE DUPLICATE ANALYSIS REPORT
===============================================================================================
+--------------------------------------------+--------------+-----------------+--------------+
| File Path                                  | Size         | Status          | Duplicates   |
+--------------------------------------------+--------------+-----------------+--------------+
| documents\report.pdf                       | 2.45 MB      | 🔴 DUPLICATE    | 2            |
| backup\report.pdf                          | 2.45 MB      | 🔴 DUPLICATE    | 2            |
| photos\vacation.jpg                        | 3.12 MB      | ✅ UNIQUE       | -            |
+--------------------------------------------+--------------+-----------------+--------------+

===============================================================================================
📊 SUMMARY STATISTICS
===============================================================================================
📄 Total files scanned:              207
✅ Unique files:                     185
🔴 Duplicate files:                  22
📁 Duplicate groups:                 11
🗑️  Files that can be removed:       11
💾 Current wasted space:             156.78 MB
💰 Space to be saved if cleaned:    156.78 MB
===============================================================================================
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution
- Additional duplicate detection methods (hash-based)
- GUI interface
- Additional file ignore patterns
- Performance optimizations
- Unit tests
- Documentation improvements

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

- Always review the preview before confirming file deletion
- Use the backup feature for safety
- Test on a small folder first
- The script does not recover deleted files (unless backed up)
- No warranty is provided - use at your own risk

## 🐛 Troubleshooting

### Issue: Script closes immediately after CSV export
**Solution**: This issue has been fixed in the latest version. Make sure you're using the most recent script.

### Issue: Permission errors when scanning system folders
**Solution**: Run the script with administrator privileges or exclude system folders.

### Issue: Large folders take too long to scan
**Solution**: Use the ignore feature to skip unnecessary files/folders.

### Issue: Can't see all duplicate groups
**Solution**: Export to CSV for complete results. The console display is limited to 20 groups for readability.

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the examples in this README

## 🔄 Version History

### v1.0.0 (2024-10-03)
- Initial release
- Multi-folder scanning
- Regex pattern support
- Parallel processing
- Backup functionality
- File ignore capability
- CSV export

## 🙏 Acknowledgments

- Built with Python standard library
- Inspired by the need for efficient duplicate file management
- Community feedback and contributions

---

**Made with ❤️ for efficient file management**

⭐ Star this repo if you find it useful!
