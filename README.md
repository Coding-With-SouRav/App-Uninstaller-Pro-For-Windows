## DEMO IMAGES

<img width="1918" height="1022" alt="image" src="https://github.com/user-attachments/assets/8e35f53e-a19a-4352-a6da-76415523143c" />

## 🎯 **Core Functionality**
- **Bulk Uninstallation**: Select and uninstall multiple applications simultaneously
- **Registry Integration**: Reads installed applications from Windows Registry (HKLM, HKCU, WOW6432Node)
- **Complete Removal**: Removes both program files and registry entries

## 🖼️ **UI/UX Features**
- **Dark Theme**: Uses ttkbootstrap with "darkly" theme
- **Icon Display**: Extracts and shows application icons from EXE files
- **Tooltip Support**: Hover tooltips show installation paths
- **Checkbox Selection**: Visual checkboxes (✅/⬜) for selecting apps
- **Responsive Layout**: Scrollable treeview with custom styling

## 📊 **Application Information Display**
- **Comprehensive List**: Shows all installed applications
- **Detailed Columns**:
  - Application Name (with icon)
  - Estimated Size
  - Selection status
  - Installation location (hidden but accessible via tooltip)
- **Smart Sorting**: Alphabetically sorted application names

## 🛠️ **Technical Features**
- **Icon Extraction**: Uses Win32 API to extract icons from EXE/ICO files
- **Fallback System**: Shows question mark icons for missing app icons
- **Resource Management**: Proper handling of bundled resources for PyInstaller
- **Configuration Persistence**: Saves window size/position between sessions

## ⚡ **User Interaction**
- **One-Click Selection**: Click anywhere on a row to select/deselect
- **Refresh Capability**: Reload application list with refresh button
- **Safety Warnings**: Clear warnings about irreversible uninstallation
- **Confirmation Dialogs**: Asks for confirmation before uninstalling

## 🚀 **Advanced Capabilities**
- **Multi-architecture Support**: Handles both 32-bit and 64-bit applications
- **Location Detection**: Automatically finds installation paths
- **Size Estimation**: Shows application size in MB
- **Robust Error Handling**: Continues operation even if some apps fail to uninstall

## 🔧 **System Integration**
- **Windows Registry Access**: Reads uninstall information from registry
- **Process Execution**: Runs official uninstaller commands
- **File System Cleanup**: Removes leftover installation directories
- **Admin Rights Ready**: Structured for potential administrator privileges

## 🎨 **Visual Enhancements**
- **Custom Tooltips**: Yellow tooltips with custom styling
- **High DPI Support**: Proper icon scaling and rendering
- **Modern Buttons**: Themed buttons with icons for actions
- **Professional Layout**: Clean, organized interface with warning labels

This is essentially a **power user's uninstaller** that provides more control and visibility than the standard Windows "Add/Remove Programs" interface, with the added convenience of bulk operations.
