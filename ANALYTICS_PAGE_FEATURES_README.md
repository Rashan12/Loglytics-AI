# 📊 Analytics Page - Features & Functions Documentation

**Last Updated:** November 6, 2025  
**Page Route:** `/dashboard/analytics`  
**Status:** ✅ **FULLY FUNCTIONAL**

---

## 🎯 **Overview**

The Analytics Dashboard provides comprehensive insights into log data and system performance. It offers real-time analytics, customizable time ranges, log file filtering, and data export capabilities.

---

## ✨ **Core Features**

### **1. Time Range Selection**
- **Purpose:** Filter analytics data by time period
- **Options:**
  - `1h` - Last Hour
  - `24h` - Last 24 Hours (default)
  - `7d` - Last 7 Days
  - `30d` - Last 30 Days
- **Functionality:**
  - Dropdown selector with clock icon
  - Automatically refreshes data when changed
  - Styled with glassmorphic design matching system theme
- **Backend Integration:**
  - Sends `time_range` parameter to `/api/v1/analytics/dashboard`
  - Backend filters data based on selected range

### **2. Log File Filtering**
- **Purpose:** Analyze specific log files or view aggregated data
- **Features:**
  - **File Selector Dropdown:**
    - Searchable list of all uploaded log files
    - Shows file metadata (entry count, file type)
    - "All Log Files" option for aggregated view
    - Visual selection indicator (checkmark)
  - **Search Functionality:**
    - Real-time search filtering
    - Case-insensitive filename matching
    - Search icon indicator
  - **File Information Display:**
    - Filename
    - Entry count
    - File type (.log, .txt, .csv, .json)
- **Backend Integration:**
  - Sends `log_file_id` parameter when a specific file is selected
  - Backend returns analytics for that specific file
  - Omitting `log_file_id` returns aggregated analytics

### **3. Summary Statistics Cards**

Four key metric cards displayed in a responsive grid:

#### **a) Total Logs**
- **Metric:** Total number of log entries analyzed
- **Icon:** FileText
- **Color Scheme:** Blue gradient
- **Data Source:** `analyticsData.total_logs`
- **Display:** Formatted with thousand separators (e.g., "1,234")

#### **b) Error Rate**
- **Metric:** Percentage of error-level logs
- **Icon:** TrendingDown
- **Color Scheme:** Red gradient
- **Data Source:** `analyticsData.error_rate`
- **Display:** Percentage with 1 decimal place (e.g., "2.5%")
- **Calculation:** (ERROR + CRITICAL logs) / Total logs × 100

#### **c) Average Response Time**
- **Metric:** Average system response time
- **Icon:** TrendingUp
- **Color Scheme:** Green gradient
- **Data Source:** `analyticsData.avgResponseTime`
- **Display:** Milliseconds (e.g., "150ms") or "N/A" if unavailable

#### **d) Active Services**
- **Metric:** Number of active services/projects
- **Icon:** Activity
- **Color Scheme:** Purple gradient
- **Data Source:** `analyticsData.activeServices` or `analyticsData.active_projects`
- **Display:** Integer count

**Card Design Features:**
- Glassmorphic styling with backdrop blur
- Gradient accent backgrounds
- Smooth animations on load
- Responsive grid layout (1 column mobile, 2 tablet, 4 desktop)
- Hover effects and visual feedback

### **4. Data Export**
- **Purpose:** Download analytics data for external analysis
- **Format:** JSON file
- **Filename:** `analytics-{timeRange}-{date}.json`
- **Content:** Complete analytics data object
- **Functionality:**
  - Gradient button with download icon
  - Automatic file download
  - Includes all current filters (time range, log file)
  - Preserves data structure for easy parsing

### **5. Loading States**
- **Purpose:** Provide user feedback during data fetching
- **Features:**
  - Animated spinner with theme-appropriate colors
  - Loading message: "Loading analytics data..."
  - 10-second timeout to prevent indefinite loading
  - Smooth transitions between states

### **6. Empty State**
- **Purpose:** Guide users when no data is available
- **Features:**
  - Professional empty state design
  - TrendingUp icon with gradient background
  - Clear messaging: "No Analytics Data"
  - Call-to-action button: "Upload Log Files"
  - Redirects to `/dashboard/log-files` page

### **7. Analytics Details Panel**
- **Purpose:** Display additional metadata about current analytics view
- **Information Shown:**
  - Current time range
  - Selected log file (if any)
  - Number of data points
- **Design:**
  - Glassmorphic card matching system theme
  - Icon indicators for each piece of information
  - Responsive layout

---

## 🔌 **Backend Integration**

### **API Endpoints Used**

#### **1. GET `/api/v1/analytics/dashboard`**
- **Purpose:** Fetch analytics dashboard data
- **Query Parameters:**
  - `time_range` (required): `1h`, `24h`, `7d`, or `30d`
  - `log_file_id` (optional): Specific log file UUID
- **Authentication:** Bearer token required
- **Response Structure:**
  ```json
  {
    "total_logs": 1234,
    "error_rate": 2.5,
    "active_projects": 5,
    "ai_insights": 10,
    "recent_analyses": [...],
    "total_analyses": 10
  }
  ```

#### **2. GET `/api/v1/logs/files`**
- **Purpose:** Fetch list of available log files
- **Authentication:** Bearer token required
- **Response Structure:**
  ```json
  {
    "items": [
      {
        "id": "uuid",
        "filename": "example.log",
        "file_size": 1024,
        "file_type": ".log",
        "upload_status": "completed",
        "created_at": "2025-11-06T...",
        "entry_count": 100
      }
    ]
  }
  ```

### **Data Flow**

1. **Page Load:**
   - Fetches log files list
   - Fetches analytics data with default time range (24h)

2. **Time Range Change:**
   - Updates `timeRange` state
   - Triggers `fetchAnalytics()` with new time range
   - Backend filters data accordingly

3. **Log File Selection:**
   - Updates `selectedLogFile` state
   - Triggers `fetchAnalytics()` with `log_file_id` parameter
   - Backend returns file-specific analytics

4. **Export:**
   - Fetches current analytics data
   - Creates JSON blob
   - Triggers browser download

---

## 🎨 **Design System Integration**

### **Theme Support**
- **Dark Mode:**
  - Background: `#0A0E1A`
  - Cards: `#1A1F3A/60` with `#2E3A5C/50` borders
  - Text: `#F9FAFB` (primary), `#94A3B8` (secondary)
  - Accents: `#2E9BFF` (blue), `#8B5CF6` (purple)

- **Light Mode:**
  - Background: `gray-50`
  - Cards: `white/80` with `gray-200` borders
  - Text: `gray-900` (primary), `gray-600` (secondary)
  - Accents: Blue and purple variants

### **Design Elements**
- **Glassmorphism:** Frosted glass effect on cards
- **Gradient Accents:** Blue-to-purple gradients on buttons and icons
- **Smooth Animations:** Framer Motion for transitions
- **Responsive Layout:** Adapts to sidebar collapse state
- **Consistent Spacing:** Matches other dashboard pages

---

## 🔄 **State Management**

### **Local State**
- `timeRange`: Current time range selection
- `analyticsData`: Fetched analytics data
- `loading`: Loading state indicator
- `logFiles`: List of available log files
- `selectedLogFile`: Currently selected file ID
- `showFileSelector`: Dropdown visibility
- `searchQuery`: File search filter

### **External State**
- `useUIStore`: Sidebar collapse state
- `useTheme`: Dark/light mode detection

---

## 🛠️ **Technical Implementation**

### **Dependencies**
- `framer-motion`: Animations
- `next-themes`: Theme management
- `lucide-react`: Icons
- `zustand`: State management (via stores)

### **Key Functions**

#### **`fetchLogFiles()`**
- Fetches list of log files on component mount
- Handles authentication token
- Updates `logFiles` state

#### **`fetchAnalytics()`**
- Fetches analytics data based on current filters
- Handles loading states
- Includes 10-second timeout
- Updates `analyticsData` state

#### **`handleExport()`**
- Creates JSON blob from current analytics data
- Triggers browser download
- Generates filename with timestamp

---

## 📋 **User Workflow**

1. **Access Analytics Page:**
   - Navigate to `/dashboard/analytics`
   - Page loads with default 24h time range

2. **View Summary Metrics:**
   - See four key statistics cards
   - Metrics update based on available data

3. **Filter by Time Range:**
   - Select from dropdown: 1h, 24h, 7d, 30d
   - Data automatically refreshes

4. **Filter by Log File (Optional):**
   - Click "Select Log File" button
   - Search or browse available files
   - Select specific file or "All Log Files"
   - Data updates to show file-specific analytics

5. **Export Data (Optional):**
   - Click "Export Data" button
   - JSON file downloads automatically

---

## 🚀 **Future Enhancements (Potential)**

Based on available analytics components, potential additions:
- **Chart Visualizations:**
  - Log Timeline (line chart)
  - Log Level Distribution (pie chart)
  - Top Errors (bar chart)
  - Error Trends (line chart with anomalies)
  - Performance Metrics (multi-line chart)
  - Anomaly Scatter Plot
  - Service Breakdown (bar chart)

- **Advanced Features:**
  - Real-time auto-refresh
  - Custom date range picker
  - Multiple log file selection
  - Export to PDF/CSV formats
  - AI-powered insights panel
  - Anomaly detection alerts

---

## ✅ **Testing Checklist**

- [x] Page loads without errors
- [x] Time range selector works
- [x] Log file selector displays files
- [x] Log file search filters correctly
- [x] Analytics data fetches successfully
- [x] Summary cards display correct data
- [x] Export functionality works
- [x] Loading states display properly
- [x] Empty state shows when no data
- [x] Dark/light mode works correctly
- [x] Responsive layout adapts to sidebar
- [x] All animations are smooth
- [x] Backend integration functional

---

## 📝 **Notes**

- The page uses the same design system as Dashboard, Projects, and other pages
- All backend API calls include authentication tokens
- Error handling is implemented for network failures
- The page gracefully handles missing or incomplete data
- All existing features are preserved and functional

---

## 🔗 **Related Files**

- **Page Component:** `frontend/src/app/dashboard/analytics/page.tsx`
- **Backend Endpoint:** `backend/app/api/v1/endpoints/analytics.py`
- **Analytics Service:** `frontend/src/services/analytics-service.ts`
- **Analytics Store:** `frontend/src/store/analytics-store.ts`
- **Analytics Components:** `frontend/src/components/analytics/`

---

**Documentation Version:** 1.0  
**Maintained By:** Development Team

