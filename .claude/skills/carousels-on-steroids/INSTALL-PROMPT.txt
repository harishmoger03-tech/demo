MOTION GRAPHIC CAROUSELS ON STEROIDS: 2 free Claude Code kits

This folder has two zips. Download one or both:

  1. carousels-on-steroids-skill.zip  →  MOTION GRAPHICS carousels
     Every slide is a looping motion-graphics video and the whole post is one continuous scene:
     smoke, sparks, ingredients and your product cross the edges as people swipe.
     (Example inside: the "Ember & Bun · The Inferno" burger launch.)

  2. Carousel-Kit.zip  →  STYLE SHEET carousels
     Finished static slides (PNG) in a ready-made look: 6 style sheets (Midnight, Archival, Celestial,
     Chalk, Sun-Faded, Sky-Blue), or built from your own photos, or from your own style-sheet image,
     with an optional mascot / avatar character.

One prompt installs whatever you downloaded, then asks which kind you want to make.

Cost: $0 by default for both. Everything is made on your own computer.
Optional: AI images with Higgsfield (connector) or kie.ai (API key, style-sheet kit). Claude always
shows you the cost and asks before spending a single credit.
Needs: Claude Code and Python 3.9+. Motion graphics also needs Google Chrome, Node.js 22+ and ffmpeg.
Claude installs anything that's missing, free.

HOW TO INSTALL (2 minutes)
1. Download the zip(s). Don't unzip them.
2. Open Claude Code (in any folder).
3. Copy everything between the lines below, paste it into Claude Code, and press Enter.

------------------------------------------------------------ copy from here
Install my free carousel kits and make sure they work, then ask me which kind of carousel I want and make my first one.

1. FIND THEM. I downloaded one or both of these (probably from Skool or Google Drive). Look in ~/Downloads first, then ~/Desktop. Each may be a .zip, a folder, or a .zip inside another .zip; unzip into a temporary folder as needed.
   - MOTION GRAPHICS: "carousels-on-steroids-skill.zip". It's the folder whose SKILL.md starts with "name: carousels-on-steroids".
   - STYLE SHEET: "Carousel-Kit.zip". It's the folder that contains ".claude/skills/carousel/SKILL.md" next to a "carousel" folder.
   Tell me which ones you found. If you can't find either, ask me where they are.

2. INSTALL THE MOTION GRAPHICS SKILL (if I downloaded it) to ~/.claude/skills/carousels-on-steroids/ (on Windows: %USERPROFILE%\.claude\skills\carousels-on-steroids). If that folder already exists, move the old one OUT of the skills folder first, to ~/.claude/skill-backups/carousels-on-steroids-<today's date> (a backup left inside ~/.claude/skills/ loads as a second, duplicate skill). Copy the whole folder, then run: chmod +x ~/.claude/skills/carousels-on-steroids/scripts/*
   Then run  bash ~/.claude/skills/carousels-on-steroids/scripts/setup.sh  until it prints "All set". If anything is missing, install it the free, official way for my computer (Node.js LTS from nodejs.org or Homebrew; ffmpeg with Homebrew, winget or apt; Python from python.org; Chrome from google.com/chrome). Ask me before any step that needs my password.
   Then run  bash ~/.claude/skills/carousels-on-steroids/scripts/selftest.sh  until it prints "SELFTEST PASSED", and look at ~/carousels-on-steroids/motion/_selftest/renders/qa/contact-sheet.jpg yourself.

3. INSTALL THE STYLE SHEET KIT (if I downloaded it) into my carousel workspace ~/carousels-on-steroids/ : copy the kit's ".claude" and "carousel" folders and its ".env.example" into ~/carousels-on-steroids/. If ~/carousels-on-steroids/carousel or ~/carousels-on-steroids/.claude/skills/carousel already exists, show me what's there and ask before overwriting anything. Then, inside ~/carousels-on-steroids, run  python3 carousel/scripts/doctor.py --fix  and keep going until it says READY. If Python itself is missing, tell me exactly what to install.

4. ASK ME WHICH KIND I want to make now (skip this if only one kit is installed):
   A) MOTION GRAPHICS: every slide moves (MP4 videos), one continuous scene across the swipe, my product drawn in code or as AI product shots.
   B) STYLE SHEET: finished static slides in a ready-made style sheet, or my own photos, or my own style-sheet image, with an optional mascot / avatar. To show me the styles, open the gallery (cd ~/carousels-on-steroids && python3 carousel/scripts/gallery.py).

5. INTERVIEW ME AND MAKE IT with the kit I picked. If I give you a website or Instagram handle, look at it.
   - A (motion graphics): read ~/.claude/skills/carousels-on-steroids/SKILL.md and its references/intake.md and follow them. Ask me the intake questions in ONE message, numbered, each with its default: my business, the topic (mine, or you find 3 angles), the goal / call to action, budget ($0, or AI product shots with Higgsfield or another AI tool I've connected), my real images, my style (brand colours, fonts, a style sheet, posts I love), the format and the words. Wait for my answers. If I choose AI images and the tool isn't connected yet, tell me exactly how to connect it and wait. Then show me the slide plan and the copy on one screen and ask "Build it?". Build it in ~/carousels-on-steroids/motion/<short-name>/, check every slide yourself (contact sheet, loop seams, slide edges, big moments), render the MP4s, open the preview for me, and give me the MP4s in posting order plus a caption.
   - B (style sheet): work inside ~/carousels-on-steroids. Read .claude/skills/carousel/SKILL.md and follow it from step 1: its questions (my Instagram handle, niche, topic, my own photos, facts, number of slides, logo), the style gallery, free or paid, the full plan and my approval, then the build. Look at every finished slide yourself before showing me, then show me the slides and give me a caption.

Rules: keep everything $0 unless I choose paid AI images, and before spending any credits (Higgsfield or kie.ai) show me the cost and wait for my "go". Only use images I own or give you. Don't change anything outside ~/.claude/skills/carousels-on-steroids, ~/.claude/skill-backups, ~/carousels-on-steroids and the free tools listed above. At the end, tell me how to start next time: for motion graphics, just ask for a motion-graphics carousel in any new Claude Code session; for style sheets, open Claude Code in ~/carousels-on-steroids and type /carousel. Remind me to start a new Claude Code session so the skills load by themselves.
------------------------------------------------------------ to here

AFTER INSTALLING (new session), TRY:
Motion graphics (any folder):
- "Make me a motion-graphics carousel for my coffee shop's new iced brown-sugar latte. $0. Find the angle."
- "Motion carousel for my app launch. Use my screenshots in ~/Desktop/app-shots and my colours #0B0B0F and #7CFF4F."
- "Use Higgsfield for real product shots of my sneakers, then build the motion carousel around them."
Style sheet (open Claude Code in ~/carousels-on-steroids):
- "/carousel 3 pricing mistakes roofers make, in the Archival style, free."
- "/carousel Use my photos in ~/Desktop/trip and make a travel-journal carousel."
- "/carousel Here's my own style sheet (image attached). Build a new style from it and make a carousel about my launch."
