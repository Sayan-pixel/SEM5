// --- LENIS SMOOTH SCROLLING ---
const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smooth: true,
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// --- GSAP SETUP ---
gsap.registerPlugin(ScrollTrigger);

// Sync Lenis with GSAP ScrollTrigger
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});
gsap.ticker.lagSmoothing(0, 0);


// --- CUSTOM MAGNETIC CURSOR ---
const cursor = document.querySelector('.cursor');
const cursorFollower = document.querySelector('.cursor-follower');
const magnetics = document.querySelectorAll('.magnetic');

document.addEventListener('mousemove', (e) => {
    gsap.to(cursor, { x: e.clientX, y: e.clientY, duration: 0 });
    gsap.to(cursorFollower, { x: e.clientX, y: e.clientY, duration: 0.3 });
});

magnetics.forEach((el) => {
    el.addEventListener('mouseenter', () => {
        cursorFollower.classList.add('active');
    });
    el.addEventListener('mouseleave', () => {
        cursorFollower.classList.remove('active');
        gsap.to(el, { x: 0, y: 0, duration: 0.3 });
    });
    el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const x = (e.clientX - rect.left - rect.width / 2) * 0.3;
        const y = (e.clientY - rect.top - rect.height / 2) * 0.3;
        gsap.to(el, { x: x, y: y, duration: 0.3 });
    });
});


// --- THREE.JS IMMERSIVE BACKGROUND ---
const canvas = document.getElementById('webgl-canvas');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// Create Particles (Neural Network / Stars)
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1000;
const posArray = new Float32Array(particlesCount * 3);

for(let i = 0; i < particlesCount * 3; i++) {
    // Distribute particles in a wide 3D space
    posArray[i] = (Math.random() - 0.5) * 20;
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

const material = new THREE.PointsMaterial({
    size: 0.02,
    color: 0x5e6ad2, // Theme accent color
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending
});

const particlesMesh = new THREE.Points(particlesGeometry, material);
scene.add(particlesMesh);
camera.position.z = 5;

// Mouse Interaction variables
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
    // Normalize mouse coordinates from -0.5 to 0.5
    mouseX = (event.clientX / window.innerWidth) - 0.5;
    mouseY = (event.clientY / window.innerHeight) - 0.5;
});

// Three.js Animation Loop
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime();

    // Slow rotation over time
    particlesMesh.rotation.y = elapsedTime * 0.05;
    particlesMesh.rotation.x = elapsedTime * 0.02;

    // Interactive mouse parallax effect
    particlesMesh.position.x += (mouseX * 1.5 - particlesMesh.position.x) * 0.05;
    particlesMesh.position.y += (-mouseY * 1.5 - particlesMesh.position.y) * 0.05;

    renderer.render(scene, camera);
}
animate();

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});


// --- GSAP SCROLL ANIMATIONS ---

// 1. Fade Up Elements
gsap.utils.toArray('.gsap-fade-up').forEach(element => {
    gsap.to(element, {
        scrollTrigger: {
            trigger: element,
            start: "top 85%", // Trigger when top of element hits 85% of viewport
            toggleActions: "play none none reverse"
        },
        opacity: 1,
        y: 0,
        duration: 1.2,
        ease: "power3.out"
    });
});

// 2. Horizontal Scroll for Projects Section
const projectsWrapper = document.querySelector('.projects-wrapper');
if (projectsWrapper) {
    // Calculate how far to move horizontally
    function getScrollAmount() {
        let wrapperWidth = projectsWrapper.scrollWidth;
        return -(wrapperWidth - window.innerWidth);
    }

    const tween = gsap.to(projectsWrapper, {
        x: getScrollAmount,
        ease: "none"
    });

    ScrollTrigger.create({
        trigger: ".projects-container",
        start: "top top",
        end: () => `+=${getScrollAmount() * -1}`,
        pin: true,
        animation: tween,
        scrub: 1,
        invalidateOnRefresh: true
    });
}
