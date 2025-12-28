# KNOWLEDGE BASE INTERFACE IMPROVEMENT PLAN
## Control Center Enhancement - KB Management System

**Created:** November 9, 2025 19:15
**Planner:** Ziggie (Top-Level Strategic Agent)
**Status:** PLANNING PHASE
**Context:** While L2 workers fix 18 Control Center issues, planning next enhancement

---

## CURRENT STATE ANALYSIS

### Backend API (COMPLETE - 450 lines)

**File:** `C:\Ziggie\control-center\control-center\backend\api\knowledge.py`

**Endpoints Available:**
```python
GET  /api/knowledge/stats           # Overall KB statistics
GET  /api/knowledge/files           # List files (pagination, filtering)
POST /api/knowledge/search          # Search content
GET  /api/knowledge/creators        # YouTube creator database
POST /api/knowledge/scan            # Trigger manual scan
GET  /api/knowledge/jobs/history    # Scan job history
GET  /api/knowledge/recent          # Recent files (limit param)
```

**Features:**
- Automatic file scanning on startup
- Manual scan triggers
- Full-text search across documents
- YouTube creator metadata extraction
- Job tracking and history
- Pagination and filtering support

**Paths Configured:**
- Knowledge Base: `C:/meowping-rts/ai-agents/knowledge-base`
- Auto-scans on service start
- Background job processing

### Frontend (PLACEHOLDER - 39 lines)

**File:** `C:\Ziggie\control-center\control-center\frontend\src\components\Knowledge\KnowledgePage.jsx`

**Current State:**
```jsx
export const KnowledgePage = () => {
  return (
    <Box>
      <Typography variant="h4">Knowledge Base</Typography>
      <Alert severity="info">
        Knowledge base management interface coming soon...
      </Alert>
      {/* Lists planned features but no implementation */}
    </Box>
  );
};
```

**Frontend API Client (INCOMPLETE):**
```javascript
// Only 3 methods implemented
export const knowledgeAPI = {
  getRecent: (limit = 10) => api.get(`/knowledge/recent?limit=${limit}`),
  search: (query) => api.post('/knowledge/search', { query }),
  getStats: () => api.get('/knowledge/stats'),
  // Missing: getFiles, getCreators, triggerScan, getJobHistory
};
```

### Gap Analysis

**MISSING:**
1. ❌ File browser with pagination
2. ❌ Search interface with results display
3. ❌ KB statistics dashboard
4. ❌ Creator database browser
5. ❌ Manual scan trigger interface
6. ❌ Job history viewer
7. ❌ File preview/viewer
8. ❌ File type filtering
9. ❌ Date range filtering
10. ❌ File metadata display

**AVAILABLE PATTERNS (from other pages):**
- ✅ Grid layout (Dashboard, ServicesPage, SystemPage)
- ✅ Card components (Dashboard)
- ✅ Search TextField (ServicesPage)
- ✅ Loading states (LoadingSpinner)
- ✅ Error handling (Alert + Snackbar)
- ✅ Refresh button pattern (SystemPage)
- ✅ Data tables (ProcessList, PortScanner)
- ✅ Promise.allSettled for parallel API calls

---

## PROPOSED INTERFACE DESIGN

### Layout Structure

**Page Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Knowledge Base                     [Scan] [Refresh] │
├─────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │ Total   │ │ Docs    │ │ Videos  │ │ Last    │   │
│ │ Files   │ │         │ │         │ │ Scan    │   │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
├─────────────────────────────────────────────────────┤
│ [Search: ____________]  [Type: All ▼] [Sort: ▼]   │
├─────────────────────────────────────────────────────┤
│ ┌───────────────────────┐ ┌─────────────────────┐ │
│ │ FILE BROWSER         │ │ FILE DETAILS        │ │
│ │                      │ │                     │ │
│ │ [Table with files]   │ │ [Metadata + Preview]│ │
│ │                      │ │                     │ │
│ │ [Pagination]         │ │                     │ │
│ └───────────────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────┤
│ ┌───────────────────────┐ ┌─────────────────────┐ │
│ │ YOUTUBE CREATORS     │ │ RECENT SCANS        │ │
│ │                      │ │                     │ │
│ │ [Creator list]       │ │ [Job history]       │ │
│ └───────────────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **KnowledgeStats** (Statistics Cards)

**Data Source:** `GET /api/knowledge/stats`

**Display:**
- Total Files count
- Documents count (by type)
- Videos count
- Last Scan timestamp
- Total Size

**Design:** 4-5 Card components in Grid (similar to SystemPage Quick Stats)

#### 2. **KnowledgeSearch** (Search & Filter Bar)

**Components:**
- Search TextField (with SearchIcon)
- Type Filter Dropdown (All, Documents, Videos, Code, Transcripts)
- Sort Dropdown (Name, Date, Size, Type)
- Date Range Picker (optional)

**API:** `POST /api/knowledge/search`

**Design:** Horizontal bar above file browser (similar to ServicesPage search)

#### 3. **FileBrowser** (Main File Table)

**Data Source:** `GET /api/knowledge/files?page=1&limit=20&type=&sort=`

**Columns:**
- Icon (by file type)
- Filename
- Type (badge)
- Size
- Created Date
- Actions (View, Download)

**Features:**
- Pagination (20 items per page)
- Row selection highlights
- Click row to show details in sidebar
- Sortable columns

**Design:** Material-UI DataGrid or custom Table component

#### 4. **FileDetails** (Sidebar Panel)

**Display When File Selected:**
- File icon (large)
- Filename
- Full path
- File type badge
- Size
- Created/Modified dates
- Preview (if text/markdown)
- Metadata (for videos: creator, duration, transcript status)
- Action buttons (Download, Open Location)

**Design:** Card component with vertical layout

#### 5. **CreatorBrowser** (YouTube Creators)

**Data Source:** `GET /api/knowledge/creators`

**Display:**
- Creator name
- Video count
- Last video date
- Total transcripts

**Design:** Simple list in Card component

#### 6. **ScanHistory** (Job History)

**Data Source:** `GET /api/knowledge/jobs/history`

**Display:**
- Scan timestamp
- Status (success/failed)
- Files scanned
- Duration
- Trigger (auto/manual)

**Design:** Timeline or list in Card component

#### 7. **ScanTrigger** (Manual Scan Button)

**API:** `POST /api/knowledge/scan`

**Location:** Header next to Refresh button

**Behavior:**
- Click → POST request
- Show loading state
- Snackbar notification on success/failure
- Auto-refresh page after scan completes

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation (4-6 hours)

**1.1 - Extend API Client** (30 min)
**File:** `frontend/src/services/api.js`

**Add Missing Methods:**
```javascript
export const knowledgeAPI = {
  // Existing
  getRecent: (limit = 10) => api.get(`/knowledge/recent?limit=${limit}`),
  search: (query) => api.post('/knowledge/search', { query }),
  getStats: () => api.get('/knowledge/stats'),

  // NEW
  getFiles: (page = 1, limit = 20, type = '', sort = 'name') =>
    api.get(`/knowledge/files?page=${page}&limit=${limit}&type=${type}&sort=${sort}`),
  getCreators: () => api.get('/knowledge/creators'),
  triggerScan: () => api.post('/knowledge/scan'),
  getJobHistory: (limit = 10) => api.get(`/knowledge/jobs/history?limit=${limit}`),
};
```

**1.2 - Create Base Components** (2 hours)

**Files to Create:**
```
frontend/src/components/Knowledge/
├── KnowledgePage.jsx          (REPLACE - main container)
├── KnowledgeStats.jsx         (NEW - statistics cards)
├── KnowledgeSearch.jsx        (NEW - search/filter bar)
├── FileBrowser.jsx            (NEW - file table)
├── FileDetails.jsx            (NEW - details sidebar)
├── CreatorBrowser.jsx         (NEW - creator list)
├── ScanHistory.jsx            (NEW - job history)
└── utils/
    └── fileIcons.js           (NEW - file type icons mapping)
```

**1.3 - Build KnowledgeStats Component** (1.5 hours)

**Features:**
- Fetch stats from API
- Display in 4 Card components
- Loading state
- Auto-refresh every 60 seconds (optional)
- Color-coded stats (primary for total, secondary for types)

**Pattern:** Similar to Dashboard Agent Summary

**1.4 - Build KnowledgeSearch Component** (1.5 hours)

**Features:**
- Search TextField with debounce (500ms)
- Type filter Select dropdown
- Sort Select dropdown
- Emit events to parent on filter changes
- Clear button when search active

**Pattern:** Similar to ServicesPage search

### Phase 2: Core Functionality (6-8 hours)

**2.1 - Build FileBrowser Component** (3-4 hours)

**Features:**
- Material-UI Table with pagination
- Column headers with sort icons
- Row hover effects
- Row click selection
- Empty state message
- File type badges (Chip components)
- Size formatting (bytes → KB/MB)
- Date formatting (relative or absolute)

**Data Flow:**
```javascript
const [files, setFiles] = useState([]);
const [page, setPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);
const [selectedFile, setSelectedFile] = useState(null);
const [filters, setFilters] = useState({ type: '', sort: 'name' });

useEffect(() => {
  loadFiles(page, filters);
}, [page, filters]);
```

**2.2 - Build FileDetails Component** (2-3 hours)

**Features:**
- Show selected file metadata
- File type icon (large)
- Badge for file type
- Metadata in key-value list
- Preview pane for text files (first 500 chars)
- Video metadata display (creator, duration, transcript status)
- Action buttons (Download)
- Empty state when no file selected

**Conditional Rendering:**
```javascript
if (!selectedFile) {
  return <Typography color="text.secondary">Select a file to view details</Typography>;
}

// Display metadata based on file type
{selectedFile.type === 'video' && (
  <VideoMetadata video={selectedFile.metadata} />
)}
```

**2.3 - Build File Type Icon System** (30 min)

**File:** `frontend/src/components/Knowledge/utils/fileIcons.js`

**Mapping:**
```javascript
import {
  Description, VideoLibrary, Code, Article,
  PictureAsPdf, Image, Folder, InsertDriveFile
} from '@mui/icons-material';

export const getFileIcon = (fileType) => {
  const iconMap = {
    'document': Description,
    'video': VideoLibrary,
    'code': Code,
    'transcript': Article,
    'pdf': PictureAsPdf,
    'image': Image,
    'folder': Folder,
  };
  return iconMap[fileType] || InsertDriveFile;
};

export const getFileColor = (fileType) => {
  const colorMap = {
    'document': 'primary',
    'video': 'secondary',
    'code': 'success',
    'transcript': 'info',
  };
  return colorMap[fileType] || 'default';
};
```

**2.4 - Integrate Search Functionality** (1 hour)

**Features:**
- Connect KnowledgeSearch to FileBrowser
- POST search query to API
- Display search results in FileBrowser
- Highlight search matches (optional)
- "Showing X results for 'query'" message
- Clear search button

### Phase 3: Additional Features (4-6 hours)

**3.1 - Build CreatorBrowser Component** (2 hours)

**Features:**
- Fetch creators from API
- Display in list/grid
- Show creator name, video count, last video date
- Click to filter FileBrowser by creator
- Empty state for no creators

**Design:** Card with scrollable list, similar to RecentActivity

**3.2 - Build ScanHistory Component** (2 hours)

**Features:**
- Fetch job history from API
- Display in timeline or table
- Status indicators (success: green, failed: red)
- Click to view job details (files scanned, errors)
- Auto-update when new scan triggered

**Design:** Card with Timeline component or simple list

**3.3 - Implement Manual Scan Trigger** (1 hour)

**Features:**
- Button in page header
- POST to /api/knowledge/scan
- Loading state while scanning
- Snackbar notification on completion
- Refresh FileBrowser and Stats after scan
- Disable button during scan

**Pattern:** Similar to Refresh button in SystemPage

**3.4 - Add Refresh Functionality** (30 min)

**Features:**
- Refresh button in header
- Reload all data (stats, files, creators, history)
- Loading state
- Success notification

### Phase 4: Polish & UX (2-3 hours)

**4.1 - Error Handling** (1 hour)

**Features:**
- Alert component for API errors
- Retry button for failed requests
- Fallback UI for missing data
- Connection status indicator

**4.2 - Loading States** (30 min)

**Features:**
- LoadingSpinner for initial load
- Skeleton components for stats cards
- Progress bar during scan
- Inline loaders for pagination

**4.3 - Responsive Design** (1 hour)

**Features:**
- Mobile-friendly layout (stack cards vertically)
- Responsive Grid sizing (xs, md, lg)
- Collapsible FileDetails sidebar on mobile
- Touch-friendly buttons and spacing

**4.4 - Accessibility** (30 min)

**Features:**
- ARIA labels for buttons
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

---

## FILE STRUCTURE

```
frontend/src/
├── services/
│   └── api.js                           (EXTEND - add KB methods)
├── components/
│   └── Knowledge/
│       ├── KnowledgePage.jsx            (REPLACE - 300+ lines)
│       ├── KnowledgeStats.jsx           (NEW - 100 lines)
│       ├── KnowledgeSearch.jsx          (NEW - 120 lines)
│       ├── FileBrowser.jsx              (NEW - 250 lines)
│       ├── FileDetails.jsx              (NEW - 200 lines)
│       ├── CreatorBrowser.jsx           (NEW - 150 lines)
│       ├── ScanHistory.jsx              (NEW - 150 lines)
│       └── utils/
│           └── fileIcons.js             (NEW - 50 lines)
```

**Total New Code:** ~1,320 lines
**Files Modified:** 1
**Files Created:** 8

---

## TECHNICAL DECISIONS

### State Management

**Approach:** React useState + useEffect (no Redux/Context needed)

**Rationale:**
- KB state is page-local (not shared)
- Simple async data fetching
- Matches existing Control Center patterns

### UI Framework

**Approach:** Material-UI components (existing dependency)

**Components to Use:**
- Grid, Box, Typography
- Card (custom wrapper component)
- Table, TableRow, TableCell
- TextField, Select, Button
- Chip (for file type badges)
- Timeline (for scan history)
- Snackbar, Alert (for notifications)

### Data Fetching

**Approach:** Promise.allSettled for parallel initial load

**Example:**
```javascript
const loadKnowledgeData = async () => {
  const [statsRes, filesRes, creatorsRes, historyRes] =
    await Promise.allSettled([
      knowledgeAPI.getStats(),
      knowledgeAPI.getFiles(1, 20),
      knowledgeAPI.getCreators(),
      knowledgeAPI.getJobHistory(5),
    ]);
  // Handle settled promises...
};
```

### Pagination

**Approach:** Server-side pagination (API supports it)

**Pattern:**
```javascript
const [page, setPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);

const handlePageChange = (newPage) => {
  setPage(newPage);
  // Triggers useEffect to reload files
};
```

### Search Debouncing

**Approach:** useEffect with timeout cleanup

**Pattern:**
```javascript
useEffect(() => {
  const timer = setTimeout(() => {
    if (searchQuery.length >= 3) {
      performSearch(searchQuery);
    }
  }, 500);
  return () => clearTimeout(timer);
}, [searchQuery]);
```

---

## API INTEGRATION DETAILS

### Stats Endpoint

**Request:**
```
GET /api/knowledge/stats
```

**Response:**
```json
{
  "total_files": 142,
  "by_type": {
    "document": 45,
    "video": 12,
    "transcript": 12,
    "code": 73
  },
  "total_size_bytes": 52428800,
  "last_scan": "2025-01-09T19:00:00Z",
  "scan_status": "completed"
}
```

### Files Endpoint

**Request:**
```
GET /api/knowledge/files?page=1&limit=20&type=document&sort=date_desc
```

**Response:**
```json
{
  "files": [
    {
      "id": "abc123",
      "filename": "PROTOCOL_v1.3.md",
      "path": "/knowledge-base/protocols/PROTOCOL_v1.3.md",
      "type": "document",
      "size_bytes": 45231,
      "created_at": "2025-01-09T18:30:00Z",
      "modified_at": "2025-01-09T18:35:00Z",
      "metadata": {
        "extension": ".md",
        "mime_type": "text/markdown"
      }
    }
  ],
  "total": 142,
  "page": 1,
  "pages": 8,
  "limit": 20
}
```

### Search Endpoint

**Request:**
```
POST /api/knowledge/search
Content-Type: application/json

{
  "query": "hierarchical deployment",
  "type": "",  // optional filter
  "limit": 50
}
```

**Response:**
```json
{
  "results": [
    {
      "file": { /* file object */ },
      "matches": [
        {
          "line": 42,
          "context": "...hierarchical deployment architecture..."
        }
      ],
      "score": 0.95
    }
  ],
  "query": "hierarchical deployment",
  "total_results": 12
}
```

### Creators Endpoint

**Request:**
```
GET /api/knowledge/creators
```

**Response:**
```json
{
  "creators": [
    {
      "name": "AI Explained",
      "video_count": 8,
      "last_video_date": "2025-01-08T10:00:00Z",
      "total_transcripts": 8
    }
  ]
}
```

### Scan Trigger

**Request:**
```
POST /api/knowledge/scan
```

**Response:**
```json
{
  "job_id": "scan_20250109_191500",
  "status": "started",
  "message": "Knowledge base scan initiated"
}
```

### Job History

**Request:**
```
GET /api/knowledge/jobs/history?limit=10
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "scan_20250109_191500",
      "started_at": "2025-01-09T19:15:00Z",
      "completed_at": "2025-01-09T19:15:42Z",
      "status": "completed",
      "files_scanned": 142,
      "files_added": 3,
      "errors": []
    }
  ]
}
```

---

## EFFORT ESTIMATES

### By Phase

| Phase | Description | Estimated Hours |
|-------|-------------|-----------------|
| Phase 1 | Foundation (API + Base Components) | 4-6 hours |
| Phase 2 | Core Functionality (Browser + Details) | 6-8 hours |
| Phase 3 | Additional Features (Creators + History) | 4-6 hours |
| Phase 4 | Polish & UX | 2-3 hours |
| **TOTAL** | **Full Implementation** | **16-23 hours** |

### By Component

| Component | Lines of Code | Estimated Hours |
|-----------|---------------|-----------------|
| API Client Extensions | 30 lines | 0.5 hours |
| KnowledgePage (main) | 300 lines | 3 hours |
| KnowledgeStats | 100 lines | 1.5 hours |
| KnowledgeSearch | 120 lines | 1.5 hours |
| FileBrowser | 250 lines | 3-4 hours |
| FileDetails | 200 lines | 2-3 hours |
| CreatorBrowser | 150 lines | 2 hours |
| ScanHistory | 150 lines | 2 hours |
| File Icons Utility | 50 lines | 0.5 hours |
| Testing & Polish | - | 2-3 hours |
| **TOTAL** | **~1,350 lines** | **18-22 hours** |

---

## DEPLOYMENT STRATEGY

### Option 1: Incremental Implementation (RECOMMENDED)

**Approach:** Build and deploy in phases

**Benefits:**
- Deliver value incrementally
- Get user feedback early
- Adjust based on real usage
- Less risk

**Timeline:**
1. **Week 1:** Phase 1 + Phase 2 (stats + file browser)
2. **Week 2:** Phase 3 (creators + history)
3. **Week 3:** Phase 4 (polish)

### Option 2: Complete Build

**Approach:** Build all features before deployment

**Benefits:**
- Cohesive user experience
- All features available immediately
- Single testing cycle

**Timeline:**
- **Sprint:** 16-23 hours over 3-5 days

### Option 3: MVP First

**Approach:** Build minimal viable product (stats + file browser only)

**Features:**
- KnowledgeStats
- FileBrowser with pagination
- Basic search
- Refresh button

**Timeline:**
- **MVP:** 8-12 hours (Phase 1 + partial Phase 2)
- **Enhancement:** Add other features later

---

## TESTING STRATEGY

### Component Testing

**What to Test:**
- Each component renders without errors
- Loading states display correctly
- Error states display correctly
- Empty states display correctly
- User interactions trigger correct actions

**Tools:** React Testing Library (already in project)

### Integration Testing

**What to Test:**
- API calls succeed with valid responses
- API calls handle errors gracefully
- Pagination works correctly
- Search returns correct results
- Scan trigger updates data

**Tools:** Mock API responses with MSW or axios-mock-adapter

### E2E Testing (Optional)

**What to Test:**
- User can browse files
- User can search files
- User can trigger scan
- User can view file details

**Tools:** Cypress or Playwright (if Control Center uses them)

---

## RISK ASSESSMENT

### Technical Risks

**1. API Backend Changes**
- **Risk:** Backend API might not match documentation
- **Mitigation:** Verify all endpoints before building UI
- **Severity:** Medium

**2. Large Dataset Performance**
- **Risk:** Thousands of files could slow pagination/search
- **Mitigation:** Server-side pagination, virtual scrolling if needed
- **Severity:** Low (API handles this)

**3. File Preview Security**
- **Risk:** Previewing arbitrary files could expose sensitive data
- **Mitigation:** Only preview safe file types (text, markdown)
- **Severity:** Low

### UX Risks

**1. Complex Interface**
- **Risk:** Too many features could overwhelm users
- **Mitigation:** Start with MVP, add features based on feedback
- **Severity:** Medium

**2. Search Performance**
- **Risk:** Search might be slow for large datasets
- **Mitigation:** Debounce input, show loading state, limit results
- **Severity:** Low

---

## SUCCESS METRICS

### Functional Completeness

- [ ] All backend endpoints integrated
- [ ] All components render correctly
- [ ] All user interactions work
- [ ] Error handling implemented
- [ ] Loading states implemented
- [ ] Mobile responsive

### Code Quality

- [ ] Follows existing Control Center patterns
- [ ] Reuses existing components where possible
- [ ] Properly typed (if using TypeScript)
- [ ] Commented for maintainability
- [ ] No console errors or warnings

### User Experience

- [ ] Fast page load (<2 seconds)
- [ ] Smooth interactions (no lag)
- [ ] Clear feedback for all actions
- [ ] Accessible (keyboard navigation, ARIA)
- [ ] Intuitive layout

---

## ALTERNATIVE APPROACHES CONSIDERED

### Approach 1: Rich Data Visualization (Knowledge Graph)

**Description:** Build interactive knowledge graph showing relationships between files

**Pros:**
- Very impressive visually
- Shows connections between documents
- Unique differentiation

**Cons:**
- Complex implementation (20-40 hours)
- Requires graph data from backend
- May not provide practical value for MVP

**Decision:** Defer to future enhancement

### Approach 2: Inline File Editor

**Description:** Allow editing files directly in Control Center

**Pros:**
- Convenient for quick edits
- No need to open external editor

**Cons:**
- Significant security risks
- Complex implementation
- Version control conflicts

**Decision:** Not recommended

### Approach 3: AI-Powered Search

**Description:** Use embeddings/semantic search instead of keyword search

**Pros:**
- More intelligent search results
- Finds related content

**Cons:**
- Backend needs embedding system
- Expensive (API costs)
- Complex implementation

**Decision:** Backend already supports keyword search, sufficient for MVP

---

## NEXT STEPS

### Immediate (This Planning Session)

1. ✅ Analyze existing Control Center frontend patterns
2. ✅ Review Knowledge Base backend API
3. ✅ Create comprehensive improvement plan
4. ⏳ **PENDING:** Get user approval for approach

### Short-Term (After Approval)

**Option A: Direct Implementation**
- Start with Phase 1 (Foundation)
- Build incrementally
- Deploy L2 workers for implementation?

**Option B: Brainstorming Session**
- Deploy L1 brainstorming team (Architecture + UX + Implementation)
- Get 3 perspectives on best approach
- Synthesize recommendations
- Then implement

**Recommendation:** Option A (direct implementation) because:
- Clear patterns already established
- Backend API is complete
- Design decisions straightforward
- Faster delivery (no brainstorming overhead)

### Medium-Term (Implementation)

1. Extend API client (30 min)
2. Create base components (2 hours)
3. Build Phase 1 features (4-6 hours)
4. Build Phase 2 features (6-8 hours)
5. Test and deploy

---

## QUESTIONS FOR USER

1. **Scope:** MVP first (8-12 hours) or complete build (16-23 hours)?
2. **Timeline:** When should this be completed?
3. **Priority:** How does this compare to other Control Center tasks?
4. **Deployment:** Deploy L2 workers to implement, or handle directly?
5. **Brainstorming:** Want L1 session for additional perspectives, or proceed with plan?

---

## APPENDIX: WIREFRAME MOCKUPS

### Main Page Layout (Desktop)

```
┌──────────────────────────────────────────────────────────────┐
│  Knowledge Base                    [Trigger Scan] [Refresh]  │
├──────────────────────────────────────────────────────────────┤
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │  142   │  │   45   │  │   12   │  │ 2 min  │            │
│  │ Files  │  │  Docs  │  │ Videos │  │  ago   │            │
│  └────────┘  └────────┘  └────────┘  └────────┘            │
├──────────────────────────────────────────────────────────────┤
│  🔍 Search files...   [Type: All ▼]  [Sort: Name ▼]        │
├────────────────────────────────────┬─────────────────────────┤
│  FILE BROWSER                      │  FILE DETAILS          │
│  ┌─────────────────────────────┐  │  ┌──────────────────┐  │
│  │ 📄 PROTOCOL_v1.3.md         │  │  │  📄 (icon)       │  │
│  │    Document  45KB  Jan 9    │  │  │                  │  │
│  ├─────────────────────────────┤  │  │  PROTOCOL_v1.3...│  │
│  │ 📹 Intro to AI Agents       │  │  │                  │  │
│  │    Video  125MB  Jan 8      │  │  │  Type: Document  │  │
│  ├─────────────────────────────┤  │  │  Size: 45.2 KB   │  │
│  │ 📝 Agent_Architecture.md    │  │  │  Created: Jan 9  │  │
│  │    Document  23KB  Jan 7    │  │  │                  │  │
│  ├─────────────────────────────┤  │  │  [Download]      │  │
│  │ ...                         │  │  └──────────────────┘  │
│  └─────────────────────────────┘  │                        │
│  [← Prev]  Page 1 of 8  [Next →] │                        │
├────────────────────────────────────┴─────────────────────────┤
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │ YOUTUBE CREATORS        │  │ RECENT SCANS            │  │
│  │  • AI Explained (8)     │  │  ✓ Jan 9, 19:15 (42s)   │  │
│  │  • Tech Channel (5)     │  │  ✓ Jan 9, 10:00 (38s)   │  │
│  │  • Code Guru (3)        │  │  ✓ Jan 8, 18:30 (51s)   │  │
│  └─────────────────────────┘  └─────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌────────────────────────┐
│  Knowledge Base        │
│  [Scan] [Refresh]      │
├────────────────────────┤
│  ┌──────┐  ┌──────┐   │
│  │ 142  │  │  45  │   │
│  │Files │  │ Docs │   │
│  └──────┘  └──────┘   │
│  ┌──────┐  ┌──────┐   │
│  │  12  │  │2 min │   │
│  │Video │  │ ago  │   │
│  └──────┘  └──────┘   │
├────────────────────────┤
│  🔍 Search...          │
│  [Type ▼]  [Sort ▼]   │
├────────────────────────┤
│  📄 PROTOCOL_v1.3.md   │
│     Document  45KB     │
│  ─────────────────────│
│  📹 Intro to AI        │
│     Video  125MB       │
│  ─────────────────────│
│  [Tap to view details]│
├────────────────────────┤
│  Page 1 of 8  [→]     │
└────────────────────────┘
```

---

**Plan Status:** COMPLETE ✓
**Ready for:** User approval and implementation
**Estimated Total Effort:** 16-23 hours (full implementation) or 8-12 hours (MVP)

---

**Created By:** Ziggie (Top-Level Strategic Agent)
**Date:** November 9, 2025 19:15
**Context:** Parallel planning while L2 workers fix Control Center issues
