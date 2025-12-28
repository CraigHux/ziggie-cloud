# Component Visual Mockups

**Design specifications for key UI components**

---

## 1. Dashboard Home Page

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [≡] Meow Ping Control Center              [🔔] [⚙️] [👤]   │ Header (64px)
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  📊 Home │  System Health                 Last 24 Hours    │
│  🤖 Agents                                                  │
│  ☁️  Services │ ╔════════════════════════════════════╗    │
│  📚 Knowledge │ ║  █   CPU: 45%    Memory: 62%      ║    │
│  🐳 Docker  │ ║  █   Disk: 34%   Network: 12 MB/s ║    │
│  🔌 APIs    │ ║  █                                 ║    │
│  📈 Monitor │ ╚════════════════════════════════════╝    │
│             │                                              │
│  🐾 Cat Zone │ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│             │ │ 🤖 Agents   │ │ ☁️  Services │ │ 📚 KB  ││
│             │ │ 584 Total   │ │ 12/15 Running│ │ 1,234  ││
│  240px      │ │ 520 Running │ │ 3 Stopped    │ │ Articles││
│  sidebar    │ └─────────────┘ └─────────────┘ └────────┘│
│             │                                              │
│             │ Quick Actions                                │
│             │ [▶ Start All] [⏸ Stop All] [🔄 Restart]    │
│             │                                              │
└─────────────┴──────────────────────────────────────────────┘
```

### Color Application

- **Sidebar Background**: `#1A2332`
- **Main Background**: `#0A1929`
- **Card Background**: `#1A2332`
- **Header Background**: `#1A2332` with border `#2D3F52`
- **Active Nav Item**: Background `#243447` with left border `#FF8C42` (3px)

---

## 2. Dashboard Card (Metric Card)

### Agent Status Card

```
┌─────────────────────────────────────┐
│ 🤖  AI Agents            [•••]      │ ← Header (H4, semibold)
│                                     │
│     584                             │ ← Large number (H1, bold)
│                                     │   Color: #FF8C42
│     Total agents configured         │ ← Subtitle (body2, secondary)
│                                     │
│     ⚫ 520 Running                  │ ← Status items
│     ⚫ 45 Stopped                   │   Green/Red dots (8px)
│     ⚫ 19 Pending                   │   Yellow dot
│                                     │
│     [View All →]                    │ ← Link button
└─────────────────────────────────────┘
        ↑ Hover effect:
        - translateY(-2px)
        - shadow-lg
```

**Specifications:**
- Border Radius: 12px
- Padding: 24px
- Shadow: `0 4px 6px rgba(0, 0, 0, 0.3)`
- Hover Shadow: `0 10px 15px rgba(0, 0, 0, 0.25)`
- Background: `#1A2332`
- Transition: 200ms ease-in-out

---

## 3. System Health Card (Large)

### Visual Layout

```
┌───────────────────────────────────────────────────────────┐
│ ❤️  System Health                          Last 24 Hours │
│                                                           │
│ ╔═══════════════════════════════════════════════════════╗│
│ ║                                                       ║│
│ ║    CPU Usage (%)                                     ║│
│ ║ 80│                      ╱╲                          ║│
│ ║ 60│          ╱╲         ╱  ╲      ╱╲                ║│
│ ║ 40│     ╱╲  ╱  ╲   ╱╲ ╱    ╲    ╱  ╲               ║│
│ ║ 20│╲   ╱  ╲╱    ╲ ╱  ╲      ╲  ╱    ╲              ║│
│ ║  0│ ╲╱            ╲                  ╲             ║│
│ ║    └────────────────────────────────────────>        ║│
│ ║    12am    6am    12pm    6pm    12am                ║│
│ ╚═══════════════════════════════════════════════════════╝│
│                                                           │
│ CPU: 45% ████████░░  Memory: 62% ████████████░           │
│ Disk: 34% ██████░░░░  Network: ⬆12 MB/s ⬇8 MB/s        │
└───────────────────────────────────────────────────────────┘
```

**Chart Styling:**
- Line Color: `#FF8C42` (Meow Orange)
- Grid Lines: `#2D3F52` (dashed, 1px)
- Axis Text: `#B2BAC2`, 12px
- Background: Transparent
- Tooltip: Background `#243447`, shadow-lg

**Progress Bars:**
- Height: 4px
- Background: `#2D3F52`
- Fill: Gradient based on percentage
  - 0-50%: `#10B981` (green)
  - 51-80%: `#F59E0B` (yellow)
  - 81-100%: `#EF4444` (red)

---

## 4. Navigation Sidebar

### Expanded State (240px)

```
┌─────────────────────────┐
│                         │
│  🐾 Meow Ping          │ ← Logo + text (H5)
│     Control Center      │   Color: #FF8C42
│                         │
├─────────────────────────┤
│                         │
│  📊 Dashboard           │ ← Nav items (body, 14px)
│  🤖 AI Agents        >  │   Icon (24px) + text
│  ☁️  Services        >  │   Padding: 12px 16px
│  📚 Knowledge Base   >  │   Height: 48px
│  🐳 Docker          >   │
│  🔌 APIs            >   │
│  📈 Monitoring      >   │
│                         │
├─────────────────────────┤
│  ⚙️  Settings           │ ← Bottom section
│  👤 Profile             │
└─────────────────────────┘
```

### Active State Styling

```
┌─────────────────────────┐
│ ┃🤖 AI Agents        >  │ ← Active item
└─────────────────────────┘
  ↑ 3px left border (#FF8C42)
    Background: #243447
    Text color: #FF8C42
    Icon color: #FF8C42
```

### Collapsed State (64px)

```
┌──────┐
│  🐾  │ ← Logo icon only
│      │
├──────┤
│  📊  │ ← Icons only
│  🤖  │   Centered
│  ☁️   │   24px size
│  📚  │   Tooltip on hover
│  🐳  │
│  🔌  │
│  📈  │
│      │
├──────┤
│  ⚙️   │
│  👤  │
└──────┘
```

---

## 5. Status Badge Component

### Running State

```
┌────────────────┐
│ ● Running      │ ← Green dot (8px) + text
└────────────────┘
```

**Specifications:**
- Background: `#10B981` (Success Green)
- Text: White, 12px, semibold
- Padding: 4px 12px
- Border Radius: 12px (pill shape)
- Dot: 8px circle, white, margin-right 6px

### All States

```
● Running     → #10B981 (green)
● Stopped     → #EF4444 (red)
● Pending     → #F59E0B (yellow)
● Error       → #EF4444 (red)
● Unknown     → #6B7A90 (gray)
```

---

## 6. Button Variants

### Primary Button

```
┌──────────────────────┐
│  ▶ Start All Agents  │ ← Icon + text
└──────────────────────┘
```

**Specifications:**
- Background: `#FF8C42`
- Text: White, 14px, semibold
- Padding: 10px 20px
- Border Radius: 8px
- Shadow: `0 1px 3px rgba(0, 0, 0, 0.4)`
- Hover: Background `#CC6600`, shadow increase
- Active: scale(0.98)

### Secondary Button (Outlined)

```
┌──────────────────────┐
│  View Details     →  │
└──────────────────────┘
```

**Specifications:**
- Background: Transparent
- Border: 1px solid `#FF8C42`
- Text: `#FF8C42`, 14px, semibold
- Padding: 10px 20px
- Border Radius: 8px
- Hover: Background `rgba(255, 140, 66, 0.08)`

### Icon Button

```
┌─────┐
│  🔄  │ ← 24px icon, centered
└─────┘
```

**Specifications:**
- Size: 40px × 40px
- Background: Transparent
- Border Radius: 8px
- Icon: 24px, `#B2BAC2`
- Hover: Background `#243447`, icon `#FF8C42`, scale(1.1)

---

## 7. Agent Management Page

### Agent Card in Grid

```
┌─────────────────────────────────┐
│ 🤖 Character Pipeline Agent     │ ← H4, semibold
│ ● Running                  [•••]│ ← Status badge + menu
│                                 │
│ Uptime: 12h 34m                 │ ← Metrics (body2)
│ Tasks: 1,234 completed          │
│ CPU: 2.3% | Mem: 45 MB          │
│                                 │
│ ┌───────────────────────────┐  │
│ │ Activity Graph            │  │ ← Mini chart
│ │ ▁▂▃▅▂▃▄▅▃▂▁▃▄▅▃▂         │  │
│ └───────────────────────────┘  │
│                                 │
│ [▶ Start] [⏸ Stop] [📋 Logs]   │ ← Action buttons
└─────────────────────────────────┘
```

**Grid Layout:**
- Desktop (lg): 3 columns
- Tablet (md): 2 columns
- Mobile (sm): 1 column
- Gap: 24px

---

## 8. Loading States

### Spinner (Cat Paw Rotating)

```
     🐾
    /  \
   rotating
   smoothly
```

**Specifications:**
- Icon: Cat paw (32px or 40px)
- Color: `#FF8C42`
- Animation: rotate 360deg, 1s linear infinite
- Background: Optional blur backdrop

### Skeleton Loader (Card)

```
┌─────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓░░░░░░░░                │ ← Shimmer effect
│                                 │   Background: #243447
│ ▓▓▓▓▓▓▓▓▓▓▓▓░░░░                │   Shimmer: lighter gradient
│ ▓▓▓▓▓▓░░░░                      │   Animation: 1.5s ease-in-out
│                                 │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓            │
│ ▓▓▓▓▓▓▓▓▓▓░░░░░░                │
└─────────────────────────────────┘
```

---

## 9. Empty State

### No Agents Configured

```
┌─────────────────────────────────┐
│                                 │
│         ／\_/\                  │
│        ( o.o )                  │ ← Friendly cat (128px)
│         > ^ <                   │   Grayscale or subtle color
│                                 │
│    No agents configured yet     │ ← H3, text primary
│                                 │
│  Get started by adding your     │ ← Body, text secondary
│  first AI agent to the system   │
│                                 │
│  ┌──────────────────────────┐  │
│  │  + Add Your First Agent  │  │ ← Primary button
│  └──────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

**Spacing:**
- Illustration to heading: 24px
- Heading to description: 12px
- Description to button: 24px
- Overall padding: 48px

---

## 10. Toast Notification

### Success Toast

```
┌─────────────────────────────────┐
│ ✓ Agent started successfully    │ ← Checkmark + message
│                              [×] │   Dismiss button
└─────────────────────────────────┘
```

**Specifications:**
- Background: `#10B981`
- Text: White, 14px
- Icon: 20px, left, margin-right 8px
- Padding: 12px 16px
- Border Radius: 8px
- Shadow: `0 4px 6px rgba(0, 0, 0, 0.3)`
- Position: top-right, stacked
- Duration: 4 seconds, auto-dismiss
- Transition: slide-in from right (300ms)

### Variants

```
✓ Success   → Green (#10B981)
! Warning   → Yellow (#F59E0B)
✕ Error     → Red (#EF4444)
ⓘ Info      → Blue (#3B82F6)
```

---

## 11. Data Table

### Agent List Table

```
┌─────────────────────────────────────────────────────────────┐
│ Name            Status    Uptime    CPU     Memory   Actions│ ← Header
├─────────────────────────────────────────────────────────────┤
│ Art Director    ● Running  12h 34m   2.3%    45 MB   [▶⏸📋]│ ← Row
│ Character Pipe  ● Running  11h 22m   3.1%    67 MB   [▶⏸📋]│
│ Environment     ● Stopped  —         —       —       [▶⏸📋]│
│ Game Systems    ● Running  10h 15m   1.8%    38 MB   [▶⏸📋]│
│ UI/UX Pipeline  ● Running  12h 30m   2.5%    52 MB   [▶⏸📋]│
└─────────────────────────────────────────────────────────────┘
```

**Styling:**
- Header: Background `#243447`, text semibold, `#E7EBF0`
- Row: Background `#1A2332`, border-bottom `#2D3F52`
- Hover Row: Background `#243447`
- Text: 14px, `#E7EBF0` (primary), `#B2BAC2` (secondary)
- Status dot: 8px, inline with text

---

## 12. Search Bar

```
┌─────────────────────────────────────────────────────┐
│ 🔍  Search agents, services, or knowledge base...   │
└─────────────────────────────────────────────────────┘
```

**Specifications:**
- Background: `#243447`
- Border: 1px solid `#2D3F52`
- Border Radius: 8px
- Padding: 10px 12px
- Icon: 20px, `#B2BAC2`, left, margin-right 8px
- Text: 14px, `#E7EBF0`
- Placeholder: `#6B7A90`
- Focus: Border `#4169E1`, shadow `0 0 0 3px rgba(65, 105, 225, 0.1)`

---

## 13. Modal / Dialog

### Confirm Action Modal

```
┌─────────────────────────────────────────┐
│ ⚠️  Stop All Agents?                    │ ← Header (H4)
├─────────────────────────────────────────┤
│                                         │
│ This will stop all 584 running agents.  │ ← Body text
│ This action may take a few minutes.     │
│                                         │
│ Are you sure you want to continue?      │
│                                         │
├─────────────────────────────────────────┤
│              [Cancel] [Stop All Agents] │ ← Actions
└─────────────────────────────────────────┘
```

**Specifications:**
- Background: `#1A2332`
- Border Radius: 12px
- Shadow: `0 20px 25px rgba(0, 0, 0, 0.2)`
- Max Width: 500px
- Padding: 24px
- Backdrop: `rgba(10, 25, 41, 0.8)` blur
- Animation: Fade in backdrop (200ms), scale in modal (250ms)

---

## 14. Breadcrumbs

```
Home  >  AI Agents  >  Character Pipeline Agent
```

**Specifications:**
- Text: 14px, `#B2BAC2`
- Active: `#E7EBF0`, semibold
- Separator: `>`, `#6B7A90`, margin 8px
- Hover: `#FF8C42` (links)

---

## Implementation Priority

1. **Essential Components (Build First):**
   - Dashboard layout (sidebar + main)
   - Card component
   - Button variants
   - Status badge
   - Navigation items

2. **Secondary Components:**
   - Charts (system health)
   - Data tables
   - Search bar
   - Loading states

3. **Nice-to-Have:**
   - Toast notifications
   - Empty states
   - Modals
   - Advanced animations

---

**Ready for implementation by UI/UX Pipeline Agent!**
