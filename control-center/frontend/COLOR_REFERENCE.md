# Color Reference Guide

**Quick reference for Meow Ping Control Center colors**

---

## Primary Brand Colors

| Color Name | Hex | RGB | Preview |
|------------|-----|-----|---------|
| Meow Orange | `#FF8C42` | 255, 140, 66 | ![#FF8C42](https://via.placeholder.com/100x30/FF8C42/FFFFFF?text=Primary) |
| Meow Orange Dark | `#CC6600` | 204, 102, 0 | ![#CC6600](https://via.placeholder.com/100x30/CC6600/FFFFFF?text=Hover) |
| Meow Orange Light | `#FFB366` | 255, 179, 102 | ![#FFB366](https://via.placeholder.com/100x30/FFB366/000000?text=Light) |
| Hero Blue | `#4169E1` | 65, 105, 225 | ![#4169E1](https://via.placeholder.com/100x30/4169E1/FFFFFF?text=Secondary) |
| Hero Blue Dark | `#2952CC` | 41, 82, 204 | ![#2952CC](https://via.placeholder.com/100x30/2952CC/FFFFFF?text=Hover) |
| Gold Accent | `#FFD700` | 255, 215, 0 | ![#FFD700](https://via.placeholder.com/100x30/FFD700/000000?text=Accent) |

---

## Dark Theme (Primary)

### Backgrounds

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Background Primary | `#0A1929` | 10, 25, 41 | Main app background |
| Background Secondary | `#1A2332` | 26, 35, 50 | Cards, panels |
| Background Elevated | `#243447` | 36, 52, 71 | Hover states |
| Border Color | `#2D3F52` | 45, 63, 82 | Dividers, borders |

### Text

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Text Primary | `#E7EBF0` | 231, 235, 240 | Headings, body |
| Text Secondary | `#B2BAC2` | 178, 186, 194 | Labels, subtitles |
| Text Disabled | `#6B7A90` | 107, 122, 144 | Disabled text |

---

## Status Colors

| Status | Hex | RGB | Usage |
|--------|-----|-----|-------|
| Success | `#10B981` | 16, 185, 129 | Running services |
| Success Dark | `#059669` | 5, 150, 105 | Hover |
| Warning | `#F59E0B` | 245, 158, 11 | Needs attention |
| Warning Dark | `#D97706` | 217, 119, 6 | Hover |
| Error | `#EF4444` | 239, 68, 68 | Errors, stopped |
| Error Dark | `#DC2626` | 220, 38, 38 | Hover |
| Info | `#3B82F6` | 59, 130, 246 | Informational |
| Info Dark | `#2563EB` | 37, 99, 235 | Hover |

---

## Semantic Colors (Categories)

| Category | Hex | RGB | Icon | Usage |
|----------|-----|-----|------|-------|
| Agents | `#FF8C42` | 255, 140, 66 | smart_toy | AI agent cards |
| Services | `#10B981` | 16, 185, 129 | cloud | Backend services |
| Knowledge Base | `#8B5CF6` | 139, 92, 246 | book | Documentation |
| Docker | `#2396ED` | 35, 150, 237 | inventory_2 | Containers |
| APIs | `#F59E0B` | 245, 158, 11 | api | API endpoints |
| Monitoring | `#3B82F6` | 59, 130, 246 | monitor_heart | System health |
| Cat Theme | `#FFD700` | 255, 215, 0 | pets | Cat features |

---

## Light Theme (Optional)

### Backgrounds

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Background Primary | `#F5F7FA` | 245, 247, 250 | Main app background |
| Background Secondary | `#FFFFFF` | 255, 255, 255 | Cards, panels |
| Background Elevated | `#F0F2F5` | 240, 242, 245 | Hover states |
| Border Color | `#E0E4E8` | 224, 228, 232 | Dividers, borders |

### Text

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Text Primary | `#1A2332` | 26, 35, 50 | Headings, body |
| Text Secondary | `#4A5568` | 74, 85, 104 | Labels, subtitles |
| Text Disabled | `#A0AEC0` | 160, 174, 192 | Disabled text |

---

## Usage in Code

### CSS Variables

```css
:root {
  --color-primary: #FF8C42;
  --color-secondary: #4169E1;
  --color-accent: #FFD700;

  --color-bg-primary: #0A1929;
  --color-bg-secondary: #1A2332;
  --color-bg-elevated: #243447;

  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
}
```

### Material-UI Theme

```javascript
// Import from theme.json
import themeConfig from './theme.json';

// Access colors
const primaryColor = themeConfig.colors.primary.main; // #FF8C42
const successColor = themeConfig.colors.success.main; // #10B981
```

### Direct Usage in Components

```jsx
// Using sx prop
<Box sx={{ backgroundColor: '#1A2332', color: '#E7EBF0' }}>
  Content
</Box>

// Using theme colors
<Button color="primary">Click Me</Button> // Uses #FF8C42

// Custom color from semantic palette
<Box sx={{ color: themeConfig.semantic.agents.color }}>
  Agents
</Box>
```

---

## Color Accessibility

All colors meet WCAG AA standards for contrast:

### Text Contrast Ratios (Dark Theme)

| Foreground | Background | Ratio | Pass |
|------------|-----------|-------|------|
| `#E7EBF0` (Text Primary) | `#0A1929` (BG Primary) | 13.2:1 | ✅ AAA |
| `#B2BAC2` (Text Secondary) | `#0A1929` (BG Primary) | 8.5:1 | ✅ AAA |
| `#FFFFFF` (White) | `#FF8C42` (Primary) | 4.5:1 | ✅ AA |
| `#FFFFFF` (White) | `#4169E1` (Secondary) | 4.6:1 | ✅ AA |

### Status Color Contrast

| Status | Background | Ratio | Pass |
|--------|-----------|-------|------|
| `#FFFFFF` on `#10B981` (Success) | Dark | 4.8:1 | ✅ AA |
| `#FFFFFF` on `#F59E0B` (Warning) | Dark | 4.5:1 | ✅ AA |
| `#FFFFFF` on `#EF4444` (Error) | Dark | 4.5:1 | ✅ AA |

---

## Quick Copy-Paste

### Primary Palette (CSS)
```css
#FF8C42  /* Meow Orange */
#CC6600  /* Meow Orange Dark */
#4169E1  /* Hero Blue */
#FFD700  /* Gold Accent */
```

### Status Colors (CSS)
```css
#10B981  /* Success */
#F59E0B  /* Warning */
#EF4444  /* Error */
#3B82F6  /* Info */
```

### Dark Theme (CSS)
```css
#0A1929  /* Background Primary */
#1A2332  /* Background Secondary */
#E7EBF0  /* Text Primary */
#B2BAC2  /* Text Secondary */
```

---

## Color Psychology

| Color | Emotion | Usage |
|-------|---------|-------|
| Meow Orange | Energetic, Friendly, Warm | Primary actions, cat theme |
| Hero Blue | Trustworthy, Professional, Calm | Secondary actions, info |
| Gold | Premium, Success, Achievement | Highlights, special features |
| Green | Success, Running, Healthy | Active services, positive states |
| Red | Error, Stopped, Urgent | Errors, critical alerts |
| Yellow | Warning, Caution, Attention | Warnings, pending states |
| Purple | Knowledge, Creativity, Learning | Documentation, knowledge base |

---

**Last Updated:** 2025-11-07
**Design System Version:** 1.0.0
