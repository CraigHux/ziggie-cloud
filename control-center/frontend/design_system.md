# Meow Ping Control Center - Design System

**Version:** 1.0.0
**Last Updated:** 2025-11-07
**Created By:** Art Director Agent (L1.1)

---

## Overview

The Meow Ping Control Center Dashboard is a professional web interface for managing 584 AI agents, services, knowledge base, APIs, Docker containers, and the entire development ecosystem. This design system balances functionality with subtle cat-themed branding to create an interface that's both powerful and delightful.

### Design Philosophy

- **Functionality First**: Clean, efficient interface optimized for developers and power users
- **Cat-Themed Subtle**: Professional with tasteful cat-themed touches
- **Dark-First**: Optimized for long usage sessions with excellent dark theme
- **Data Dense**: Dashboard efficiently displays complex information
- **Comic Book Influence**: Subtle nods to Meow Ping RTS's comic book art style

---

## 1. Color Scheme

### Primary Colors

The primary palette draws from the Meow Ping hero character while maintaining professionalism.

| Color Name | Hex Code | Usage | RGB |
|------------|----------|-------|-----|
| **Meow Orange** | `#FF8C42` | Primary brand color, CTAs, hero elements | 255, 140, 66 |
| **Meow Orange Dark** | `#CC6600` | Hover states, darker accents | 204, 102, 0 |
| **Meow Orange Light** | `#FFB366` | Light accents, hover backgrounds | 255, 179, 102 |
| **Hero Blue** | `#4169E1` | Secondary brand, informational elements | 65, 105, 225 |
| **Hero Blue Dark** | `#2952CC` | Button hover, active states | 41, 82, 204 |
| **Gold Accent** | `#FFD700` | Premium features, highlights, success states | 255, 215, 0 |

### Dark Theme (Primary)

Optimized for long usage sessions and reduced eye strain.

| Element | Hex Code | Usage | RGB |
|---------|----------|-------|-----|
| **Background Primary** | `#0A1929` | Main app background (deep navy) | 10, 25, 41 |
| **Background Secondary** | `#1A2332` | Cards, panels, raised surfaces | 26, 35, 50 |
| **Background Elevated** | `#243447` | Hover states, selected items | 36, 52, 71 |
| **Border Color** | `#2D3F52` | Dividers, card borders | 45, 63, 82 |
| **Text Primary** | `#E7EBF0` | Main text, headings | 231, 235, 240 |
| **Text Secondary** | `#B2BAC2` | Secondary text, labels | 178, 186, 194 |
| **Text Disabled** | `#6B7A90` | Disabled text, placeholders | 107, 122, 144 |

### Light Theme (Optional)

For daytime use or user preference.

| Element | Hex Code | Usage | RGB |
|---------|----------|-------|-----|
| **Background Primary** | `#F5F7FA` | Main app background (soft gray) | 245, 247, 250 |
| **Background Secondary** | `#FFFFFF` | Cards, panels, raised surfaces | 255, 255, 255 |
| **Background Elevated** | `#F0F2F5` | Hover states, selected items | 240, 242, 245 |
| **Border Color** | `#E0E4E8` | Dividers, card borders | 224, 228, 232 |
| **Text Primary** | `#1A2332` | Main text, headings | 26, 35, 50 |
| **Text Secondary** | `#4A5568` | Secondary text, labels | 74, 85, 104 |
| **Text Disabled** | `#A0AEC0` | Disabled text, placeholders | 160, 174, 192 |

### Status Colors

Essential for system monitoring and alerts.

| Status | Hex Code | Usage | RGB |
|--------|----------|-------|-----|
| **Success** | `#10B981` | Running services, successful operations | 16, 185, 129 |
| **Success Dark** | `#059669` | Hover states | 5, 150, 105 |
| **Warning** | `#F59E0B` | Warnings, needs attention | 245, 158, 11 |
| **Warning Dark** | `#D97706` | Hover states | 217, 119, 6 |
| **Error** | `#EF4444` | Errors, stopped services, critical alerts | 239, 68, 68 |
| **Error Dark** | `#DC2626` | Hover states | 220, 38, 38 |
| **Info** | `#3B82F6` | Informational messages, tips | 59, 130, 246 |
| **Info Dark** | `#2563EB` | Hover states | 37, 99, 235 |

### Semantic Colors

Category-specific colors for different system components.

| Category | Hex Code | Usage | Icon | RGB |
|----------|----------|-------|------|-----|
| **Agents** | `#FF8C42` | AI agent cards, agent metrics | smart_toy | 255, 140, 66 |
| **Services** | `#10B981` | Backend services, APIs | cloud | 16, 185, 129 |
| **Knowledge Base** | `#8B5CF6` | Documentation, learning resources | book | 139, 92, 246 |
| **Docker** | `#2396ED` | Container management | docker | 35, 150, 237 |
| **APIs** | `#F59E0B` | API endpoints, integrations | api | 245, 158, 11 |
| **Monitoring** | `#3B82F6` | System health, metrics | monitoring | 59, 130, 246 |
| **Cat Theme** | `#FFD700` | Cat-themed features, easter eggs | pets | 255, 215, 0 |

---

## 2. Typography System

### Font Families

```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'Fira Code', 'JetBrains Mono', 'Courier New', monospace;
```

**Inter** is the primary font family for its excellent readability and modern appearance. For monospace (code, logs, technical data), use **Fira Code** or **JetBrains Mono**.

### Font Sizes

| Element | Size | Line Height | Weight | Usage |
|---------|------|-------------|--------|-------|
| **H1** | 32px (2rem) | 40px (1.25) | 700 (Bold) | Page titles, main headings |
| **H2** | 24px (1.5rem) | 32px (1.33) | 600 (Semibold) | Section headings |
| **H3** | 20px (1.25rem) | 28px (1.4) | 600 (Semibold) | Subsection headings |
| **H4** | 18px (1.125rem) | 24px (1.33) | 600 (Semibold) | Card titles |
| **H5** | 16px (1rem) | 24px (1.5) | 600 (Semibold) | Small headings |
| **H6** | 14px (0.875rem) | 20px (1.43) | 600 (Semibold) | Labels, captions |
| **Body Large** | 16px (1rem) | 24px (1.5) | 400 (Regular) | Primary body text |
| **Body** | 14px (0.875rem) | 20px (1.43) | 400 (Regular) | Default body text |
| **Body Small** | 12px (0.75rem) | 16px (1.33) | 400 (Regular) | Secondary text, captions |
| **Code** | 14px (0.875rem) | 20px (1.43) | 400 (Regular) | Inline code, technical data |
| **Button** | 14px (0.875rem) | 20px (1.43) | 600 (Semibold) | Button labels |

### Font Weights

- **Regular (400)**: Body text, default
- **Medium (500)**: Emphasized text (optional)
- **Semibold (600)**: Headings, buttons, labels
- **Bold (700)**: H1, strong emphasis

### Type Scale

```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 2rem;      /* 32px */
```

---

## 3. Icon System

### Icon Library: Material Icons

**Recommended**: `@mui/icons-material` (already in dependencies)

**Alternative**: Lucide Icons for sharper, more modern icons

### Icon Style

- **Style**: Rounded (softer, friendlier for cat theme)
- **Weight**: Regular (400) for most, Bold (700) for emphasis
- **Variant**: Outlined for secondary actions, Filled for primary actions

### Icon Sizes

| Size Name | Pixels | Usage |
|-----------|--------|-------|
| **Small** | 16px | Inline icons, tight spaces |
| **Medium** | 24px | Default, buttons, navigation |
| **Large** | 32px | Card headers, feature icons |
| **XLarge** | 48px | Empty states, hero sections |

### Semantic Icons

Consistent icon usage across the dashboard:

| Feature | Icon Name | MUI Import | Color |
|---------|-----------|------------|-------|
| **AI Agents** | `smart_toy` | `SmartToyRounded` | Meow Orange |
| **Services** | `cloud` | `CloudRounded` | Success Green |
| **Knowledge Base** | `book` | `MenuBookRounded` | Purple |
| **Docker** | `docker` or `inventory` | `Inventory2Rounded` | Docker Blue |
| **APIs** | `api` | `ApiRounded` | Warning Orange |
| **Monitoring** | `monitoring` | `MonitorHeartRounded` | Info Blue |
| **Settings** | `settings` | `SettingsRounded` | Text Secondary |
| **Dashboard** | `dashboard` | `DashboardRounded` | Primary |
| **Health Check** | `favorite` | `FavoriteRounded` | Error Red (healthy) |
| **Logs** | `description` | `DescriptionRounded` | Text Secondary |
| **Terminal** | `terminal` | `TerminalRounded` | Text Primary |
| **Cat Theme** | `pets` | `PetsRounded` | Gold |
| **Status Running** | `play_circle` | `PlayCircleRounded` | Success |
| **Status Stopped** | `stop_circle` | `StopCircleRounded` | Error |
| **Status Pending** | `pending` | `PendingRounded` | Warning |
| **Refresh** | `refresh` | `RefreshRounded` | Primary |
| **Add** | `add_circle` | `AddCircleRounded` | Primary |
| **Delete** | `delete` | `DeleteRounded` | Error |
| **Edit** | `edit` | `EditRounded` | Primary |
| **Search** | `search` | `SearchRounded` | Text Secondary |
| **Notifications** | `notifications` | `NotificationsRounded` | Warning |

---

## 4. Layout & Spacing

### Spacing Scale

Based on 8px grid system for consistent spacing.

```css
--space-1: 4px;    /* 0.25rem */
--space-2: 8px;    /* 0.5rem */
--space-3: 12px;   /* 0.75rem */
--space-4: 16px;   /* 1rem */
--space-5: 20px;   /* 1.25rem */
--space-6: 24px;   /* 1.5rem */
--space-8: 32px;   /* 2rem */
--space-10: 40px;  /* 2.5rem */
--space-12: 48px;  /* 3rem */
--space-16: 64px;  /* 4rem */
```

### Border Radius

```css
--radius-sm: 4px;    /* Small elements, badges */
--radius-md: 8px;    /* Default, buttons, inputs */
--radius-lg: 12px;   /* Cards, modals */
--radius-xl: 16px;   /* Large cards, featured elements */
--radius-full: 9999px; /* Circular elements, avatar */
```

### Shadows (Elevation System)

```css
/* Dark Theme Shadows */
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.25);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.2);

/* Light Theme Shadows */
--shadow-sm-light: 0 1px 3px rgba(0, 0, 0, 0.12);
--shadow-md-light: 0 2px 4px rgba(0, 0, 0, 0.1);
--shadow-lg-light: 0 4px 8px rgba(0, 0, 0, 0.08);
--shadow-xl-light: 0 8px 16px rgba(0, 0, 0, 0.06);
```

### Grid System

```css
--container-max-width: 1440px;
--sidebar-width: 240px;
--sidebar-collapsed-width: 64px;
--header-height: 64px;
```

**Dashboard Grid:**
- 12-column responsive grid
- Gutter: 24px (space-6)
- Column gap: 24px
- Row gap: 24px

**Breakpoints:**
```css
--breakpoint-xs: 0px;      /* Mobile portrait */
--breakpoint-sm: 600px;    /* Mobile landscape */
--breakpoint-md: 900px;    /* Tablet */
--breakpoint-lg: 1200px;   /* Desktop */
--breakpoint-xl: 1536px;   /* Large desktop */
```

---

## 5. Component Styling Guidelines

### Dashboard Cards

**Metrics Card:**
```
- Background: Background Secondary
- Border: 1px solid Border Color
- Border Radius: 12px (radius-lg)
- Padding: 24px (space-6)
- Shadow: shadow-md
- Hover: Slight elevation increase (shadow-lg)
```

**Card Structure:**
- Header with icon (left) and title (semibold, H4)
- Metric value (large, bold, colored by status)
- Subtitle or description (small, secondary text)
- Optional action button or link (top-right)

### Navigation

**Sidebar Navigation (Recommended):**
```
- Width: 240px (expanded), 64px (collapsed)
- Background: Background Secondary
- Border Right: 1px solid Border Color
- Fixed position: left
- Items:
  - Height: 48px
  - Padding: 12px 16px
  - Icon: 24px, left-aligned
  - Label: Body text, margin-left 12px
  - Hover: Background Elevated
  - Active: Background Elevated + Primary color accent (left border 3px)
```

**Top Navigation (Alternative):**
```
- Height: 64px
- Background: Background Secondary
- Border Bottom: 1px solid Border Color
- Fixed position: top
- Logo: Left (with cat icon)
- Navigation items: Center
- User/settings: Right
```

### Buttons

**Primary Button:**
```
- Background: Meow Orange (#FF8C42)
- Text: White (#FFFFFF)
- Border Radius: 8px (radius-md)
- Padding: 10px 20px (space-2 space-5)
- Font: 14px, Semibold (600)
- Hover: Meow Orange Dark (#CC6600)
- Active: Darker, slight scale (0.98)
- Shadow: shadow-sm
```

**Secondary Button:**
```
- Background: Transparent
- Text: Primary color (Meow Orange)
- Border: 1px solid Primary color
- Border Radius: 8px
- Padding: 10px 20px
- Font: 14px, Semibold
- Hover: Background Elevated, border darker
```

**Danger Button:**
```
- Background: Error (#EF4444)
- Text: White
- Border Radius: 8px
- Padding: 10px 20px
- Font: 14px, Semibold
- Hover: Error Dark (#DC2626)
```

**Icon Button:**
```
- Size: 40px x 40px
- Background: Transparent
- Border Radius: 8px
- Icon: 24px, Text Secondary
- Hover: Background Elevated, Icon Primary
- Padding: 8px
```

### Status Indicators

**Status Badge:**
```
- Border Radius: 12px (radius-full for pill shape)
- Padding: 4px 12px (space-1 space-3)
- Font: 12px, Semibold
- Text: White
- Background: Status color (Success/Warning/Error/Info)
- Icon: Optional, 16px, left of text
```

**Status Dot:**
```
- Size: 8px x 8px
- Border Radius: 50% (circular)
- Background: Status color
- Pulse animation: Optional for "running" state
```

**Examples:**
- Running: Green dot + "Running" text
- Stopped: Red dot + "Stopped" text
- Pending: Yellow dot + "Pending" text
- Error: Red dot + "Error" text

### Charts

**Color Choices for Graphs:**

Use semantic colors consistently:
- **Line 1 (Primary Metric)**: Meow Orange (#FF8C42)
- **Line 2 (Secondary)**: Hero Blue (#4169E1)
- **Line 3 (Tertiary)**: Purple (#8B5CF6)
- **Line 4+**: Rotate through semantic colors

**Chart Styling:**
```
- Background: Transparent
- Grid Lines: Border Color, 1px dashed
- Axis Text: Text Secondary, 12px
- Tooltip: Background Secondary, shadow-lg, 12px radius
- Legend: Text Secondary, 14px, horizontal below chart
```

### Forms

**Input Fields:**
```
- Background: Background Elevated (dark theme) / White (light theme)
- Border: 1px solid Border Color
- Border Radius: 8px
- Padding: 10px 12px
- Font: 14px, Regular
- Focus: Border Hero Blue, shadow-sm in primary color
- Error: Border Error, error message below (12px, error color)
```

**Select Dropdowns:**
```
- Same as input fields
- Chevron icon: Right-aligned, 20px
- Dropdown menu: Background Secondary, shadow-xl, max-height 300px
- Dropdown items: Hover Background Elevated
```

---

## 6. Brand Elements

### Cat-Themed Touches

Subtle, professional integration of cat theme:

1. **Logo**: Cat paw icon with "Meow Ping Control Center" text
2. **Loading States**: Animated cat paw prints or bouncing cat icon
3. **Empty States**: Friendly cat illustration with helpful message
4. **404 Page**: Curious cat with "Lost? We'll help you find your way home"
5. **Success Messages**: Subtle cat paw icon in success toasts
6. **Easter Eggs**:
   - "Purr-formance" metrics
   - "Cat-alog" for knowledge base
   - "Meow-nitoring" for system health
   - Hidden cat images on special pages (sparingly)

### Logo Specifications

**Full Logo:**
```
- Cat paw icon (32px) + "Meow Ping Control Center" text
- Color: Meow Orange icon, Text Primary text
- Spacing: 12px between icon and text
- Usage: Sidebar header, login page, about page
```

**Icon Only:**
```
- Cat paw icon (24px or 32px)
- Color: Meow Orange
- Usage: Favicon, collapsed sidebar, mobile header
```

### Loading States

**Spinner:**
```
- Size: 40px (default) or 24px (small)
- Color: Primary (Meow Orange)
- Animation: Smooth rotation (1s duration)
- Optional: Cat paw icon rotating
```

**Skeleton Loaders:**
```
- Background: Background Elevated
- Shimmer: Gradient animation (light shimmer effect)
- Border Radius: Match component (8px or 12px)
- Usage: Card loading, list items, table rows
```

**Progress Bar:**
```
- Height: 4px
- Background: Border Color
- Fill: Primary (Meow Orange)
- Border Radius: 2px (fully rounded)
- Animation: Smooth progress or indeterminate shimmer
```

### Empty States

**Structure:**
```
- Illustration: Friendly cat (128px x 128px), grayscale or subtle color
- Heading: H3, "No [items] yet"
- Description: Body text, helpful message
- Action Button: Primary button, "Add [item]" or "Get Started"
- Spacing:
  - Illustration to heading: 24px
  - Heading to description: 12px
  - Description to button: 24px
```

**Examples:**
- No Agents: Cat looking at empty box, "No agents configured yet. Let's add one!"
- No Services: Cat with wrench, "No services running. Start your first service!"
- No Logs: Cat with magnifying glass, "No logs to display. Check back soon!"

### Toast Notifications

**Success Toast:**
```
- Background: Success Green
- Text: White, 14px
- Icon: Checkmark (or cat paw), 20px, left
- Border Radius: 8px
- Padding: 12px 16px
- Position: Top-right or bottom-right
- Duration: 3-5 seconds, dismissible
```

**Error Toast:**
```
- Background: Error Red
- Text: White, 14px
- Icon: Error icon, 20px, left
- Border Radius: 8px
- Padding: 12px 16px
```

**Info/Warning Toast:**
```
- Background: Info Blue / Warning Orange
- Text: White, 14px
- Icon: Info / Warning icon, 20px, left
```

---

## 7. Accessibility

### Color Contrast

All text meets WCAG AA standards:
- Normal text: 4.5:1 contrast ratio minimum
- Large text (18px+): 3:1 contrast ratio minimum
- Buttons and interactive elements: Clear hover/focus states

### Focus States

```
- Focus ring: 2px solid Hero Blue
- Offset: 2px
- Border Radius: Inherit from component
- Visible on keyboard navigation only (not mouse clicks)
```

### Motion & Animation

```
- Transition duration: 150-300ms (fast), 300-500ms (medium)
- Easing: ease-in-out (smooth) or ease-out (snappy)
- Respect prefers-reduced-motion for accessibility
```

---

## 8. Responsive Design

### Mobile-First Approach

**Mobile (< 600px):**
- Collapsed sidebar (hamburger menu)
- Single-column layout
- Stacked cards (full width)
- Touch-friendly buttons (min 44px height)

**Tablet (600px - 900px):**
- Expandable sidebar or bottom tab navigation
- 2-column grid for dashboard cards
- Condensed metrics

**Desktop (900px+):**
- Full sidebar navigation (240px)
- Multi-column grid (up to 4 columns)
- Expanded metrics and charts

---

## 9. Animation & Micro-interactions

### Hover Effects

```css
/* Card hover */
transition: box-shadow 200ms ease-in-out, transform 150ms ease-out;
transform: translateY(-2px);
box-shadow: shadow-lg;

/* Button hover */
transition: background-color 150ms ease-in-out;
background-color: darker shade;

/* Icon hover */
transition: color 150ms ease-in-out, transform 150ms ease-out;
transform: scale(1.1);
```

### Page Transitions

```
- Fade in: 300ms
- Slide in (sidebar): 200ms ease-out
- Modal: Backdrop fade (200ms) + content scale (250ms)
```

---

## 10. Usage Examples

### Dashboard Home Page

```
Layout:
- Sidebar (left, 240px)
- Header (top, 64px, with breadcrumbs)
- Main content (grid, 3 columns on desktop)

Cards:
1. System Health (large card, 2 columns wide)
   - Icon: Heart (monitoring)
   - Color: Success if healthy
   - Metrics: CPU, Memory, Disk
   - Chart: Line chart, last 24h

2. Agents Status (1 column)
   - Icon: Smart Toy
   - Color: Meow Orange
   - Metric: "584 Total | 520 Running"
   - Status badges: Running (green), Stopped (red)

3. Services Status (1 column)
   - Icon: Cloud
   - Color: Success Green
   - Metric: "12/15 Running"
   - List: Service names + status dots

4. Quick Actions (full width)
   - Button group: "Start All", "Stop All", "Restart Services"
   - Style: Primary buttons, icon + text
```

### Agent Management Page

```
Layout:
- Search bar (top, full width)
- Filter buttons (categories: All, Running, Stopped, Error)
- Agent cards (grid, 3 columns desktop, 2 tablet, 1 mobile)

Agent Card:
- Header: Agent name (H4) + status badge
- Icon: Smart Toy (colored by status)
- Metrics: Uptime, Tasks Completed, CPU usage
- Actions: Start/Stop/Restart/View Logs (icon buttons)
- Hover: Elevation increase, show more details
```

---

## 11. CSS Variables

Complete CSS variable set for easy theming:

```css
:root {
  /* Primary Colors */
  --color-primary: #FF8C42;
  --color-primary-dark: #CC6600;
  --color-primary-light: #FFB366;
  --color-secondary: #4169E1;
  --color-secondary-dark: #2952CC;
  --color-accent: #FFD700;

  /* Dark Theme */
  --color-bg-primary: #0A1929;
  --color-bg-secondary: #1A2332;
  --color-bg-elevated: #243447;
  --color-border: #2D3F52;
  --color-text-primary: #E7EBF0;
  --color-text-secondary: #B2BAC2;
  --color-text-disabled: #6B7A90;

  /* Status Colors */
  --color-success: #10B981;
  --color-success-dark: #059669;
  --color-warning: #F59E0B;
  --color-warning-dark: #D97706;
  --color-error: #EF4444;
  --color-error-dark: #DC2626;
  --color-info: #3B82F6;
  --color-info-dark: #2563EB;

  /* Semantic Colors */
  --color-agents: #FF8C42;
  --color-services: #10B981;
  --color-knowledge: #8B5CF6;
  --color-docker: #2396ED;
  --color-apis: #F59E0B;
  --color-monitoring: #3B82F6;
  --color-cat-theme: #FFD700;

  /* Typography */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Fira Code', 'JetBrains Mono', 'Courier New', monospace;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.25);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.2);

  /* Layout */
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --header-height: 64px;
  --container-max-width: 1440px;
}
```

---

## 12. Implementation Notes

### Material-UI Theme Integration

The companion `theme.json` file contains a complete Material-UI theme configuration that implements this design system. Import it using:

```javascript
import { createAppTheme } from './theme';
import themeConfig from './theme.json';

const theme = createAppTheme('dark', themeConfig);
```

### Component Library

Build reusable components following this design system:
- `Card.jsx`: Dashboard cards with consistent styling
- `StatusBadge.jsx`: Status indicators
- `Button.jsx`: Primary, secondary, danger variants
- `IconButton.jsx`: Icon-only buttons
- `LoadingSpinner.jsx`: Cat-themed loading animations
- `EmptyState.jsx`: Empty state illustrations
- `Toast.jsx`: Notification toasts

### Performance Considerations

- Use CSS-in-JS for dynamic theming (Material-UI's `styled` or Emotion)
- Optimize icon imports: `import PlayCircleRounded from '@mui/icons-material/PlayCircleRounded'`
- Lazy load charts and heavy components
- Use skeleton loaders during data fetching

---

## 13. Design Tokens (JSON Format)

For programmatic access:

```json
{
  "colors": {
    "primary": "#FF8C42",
    "primaryDark": "#CC6600",
    "primaryLight": "#FFB366",
    "secondary": "#4169E1",
    "secondaryDark": "#2952CC",
    "accent": "#FFD700"
  },
  "darkTheme": {
    "bgPrimary": "#0A1929",
    "bgSecondary": "#1A2332",
    "bgElevated": "#243447",
    "border": "#2D3F52",
    "textPrimary": "#E7EBF0",
    "textSecondary": "#B2BAC2",
    "textDisabled": "#6B7A90"
  },
  "status": {
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6"
  }
}
```

---

## 14. Maintenance & Evolution

### Version Control

- Document all design system changes in this file
- Increment version number for breaking changes
- Notify UI/UX Pipeline Agent of updates

### Feedback Loop

- Gather user feedback on usability
- A/B test color schemes or layouts if needed
- Iterate based on real-world usage

### Future Enhancements

- Light theme refinements based on usage
- Additional semantic categories as system grows
- Animated cat mascot for special events
- Customizable themes (user preferences)

---

**End of Design System Document**

For implementation details, refer to `theme.json` and Material-UI documentation.

**Questions or suggestions?** Contact the Art Director Agent (L1.1) or UI/UX Pipeline Agent (L1.5).
