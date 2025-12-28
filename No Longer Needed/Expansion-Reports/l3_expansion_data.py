#!/usr/bin/env python3
"""
L3 Micro-Agent Expansion Data
Complete dataset for expanding from 729 to 1,728 L3 agents
"""

# This file contains all the new L3 agent data organized systematically

# PHASE 1: Add L3.10, L3.11, L3.12 to existing 81 L2 agents (243 new L3s)
EXISTING_L2_EXPANSIONS = {
    # L1.1 ART DIRECTOR AGENT
    "L2.1.1": {
        "name": "Style Consistency Analyst",
        "new_l3s": [
            ("L3.1.1.10", "Background Detail Auditor", "Verify background consistency and detail level matches foreground style"),
            ("L3.1.1.11", "Shadow Direction Validator", "Ensure consistent light source and shadow direction across all assets"),
            ("L3.1.1.12", "Style Reference Matcher", "Compare new assets against approved style reference library"),
        ]
    },
    "L2.1.2": {
        "name": "Roast Master (Brutal Honesty Critic)",
        "new_l3s": [
            ("L3.1.2.10", "Anatomy Error Roaster", "Ruthlessly identify anatomical mistakes and proportion errors"),
            ("L3.1.2.11", "Perspective Fail Detector", "Call out incorrect perspective, foreshortening, and spatial errors"),
            ("L3.1.2.12", "Lazy Work Identifier", "Detect rushed, low-effort, or cut-corner work"),
        ]
    },
    "L2.1.3": {
        "name": "Color Palette Guardian",
        "new_l3s": [
            ("L3.1.3.10", "Color Harmony Optimizer", "Suggest complementary color palette improvements"),
            ("L3.1.3.11", "Brand Color Enforcer", "Ensure faction and brand colors are used correctly"),
            ("L3.1.3.12", "Accessibility Color Checker", "Verify color contrast ratios for colorblind accessibility"),
        ]
    },
    "L2.1.4": {
        "name": "Asset Naming Enforcer",
        "new_l3s": [
            ("L3.1.4.10", "Version Control Namer", "Add proper version suffixes (_v1, _v2, _final, etc.)"),
            ("L3.1.4.11", "Bulk Rename Validator", "Verify batch rename operations before execution to prevent errors"),
            ("L3.1.4.12", "Naming Convention Migrator", "Migrate assets from old naming schemes to new standards"),
        ]
    },
    "L2.1.5": {
        "name": "Animation Frame Validator",
        "new_l3s": [
            ("L3.1.5.10", "Frame Interpolation Checker", "Verify smooth visual transitions between animation frames"),
            ("L3.1.5.11", "Animation Timing Optimizer", "Adjust frame durations for optimal animation flow and feel"),
            ("L3.1.5.12", "Sprite Sheet Packer", "Generate optimized sprite sheets from individual animation frames"),
        ]
    },
    "L2.1.6": {
        "name": "Character Expression Specialist",
        "new_l3s": [
            ("L3.1.6.10", "Micro-Expression Analyst", "Add subtle facial detail variations for emotional depth"),
            ("L3.1.6.11", "Expression Intensity Calibrator", "Ensure emotion strength appropriately matches scene context"),
            ("L3.1.6.12", "Cross-Character Expression Matcher", "Maintain consistent expression styles across all characters"),
        ]
    },
    "L2.1.7": {
        "name": "Asset Archival Specialist",
        "new_l3s": [
            ("L3.1.7.10", "Deprecated Asset Marker", "Tag outdated assets for archival and removal from active library"),
            ("L3.1.7.11", "Asset Usage Tracker", "Monitor which assets are actually used in production builds"),
            ("L3.1.7.12", "Archive Compression Optimizer", "Compress archived assets with maximum efficiency"),
        ]
    },
    "L2.1.8": {
        "name": "Render Settings Optimizer",
        "new_l3s": [
            ("L3.1.8.10", "Batch Render Queue Manager", "Organize and prioritize multiple render jobs efficiently"),
            ("L3.1.8.11", "Render Farm Coordinator", "Distribute render workloads across multiple machines"),
            ("L3.1.8.12", "Render Quality Predictor", "Estimate final output quality before committing to full render"),
        ]
    },
    "L2.1.9": {
        "name": "Design Systems Architect",
        "new_l3s": [
            ("L3.1.9.10", "Design Token Validator", "Verify design tokens are correctly implemented across all systems"),
            ("L3.1.9.11", "Component Deprecation Manager", "Handle graceful retirement of old design components"),
            ("L3.1.9.12", "Design System Documentation Generator", "Auto-generate comprehensive design system documentation"),
        ]
    },

    # L1.2 CHARACTER PIPELINE AGENT
    "L2.2.1": {
        "name": "Workflow Optimizer",
        "new_l3s": [
            ("L3.2.1.10", "Generation Speed Tracker", "Monitor and analyze generation times to identify optimization opportunities"),
            ("L3.2.1.11", "Failed Generation Analyzer", "Identify patterns and root causes in failed generation attempts"),
            ("L3.2.1.12", "Workflow Automation Suggester", "Recommend workflow steps that can be automated for efficiency"),
        ]
    },
    "L2.2.2": {
        "name": "Prompt Engineer",
        "new_l3s": [
            ("L3.2.2.10", "Prompt Template Manager", "Store, organize, and version control reusable prompt templates"),
            ("L3.2.2.11", "Prompt A/B Tester", "Compare effectiveness of different prompt variations systematically"),
            ("L3.2.2.12", "Prompt Optimization Coach", "Analyze and suggest improvements to user-written prompts"),
        ]
    },
    "L2.2.3": {
        "name": "ControlNet Specialist",
        "new_l3s": [
            ("L3.2.3.10", "Multi-ControlNet Coordinator", "Optimize simultaneous use of multiple ControlNet models"),
            ("L3.2.3.11", "ControlNet Preprocessor Selector", "Automatically choose best preprocessor for each specific use case"),
            ("L3.2.3.12", "ControlNet Weight Scheduler", "Dynamically adjust ControlNet weights during generation process"),
        ]
    },
    "L2.2.4": {
        "name": "IP-Adapter Specialist",
        "new_l3s": [
            ("L3.2.4.10", "Face ID Consistency Tracker", "Monitor and ensure face consistency across multiple generations"),
            ("L3.2.4.11", "Style Transfer Balancer", "Balance IP-Adapter influence with text prompt guidance"),
            ("L3.2.4.12", "Multi-Face IP-Adapter Handler", "Manage and coordinate multiple face reference images"),
        ]
    },
    "L2.2.5": {
        "name": "Output Quality Validator",
        "new_l3s": [
            ("L3.2.5.10", "Resolution Upscale Validator", "Verify upscaled images maintain quality without introducing artifacts"),
            ("L3.2.5.11", "Compression Artifact Detector", "Identify and flag lossy compression quality issues"),
            ("L3.2.5.12", "Batch Quality Scorer", "Automatically score and rank entire batches of generated outputs"),
        ]
    },
    "L2.2.6": {
        "name": "Reference Image Manager",
        "new_l3s": [
            ("L3.2.6.10", "Reference Library Organizer", "Categorize, tag, and organize reference image collections"),
            ("L3.2.6.11", "Reference Similarity Finder", "Find visually similar reference images using computer vision"),
            ("L3.2.6.12", "Reference Usage Tracker", "Track which reference images produce best generation results"),
        ]
    },
    "L2.2.7": {
        "name": "Character Variation Generator",
        "new_l3s": [
            ("L3.2.7.10", "Outfit Randomizer", "Generate random but aesthetically coherent outfit combinations"),
            ("L3.2.7.11", "Pose Variation Suggester", "Suggest complementary pose variations for character sets"),
            ("L3.2.7.12", "Expression Mood Mapper", "Map emotional states to appropriate facial expressions"),
        ]
    },
    "L2.2.8": {
        "name": "Batch Processing Coordinator",
        "new_l3s": [
            ("L3.2.8.10", "Queue Priority Manager", "Dynamically prioritize urgent or time-sensitive batch jobs"),
            ("L3.2.8.11", "Batch Progress Reporter", "Provide real-time updates on batch processing status and ETAs"),
            ("L3.2.8.12", "Failed Batch Recovery Specialist", "Automatically recover and retry failed items in batch processing"),
        ]
    },
    "L2.2.9": {
        "name": "Model Version Manager",
        "new_l3s": [
            ("L3.2.9.10", "Model Changelog Generator", "Automatically document changes and improvements between model versions"),
            ("L3.2.9.11", "Model Rollback Coordinator", "Safely rollback to previous stable model versions when needed"),
            ("L3.2.9.12", "Model Testing Automation", "Automatically test new model versions against quality benchmarks"),
        ]
    },

    # L1.3 ENVIRONMENT PIPELINE AGENT
    "L2.3.1": {
        "name": "Building Generation Specialist",
        "new_l3s": [
            ("L3.3.1.10", "Building Style Mixer", "Intelligently blend multiple architectural styles coherently"),
            ("L3.3.1.11", "Interior-Exterior Consistency Checker", "Ensure buildings make structural and logical sense"),
            ("L3.3.1.12", "Building Damage State Generator", "Create damaged and destroyed building state variants"),
        ]
    },
    "L2.3.2": {
        "name": "Terrain Generation Specialist",
        "new_l3s": [
            ("L3.3.2.10", "Terrain Transition Blender", "Create smooth visual transitions between different terrain types"),
            ("L3.3.2.11", "Elevation Map Generator", "Generate strategic height maps for tactical gameplay"),
            ("L3.3.2.12", "Terrain Texture Variation Adder", "Add subtle texture variations to prevent visual repetition"),
        ]
    },
    "L2.3.3": {
        "name": "VFX Sprite Specialist",
        "new_l3s": [
            ("L3.3.3.10", "VFX Animation Looper", "Create seamless looping VFX animations without visible seams"),
            ("L3.3.3.11", "VFX Intensity Scaler", "Scale visual effect intensity based on ability power levels"),
            ("L3.3.3.12", "VFX Color Theme Coordinator", "Match VFX color schemes to faction-specific themes"),
        ]
    },
    "L2.3.4": {
        "name": "Tileset Creator",
        "new_l3s": [
            ("L3.3.4.10", "Tile Edge Matcher", "Ensure seamless visual transitions between adjacent tiles"),
            ("L3.3.4.11", "Autotile Rule Generator", "Generate autotiling rules and logic for tile sets"),
            ("L3.3.4.12", "Tile Variation Generator", "Create multiple visual variations of each tile type"),
        ]
    },
    "L2.3.5": {
        "name": "Environmental Storytelling Agent",
        "new_l3s": [
            ("L3.3.5.10", "Environmental Clue Placer", "Position subtle narrative clues within environment layouts"),
            ("L3.3.5.11", "Faction Territory Marker", "Add visual markers indicating faction territorial control"),
            ("L3.3.5.12", "Battle Aftermath Designer", "Create post-battle environmental destruction and effects"),
        ]
    },
    "L2.3.6": {
        "name": "Weather Effect Generator",
        "new_l3s": [
            ("L3.3.6.10", "Particle Weather System", "Generate particle-based weather effects (rain, snow, fog)"),
            ("L3.3.6.11", "Weather Transition Manager", "Create smooth transitions between different weather states"),
            ("L3.3.6.12", "Gameplay Weather Impact Calculator", "Calculate weather effects on unit visibility and movement"),
        ]
    },
    "L2.3.7": {
        "name": "Lighting System Designer",
        "new_l3s": [
            ("L3.3.7.10", "Dynamic Shadow Calculator", "Calculate real-time shadow positions based on light sources"),
            ("L3.3.7.11", "Ambient Lighting Optimizer", "Optimize ambient occlusion and global illumination for performance"),
            ("L3.3.7.12", "Day-Night Cycle Coordinator", "Manage lighting transitions through complete day-night cycles"),
        ]
    },
    "L2.3.8": {
        "name": "Minimap Icon Designer",
        "new_l3s": [
            ("L3.3.8.10", "Minimap Icon Clarity Tester", "Ensure icons remain readable at minimap scale"),
            ("L3.3.8.11", "Faction Icon Differentiator", "Make faction icons easily distinguishable at a glance"),
            ("L3.3.8.12", "Minimap Animation Designer", "Create animated indicators for minimap events and alerts"),
        ]
    },
    "L2.3.9": {
        "name": "Prop and Decoration Generator",
        "new_l3s": [
            ("L3.3.9.10", "Prop Density Optimizer", "Balance environmental prop placement for visual richness vs performance"),
            ("L3.3.9.11", "Interactive Prop Highlighter", "Visually distinguish interactive props from background decoration"),
            ("L3.3.9.12", "Seasonal Prop Variant Creator", "Generate seasonal and holiday-themed prop variants"),
        ]
    },

    # L1.4 GAME SYSTEMS DEVELOPER
    "L2.4.1": {
        "name": "Unit Behavior Programmer",
        "new_l3s": [
            ("L3.4.1.10", "Unit Formation Coordinator", "Maintain proper unit formations during movement and combat"),
            ("L3.4.1.11", "Target Priority Calculator", "Determine optimal attack target selection for units"),
            ("L3.4.1.12", "Unit Morale System", "Implement morale-based behavior changes and retreat mechanics"),
        ]
    },
    "L2.4.2": {
        "name": "Combat System Architect",
        "new_l3s": [
            ("L3.4.2.10", "Critical Hit Calculator", "Manage critical hit probability, damage, and special animations"),
            ("L3.4.2.11", "Combo System Designer", "Create ability combo mechanics and synergy bonuses"),
            ("L3.4.2.12", "Damage Type Resistance Manager", "Handle multiple damage types and resistance calculations"),
        ]
    },
    "L2.4.3": {
        "name": "Resource System Developer",
        "new_l3s": [
            ("L3.4.3.10", "Resource Income Balancer", "Balance resource generation rates for fair gameplay"),
            ("L3.4.3.11", "Resource Stockpile Manager", "Handle resource storage limits and overflow mechanics"),
            ("L3.4.3.12", "Resource Trading System", "Implement player-to-player resource exchange mechanics"),
        ]
    },
    "L2.4.4": {
        "name": "AI Opponent Programmer",
        "new_l3s": [
            ("L3.4.4.10", "AI Difficulty Scaler", "Dynamically adjust AI difficulty based on player performance"),
            ("L3.4.4.11", "AI Cheat Prevention", "Ensure AI opponents play by same rules as human players"),
            ("L3.4.4.12", "AI Personality System", "Give AI opponents distinct and recognizable play styles"),
        ]
    },
    "L2.4.5": {
        "name": "Physics Engine Specialist",
        "new_l3s": [
            ("L3.4.5.10", "Projectile Trajectory Calculator", "Calculate realistic projectile physics and ballistics"),
            ("L3.4.5.11", "Collision Optimization Specialist", "Optimize collision detection algorithms for performance"),
            ("L3.4.5.12", "Physics Material Designer", "Define friction, bounce, and interaction properties for materials"),
        ]
    },
    "L2.4.6": {
        "name": "Network/Multiplayer Engineer",
        "new_l3s": [
            ("L3.4.6.10", "Network Bandwidth Optimizer", "Minimize network traffic and data transmission requirements"),
            ("L3.4.6.11", "Connection Quality Monitor", "Track and display real-time connection quality metrics"),
            ("L3.4.6.12", "Network Protocol Versioning", "Manage backward compatibility across network protocol versions"),
        ]
    },
    "L2.4.7": {
        "name": "Save/Load System Developer",
        "new_l3s": [
            ("L3.4.7.10", "Save File Compressor", "Compress save game files with efficient encoding algorithms"),
            ("L3.4.7.11", "Save Migration Handler", "Migrate save files from old game versions to new formats"),
            ("L3.4.7.12", "Autosave Scheduler", "Manage intelligent autosave timing, frequency, and rotation"),
        ]
    },
    "L2.4.8": {
        "name": "Performance Profiler",
        "new_l3s": [
            ("L3.4.8.10", "CPU Bottleneck Identifier", "Identify and profile CPU performance bottlenecks"),
            ("L3.4.8.11", "Memory Leak Detector", "Detect, track, and report memory leak sources"),
            ("L3.4.8.12", "Frame Time Analyzer", "Analyze frame timing consistency and identify stuttering causes"),
        ]
    },
    "L2.4.9": {
        "name": "Network Synchronization Specialist",
        "new_l3s": [
            ("L3.4.9.10", "Input Prediction Validator", "Verify accuracy of client-side prediction algorithms"),
            ("L3.4.9.11", "Server Reconciliation Manager", "Handle discrepancies between client and server game state"),
            ("L3.4.9.12", "Network Interpolation Smoother", "Smooth entity movement between discrete network updates"),
        ]
    },

    # L1.5 UI/UX DEVELOPER
    "L2.5.1": {
        "name": "HUD Designer",
        "new_l3s": [
            ("L3.5.1.10", "HUD Opacity Controller", "Manage per-element HUD transparency and visibility preferences"),
            ("L3.5.1.11", "HUD Scale Adapter", "Dynamically adapt HUD sizing for different screen resolutions"),
            ("L3.5.1.12", "Critical Information Highlighter", "Emphasize time-sensitive or urgent HUD information"),
        ]
    },
    "L2.5.2": {
        "name": "Menu System Developer",
        "new_l3s": [
            ("L3.5.2.10", "Menu Navigation Optimizer", "Optimize menu navigation flow and reduce click depth"),
            ("L3.5.2.11", "Menu Loading State Manager", "Handle asynchronous menu loading and smooth transitions"),
            ("L3.5.2.12", "Menu Preset Manager", "Save and load player-customized menu configuration presets"),
        ]
    },
    "L2.5.3": {
        "name": "Tutorial System Designer",
        "new_l3s": [
            ("L3.5.3.10", "Tutorial Progress Tracker", "Track player tutorial completion and knowledge acquisition"),
            ("L3.5.3.11", "Contextual Tip Generator", "Display context-aware tips based on current player actions"),
            ("L3.5.3.12", "Tutorial Skip Detection", "Detect when players skip tutorials and adjust future guidance"),
        ]
    },
    "L2.5.4": {
        "name": "Input/Control Mapper",
        "new_l3s": [
            ("L3.5.4.10", "Control Conflict Detector", "Automatically detect and warn about input mapping conflicts"),
            ("L3.5.4.11", "Default Control Preset Manager", "Manage multiple platform-specific default control schemes"),
            ("L3.5.4.12", "Control Sensitivity Calibrator", "Guide players through input sensitivity calibration process"),
        ]
    },
    "L2.5.5": {
        "name": "Accessibility Features Implementer",
        "new_l3s": [
            ("L3.5.5.10", "Screen Reader Integration", "Integrate full screen reader support for visually impaired players"),
            ("L3.5.5.11", "High Contrast Mode Designer", "Implement high contrast visual modes for visibility"),
            ("L3.5.5.12", "Motion Sickness Reducer", "Add camera and animation options to reduce motion sickness"),
        ]
    },
    "L2.5.6": {
        "name": "UI Animation Specialist",
        "new_l3s": [
            ("L3.5.6.10", "UI Transition Choreographer", "Design fluid, aesthetically pleasing UI state transitions"),
            ("L3.5.6.11", "Button Feedback Animator", "Create satisfying tactile button press feedback animations"),
            ("L3.5.6.12", "UI Animation Performance Optimizer", "Optimize UI animations to minimize performance impact"),
        ]
    },
    "L2.5.7": {
        "name": "Localization Manager",
        "new_l3s": [
            ("L3.5.7.10", "Text Overflow Handler", "Gracefully handle text overflow in translations with longer text"),
            ("L3.5.7.11", "Right-to-Left Language Support", "Implement proper RTL language support (Arabic, Hebrew)"),
            ("L3.5.7.12", "Translation Placeholder Manager", "Manage missing translation placeholders and fallbacks"),
        ]
    },
    "L2.5.8": {
        "name": "UI Performance Optimizer",
        "new_l3s": [
            ("L3.5.8.10", "UI Draw Call Reducer", "Minimize UI rendering draw calls through batching and atlasing"),
            ("L3.5.8.11", "UI Asset Preloader", "Intelligently preload UI assets to prevent in-game stuttering"),
            ("L3.5.8.12", "UI Memory Footprint Analyzer", "Analyze and strategically reduce UI memory consumption"),
        ]
    },
    "L2.5.9": {
        "name": "Input System Architect",
        "new_l3s": [
            ("L3.5.9.10", "Input Macro Recorder", "Record and playback complex input sequences as macros"),
            ("L3.5.9.11", "Input Device Switcher", "Handle seamless runtime switching between input device types"),
            ("L3.5.9.12", "Input Latency Measurer", "Measure and display end-to-end input latency metrics"),
        ]
    },

    # L1.6 CONTENT DESIGNER
    "L2.6.1": {
        "name": "Unit Stats Balancer",
        "new_l3s": [
            ("L3.6.1.10", "Unit Cost-Effectiveness Analyzer", "Ensure units provide fair value for their resource cost"),
            ("L3.6.1.11", "Unit Counter Relationship Designer", "Design clear rock-paper-scissors unit counter relationships"),
            ("L3.6.1.12", "Unit Power Curve Manager", "Balance unit power scaling throughout game progression"),
        ]
    },
    "L2.6.2": {
        "name": "Mission Designer",
        "new_l3s": [
            ("L3.6.2.10", "Mission Pacing Analyzer", "Analyze and optimize mission pacing and intensity curves"),
            ("L3.6.2.11", "Mission Failure State Designer", "Design meaningful and fair mission failure conditions"),
            ("L3.6.2.12", "Mission Branching Path Creator", "Create divergent mission paths based on player choices"),
        ]
    },
    "L2.6.3": {
        "name": "Tech Tree Architect",
        "new_l3s": [
            ("L3.6.3.10", "Tech Tree Visualization Designer", "Design clear, intuitive tech tree UI representations"),
            ("L3.6.3.11", "Technology Unlock Validator", "Verify technology prerequisites and unlocks are properly gated"),
            ("L3.6.3.12", "Tech Tree Balance Analyzer", "Balance multiple technology research path viability"),
        ]
    },
    "L2.6.4": {
        "name": "Economy Balancer",
        "new_l3s": [
            ("L3.6.4.10", "Inflation/Deflation Monitor", "Track and respond to in-game economic inflation trends"),
            ("L3.6.4.11", "Price Elasticity Calculator", "Model player behavioral response to price changes"),
            ("L3.6.4.12", "Economic Exploit Detector", "Identify and patch exploitable economic strategies"),
        ]
    },
    "L2.6.5": {
        "name": "Difficulty Curve Designer",
        "new_l3s": [
            ("L3.6.5.10", "Difficulty Spike Detector", "Identify and smooth problematic difficulty spikes"),
            ("L3.6.5.11", "Player Skill Estimator", "Estimate player skill level from performance metrics"),
            ("L3.6.5.12", "Adaptive Difficulty Tuner", "Dynamically adjust game difficulty to player skill"),
        ]
    },
    "L2.6.6": {
        "name": "Lore/Story Writer",
        "new_l3s": [
            ("L3.6.6.10", "Lore Consistency Checker", "Verify narrative consistency across all story content"),
            ("L3.6.6.11", "Character Arc Designer", "Design compelling character development and growth arcs"),
            ("L3.6.6.12", "Plot Twist Generator", "Create surprising but logically consistent plot twists"),
        ]
    },
    "L2.6.7": {
        "name": "Ability/Spell Designer",
        "new_l3s": [
            ("L3.6.7.10", "Ability Cooldown Balancer", "Balance ability cooldowns relative to power and utility"),
            ("L3.6.7.11", "Ability Combo Discoverer", "Identify powerful or problematic ability combinations"),
            ("L3.6.7.12", "Ability Visual Clarity Enforcer", "Ensure abilities are visually distinct and readable"),
        ]
    },
    "L2.6.8": {
        "name": "Progression System Architect",
        "new_l3s": [
            ("L3.6.8.10", "XP Curve Optimizer", "Design satisfying and balanced XP progression curves"),
            ("L3.6.8.11", "Reward Schedule Designer", "Schedule reward timing to maximize player engagement"),
            ("L3.6.8.12", "Prestige System Architect", "Design compelling endgame prestige and reset mechanics"),
        ]
    },
    "L2.6.9": {
        "name": "Narrative Designer",
        "new_l3s": [
            ("L3.6.9.10", "Dialogue Branch Mapper", "Map complex dialogue conversation tree structures"),
            ("L3.6.9.11", "Character Relationship Tracker", "Track dynamic relationships between NPCs and player"),
            ("L3.6.9.12", "Narrative Choice Consequencer", "Design meaningful short and long-term choice consequences"),
        ]
    },

    # L1.7 INTEGRATION AGENT
    "L2.7.1": {
        "name": "Asset Import Specialist",
        "new_l3s": [
            ("L3.7.1.10", "Asset Validation Pipeline", "Automatically validate imported assets against quality standards"),
            ("L3.7.1.11", "Asset Metadata Extractor", "Extract and store comprehensive asset metadata during import"),
            ("L3.7.1.12", "Asset Duplicate Detector", "Detect and prevent duplicate asset imports"),
        ]
    },
    "L2.7.2": {
        "name": "Version Control Manager",
        "new_l3s": [
            ("L3.7.2.10", "Binary File Conflict Resolver", "Handle merge conflicts in binary game assets"),
            ("L3.7.2.11", "Commit Message Validator", "Enforce commit message standards and conventions"),
            ("L3.7.2.12", "Branch Strategy Enforcer", "Enforce consistent branching workflows and policies"),
        ]
    },
    "L2.7.3": {
        "name": "Build System Engineer",
        "new_l3s": [
            ("L3.7.3.10", "Build Cache Optimizer", "Optimize build caching strategies for maximum speed"),
            ("L3.7.3.11", "Incremental Build Manager", "Manage incremental build dependencies and invalidation"),
            ("L3.7.3.12", "Build Artifact Archiver", "Archive and organize historical build artifacts"),
        ]
    },
    "L2.7.4": {
        "name": "CI/CD Pipeline Manager",
        "new_l3s": [
            ("L3.7.4.10", "Pipeline Failure Notifier", "Send intelligent notifications on pipeline failures with context"),
            ("L3.7.4.11", "Deployment Gate Controller", "Manage manual and automated deployment approval gates"),
            ("L3.7.4.12", "Pipeline Performance Monitor", "Track and optimize CI/CD pipeline execution performance"),
        ]
    },
    "L2.7.5": {
        "name": "Dependency Manager",
        "new_l3s": [
            ("L3.7.5.10", "Dependency Vulnerability Scanner", "Continuously scan dependencies for security vulnerabilities"),
            ("L3.7.5.11", "Dependency Update Automator", "Automatically propose and test safe dependency updates"),
            ("L3.7.5.12", "Dependency License Checker", "Verify all dependencies comply with license requirements"),
        ]
    },
    "L2.7.6": {
        "name": "Deployment Specialist",
        "new_l3s": [
            ("L3.7.6.10", "Deployment Health Checker", "Verify deployment health and functionality post-deploy"),
            ("L3.7.6.11", "Blue-Green Deployment Manager", "Manage zero-downtime blue-green deployment strategies"),
            ("L3.7.6.12", "Canary Deployment Controller", "Control gradual canary deployment rollout percentages"),
        ]
    },
    "L2.7.7": {
        "name": "Environment Configuration Manager",
        "new_l3s": [
            ("L3.7.7.10", "Environment Secrets Manager", "Securely manage environment-specific secrets and credentials"),
            ("L3.7.7.11", "Configuration Drift Detector", "Detect unintended configuration drift between environments"),
            ("L3.7.7.12", "Environment Provisioning Automator", "Automate complete environment setup and configuration"),
        ]
    },
    "L2.7.8": {
        "name": "Pipeline Monitoring Specialist",
        "new_l3s": [
            ("L3.7.8.10", "Pipeline Metrics Dashboard", "Display real-time pipeline performance metrics and trends"),
            ("L3.7.8.11", "Build Time Trend Analyzer", "Analyze build time trends and predict future performance"),
            ("L3.7.8.12", "Pipeline Cost Optimizer", "Optimize CI/CD infrastructure costs and resource usage"),
        ]
    },
    "L2.7.9": {
        "name": "Deployment Orchestrator",
        "new_l3s": [
            ("L3.7.9.10", "Multi-Environment Sync Coordinator", "Coordinate synchronized deployments across environments"),
            ("L3.7.9.11", "Deployment Rollback Automator", "Automate safe rollback procedures for failed deployments"),
            ("L3.7.9.12", "Deployment Verification Tester", "Run comprehensive post-deployment verification test suites"),
        ]
    },

    # L1.8 QA/TESTING AGENT
    "L2.8.1": {
        "name": "Automated Test Framework Developer",
        "new_l3s": [
            ("L3.8.1.10", "Test Flakiness Detector", "Identify, track, and help fix flaky unreliable tests"),
            ("L3.8.1.11", "Test Coverage Analyzer", "Analyze code coverage and identify untested code paths"),
            ("L3.8.1.12", "Test Data Generator", "Generate realistic and edge-case test data automatically"),
        ]
    },
    "L2.8.2": {
        "name": "Manual Testing Coordinator",
        "new_l3s": [
            ("L3.8.2.10", "Test Case Priority Ranker", "Prioritize test cases by risk, impact, and likelihood"),
            ("L3.8.2.11", "Exploratory Testing Guide", "Guide systematic exploratory testing sessions"),
            ("L3.8.2.12", "Test Session Recorder", "Record and comprehensively document manual test sessions"),
        ]
    },
    "L2.8.3": {
        "name": "Bug Reproduction Specialist",
        "new_l3s": [
            ("L3.8.3.10", "Minimal Reproduction Creator", "Create minimal reproducible test cases for bugs"),
            ("L3.8.3.11", "Bug Environment Replicator", "Replicate exact environmental conditions for bug reproduction"),
            ("L3.8.3.12", "Intermittent Bug Tracker", "Track patterns and conditions in hard-to-reproduce intermittent bugs"),
        ]
    },
    "L2.8.4": {
        "name": "Performance Profiler",
        "new_l3s": [
            ("L3.8.4.10", "Performance Regression Detector", "Detect performance regressions in automated test runs"),
            ("L3.8.4.11", "Performance Baseline Manager", "Manage and update performance baseline expectations"),
            ("L3.8.4.12", "Performance Report Generator", "Generate detailed performance analysis reports with visualizations"),
        ]
    },
    "L2.8.5": {
        "name": "Compatibility Tester",
        "new_l3s": [
            ("L3.8.5.10", "Device Farm Coordinator", "Coordinate automated testing across diverse device farms"),
            ("L3.8.5.11", "Browser Compatibility Matrix", "Track and report browser compatibility test status"),
            ("L3.8.5.12", "OS Version Compatibility Tracker", "Track compatibility across operating system versions"),
        ]
    },
    "L2.8.6": {
        "name": "Regression Test Manager",
        "new_l3s": [
            ("L3.8.6.10", "Regression Test Selector", "Intelligently select relevant regression tests based on changes"),
            ("L3.8.6.11", "Regression Suite Optimizer", "Optimize regression test suite for minimum execution time"),
            ("L3.8.6.12", "Regression Failure Analyzer", "Analyze regression test failures to identify root causes"),
        ]
    },
    "L2.8.7": {
        "name": "User Experience Tester",
        "new_l3s": [
            ("L3.8.7.10", "User Flow Tester", "Systematically test critical end-to-end user flows"),
            ("L3.8.7.11", "Accessibility Audit Conductor", "Conduct comprehensive WCAG accessibility audits"),
            ("L3.8.7.12", "User Frustration Detector", "Identify UI/UX patterns that cause player frustration"),
        ]
    },
    "L2.8.8": {
        "name": "Security Tester",
        "new_l3s": [
            ("L3.8.8.10", "Penetration Test Coordinator", "Coordinate professional security penetration testing"),
            ("L3.8.8.11", "Security Vulnerability Prioritizer", "Prioritize security vulnerabilities by severity and impact"),
            ("L3.8.8.12", "Security Compliance Checker", "Verify compliance with security standards and regulations"),
        ]
    },
    "L2.8.9": {
        "name": "Security Tester",
        "new_l3s": [
            ("L3.8.9.10", "API Security Tester", "Test API endpoints for security vulnerabilities and exploits"),
            ("L3.8.9.11", "Authentication Flow Validator", "Validate authentication and authorization security"),
            ("L3.8.9.12", "Data Encryption Verifier", "Verify proper implementation of data encryption"),
        ]
    },

    # L1.9 ANALYTICS & INSIGHTS AGENT
    "L2.9.1": {
        "name": "Player Behavior Analyst",
        "new_l3s": [
            ("L3.9.1.10", "Player Journey Mapper", "Map and visualize typical player journey paths"),
            ("L3.9.1.11", "Drop-off Point Identifier", "Identify where and why players quit the game"),
            ("L3.9.1.12", "Engagement Pattern Recognizer", "Recognize patterns in player engagement over time"),
        ]
    },
    "L2.9.2": {
        "name": "Performance Metrics Collector",
        "new_l3s": [
            ("L3.9.2.10", "FPS Statistics Aggregator", "Aggregate frame rate statistics across player base"),
            ("L3.9.2.11", "Load Time Tracker", "Track and analyze game loading times across sessions"),
            ("L3.9.2.12", "Crash Rate Monitor", "Monitor, track, and report game crash frequencies and causes"),
        ]
    },
    "L2.9.3": {
        "name": "Balance Analytics Specialist",
        "new_l3s": [
            ("L3.9.3.10", "Win Rate Analyzer", "Analyze win rates by faction, unit type, and player skill"),
            ("L3.9.3.11", "Meta Strategy Detector", "Detect emerging dominant meta strategies in competitive play"),
            ("L3.9.3.12", "Balance Outlier Identifier", "Identify statistically overpowered or underpowered game elements"),
        ]
    },
    "L2.9.4": {
        "name": "A/B Testing Coordinator",
        "new_l3s": [
            ("L3.9.4.10", "Test Variant Designer", "Design statistically sound A/B test variants"),
            ("L3.9.4.11", "Statistical Significance Calculator", "Calculate statistical significance of A/B test results"),
            ("L3.9.4.12", "A/B Test Result Visualizer", "Create visual reports of A/B test outcomes and insights"),
        ]
    },
    "L2.9.5": {
        "name": "Telemetry Data Processor",
        "new_l3s": [
            ("L3.9.5.10", "Data Pipeline Optimizer", "Optimize telemetry data collection and processing pipelines"),
            ("L3.9.5.11", "Anomaly Detection System", "Automatically detect anomalies in telemetry data streams"),
            ("L3.9.5.12", "Data Retention Policy Manager", "Manage data retention policies for compliance and storage"),
        ]
    },
    "L2.9.6": {
        "name": "Dashboard & Reporting System",
        "new_l3s": [
            ("L3.9.6.10", "Custom Dashboard Builder", "Build custom analytics dashboards for different stakeholders"),
            ("L3.9.6.11", "Automated Report Scheduler", "Schedule and automatically send periodic analytics reports"),
            ("L3.9.6.12", "Data Export Formatter", "Format analytics data for export in multiple formats"),
        ]
    },
    "L2.9.7": {
        "name": "Predictive Analytics Engine",
        "new_l3s": [
            ("L3.9.7.10", "Churn Prediction Model", "Predict player churn probability using machine learning"),
            ("L3.9.7.11", "Revenue Forecaster", "Forecast future revenue trends based on player behavior"),
            ("L3.9.7.12", "Player Lifetime Value Estimator", "Estimate expected lifetime value of player segments"),
        ]
    },
    "L2.9.8": {
        "name": "User Feedback Analyzer",
        "new_l3s": [
            ("L3.9.8.10", "Sentiment Analysis Engine", "Analyze sentiment of player feedback and reviews"),
            ("L3.9.8.11", "Common Issue Aggregator", "Aggregate and prioritize commonly reported player issues"),
            ("L3.9.8.12", "Feature Request Prioritizer", "Prioritize feature requests based on demand and impact"),
        ]
    },
    "L2.9.9": {
        "name": "Insights & Recommendations Generator",
        "new_l3s": [
            ("L3.9.9.10", "Actionable Insight Identifier", "Identify insights that can drive concrete actions"),
            ("L3.9.9.11", "Recommendation Impact Estimator", "Estimate potential impact of recommendations before implementation"),
            ("L3.9.9.12", "Priority Insight Ranker", "Rank insights by business priority and urgency"),
        ]
    },
}

print(f"L3 expansion data loaded: {len(EXISTING_L2_EXPANSIONS)} L2 agents with new L3s")
print(f"Total new L3s in Phase 1: {len(EXISTING_L2_EXPANSIONS) * 3}")
