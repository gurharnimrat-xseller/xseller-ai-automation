# Xseller.ai Dashboard Style Guide

## Overview

This style guide documents the design system, components, and visual patterns used in the Xseller.ai dashboard. It ensures consistency across all UI elements and provides guidelines for future development.

## Color Palette

### Primary Colors (Xseller.ai Brand)
```css
--primary-50: #f0f9ff   /* Lightest blue */
--primary-100: #e0f2fe
--primary-200: #bae6fd
--primary-300: #7dd3fc
--primary-400: #38bdf8
--primary-500: #0ea5e9  /* Primary brand color */
--primary-600: #0284c7  /* Primary hover state */
--primary-700: #0369a1
--primary-800: #075985
--primary-900: #0c4a6e  /* Darkest blue */
```

### Semantic Colors
```css
/* Success States */
--success-500: #22c55e
--success-600: #16a34a

/* Warning States */
--warning-500: #f59e0b
--warning-600: #d97706

/* Error States */
--error-500: #ef4444
--error-600: #dc2626

/* Info States */
--info-500: #3b82f6
--info-600: #2563eb
```

### Neutral Grays
```css
--gray-50: #f9fafb   /* Background primary */
--gray-100: #f3f4f6 /* Background secondary */
--gray-200: #e5e7eb /* Border primary */
--gray-300: #d1d5db /* Border secondary */
--gray-400: #9ca3af
--gray-500: #6b7280 /* Text muted */
--gray-600: #4b5563 /* Text secondary */
--gray-700: #374151 /* Text primary */
--gray-800: #1f2937
--gray-900: #111827
```

## Typography

### Font Family
- **Primary**: Inter (sans-serif)
- **Fallback**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue'

### Font Sizes
```css
--text-xs: 0.75rem   /* 12px */
--text-sm: 0.875rem  /* 14px */
--text-base: 1rem    /* 16px */
--text-lg: 1.125rem  /* 18px */
--text-xl: 1.25rem   /* 20px */
--text-2xl: 1.5rem   /* 24px */
--text-3xl: 1.875rem /* 30px */
```

### Font Weights
- **Regular**: 400
- **Medium**: 500
- **Semibold**: 600
- **Bold**: 700

## Spacing Scale

```css
--space-1: 0.25rem  /* 4px */
--space-2: 0.5rem   /* 8px */
--space-3: 0.75rem  /* 12px */
--space-4: 1rem     /* 16px */
--space-5: 1.25rem  /* 20px */
--space-6: 1.5rem   /* 24px */
--space-8: 2rem     /* 32px */
--space-10: 2.5rem  /* 40px */
--space-12: 3rem    /* 48px */
--space-16: 4rem    /* 64px */
--space-20: 5rem    /* 80px */
--space-24: 6rem    /* 96px */
```

## Border Radius

```css
--radius-sm: 0.25rem   /* 4px */
--radius: 0.375rem     /* 6px */
--radius-md: 0.5rem    /* 8px */
--radius-lg: 0.75rem   /* 12px */
--radius-xl: 1rem      /* 16px */
--radius-2xl: 1.5rem   /* 24px */
```

## Shadows

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
```

## Component Patterns

### Cards

#### Standard Card
```tsx
<Card className="shadow-sm border border-gray-200 rounded-xl">
  <CardHeader>
    <h3 className="text-lg font-semibold text-gray-900">Card Title</h3>
  </CardHeader>
  <CardContent className="p-6">
    {/* Content */}
  </CardContent>
</Card>
```

#### Gradient Card (Dashboard Stats)
```tsx
<Card className="bg-gradient-to-br from-blue-50 via-blue-100/50 to-indigo-100/30 border-l-4 border-l-blue-500 shadow-lg backdrop-blur-sm bg-white/80">
  {/* Content */}
</Card>
```

#### Glass Card
```tsx
<Card className="bg-white/80 backdrop-blur-sm border-2 border-gray-100/50 shadow-xl">
  {/* Content */}
</Card>
```

### Buttons

#### Primary Button
```tsx
<Button className="bg-primary-500 hover:bg-primary-600 text-white">
  Primary Action
</Button>
```

#### Secondary Button
```tsx
<Button variant="outline" className="border-gray-200 hover:bg-gray-50">
  Secondary Action
</Button>
```

#### Ghost Button
```tsx
<Button variant="ghost" className="hover:bg-gray-100">
  Ghost Action
</Button>
```

### Badges

#### Status Badges
```tsx
<Badge variant="success" className="bg-green-100 text-green-700 border-green-200">
  Active
</Badge>

<Badge variant="warning" className="bg-yellow-100 text-yellow-700 border-yellow-200">
  Pending
</Badge>

<Badge variant="error" className="bg-red-100 text-red-700 border-red-200">
  Error
</Badge>
```

### Panels (Kibana-style)

#### Generic Panel
```tsx
<Panel
  title="Panel Title"
  subtitle="Panel description"
  icon={<Icon />}
  variant="gradient"
  gradient="blue"
  showRefresh
  showMaximize
  onRefresh={() => {}}
>
  {/* Content */}
</Panel>
```

#### Metric Panel
```tsx
<MetricPanel
  title="Active Agents"
  value="6"
  label="Current agents"
  trend={{ value: 2, isPositive: true }}
  icon={<Bot className="w-6 h-6" />}
  gradient="emerald"
>
  {/* Additional content */}
</MetricPanel>
```

#### Status Panel
```tsx
<StatusPanel
  title="System Status"
  status="success"
  statusText="All systems operational"
>
  {/* Status details */}
</StatusPanel>
```

## Layout Patterns

### Dashboard Grid
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
  {/* Stat cards */}
</div>
```

### Main Content Layout
```tsx
<div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
  {/* Main panels */}
</div>
```

### Bottom Section
```tsx
<div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
  {/* Secondary panels */}
</div>
```

## Animation Guidelines

### Entrance Animations
- **Staggered items**: Use `dashboard-item` class with `animate-slide-in-up`
- **Delay**: 0.1s increments for sequential appearance
- **Duration**: 0.6s with cubic-bezier easing

### Hover Effects
- **Cards**: `transform: translateY(-2px)` with shadow enhancement
- **Buttons**: Scale effects on press
- **Duration**: 0.2-0.3s transitions

### Loading States
- **Shimmer**: `animate-shimmer` for skeleton loading
- **Pulse**: `animate-gentle-pulse` for status indicators
- **Spinner**: Standard loading spinner for actions

## Accessibility Standards

### Color Contrast
- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text**: 3:1 minimum contrast ratio
- **Interactive elements**: 3:1 minimum contrast ratio

### Focus Management
- **Focus outline**: 2px solid primary color
- **Skip links**: Available for keyboard navigation
- **Focus trapping**: Proper modal focus management

### Motion Preferences
- **Reduced motion**: Respects `prefers-reduced-motion` setting
- **High contrast**: Enhanced borders in high contrast mode

### ARIA Labels
- **Badges**: Include status information
- **Buttons**: Clear action descriptions
- **Panels**: Proper heading hierarchy

## Responsive Breakpoints

```css
/* Mobile First */
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### Grid Adjustments
- **Mobile**: Single column layouts
- **Tablet**: 2-column stats, stacked main content
- **Desktop**: 4-column stats, 3-column main content
- **Large**: 2-column bottom section

## Icon Usage

### Lucide Icons
- **Size**: 16px (w-4 h-4) for small, 20px (w-5 h-5) for medium, 24px (w-6 h-6) for large
- **Color**: Inherit from parent or use semantic colors
- **Consistency**: Use same icon for same actions across components

### Icon Placement
- **Navigation**: Left-aligned in sidebar items
- **Headers**: Left of titles in panels
- **Actions**: Within buttons or as standalone controls
- **Status**: Small indicators with appropriate colors

## Implementation Notes

### CSS Custom Properties
- All design tokens available as CSS variables
- Consistent naming convention: `--category-modifier`
- Fallback values for browser compatibility

### Component Architecture
- **Composition**: Prefer composition over inheritance
- **Props-based**: Configuration through props, not CSS classes
- **TypeScript**: Full type safety for all components
- **Accessibility**: Built-in ARIA support

### Performance Considerations
- **Bundle size**: Tree-shake unused components
- **Animations**: Use CSS transforms over layout properties
- **Images**: Optimize and lazy load where appropriate
- **Caching**: Leverage CSS custom properties for theme switching

## Maintenance Guidelines

### Adding New Components
1. Check existing patterns in this guide
2. Use established color tokens and spacing
3. Include accessibility features
4. Add TypeScript interfaces
5. Update this style guide

### Modifying Existing Styles
1. Test across all breakpoints
2. Verify accessibility compliance
3. Update documentation
4. Consider impact on existing components

### Color Additions
1. Use established color scales
2. Ensure WCAG compliance
3. Add to CSS custom properties
4. Update semantic color mappings

This style guide should be updated whenever new patterns are established or existing ones are modified to maintain consistency across the Xseller.ai dashboard.