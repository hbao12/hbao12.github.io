# Design System Documentation: The Nocturnal Portfolio

## 1. Overview & Creative North Star
**Creative North Star: The Digital Curator**
This design system is built to move away from the "template" aesthetic of standard portfolios and toward a high-end, editorial experience. It treats digital space like a physical gallery—dark, focused, and intentionally quiet. By leveraging deep tonal shifts instead of rigid lines and using dramatic typographic scales, we create an environment that feels both professional and tech-forward. 

We break the standard grid through **intentional asymmetry**. Hero sections should feature overlapping elements—such as a large `display-lg` headline partially obscured by a glass-morphic image container—to create depth. The goal is a "Signature" look: a layout that feels bespoke, where every element is positioned with the precision of a luxury magazine layout.

---

## 2. Colors & Surface Philosophy
The palette is rooted in the depth of `background: #0e0e11`. We use the primary deep purple (`#8A2BE2`) not as a filler, but as a high-energy pulse across a monochromatic landscape.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning or containment. Traditional lines create "visual noise" that feels cheap. Instead, define boundaries through:
- **Tonal Shifts:** Transitioning from `surface` to `surface-container-low`.
- **Vertical Air:** Utilizing the spacing scale to create distinct content blocks.
- **Soft Gradients:** Using a subtle linear-gradient (e.g., `surface` to `surface-container-lowest`) to guide the eye.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked physical layers.
- **Level 0 (Base):** `surface` (#0e0e11).
- **Level 1 (Sections):** `surface-container-low` (#131316) for large content areas.
- **Level 2 (Cards/Modules):** `surface-container` (#19191d) or `surface-container-high` (#1f1f23) for interactive elements.
- **Level 3 (Floating/Active):** `surface-bright` (#2c2c30) for high-priority overlays.

### The "Glass & Gradient" Rule
To achieve a "Tech-Forward" feel, use **Glassmorphism** for floating elements (nav bars, project tags). Use `surface-container` at 60% opacity with a `backdrop-filter: blur(20px)`. 
**Signature Textures:** For primary CTAs, do not use flat hex codes. Apply a subtle diagonal gradient: `linear-gradient(135deg, #ca98ff 0%, #8A2BE2 100%)`. This adds "soul" and a sense of illumination.

---

## 3. Typography
We utilize a dual-font strategy to balance editorial flair with technical precision.

*   **Display & Headlines (Manrope):** This is your "voice." Use `display-lg` for hero statements. Tighten the letter-spacing (-0.04em) and use `primary` color sparingly for emphasis words to create high-contrast focal points.
*   **Body & Labels (Inter):** This is your "utility." Inter provides the "Clean Sans-Serif" look. Use `body-lg` for project descriptions to ensure maximum readability against the dark background.
*   **The Hierarchy Goal:** Create a "Typographic Waterfall." A massive `display-lg` headline should be followed by a significantly smaller `title-md` subhead. This intentional gap in scale conveys confidence and authority.

---

## 4. Elevation & Depth
In this design system, depth is felt, not seen.

*   **The Layering Principle:** Depth must be achieved by "stacking" the surface-container tiers. For example, place a `surface-container-lowest` card on a `surface-container-low` section to create a soft, natural "inset" look.
*   **Ambient Shadows:** If a "floating" effect is required, use extra-diffused shadows. 
    *   *Spec:* `0px 20px 40px rgba(0, 0, 0, 0.4)`. The shadow must never be pure grey; it should feel like the absence of light from the deep purple primary.
*   **The "Ghost Border" Fallback:** If a container absolutely needs a boundary (e.g., in a complex data grid), use a **Ghost Border**: `outline-variant` (#48474b) at 15% opacity. It should be nearly invisible, felt only when the eye seeks a boundary.

---

## 5. Components

### Buttons
- **Primary:** High-contrast. Background: `primary_container` (#c185ff) gradient. Text: `on_primary_container`. Shape: `md` (0.375rem).
- **Secondary (The Glass Button):** Semi-transparent `surface-variant` with a `backdrop-blur`. No border.
- **Tertiary:** Text-only in `primary` with a `label-md` weight. On hover, a subtle `surface-container-high` background bloom.

### Cards (Project Showcase)
- **Rules:** Forbid the use of divider lines. 
- **Structure:** Use `surface-container-low` as the base. Content is separated by large padding (2rem+). Use `primary` for small `label-sm` category tags (all caps, +0.1em tracking).

### Input Fields
- **Base:** `surface-container-highest` (#25252a). 
- **Active State:** Change background to `surface-bright` and add a "Ghost Border" of `primary` at 30% opacity. 
- **Typography:** Placeholder text must use `on_surface_variant`.

### Selection Chips
- Use `full` roundedness (pill shape). 
- Unselected: `surface-container-high`.
- Selected: `primary` background with `on_primary` text.

---

## 6. Do's and Don'ts

### Do:
- **Do use "Breathable" Spacing:** If you think there’s enough margin, double it. Minimalism requires negative space to feel premium.
- **Do use Asymmetric Compositions:** Offset images from text blocks to create a custom, editorial feel.
- **Do leverage High Contrast:** Ensure `on_surface` text (#f0edf1) is used for all primary reading to maintain accessibility on the `#0e0e11` background.

### Don't:
- **Don't use 100% Opacity Borders:** They break the "Liquid" feel of the dark mode theme.
- **Don't use pure Black (#000000) for sections:** Stick to the `surface` and `surface-container` tiers to keep the "Deep Purple" tonal atmosphere.
- **Don't use Default Drop Shadows:** Standard CSS `box-shadow` is too harsh. Always use the Ambient Shadow spec.
- **Don't use Dividers:** Avoid horizontal rules (`<hr>`). Use a 64px or 128px vertical gap instead.