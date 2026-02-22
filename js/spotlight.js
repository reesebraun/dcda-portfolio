/**
 * Featured Project Spotlight - Vanilla JavaScript
 * Handles thumbnail switching with smooth fade + slide animations
 */

// Project data array - easy to update with new projects
const projects = [
    {
        title: 'AI Tool Evaluation',
        description: 'A comprehensive analysis of AI tools and their capabilities, exploring how artificial intelligence is transforming digital culture and everyday workflows.',
        image: 'images/Screenshot 2026-02-22 at 1.28.34 PM.png',
        link: 'lab02.html',
        alt: 'AI Tool Evaluation project preview'
    },
    {
        title: 'Tufte Critique',
        description: 'Critical analysis of a data visualization using Edward Tufte\'s principles of graphical excellence, examining clarity, precision, and visual integrity.',
        image: 'images/1112-rome-plastic-bottles.png',
        link: 'lab03.html',
        alt: 'Tufte Critique project preview'
    },
    {
        title: 'Tableau Visualization',
        description: 'Interactive data visualization created with Tableau Public, exploring patterns in real-world data through engaging charts and dashboards.',
        image: 'images/Screenshot 2026-02-22 at 1.31.35 PM.png',
        link: 'lab04.html',
        alt: 'Tableau Visualization project preview'
    },
    {
        title: 'Hometown Map',
        description: 'Interactive Folium map showcasing meaningful locations from my hometown, combining geospatial data with personal storytelling and reflections.',
        image: 'images/mapbox_image.png',
        link: 'hometown-map.html',
        alt: 'Hometown Map project preview'
    }
];

// Get DOM elements
const featuredContainer = document.getElementById('spotlightFeatured');
const featuredImage = document.getElementById('featuredImage');
const featuredTitle = document.getElementById('featuredTitle');
const featuredDescription = document.getElementById('featuredDescription');
const featuredLink = document.getElementById('featuredLink');
const thumbnailButtons = document.querySelectorAll('.thumbnail-btn');

let currentIndex = 0;
let isAnimating = false; // Prevent double-clicks during animation

/**
 * Updates the featured project content
 * @param {number} index - Index of the project to display
 */
function updateFeaturedProject(index) {
    // Prevent multiple animations at once
    if (isAnimating || index === currentIndex) return;
    
    isAnimating = true;
    const project = projects[index];
    
    // Add fade-out and slide-out animation
    featuredContainer.classList.add('fade-out');
    
    // After fade-out completes, update content and fade back in
    setTimeout(() => {
        // Update content
        featuredImage.src = project.image;
        featuredImage.alt = project.alt;
        featuredTitle.textContent = project.title;
        featuredDescription.textContent = project.description;
        featuredLink.href = project.link;
        
        // Remove fade-out and let content fade back in
        featuredContainer.classList.remove('fade-out');
        
        // Update active thumbnail
        thumbnailButtons.forEach((btn, i) => {
            if (i === index) {
                btn.classList.add('active');
                btn.setAttribute('aria-pressed', 'true');
            } else {
                btn.classList.remove('active');
                btn.setAttribute('aria-pressed', 'false');
            }
        });
        
        currentIndex = index;
        
        // Re-enable interactions after animation
        setTimeout(() => {
            isAnimating = false;
        }, 300);
    }, 300); // Match CSS transition duration
}

/**
 * Initialize event listeners for thumbnails
 */
function initSpotlight() {
    thumbnailButtons.forEach((button, index) => {
        // Click handler
        button.addEventListener('click', () => {
            updateFeaturedProject(index);
        });
        
        // Keyboard navigation (Enter and Space)
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                updateFeaturedProject(index);
            }
        });
        
        // Set initial aria-pressed state
        if (index === 0) {
            button.setAttribute('aria-pressed', 'true');
        } else {
            button.setAttribute('aria-pressed', 'false');
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSpotlight);
} else {
    initSpotlight();
}
