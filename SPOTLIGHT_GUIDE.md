# Featured Project Spotlight - Implementation Guide

## Overview
This feature adds an interactive project showcase to your homepage with smooth animations and full accessibility support. Visitors can click thumbnail buttons to dynamically update the featured project without page reloads.

## Files Created/Modified

### 1. HTML Structure (`index.html`)
Added a new `#featured-project` section with:
- **Featured Area**: Large image, title, description, and "View Project" button
- **Thumbnail Navigation**: 4 button elements with small images and labels
- Each thumbnail has:
  - `data-project` attribute for identifying which project to show
  - `aria-label` for screen reader users
  - Empty alt text on thumbnail images (decorative, label provides context)
  - Meaningful alt text on the featured image

### 2. CSS Styling (`css/styles.css`)
Key features:
- **Grid Layout**: Featured area uses CSS Grid (2 columns on desktop, stacks on mobile)
- **Animations**: `.fade-out` class creates smooth transitions using `opacity` and `transform`
- **Active State**: Selected thumbnail gets colored border and background gradient
- **Focus Styles**: Clear `:focus-visible` outlines for keyboard navigation
- **Responsive**: Adjusts thumbnail grid from 4 columns → 2 columns on smaller screens

### 3. JavaScript Logic (`js/spotlight.js`)
Core components:

#### Projects Data Array
```javascript
const projects = [
    {
        title: 'AI Tool Evaluation',
        description: '...',
        image: 'images/ai-evaluation-preview.jpg',
        link: 'lab02.html',
        alt: 'AI Tool Evaluation project preview'
    },
    // ... more projects
];
```
Easy to update! Just modify this array to change content.

#### How It Works

1. **Initialization** (`initSpotlight()`)
   - Attaches click handlers to all thumbnail buttons
   - Adds keyboard support (Enter and Space keys)
   - Sets initial `aria-pressed` states

2. **Project Switching** (`updateFeaturedProject(index)`)
   - **Prevents double-clicks**: Uses `isAnimating` flag
   - **Animation sequence**:
     1. Adds `.fade-out` class (fades out, slides up slightly)
     2. Waits 300ms for animation to complete
     3. Updates all content (image, title, description, link)
     4. Removes `.fade-out` class (fades back in)
     5. Updates active thumbnail styling
     6. Re-enables interactions

3. **Accessibility Features**
   - Uses `<button>` elements (not divs!)
   - Keyboard operable (Enter/Space keys)
   - `aria-pressed` attribute shows current selection
   - `aria-label` provides clear button purpose
   - Clear focus indicators via `:focus-visible`

## How to Customize

### Adding New Projects
Edit `js/spotlight.js`:
```javascript
const projects = [
    // ... existing projects
    {
        title: 'New Project',
        description: 'Your description here',
        image: 'images/new-project-preview.jpg',
        link: 'new-project.html',
        alt: 'New Project preview showing...'
    }
];
```

Then add a new thumbnail button in `index.html`:
```html
<button 
    class="thumbnail-btn" 
    data-project="4"
    aria-label="Show New Project"
>
    <img src="images/new-project-preview.jpg" alt="">
    <span>New Project</span>
</button>
```

### Changing Animation Speed
In `css/styles.css`, adjust transition duration:
```css
.spotlight-featured {
    transition: opacity 0.3s ease, transform 0.3s ease;
    /* Change 0.3s to desired duration */
}
```

In `js/spotlight.js`, match the setTimeout values:
```javascript
setTimeout(() => {
    // ... update content
}, 300); // Match CSS duration in milliseconds
```

### Changing Colors
Edit CSS variables in `css/styles.css`:
```css
:root {
    --accent-color: #06b6d4;      /* Button color */
    --secondary-color: #3b82f6;   /* Active border color */
}
```

### Replacing Placeholder Images
Replace these images in the `images/` folder with actual project screenshots:
- `ai-evaluation-preview.jpg`
- `tufte-preview.jpg`
- `tableau-preview.jpg`
- `map-preview.jpg`

Recommended size: 600×400px (maintains 3:2 aspect ratio)

## Browser Compatibility
- Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- Uses vanilla JavaScript (no dependencies)
- CSS transitions supported everywhere
- Gracefully degrades if JavaScript is disabled (shows first project)

## Accessibility Testing Checklist
✅ Tab through thumbnails with keyboard  
✅ Activate with Enter or Space key  
✅ Clear focus indicators visible  
✅ Screen reader announces button labels  
✅ `aria-pressed` updates correctly  
✅ Images have meaningful alt text  

## Performance Notes
- Animation locked to prevent rapid clicking
- Uses CSS transforms (GPU accelerated)
- Smooth 60fps transitions
- Lightweight (~100 lines of JavaScript)

Enjoy your new Featured Project Spotlight! 🎨
