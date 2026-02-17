/**
 * Hamburger Menu Toggle
 * Handles mobile navigation menu opening/closing
 */

// Get DOM elements
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const body = document.body;

// Toggle menu function
function toggleMenu() {
    const isOpen = hamburger.classList.contains('active');
    
    // Toggle classes
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
    body.classList.toggle('menu-open');
    
    // Update ARIA attribute for accessibility
    hamburger.setAttribute('aria-expanded', !isOpen);
}

// Click event listener
hamburger.addEventListener('click', toggleMenu);

// Close menu when clicking on a link (smooth UX)
const navLinks = document.querySelectorAll('.nav-menu a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (navMenu.classList.contains('active')) {
            toggleMenu();
        }
    });
});

// Close menu when clicking outside (on the overlay)
document.addEventListener('click', (e) => {
    const isClickInsideNav = navMenu.contains(e.target);
    const isClickOnHamburger = hamburger.contains(e.target);
    
    if (!isClickInsideNav && !isClickOnHamburger && navMenu.classList.contains('active')) {
        toggleMenu();
    }
});

// Close menu on ESC key press
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navMenu.classList.contains('active')) {
        toggleMenu();
    }
});
