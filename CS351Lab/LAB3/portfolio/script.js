// Mobile Navigation Toggle
const burger = document.querySelector('.burger');
const nav = document.querySelector('.nav-links');
const navLinks = document.querySelectorAll('.nav-links li');

burger.addEventListener('click', () => {
    // Toggle Nav
    nav.classList.toggle('nav-active');

    // Burger Animation
    burger.classList.toggle('toggle');
    const line1 = document.querySelector('.line1');
    const line2 = document.querySelector('.line2');
    const line3 = document.querySelector('.line3');
    
    if(nav.classList.contains('nav-active')){
        line1.style.transform = 'rotate(-45deg) translate(-5px, 6px)';
        line2.style.opacity = '0';
        line3.style.transform = 'rotate(45deg) translate(-5px, -6px)';
    } else {
        line1.style.transform = 'none';
        line2.style.opacity = '1';
        line3.style.transform = 'none';
    }
});

// Close mobile menu when a link is clicked
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        if(nav.classList.contains('nav-active')) {
            burger.click();
        }
    });
});

// Smooth Scrolling for Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if(target){
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add scroll event listener to change nav styling on scroll
window.addEventListener('scroll', () => {
    const navBar = document.querySelector('nav');
    if (window.scrollY > 50) {
        navBar.style.background = 'rgba(15, 23, 42, 0.9)';
        navBar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.2)';
    } else {
        navBar.style.background = 'rgba(15, 23, 42, 0.7)';
        navBar.style.boxShadow = 'none';
    }
});
