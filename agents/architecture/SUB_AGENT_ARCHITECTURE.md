# SUB-AGENT TEAM ARCHITECTURE
## 8 Sub-Agents × 8 Main Agents = 64 Specialized Support Agents

**Created:** 2025-11-07
**Purpose:** Deep specialization for every aspect of game development

---

## Architecture Overview

```
Main Agent (8)
├── Sub-Agent 1: Research/Analysis
├── Sub-Agent 2: Quality Control
├── Sub-Agent 3: Optimization
├── Sub-Agent 4: Documentation
├── Sub-Agent 5: Troubleshooting
├── Sub-Agent 6: Innovation/R&D
├── Sub-Agent 7: Cross-Team Liaison
└── Sub-Agent 8: Metrics/Reporting
```

---

# 1. 🎨 ART DIRECTOR AGENT

## Main Role: Visual consistency guardian

### Sub-Agent 1.1: **Style Analyst**
**Role:** Deep image analysis and style verification

**Capabilities:**
- Pixel-level comparison between reference and generated
- Color histogram analysis
- Style transfer validation
- Composition analysis
- Proportions checking

**Use Case:**
```
"Analyze this generated Meow Ping vs reference:
- Check facial feature positions (eyes, nose, mouth)
- Verify muscle definition matches
- Compare color values (allow ±5% tolerance)
- Measure proportions (head:body ratio)
- Generate detailed diff report"
```

---

### Sub-Agent 1.2: **Roast Master**
**Role:** Brutal honesty image critic (like we did!)

**Capabilities:**
- Identify what's wrong vs right
- Provide constructive criticism
- Rate consistency (1-100 scale)
- Suggest specific fixes
- No sugar-coating

**Use Case:**
```
"Roast this character sprite:
- Compare to reference
- List every difference
- Grade each aspect (face, colors, equipment)
- Explain WHY it's different
- Provide exact fix instructions"
```

---

### Sub-Agent 1.3: **Color Palette Guardian**
**Role:** Color consistency enforcer

**Capabilities:**
- Extract color palettes from images
- Verify hex values match specifications
- Detect color drift
- Suggest palette corrections
- Generate color swatches

**Use Case:**
```
"Check if this sprite uses approved colors:
- Extract all colors
- Compare to faction palette
- Flag any deviations
- Suggest corrections for out-of-palette colors"
```

---

### Sub-Agent 1.4: **Art Style Researcher**
**Role:** Find and analyze style references

**Capabilities:**
- Research comic book art styles
- Find reference images
- Analyze successful RTS game art
- Document style patterns
- Create mood boards

**Use Case:**
```
"Research comic book character designs for inspiration:
- Find 10 superhero cat references
- Analyze what makes them appealing
- Document common design patterns
- Create style guide additions"
```

---

### Sub-Agent 1.5: **Asset Cataloger**
**Role:** Maintain asset database and metadata

**Capabilities:**
- Auto-tag assets (character, pose, tier, etc.)
- Generate asset manifests
- Track versions and iterations
- Create searchable database
- Identify missing assets

**Use Case:**
```
"Catalog all character assets:
- List all existing characters
- Identify missing views (front/side/back)
- Track which have animations
- Generate gap analysis report"
```

---

### Sub-Agent 1.6: **Quality Benchmark Setter**
**Role:** Define and update quality standards

**Capabilities:**
- Establish quality metrics
- Create scoring rubrics
- Define approval thresholds
- Update standards based on learnings
- A/B test quality criteria

**Use Case:**
```
"Create quality rubric for character assets:
- Define measurable criteria
- Set pass/fail thresholds
- Create scoring system
- Document edge cases"
```

---

### Sub-Agent 1.7: **Cross-Team Style Liaison**
**Role:** Ensure style consistency across all pipelines

**Capabilities:**
- Review environment assets for character style match
- Verify UI elements match game art style
- Coordinate color palettes across teams
- Ensure VFX matches art direction

**Use Case:**
```
"Review environment assets from Environment Pipeline:
- Do building styles match character art?
- Are colors cohesive?
- Does shading style match?
- Provide feedback for consistency"
```

---

### Sub-Agent 1.8: **Art Direction Reporter**
**Role:** Track and report art pipeline metrics

**Capabilities:**
- Approval rate tracking
- Common rejection reasons
- Time-to-approval metrics
- Quality trend analysis
- Generate weekly reports

**Use Case:**
```
"Generate weekly art report:
- Assets reviewed: 47
- Approval rate: 89%
- Top rejection reasons
- Quality trends
- Recommendations for improvement"
```

---

# 2. 🐱 CHARACTER PIPELINE AGENT

## Main Role: Character asset generation specialist

### Sub-Agent 2.1: **Workflow Optimizer**
**Role:** Fine-tune ComfyUI settings for specific cases

**Capabilities:**
- A/B test workflow parameters
- Find optimal settings for edge cases
- Document parameter relationships
- Create setting presets
- Benchmark generation quality

**Use Case:**
```
"Find optimal settings for 'muscular cat with cape':
- Test denoise 0.30-0.50 in 0.05 increments
- Test IP-Adapter 0.3-0.6
- Generate quality scores for each combo
- Recommend best settings"
```

---

### Sub-Agent 2.2: **Prompt Engineer**
**Role:** Craft perfect prompts for specific outcomes

**Capabilities:**
- Analyze successful prompts
- Test prompt variations
- Build prompt templates
- Optimize keyword ordering
- Negative prompt strategy

**Use Case:**
```
"Create optimal prompt for red cape character:
- Test keyword variations
- Find words that trigger red cape best
- Test negative prompts for avoiding blue
- Document winning combination"
```

---

### Sub-Agent 2.3: **Generation Debugger**
**Role:** Diagnose and fix generation failures

**Capabilities:**
- Analyze error logs
- Identify root causes (memory, settings, files)
- Provide step-by-step fixes
- Document solutions
- Predict potential issues

**Use Case:**
```
"Generation failed with memory error:
- Check reference image size
- Verify ImageScale node settings
- Check available RAM
- Suggest resolution (resize input, restart ComfyUI)
- Document fix for future"
```

---

### Sub-Agent 2.4: **Batch Processor**
**Role:** Automate bulk generation tasks

**Capabilities:**
- Generate multiple variations at once
- Queue management
- Parallel processing coordination
- Progress tracking
- Error handling for batch jobs

**Use Case:**
```
"Generate all views for Meow Ping Tier 2:
- Queue: front, side, back, 3quarter
- Use equipment_variations workflow
- Same settings for all
- Auto-submit to Art Director when complete
- Handle any failures gracefully"
```

---

### Sub-Agent 2.5: **Reference Image Analyst**
**Role:** Analyze reference images for generation strategy

**Capabilities:**
- Detect image resolution and format
- Identify pose complexity
- Analyze color distribution
- Predict generation difficulty
- Recommend preprocessing steps

**Use Case:**
```
"Analyze this reference image:
- Resolution: 2048x1536 (needs resize)
- Pose: Complex action pose (use animation workflow)
- Colors: High saturation (good for cloning)
- Recommendation: Resize to 512x512, use denoise 0.35"
```

---

### Sub-Agent 2.6: **Animation Frame Interpolator**
**Role:** Generate smooth animation transitions

**Capabilities:**
- Analyze keyframe requirements
- Generate in-between frames
- Ensure motion smoothness
- Verify frame consistency
- Create sprite sheets

**Use Case:**
```
"Create walk cycle for Warrior Cat:
- Keyframes: contact, down, passing, up
- Generate 2 in-betweens for each
- Total: 12 frames @ 12 FPS
- Verify character stays on-model
- Export as sprite sheet"
```

---

### Sub-Agent 2.7: **Pipeline Liaison**
**Role:** Coordinate with Art Director and Integration

**Capabilities:**
- Submit assets for review
- Track approval status
- Respond to feedback
- Coordinate revisions
- Update manifests

**Use Case:**
```
"Meow Ping Tier 2 generation complete:
- Submit 4 views to Art Director
- Track review status
- If rejected: parse feedback, adjust settings, regenerate
- If approved: notify Integration for import
- Update asset manifest"
```

---

### Sub-Agent 2.8: **Generation Metrics Tracker**
**Role:** Monitor pipeline performance

**Capabilities:**
- Track generation times
- Success/failure rates
- Quality scores over time
- Resource utilization
- Bottleneck identification

**Use Case:**
```
"Weekly pipeline report:
- Assets generated: 23
- Avg generation time: 38s
- Success rate: 96%
- Most common failure: memory (2 times)
- Recommendation: Increase batch size optimization"
```

---

# 3. 🏗️ ENVIRONMENT PIPELINE AGENT

## Main Role: Non-character asset generation

### Sub-Agent 3.1: **Tileset Generator**
**Role:** Create seamless tilesets for terrain

**Capabilities:**
- Generate tileable patterns
- Create edge transitions (grass→desert)
- Ensure seamless repetition
- Variant creation (flat, hill, water)
- Test tiling in-engine

**Use Case:**
```
"Generate grass tileset:
- Base flat tile (seamless edges)
- 4 corner variants
- 4 edge variants
- 2 decorative variants (flowers, rocks)
- Test: should tile perfectly when placed 3x3"
```

---

### Sub-Agent 3.2: **Building Design Specialist**
**Role:** Generate faction-appropriate buildings

**Capabilities:**
- Research architectural styles
- Generate cat faction buildings (organic, warm)
- Generate AI faction buildings (mechanical, cold)
- Create upgrade tiers (basic → advanced)
- Ensure RTS readability

**Use Case:**
```
"Generate Cat Barracks:
- Tier 1: Wood and stone, blue roof, welcoming
- Tier 2: Reinforced stone, larger, gold trim
- Tier 3: Fortress-like, banners, imposing
- All must be readable from RTS camera angle"
```

---

### Sub-Agent 3.3: **Icon Designer**
**Role:** Create clear, recognizable icons

**Capabilities:**
- Design unit portraits (32x32, 64x64)
- Create ability icons
- Resource icons
- Status effect icons
- Readability testing

**Use Case:**
```
"Design ability icons for Meow Ping:
- Leap Attack: Cat mid-jump
- Inspire: Glowing aura
- Each 64x64, comic style
- Clear silhouette
- Recognizable at small size"
```

---

### Sub-Agent 3.4: **VFX Sprite Creator**
**Role:** Generate visual effects

**Capabilities:**
- Explosion animations (small, medium, large)
- Laser beam effects (cat blue, AI red)
- Shield and buff effects
- Hit impacts and sparks
- Particle sprite sheets

**Use Case:**
```
"Create laser beam effect:
- Cat faction: Blue energy beam
- Animated: 4 frames (pulse effect)
- Additive blend mode
- Clear directionality
- Works on any background"
```

---

### Sub-Agent 3.5: **Environment Variation Generator**
**Role:** Create diverse but consistent environments

**Capabilities:**
- Generate biome variations (grass, snow, desert)
- Seasonal variants
- Day/night versions
- Weather effects
- Decoration placement

**Use Case:**
```
"Create snow biome variants:
- Fresh snow (white, pristine)
- Trampled snow (gray, footprints)
- Icy patches (reflective)
- Snow-covered trees
- All maintain comic art style"
```

---

### Sub-Agent 3.6: **Asset Scale Validator**
**Role:** Ensure all assets are correctly scaled

**Capabilities:**
- Verify building sizes relative to units
- Check icon readability
- Test VFX visibility
- Validate terrain tile proportions
- In-game scale testing

**Use Case:**
```
"Validate building scales:
- Cat Base: Should be 3x unit height
- Barracks: Should be 2x unit height
- All buildings: Clearly visible from RTS camera
- Test: Place units next to buildings, screenshot, verify proportions"
```

---

### Sub-Agent 3.7: **Environment-Character Liaison**
**Role:** Ensure environment matches character art

**Capabilities:**
- Compare style consistency
- Verify color palette cohesion
- Check shading style match
- Test character-environment integration
- Provide feedback loop

**Use Case:**
```
"Review grass tileset with Meow Ping character:
- Do colors complement each other?
- Is shading style consistent?
- Does character stand out clearly?
- Any visual conflicts?
- Recommendations for adjustment"
```

---

### Sub-Agent 3.8: **Environment Asset Reporter**
**Role:** Track environment pipeline metrics

**Capabilities:**
- Catalog all environment assets
- Track completion status
- Identify gaps (missing biomes, buildings)
- Monitor asset variety
- Generate coverage reports

**Use Case:**
```
"Environment asset status:
- Buildings: Cat 8/12 complete, AI 5/12 complete
- Tilesets: Grass ✓, Snow 80%, Desert 20%, Urban 0%
- Icons: 45/60 complete
- VFX: 12/20 complete
- Priority: Urban tileset, AI buildings"
```

---

# 4. 💻 GAME SYSTEMS DEVELOPER AGENT

## Main Role: Core gameplay programming

### Sub-Agent 4.1: **Bug Hunter**
**Role:** Proactive bug detection and prevention

**Capabilities:**
- Static code analysis
- Pattern recognition for common bugs
- Memory leak detection
- Logic error identification
- Security vulnerability scanning

**Use Case:**
```
"Scan pathfinding code for bugs:
- Check for infinite loops
- Verify boundary conditions
- Test edge cases (map corners, obstacles)
- Identify potential crashes
- Suggest defensive programming fixes"
```

---

### Sub-Agent 4.2: **Performance Profiler**
**Role:** Optimize code performance

**Capabilities:**
- Identify performance bottlenecks
- CPU profiling
- Memory profiling
- Algorithm optimization suggestions
- Benchmark comparisons

**Use Case:**
```
"Profile unit AI system:
- CPU usage per unit (target: <0.1ms)
- Memory per unit (target: <1KB)
- Bottlenecks: Update loop taking 5ms (too slow!)
- Suggestion: Spatial hashing for unit queries
- Expected improvement: 10x faster"
```

---

### Sub-Agent 4.3: **Unit Testing Generator**
**Role:** Auto-generate comprehensive tests

**Capabilities:**
- Generate unit tests for functions
- Create integration tests
- Edge case identification
- Mock data generation
- Test coverage analysis

**Use Case:**
```
"Generate tests for combat system:
- Test: Unit attacks enemy, damage applied correctly
- Test: Unit dies at 0 HP
- Test: Armor reduces damage
- Test: Critical hits work
- Test: Edge case - attacking dead unit (should do nothing)
- Coverage: 95% of combat code"
```

---

### Sub-Agent 4.4: **Game Balance Simulator**
**Role:** Simulate gameplay scenarios for balance

**Capabilities:**
- Run AI vs AI simulations
- Test unit counter effectiveness
- Economy balance testing
- Tech tree progression simulation
- Statistical analysis of outcomes

**Use Case:**
```
"Simulate Cat Warriors vs AI Ranged (1000 matches):
- Cat Warriors win: 723 times (72.3%)
- Avg time to victory: 45s
- Analysis: Warriors too strong
- Recommendation: Reduce warrior HP by 10% OR increase AI ranged damage by 15%"
```

---

### Sub-Agent 4.5: **Code Documentation Writer**
**Role:** Auto-document code and systems

**Capabilities:**
- Generate function documentation
- Create system architecture diagrams
- Write API documentation
- Explain complex algorithms
- Keep docs in sync with code

**Use Case:**
```
"Document pathfinding system:
- High-level: How pathfinding works
- Algorithm: A* implementation details
- API: How other systems use it
- Performance: Complexity analysis
- Diagrams: Visual representation"
```

---

### Sub-Agent 4.6: **AI Behavior Designer**
**Role:** Create intelligent AI opponent strategies

**Capabilities:**
- Design AI decision trees
- Create build orders
- Attack timing strategies
- Resource management logic
- Difficulty scaling

**Use Case:**
```
"Design AI for Hard difficulty:
- Early game: Scout aggressively, expand fast
- Mid game: Tech to Tier 2, build army
- Late game: Multi-pronged attacks
- Special: Adapt to player strategy (counter units)
- Testing: Should beat Easy AI 95% of time"
```

---

### Sub-Agent 4.7: **Systems Integration Liaison**
**Role:** Coordinate between game systems

**Capabilities:**
- Ensure systems communicate correctly
- Design event systems
- Coordinate with UI/UX for data display
- Work with Content Designer on data formats
- Integration testing

**Use Case:**
```
"Integrate combat system with UI:
- Combat system fires 'UnitDamaged' event
- UI subscribes to event
- UI displays damage numbers
- Test: Verify numbers appear, correct values
- Performance: No lag from events"
```

---

### Sub-Agent 4.8: **Game Systems Metrics Tracker**
**Role:** Monitor code quality and system health

**Capabilities:**
- Track bug count and resolution time
- Monitor code complexity
- Test coverage tracking
- Performance benchmarks
- Technical debt identification

**Use Case:**
```
"Weekly systems report:
- Bugs: 3 new, 5 fixed, 2 remaining
- Avg fix time: 18 hours (target: <24h) ✓
- Test coverage: 87% (target: >80%) ✓
- Performance: All systems within budget ✓
- Technical debt: Pathfinding needs refactor (priority: medium)"
```

---

# 5. 🖥️ UI/UX DEVELOPER AGENT

## Main Role: Player interface implementation

### Sub-Agent 5.1: **Usability Tester**
**Role:** Test UI from player perspective

**Capabilities:**
- Simulate player interactions
- Identify confusing UI elements
- Test information hierarchy
- Verify button placement
- Readability testing

**Use Case:**
```
"Test main menu usability:
- Can user find 'New Game' in <2 seconds? ✓
- Is 'Settings' clearly labeled? ✓
- Are buttons big enough for clicking? ✗ (Too small!)
- Visual hierarchy clear? ✗ (All buttons same size)
- Recommendations: Increase button size, make 'New Game' larger"
```

---

### Sub-Agent 5.2: **Accessibility Checker**
**Role:** Ensure UI is accessible to all players

**Capabilities:**
- Color blind mode testing
- Screen reader compatibility
- Font size verification
- Contrast ratio checking
- Keyboard navigation testing

**Use Case:**
```
"Check HUD accessibility:
- Colorblind test: Red health bar not visible to deuteranopia ✗
- Solution: Add texture/pattern to health bar
- Contrast: 4.8:1 (target: >4.5:1) ✓
- Font size: 14px (target: >12px) ✓
- Keyboard: All functions accessible ✓"
```

---

### Sub-Agent 5.3: **Responsive Layout Designer**
**Role:** Ensure UI works at different resolutions

**Capabilities:**
- Test 1920x1080, 2560x1440, 3840x2160
- Test ultrawide (21:9, 32:9)
- Scale UI elements appropriately
- Anchor positioning verification
- Minimum resolution testing

**Use Case:**
```
"Test UI at 1366x768 (minimum spec):
- HUD: Fits correctly ✓
- Minimap: Slightly cut off ✗
- Fix: Reduce minimap size at low res
- Buttons: All clickable ✓
- Text: Readable ✓"
```

---

### Sub-Agent 5.4: **UI Animation Specialist**
**Role:** Create smooth, responsive UI animations

**Capabilities:**
- Button hover effects
- Menu transitions
- Tooltip animations
- Victory/defeat sequences
- Loading screens

**Use Case:**
```
"Create button hover animation:
- Default: Gray button
- Hover: Scale 1.0 → 1.05, brighten 10%
- Click: Scale 0.95, darken 5%
- Duration: 150ms
- Easing: EaseOutQuad
- Feel: Responsive, satisfying"
```

---

### Sub-Agent 5.5: **Tooltip Generator**
**Role:** Create informative, concise tooltips

**Capabilities:**
- Write clear descriptions
- Format stat information
- Show ability details
- Cost displays
- Cooldown timers

**Use Case:**
```
"Generate tooltip for Meow Ping:
- Name: Meow Ping
- Type: Hero Unit
- Stats: HP 200, Damage 25, Speed 6
- Abilities: Leap Attack, Inspire
- Cost: 150 Energy, 20s build
- Flavor text: 'Leader of the cat resistance'"
```

---

### Sub-Agent 5.6: **UI Sound Designer**
**Role:** Coordinate UI audio feedback

**Capabilities:**
- Assign sounds to UI actions
- Volume balancing
- Audio feedback testing
- Sound cue effectiveness
- Accessibility (visual alternatives)

**Use Case:**
```
"Add audio feedback to menu:
- Button hover: Soft beep
- Button click: Satisfying click
- Menu open: Whoosh
- Error: Negative buzz
- Victory screen: Triumphant fanfare
- All sounds <0.5s duration"
```

---

### Sub-Agent 5.7: **UI-Game Systems Liaison**
**Role:** Coordinate UI data display with game systems

**Capabilities:**
- Design data binding architecture
- Optimize UI updates
- Handle real-time data display
- Error state handling
- Performance optimization

**Use Case:**
```
"Display unit HP in selection panel:
- Get HP from game system (current/max)
- Update every frame? No, too expensive
- Update on damage event? Yes! ✓
- Format: 'HP: 150/200'
- Visual: Progress bar + text
- Performance: <0.1ms per update"
```

---

### Sub-Agent 5.8: **UI Metrics Tracker**
**Role:** Monitor UI performance and user interactions

**Capabilities:**
- Track button click rates
- Menu navigation patterns
- Error occurrence rates
- UI performance metrics
- User flow analysis

**Use Case:**
```
"UI analytics report:
- Most clicked button: 'New Game' (87%)
- Settings menu visits: 23%
- Avg time to start game: 8 seconds
- UI lag: 0 instances ✓
- Tooltip hover rate: 45%
- Recommendation: Most users skip tutorial, improve visibility"
```

---

# 6. ⚖️ CONTENT DESIGNER AGENT

## Main Role: Game balance and content creation

### Sub-Agent 6.1: **Balance Mathematician**
**Role:** Calculate and verify numerical balance

**Capabilities:**
- DPS (damage per second) calculations
- Cost efficiency analysis
- Win rate predictions
- Meta game analysis
- Statistical modeling

**Use Case:**
```
"Calculate if Warrior Cat is balanced:
- DPS: 16.7 (25 damage / 1.5 attack speed)
- Cost efficiency: 0.11 DPS per energy
- Compare to other Tier 1 units
- Analysis: 15% stronger than average
- Recommendation: Reduce damage to 23 OR increase cost to 175"
```

---

### Sub-Agent 6.2: **Mission Designer**
**Role:** Create engaging mission content

**Capabilities:**
- Objective design
- Difficulty pacing
- Reward structure
- Story integration
- Playtesting simulation

**Use Case:**
```
"Design Mission 5: 'Tech Race'
- Objective: Build 3 Tier 2 units before AI
- Secondary: Destroy AI's resource gatherers
- Starting: 500 energy, 1 base
- Enemy: Medium AI, 10 min head start
- Reward: Unlock Tier 3 tech
- Difficulty: Medium-Hard"
```

---

### Sub-Agent 6.3: **Tech Tree Architect**
**Role:** Design progression systems

**Capabilities:**
- Create tech dependencies
- Balance research costs
- Design upgrade paths
- Ensure meaningful choices
- Meta-game progression

**Use Case:**
```
"Design Tier 2 tech tree:
- Requires: Tier 1 base, 1000 energy
- Unlocks: Advanced Barracks, Engineer, Tier 2 upgrades
- Time: 60 seconds research
- Choice: Offensive (damage) vs Defensive (armor) path
- Both paths viable for different strategies"
```

---

### Sub-Agent 6.4: **Economy Designer**
**Role:** Balance resource systems

**Capabilities:**
- Resource generation rates
- Building costs
- Unit production costs
- Economic pacing
- Expansion incentives

**Use Case:**
```
"Balance economy progression:
- Early (0-5 min): 50 energy/sec, focus on base
- Mid (5-15 min): 150 energy/sec, expansion phase
- Late (15+ min): 300+ energy/sec, epic battles
- Scrap (secondary): Slower gain, enables special units
- Testing: Ensures 15-20 min game length"
```

---

### Sub-Agent 6.5: **Unit Roster Designer**
**Role:** Create diverse, interesting units

**Capabilities:**
- Define unit roles (tank, DPS, support, etc.)
- Design abilities
- Create counter relationships
- Faction identity
- Visual concept coordination

**Use Case:**
```
"Design Engineer Cat unit:
- Role: Support, base builder
- Stats: Low HP (80), no attack
- Ability: Repair (restores 50 HP to buildings)
- Cost: 75 energy, fast build (10s)
- Counter: Weak to all combat units
- Faction fit: Cat ingenuity vs AI mechanics"
```

---

### Sub-Agent 6.6: **Difficulty Tuner**
**Role:** Create appropriate challenge levels

**Capabilities:**
- AI difficulty scaling
- Resource multipliers
- Starting advantage/disadvantage
- Tech unlock timing
- Player skill estimation

**Use Case:**
```
"Tune Hard difficulty:
- AI: 125% production speed
- AI: Better unit micro (retreats damaged units)
- AI: Faster tech (80% research time)
- Player: Standard rates
- Result: Should challenge experienced players, ~60% win rate"
```

---

### Sub-Agent 6.7: **Content-Systems Liaison**
**Role:** Coordinate content with implementation

**Capabilities:**
- Provide data files to Game Systems Developer
- Verify implementation matches design
- Test balance in actual gameplay
- Iterate based on playtesting
- Document design rationale

**Use Case:**
```
"Deliver Meow Ping Tier 2 spec to Systems Dev:
- JSON: Stats, abilities, costs
- Notes: Should feel 40% stronger than Tier 1
- Testing checklist: HP correct, abilities work, cost displayed
- Follow-up: Play 5 test games, verify balance feels right"
```

---

### Sub-Agent 6.8: **Content Metrics Tracker**
**Role:** Monitor balance and player experience

**Capabilities:**
- Win rate tracking
- Unit usage statistics
- Mission completion rates
- Player progression pacing
- Balance trend analysis

**Use Case:**
```
"Weekly balance report:
- Meow Ping: 68% win rate (target: 55-60%) → Too strong!
- Warrior Cat: 45% usage (most popular unit)
- Mission 3: 35% completion rate (too hard?)
- Avg game length: 18 min (target: 15-20) ✓
- Action: Nerf Meow Ping 5%, re-balance Mission 3"
```

---

# 7. 🔧 INTEGRATION AGENT

## Main Role: Asset pipeline and build automation

### Sub-Agent 7.1: **Asset Import Specialist**
**Role:** Automate asset importing

**Capabilities:**
- Monitor asset folders for new files
- Auto-validate format and naming
- Convert formats (PNG → engine format)
- Generate sprite sheets
- Update asset database

**Use Case:**
```
"New asset detected: cat_hero_meowping_tier2_front.png
- Validation: ✓ PNG format, ✓ naming convention
- Size: 512x512 ✓
- Convert: PNG → Texture2D
- Import to: Unity/Godot assets folder
- Update: asset-manifest.json
- Notify: Character Pipeline Agent (import complete)"
```

---

### Sub-Agent 7.2: **Build Automation Engineer**
**Role:** Create and maintain build pipelines

**Capabilities:**
- CI/CD pipeline setup
- Automated testing before build
- Platform-specific builds (Win/Mac/Linux)
- Build artifact management
- Deployment automation

**Use Case:**
```
"Automated build pipeline:
1. Git push detected
2. Run all unit tests (pass: proceed, fail: abort)
3. Build Windows/Mac/Linux versions
4. Run integration tests on builds
5. Upload to test server
6. Notify QA Agent (new build ready)
- Total time: 10 minutes"
```

---

### Sub-Agent 7.3: **Version Control Specialist**
**Role:** Manage Git workflow and branching

**Capabilities:**
- Create feature branches
- Merge strategy
- Conflict resolution
- Commit message formatting
- Code review coordination

**Use Case:**
```
"Create feature branch for Meow Ping Tier 2:
- Branch: feature/meowping-tier2
- Commits: Organized by asset type
  - 'Add Meow Ping Tier 2 sprites (front/side/back/3quarter)'
  - 'Add Tier 2 stats configuration'
  - 'Implement Tier 2 upgrade button'
- PR: Ready for review
- Reviewers: Art Director (assets), Systems Dev (code)"
```

---

### Sub-Agent 7.4: **Dependency Manager**
**Role:** Track and manage project dependencies

**Capabilities:**
- Monitor library versions
- Update dependencies
- Vulnerability scanning
- License compliance
- Dependency conflict resolution

**Use Case:**
```
"Dependency audit:
- Game engine: Unity 2023.1.5 ✓ (latest stable)
- Physics: Built-in ✓
- UI: Unity UI ✓
- ComfyUI: Latest commit ✓
- Python deps: All up-to-date ✓
- Vulnerabilities: 0 found ✓"
```

---

### Sub-Agent 7.5: **Build Performance Optimizer**
**Role:** Speed up build and asset processing

**Capabilities:**
- Identify slow build steps
- Optimize asset import
- Parallel processing
- Incremental builds
- Cache management

**Use Case:**
```
"Build taking 15 minutes, too slow!
- Bottleneck: Asset import (8 min)
- Solution: Enable incremental import (only changed assets)
- Solution: Parallel texture compression
- Result: Build time → 4 minutes (73% faster!)"
```

---

### Sub-Agent 7.6: **Environment Configuration Manager**
**Role:** Manage dev/test/prod environments

**Capabilities:**
- Environment variable management
- Configuration files
- Secrets management
- Environment-specific builds
- Deployment targeting

**Use Case:**
```
"Environment setup:
- Dev: Local testing, debug enabled, fast iteration
- Test: QA server, performance profiling enabled
- Prod: Release build, optimizations enabled, no debug
- Each has separate configs, easy switching"
```

---

### Sub-Agent 7.7: **Integration Monitoring Agent**
**Role:** Monitor build and deployment health

**Capabilities:**
- Build success/failure tracking
- Deployment status
- Error log aggregation
- Alert on failures
- System health checks

**Use Case:**
```
"Monitoring alert:
- Build #47 FAILED
- Reason: Unit test failure in pathfinding
- Culprit: Recent commit by Systems Dev
- Action: Auto-notify Systems Dev
- Rollback: Previous build #46 still deployed
- Status: QA testing not affected"
```

---

### Sub-Agent 7.8: **Integration Metrics Tracker**
**Role:** Track pipeline efficiency

**Capabilities:**
- Build time tracking
- Success rate monitoring
- Asset import metrics
- Deployment frequency
- Pipeline bottleneck identification

**Use Case:**
```
"Weekly integration report:
- Builds: 23 total, 22 success (96%)
- Avg build time: 4.2 minutes
- Assets imported: 47 (38s avg import time)
- Deployments: 8 to test server
- Bottleneck: Texture compression (34% of build time)
- Recommendation: Upgrade compression library"
```

---

# 8. 🐛 QA/TESTING AGENT

## Main Role: Quality assurance

### Sub-Agent 8.1: **Test Case Generator**
**Role:** Auto-generate comprehensive test cases

**Capabilities:**
- Analyze features to create test plans
- Generate edge case tests
- Create regression test suites
- Design stress tests
- Prioritize test coverage

**Use Case:**
```
"Generate tests for new unit (Engineer Cat):
- Functional: Can build, repair works, stats correct
- Edge cases: Repair dead unit (should fail), repair full HP (no effect)
- Integration: Works with unit selection, displays in UI
- Performance: 100 engineers on map (should maintain 60 FPS)
- Regression: Doesn't break existing units"
```

---

### Sub-Agent 8.2: **Automated Tester**
**Role:** Run automated test suites

**Capabilities:**
- Execute unit tests
- Run integration tests
- Perform UI automation
- Load testing
- Continuous testing

**Use Case:**
```
"Nightly automated test run:
- Unit tests: 247/247 passed ✓
- Integration tests: 45/47 passed (2 failures)
- UI tests: 23/23 passed ✓
- Performance: All benchmarks within targets ✓
- Failures investigated: Pathfinding edge case, AI timeout
- Report generated and sent to developers"
```

---

### Sub-Agent 8.3: **Bug Reproduction Specialist**
**Role:** Reliably reproduce reported bugs

**Capabilities:**
- Analyze bug reports
- Create reproduction steps
- Identify minimum case
- Document conditions
- Verify fixes

**Use Case:**
```
"Bug #52: Units sometimes don't move

Reproduction:
1. Start Mission 3
2. Select 10 Warrior Cats
3. Right-click to map corner (512, 890)
4. Units path but stop at (512, 888)
5. Reproducible: 8/10 attempts

Root cause: Pathfinding fails near map edges
Assigned to: Game Systems Developer"
```

---

### Sub-Agent 8.4: **Performance Analyst**
**Role:** Deep-dive performance profiling

**Capabilities:**
- FPS analysis
- Memory leak detection
- CPU profiling
- GPU profiling
- Optimization recommendations

**Use Case:**
```
"Performance profile of Mission 5:
- FPS: Drops to 45 in large battles (target: 60) ✗
- CPU: 78% usage (acceptable)
- Memory: Stable at 1.8GB ✓
- Bottleneck: Unit rendering (45% frame time)
- Recommendation: Implement sprite batching
- Expected gain: +20 FPS"
```

---

### Sub-Agent 8.5: **Compatibility Tester**
**Role:** Test across platforms and configurations

**Capabilities:**
- Windows (7/10/11) testing
- Mac (Intel/M1) testing
- Linux distributions
- Different graphics cards
- Various screen resolutions

**Use Case:**
```
"Compatibility test matrix:
- Windows 10 + NVIDIA: ✓ Pass
- Windows 11 + AMD: ✓ Pass
- Mac M1: ✓ Pass (60 FPS stable)
- Mac Intel: ⚠️ Warning (48 FPS, playable)
- Linux Ubuntu: ✓ Pass
- Steam Deck: ✗ Fail (controls not adapted)
- Action: Add Steam Deck controller support"
```

---

### Sub-Agent 8.6: **User Experience Tester**
**Role:** Test from player perspective

**Capabilities:**
- First-time player simulation
- Tutorial effectiveness
- Controls intuitiveness
- Fun factor assessment
- Frustration point identification

**Use Case:**
```
"New player experience test:
- Tutorial: Clear instructions ✓
- First mission: Too easy, boring ✗
- Controls: Took 2 minutes to find unit abilities ✗
- Fun: Mission 2 very engaging ✓
- Frustration: Mission 3 difficulty spike too high ✗
- Recommendations: Buff Mission 1 enemies, improve ability discoverability, ease Mission 3"
```

---

### Sub-Agent 8.7: **Regression Tester**
**Role:** Ensure fixes don't break existing features

**Capabilities:**
- Maintain regression test suite
- Run tests on every build
- Compare behavior to baseline
- Identify regressions early
- Prioritize regression fixes

**Use Case:**
```
"Regression test after pathfinding fix:
- Fixed: Units now reach map edges ✓
- Regression: Units now slower on hills ✗
- Regression: Units sometimes overlap ✗
- Analysis: Pathfinding fix introduced new bugs
- Action: Systems Dev needs to fix regressions before merge"
```

---

### Sub-Agent 8.8: **QA Metrics Tracker**
**Role:** Track testing and quality metrics

**Capabilities:**
- Bug count tracking
- Test pass rate
- Coverage analysis
- Time-to-fix metrics
- Quality trend analysis

**Use Case:**
```
"Weekly QA report:
- Bugs found: 7 new
- Bugs fixed: 9 (net: -2, good!)
- Open bugs: 5 (1 critical, 2 high, 2 low)
- Test coverage: 89% (target: >85%) ✓
- Avg time-to-fix: 22 hours (target: <24h) ✓
- Build stability: 96% (excellent)
- Trend: Quality improving week-over-week ✓"
```

---

# HIERARCHY VISUALIZATION

```
Main Agent (L1)
│
├── Research & Analysis Sub-Agent (L2)
│   └── Deep dive into domain knowledge
│
├── Quality Control Sub-Agent (L2)
│   └── Verify output quality
│
├── Optimization Sub-Agent (L2)
│   └── Improve efficiency
│
├── Documentation Sub-Agent (L2)
│   └── Maintain knowledge base
│
├── Troubleshooting Sub-Agent (L2)
│   └── Diagnose and fix issues
│
├── Innovation Sub-Agent (L2)
│   └── Research new techniques
│
├── Liaison Sub-Agent (L2)
│   └── Coordinate with other agents
│
└── Metrics Sub-Agent (L2)
    └── Track and report performance
```

---

# COORDINATION BETWEEN SUB-AGENTS

## Example: Generating a New Character

### Character Pipeline Main Agent receives request

1. **Prompt Engineer (2.2)** crafts optimal prompt
2. **Workflow Optimizer (2.1)** selects best settings
3. **Main Agent** executes generation
4. **Generation Debugger (2.3)** monitors for errors
5. **Reference Image Analyst (2.5)** validates output quality
6. **Pipeline Liaison (2.7)** submits to Art Director

### Art Director Main Agent reviews

7. **Art Director receives** from Character Pipeline
8. **Style Analyst (1.1)** performs pixel-level comparison
9. **Roast Master (1.2)** provides brutal critique
10. **Color Palette Guardian (1.3)** verifies colors
11. **Main Agent** makes approval decision
12. **Pipeline Liaison (1.7)** sends feedback or approval

### If Revision Needed

13. **Character Pipeline** receives feedback
14. **Prompt Engineer (2.2)** adjusts prompt based on critique
15. **Workflow Optimizer (2.1)** tweaks settings
16. **Main Agent** regenerates
17. Repeat until approved

### Integration Phase

18. **Integration Main Agent** receives approved asset
19. **Asset Import Specialist (7.1)** converts and imports
20. **Version Control Specialist (7.3)** commits to repo
21. **Build Automation Engineer (7.2)** triggers build
22. **Integration Monitoring (7.7)** verifies success

### Quality Assurance

23. **QA Main Agent** receives new build
24. **Automated Tester (8.2)** runs test suite
25. **Performance Analyst (8.4)** profiles character in-game
26. **User Experience Tester (8.6)** validates feel
27. **Main Agent** reports results

---

# BENEFITS OF SUB-AGENT ARCHITECTURE

## 1. Deep Specialization
Each sub-agent is an expert in their micro-domain

## 2. Parallel Processing
Multiple sub-agents can work simultaneously

## 3. Quality Assurance Layers
Multiple checks at every stage

## 4. Continuous Improvement
Metrics agents identify optimization opportunities

## 5. Knowledge Preservation
Documentation agents capture all learnings

## 6. Proactive Problem Detection
Analysis agents catch issues before they escalate

## 7. Cross-Team Coordination
Liaison agents ensure smooth collaboration

## 8. Measurable Progress
Metrics agents provide data-driven insights

---

# FUTURE EXPANSION: L3 MICRO-AGENTS

Each Sub-Agent could have its own 4-8 micro-specialists:

```
Character Pipeline Agent (L1)
├── Workflow Optimizer (L2)
│   ├── Denoise Tuner (L3)
│   ├── IP-Adapter Specialist (L3)
│   ├── ControlNet Expert (L3)
│   └── Parameter A/B Tester (L3)
```

**Total potential:** 8 L1 agents × 8 L2 sub-agents × 4 L3 micro-agents = **256 specialized agents!**

---

# HOW TO USE SUB-AGENTS

## Option 1: Explicit Invocation
```
"Agent: Character Pipeline Agent
Sub-Agent: Workflow Optimizer

Task: Find optimal settings for muscular character with armor
Test range: Denoise 0.30-0.50, IP 0.3-0.6
Generate quality scores for each combination"
```

## Option 2: Automatic Delegation
Main agent automatically delegates to appropriate sub-agent based on task type

## Option 3: Sub-Agent Chain
```
"Character Pipeline → Prompt Engineer (craft prompt)
→ Workflow Optimizer (select settings)
→ Main Agent (generate)
→ Reference Image Analyst (validate)
→ Pipeline Liaison (submit for review)"
```

---

**Total Agent Count:**
- Level 1 (Main): 8 agents
- Level 2 (Sub): 64 agents (8 × 8)
- **Total: 72 specialized AI agents working together!**

**Created:** 2025-11-07
**Purpose:** Maximum specialization and efficiency
**Status:** Architectural design complete, ready for implementation

🐱 Cats rule. AI falls... with overwhelming AI agent firepower! 🤖
