# David Heckhoff Portfolio - Website Analysis
(URL: https://david-hckh.com/)

This document contains a comprehensive, point-by-point breakdown of the website's design, layout, interactions, and structure to serve as a blueprint for recreating the same website.

## 1. Technical Stack & SEO Information
- **Framework/Bundler:** The site appears to be built with a modern JavaScript framework (likely Vue or React) and bundled with Vite (implied by `<script type="module" crossorigin src="/chunks/index-BI8DnNgg.js">`).
- **3D Graphics:** Uses Three.js & WebGL for the interactive 3D canvas that overlays/integrates with the DOM.
- **Styling:** Custom CSS, possibly pre-processed with SCSS/SASS (`/assets/BYmwxED6.css`), emphasizing a clean layout and responsive grid design.
- **Fonts:** Uses "Urbanist" (Weights 400, 700, 900) for standard typography and "Pro Font Windows" (Weights 400, 700) for code/monospace text.
- **Theme Colors:** The primary light theme color is `#dfd1bc` or `#EFECE6` (a warm off-white/cream).
- **SEO Elements:**
  - **Title:** `David Heckhoff - Web Developer (WebGL & Node.js)`
  - **Meta Description:** `Web developer creating interactive 3D web experiences and real-time apps with WebGL, TypeScript, and Node.js for high-performance, engaging websites.`
  - Open Graph (OG) and Twitter Card tags are correctly configured with preview images (`og-image.webp`, `twitter-image.webp`).

## 2. Visual Aesthetics & General Theme
- **Color Palette:**
  - **Light Mode (Default):** Warm cream/beige background. Minimalist, clean, and friendly.
  - **Dark Mode (Scroll Transition):** Dark navy blue space/grid environment. Represents a transition from a physical desk to a digital/coding space.
- **Typography:** Sans-serif, bold geometric headings (Urbanist font), and very clean, legible body text.
- **3D Elements:** High-quality low-poly/chibi style 3D models (a character resembling the developer, a computer desk setup, cardboard boxes, scattered letters).

## 3. Layout Structure & Navigation
- **Global Header (Fixed):**
  - **Left:** Title "David Heckhoff" and an angled "WEB DEVELOPER" badge (white text on a dark blue background). When the user scrolls past the hero section, a cube logo containing `<>` appears on the far left.
  - **Center:** Navigation Links: "ABOUT", "PROJECTS", "CONTACT". Active links get highlighted with a blue background capsule shape.
  - **Right:** An orange "GET IN TOUCH" button with white text, and a circular sound toggle button (dark grey background with a speaker icon) for background music.
- **Global Preloader:**
  - An SVG mask animation showing a stylized "D" logo filling up vertically as the site loads.

## 4. Section-by-Section Breakdown

### A. Home Hero Section
- **Left Column:** Large bold text "David Heckhoff", followed by an angled "WEB DEVELOPER" badge underneath.
- **Right Column:** A 3D desk environment featuring the character sitting and typing on a computer.
- **Bottom Center:** A scrolling mouse indicator icon prompting the user to scroll down.

### B. About Section & Scroll Transition 1 (The "Digital Space")
- **Transition Animation:**
  - Scrolling down triggers a smooth background color change from cream to dark navy blue.
  - Header links adapt to the dark theme (`header-link-dark`).
  - The 3D desk zooms out and moves upwards/out of view.
  - The 3D character stands up and is positioned on a circular blue platform with a numerical loading indicator incrementing from `000` to `100`.
  - A glowing neon blue wireframe hologram effect starts from the character's feet and moves upwards until the entire character becomes a blue wireframe hologram at `100%`.
- **Content (Floating UI Elements):**
  - The character stands center-stage on a grid-like blue perspective floor.
  - Floating info boxes appear with line connectors pointing to the character as you scroll:
    - **Box 1 (Left, ~20% scroll):** Header: Sayan Shit Pre-finalist CSE @IIITG
    Content: "📍Medinipur, West Bengal, India

    Computer Science student at IIIT Guwahati, passionate about software development, problem solving, and emerging technologies... "read more..." link."
    <!-- I enjoy turning ideas into practical projects and continuously learning through hands-on experience. -->

    - **Box 2 (Left, ~40% scroll):** Header: Technical Skills
     Content: "Languages:
    Java, Python...

    Frameworks & Libraries : 
    React.js, Next.js...

    Tools & Technologies :
    Git, GitHub...

    Relevant Coursework:..."  "read more..." link.
    - **Box 3 (Left, ~60% scroll):** Header: "Projects", Content: 
    Project 1 — Lunar Lander AI.
    Project 2 — Real Estate Management System 
    "read more..." link.
    - **Box 4 (Right, ~80% scroll):** Header: DSA  and Competitive Programming ,
    "Content : add one to two line context"
    - **Box 5 (Right, ~100% scroll):** Header: Extracurricular Activities, Content : "I&E Cell — IIIT Guwahati

    Event Management Team

    Highlight: (using bulletins)

    Event coordination
    Teamwork
    Collaboration
    Organizational experience
    Innovation/entrepreneurship ecosystem
    "

### C. Projects Section & Scroll Transition 2
- **Transition Animation:**
  - The background transitions back to the light cream/beige theme.
  - The "PROJECTS" nav item in the header gets the blue capsule highlight.
- **Layout & Content:**
  - A slanted "SELECTED" badge sits on top of the section title "Projects" (large bold text).
  - A 2x3 grid of project cards:
    1. **CubeWar:** Multiplayer strategy game. (Link: `/project/cubewar`)
    2. **Quibbo:** Multiplayer gaming platform. (Link: `/project/quibbo`)
    3. **Sharkie:** 2D adventure game. (Link: `/project/sharkie`)
    4. **WebGL Particles:** Dynamic 3D particles. (Link: `/project/particles`)
    5. **Pokédex:** Open-source learning project. (Link: `/project/pokedex`)
    6. **New Project Card:** Shows a "+" icon with the text "Start a new project". (Link: `mailto:me@david-hckh.com`)

### D. Contact Section & Scroll Transition 3
- **Layout & Content:**
  - **Left Column:** Heading "Let's work together!".
  - **Below Heading:** A row of 4 interactive circular social links:
    - Email Envelope (`mailto:me@david-hckh.com`)
    - GitHub (`https://github.com/davidhckh`)
    - LinkedIn (`https://www.linkedin.com/in/david-heckhoff/`)
    - X/Twitter (`https://x.com/DavidHckh`)
  - **Right Column (3D Interactive Area):** The 3D character stands next to cardboard boxes.
    - If scrolled up slightly, the character is sleeping (eyes closed, animated "Z Z Z" floating).
    - If fully scrolled down, the character wakes up (stands up, arms crossed, smiling, letters scattered on the floor).

### E. Footer Layout
- **Center:** A back-to-top button (circular with an up-arrow icon). Clicking it scrolls smoothly back to the hero section.
- **Right:**
  - "Privacy" link (`/privacy`)
  - "Legal Notice" link (`/legal`)
  - Language toggle button ("DE" / "EN" to switch languages, styled with a thin border).
- **Bottom Center:**
  - "Music produced by HM Surf" (Link: `https://soundcloud.com/hmsurf`)
  - Copyright info: "© 2026 David Heckhoff"

## 5. Additional Features & Interactive Details
- **Multi-language Support (i18n):** The entire site toggles between English and German via the footer button. The URL path updates for subpages (e.g., `/de/privacy`).
- **Sound/Music:** Background music can be toggled on/off using the speaker button in the top right header.
- **Project Detail Pages:** Each project card clicks through to a dedicated subpage detailing the project, maintaining the consistent styling and navigation header, which includes a "back" button to return home.
- **Responsive Animations:** The 3D interactions are tied to scroll progress using a library (likely GSAP ScrollTrigger or similar) synchronizing DOM scroll position with Three.js camera/model animations.
