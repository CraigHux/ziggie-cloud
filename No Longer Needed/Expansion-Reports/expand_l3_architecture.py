#!/usr/bin/env python3
"""
Expand L3 Micro-Agent Architecture from 729 to 1,728 agents.

Expansion Plan:
- Current: 9 L1 × 9 L2 × 9 L3 = 729
- Target: 12 L1 × 12 L2 × 12 L3 = 1,728
- New L3s needed: 999
"""

import re
from pathlib import Path

# Define the new L3 agents to add (L3.10, L3.11, L3.12 for each L2)
L3_ADDITIONS = {
    # L1.1 Art Director Agent
    "L2.1.1": {
        "name": "Style Consistency Analyst",
        "l3s": [
            ("L3.1.1.10", "Background Detail Auditor", "Verify background consistency with foreground style"),
            ("L3.1.1.11", "Shadow Direction Validator", "Ensure consistent light source across all assets"),
            ("L3.1.1.12", "Style Reference Matcher", "Compare new assets against approved style references"),
        ]
    },
    "L2.1.2": {
        "name": "Roast Master (Brutal Honesty Critic)",
        "l3s": [
            ("L3.1.2.10", "Anatomy Error Roaster", "Ruthlessly identify anatomical mistakes"),
            ("L3.1.2.11", "Perspective Fail Detector", "Call out incorrect perspective and foreshortening"),
            ("L3.1.2.12", "Lazy Work Identifier", "Detect rushed or low-effort work"),
        ]
    },
    "L2.1.3": {
        "name": "Color Palette Guardian",
        "l3s": [
            ("L3.1.3.10", "Color Harmony Optimizer", "Suggest complementary color improvements"),
            ("L3.1.3.11", "Brand Color Enforcer", "Ensure faction/brand colors are used correctly"),
            ("L3.1.3.12", "Accessibility Color Checker", "Verify color contrast for colorblind players"),
        ]
    },
    "L2.1.4": {
        "name": "Asset Naming Enforcer",
        "l3s": [
            ("L3.1.4.10", "Version Control Namer", "Add version suffixes (_v1, _v2, etc.)"),
            ("L3.1.4.11", "Bulk Rename Validator", "Verify batch rename operations before execution"),
            ("L3.1.4.12", "Naming Convention Updater", "Migrate old naming schemes to new standards"),
        ]
    },
    "L2.1.5": {
        "name": "Animation Frame Validator",
        "l3s": [
            ("L3.1.5.10", "Frame Interpolation Checker", "Verify smooth transitions between frames"),
            ("L3.1.5.11", "Animation Timing Optimizer", "Adjust frame durations for optimal flow"),
            ("L3.1.5.12", "Sprite Sheet Packer", "Generate optimized sprite sheets from frames"),
        ]
    },
    "L2.1.6": {
        "name": "Character Expression Specialist",
        "l3s": [
            ("L3.1.6.10", "Micro-Expression Analyst", "Add subtle facial detail variations"),
            ("L3.1.6.11", "Expression Intensity Calibrator", "Ensure emotion strength matches context"),
            ("L3.1.6.12", "Cross-Character Expression Matcher", "Maintain consistent expression styles across characters"),
        ]
    },
    "L2.1.7": {
        "name": "Asset Archival Specialist",
        "l3s": [
            ("L3.1.7.10", "Deprecated Asset Marker", "Tag old assets for archival"),
            ("L3.1.7.11", "Asset Usage Tracker", "Monitor which assets are actually used in builds"),
            ("L3.1.7.12", "Archive Compression Optimizer", "Compress archived assets efficiently"),
        ]
    },
    "L2.1.8": {
        "name": "Render Settings Optimizer",
        "l3s": [
            ("L3.1.8.10", "Batch Render Queue Manager", "Organize multiple renders efficiently"),
            ("L3.1.8.11", "Render Farm Coordinator", "Distribute renders across multiple machines"),
            ("L3.1.8.12", "Render Quality Predictor", "Estimate output quality before committing"),
        ]
    },
    "L2.1.9": {
        "name": "Design Systems Architect",
        "l3s": [
            ("L3.1.9.10", "Design Token Validator", "Verify design tokens are correctly implemented"),
            ("L3.1.9.11", "Component Deprecation Manager", "Handle retirement of old design components"),
            ("L3.1.9.12", "Design System Documentation Generator", "Auto-generate design system docs"),
        ]
    },

    # L1.2 Character Pipeline Agent
    "L2.2.1": {
        "name": "Workflow Optimizer",
        "l3s": [
            ("L3.2.1.10", "Generation Speed Tracker", "Monitor and optimize generation times"),
            ("L3.2.1.11", "Failed Generation Analyzer", "Identify patterns in failed generations"),
            ("L3.2.1.12", "Workflow Automation Suggester", "Recommend automation opportunities"),
        ]
    },
    "L2.2.2": {
        "name": "Prompt Engineer",
        "l3s": [
            ("L3.2.2.10", "Prompt Template Manager", "Store and organize reusable prompt templates"),
            ("L3.2.2.11", "Prompt A/B Tester", "Compare effectiveness of prompt variations"),
            ("L3.2.2.12", "Prompt Optimization Coach", "Suggest improvements to user prompts"),
        ]
    },
    "L2.2.3": {
        "name": "ControlNet Specialist",
        "l3s": [
            ("L3.2.3.10", "Multi-ControlNet Coordinator", "Optimize using multiple ControlNets simultaneously"),
            ("L3.2.3.11", "ControlNet Preprocessor Selector", "Choose best preprocessor for each use case"),
            ("L3.2.3.12", "ControlNet Weight Scheduler", "Dynamically adjust weights during generation"),
        ]
    },
    "L2.2.4": {
        "name": "IP-Adapter Specialist",
        "l3s": [
            ("L3.2.4.10", "Face ID Consistency Tracker", "Monitor face consistency across generations"),
            ("L3.2.4.11", "Style Transfer Balancer", "Balance IP-Adapter with prompt guidance"),
            ("L3.2.4.12", "Multi-Face IP-Adapter Handler", "Manage multiple face references"),
        ]
    },
    "L2.2.5": {
        "name": "Output Quality Validator",
        "l3s": [
            ("L3.2.5.10", "Resolution Upscale Validator", "Verify upscaled images maintain quality"),
            ("L3.2.5.11", "Compression Artifact Detector", "Identify and flag compression issues"),
            ("L3.2.5.12", "Batch Quality Scorer", "Score entire batches of outputs"),
        ]
    },
    "L2.2.6": {
        "name": "Reference Image Manager",
        "l3s": [
            ("L3.2.6.10", "Reference Library Organizer", "Categorize and tag reference images"),
            ("L3.2.6.11", "Reference Similarity Finder", "Find similar reference images"),
            ("L3.2.6.12", "Reference Usage Tracker", "Track which references are most effective"),
        ]
    },
    "L2.2.7": {
        "name": "Character Variation Generator",
        "l3s": [
            ("L3.2.7.10", "Outfit Randomizer", "Generate random but coherent outfit combinations"),
            ("L3.2.7.11", "Pose Variation Suggester", "Suggest complementary pose variations"),
            ("L3.2.7.12", "Expression Mood Mapper", "Map emotions to appropriate expressions"),
        ]
    },
    "L2.2.8": {
        "name": "Batch Processing Coordinator",
        "l3s": [
            ("L3.2.8.10", "Queue Priority Manager", "Prioritize urgent batch jobs"),
            ("L3.2.8.11", "Batch Progress Reporter", "Provide real-time batch processing updates"),
            ("L3.2.8.12", "Failed Batch Recovery Specialist", "Recover and retry failed batch items"),
        ]
    },
    "L2.2.9": {
        "name": "Model Version Manager",
        "l3s": [
            ("L3.2.9.10", "Model Changelog Generator", "Document changes between model versions"),
            ("L3.2.9.11", "Model Rollback Coordinator", "Safely rollback to previous model versions"),
            ("L3.2.9.12", "Model Testing Automation", "Automatically test new model versions"),
        ]
    },

    # L1.3 Environment Pipeline Agent
    "L2.3.1": {
        "name": "Building Generation Specialist",
        "l3s": [
            ("L3.3.1.10", "Building Style Mixer", "Blend architectural styles coherently"),
            ("L3.3.1.11", "Interior-Exterior Consistency Checker", "Ensure buildings make structural sense"),
            ("L3.3.1.12", "Building Damage State Generator", "Create damaged/destroyed building variants"),
        ]
    },
    "L2.3.2": {
        "name": "Terrain Generation Specialist",
        "l3s": [
            ("L3.3.2.10", "Terrain Transition Blender", "Smooth transitions between terrain types"),
            ("L3.3.2.11", "Elevation Map Generator", "Create height maps for strategic gameplay"),
            ("L3.3.2.12", "Terrain Texture Variation Adder", "Add subtle texture variations to avoid repetition"),
        ]
    },
    "L2.3.3": {
        "name": "VFX Sprite Specialist",
        "l3s": [
            ("L3.3.3.10", "VFX Animation Looper", "Create seamless looping VFX animations"),
            ("L3.3.3.11", "VFX Intensity Scaler", "Scale VFX for different ability power levels"),
            ("L3.3.3.12", "VFX Color Theme Coordinator", "Match VFX colors to faction themes"),
        ]
    },
    "L2.3.4": {
        "name": "Tileset Creator",
        "l3s": [
            ("L3.3.4.10", "Tile Edge Matcher", "Ensure seamless tile transitions"),
            ("L3.3.4.11", "Autotile Rule Generator", "Create autotiling rules for tile sets"),
            ("L3.3.4.12", "Tile Variation Generator", "Generate multiple variations of each tile"),
        ]
    },
    "L2.3.5": {
        "name": "Environmental Storytelling Agent",
        "l3s": [
            ("L3.3.5.10", "Environmental Clue Placer", "Position narrative clues in environments"),
            ("L3.3.5.11", "Faction Territory Marker", "Add visual markers showing faction control"),
            ("L3.3.5.12", "Battle Aftermath Designer", "Create post-battle environmental effects"),
        ]
    },
    "L2.3.6": {
        "name": "Weather Effect Generator",
        "l3s": [
            ("L3.3.6.10", "Particle Weather System", "Generate particle-based weather effects"),
            ("L3.3.6.11", "Weather Transition Manager", "Smooth transitions between weather states"),
            ("L3.3.6.12", "Gameplay Weather Impact Calculator", "Calculate weather effects on gameplay"),
        ]
    },
    "L2.3.7": {
        "name": "Lighting System Designer",
        "l3s": [
            ("L3.3.7.10", "Dynamic Shadow Calculator", "Calculate real-time shadow positions"),
            ("L3.3.7.11", "Ambient Lighting Optimizer", "Optimize ambient light for performance"),
            ("L3.3.7.12", "Day-Night Cycle Coordinator", "Manage lighting through day-night transitions"),
        ]
    },
    "L2.3.8": {
        "name": "Minimap Icon Designer",
        "l3s": [
            ("L3.3.8.10", "Minimap Icon Clarity Tester", "Ensure icons are readable at small size"),
            ("L3.3.8.11", "Faction Icon Differentiator", "Make faction icons easily distinguishable"),
            ("L3.3.8.12", "Minimap Animation Designer", "Create animated minimap indicators"),
        ]
    },
    "L2.3.9": {
        "name": "Prop and Decoration Generator",
        "l3s": [
            ("L3.3.9.10", "Prop Density Optimizer", "Balance prop placement for performance"),
            ("L3.3.9.11", "Interactive Prop Highlighter", "Visually distinguish interactive props"),
            ("L3.3.9.12", "Seasonal Prop Variant Creator", "Generate seasonal versions of props"),
        ]
    },

    # L1.4 Game Systems Developer
    "L2.4.1": {
        "name": "Unit Behavior Programmer",
        "l3s": [
            ("L3.4.1.10", "Unit Formation Coordinator", "Maintain unit formations during movement"),
            ("L3.4.1.11", "Target Priority Calculator", "Determine optimal attack targets"),
            ("L3.4.1.12", "Unit Morale System", "Implement morale-based behavior changes"),
        ]
    },
    "L2.4.2": {
        "name": "Combat System Architect",
        "l3s": [
            ("L3.4.2.10", "Critical Hit Calculator", "Manage critical hit mechanics and animations"),
            ("L3.4.2.11", "Combo System Designer", "Create ability combo mechanics"),
            ("L3.4.2.12", "Damage Type Resistance Manager", "Handle multiple damage types and resistances"),
        ]
    },
    "L2.4.3": {
        "name": "Resource System Developer",
        "l3s": [
            ("L3.4.3.10", "Resource Income Balancer", "Balance resource generation rates"),
            ("L3.4.3.11", "Resource Stockpile Manager", "Handle resource storage and caps"),
            ("L3.4.3.12", "Resource Trading System", "Implement resource exchange mechanics"),
        ]
    },
    "L2.4.4": {
        "name": "AI Opponent Programmer",
        "l3s": [
            ("L3.4.4.10", "AI Difficulty Scaler", "Adjust AI difficulty dynamically"),
            ("L3.4.4.11", "AI Cheat Prevention", "Ensure AI plays by the same rules"),
            ("L3.4.4.12", "AI Personality System", "Give AI opponents distinct play styles"),
        ]
    },
    "L2.4.5": {
        "name": "Physics Engine Specialist",
        "l3s": [
            ("L3.4.5.10", "Projectile Trajectory Calculator", "Calculate realistic projectile paths"),
            ("L3.4.5.11", "Collision Optimization Specialist", "Optimize collision detection performance"),
            ("L3.4.5.12", "Physics Material Designer", "Define material physics properties"),
        ]
    },
    "L2.4.6": {
        "name": "Network/Multiplayer Engineer",
        "l3s": [
            ("L3.4.6.10", "Network Bandwidth Optimizer", "Minimize network traffic"),
            ("L3.4.6.11", "Connection Quality Monitor", "Track and display connection quality"),
            ("L3.4.6.12", "Network Protocol Versioning", "Manage network protocol compatibility"),
        ]
    },
    "L2.4.7": {
        "name": "Save/Load System Developer",
        "l3s": [
            ("L3.4.7.10", "Save File Compressor", "Compress save files efficiently"),
            ("L3.4.7.11", "Save Migration Handler", "Migrate old save files to new formats"),
            ("L3.4.7.12", "Autosave Scheduler", "Manage autosave timing and frequency"),
        ]
    },
    "L2.4.8": {
        "name": "Performance Profiler",
        "l3s": [
            ("L3.4.8.10", "CPU Bottleneck Identifier", "Identify CPU performance bottlenecks"),
            ("L3.4.8.11", "Memory Leak Detector", "Detect and report memory leaks"),
            ("L3.4.8.12", "Frame Time Analyzer", "Analyze frame timing consistency"),
        ]
    },
    "L2.4.9": {
        "name": "Network Synchronization Specialist",
        "l3s": [
            ("L3.4.9.10", "Input Prediction Validator", "Verify client-side prediction accuracy"),
            ("L3.4.9.11", "Server Reconciliation Manager", "Handle server-client state differences"),
            ("L3.4.9.12", "Network Interpolation Smoother", "Smooth movement between network updates"),
        ]
    },

    # L1.5 UI/UX Developer
    "L2.5.1": {
        "name": "HUD Designer",
        "l3s": [
            ("L3.5.1.10", "HUD Opacity Controller", "Manage HUD transparency preferences"),
            ("L3.5.1.11", "HUD Scale Adapter", "Adapt HUD for different screen sizes"),
            ("L3.5.1.12", "Critical Information Highlighter", "Emphasize urgent HUD information"),
        ]
    },
    "L2.5.2": {
        "name": "Menu System Developer",
        "l3s": [
            ("L3.5.2.10", "Menu Navigation Optimizer", "Optimize menu navigation flow"),
            ("L3.5.2.11", "Menu Loading State Manager", "Handle menu loading and transitions"),
            ("L3.5.2.12", "Menu Preset Manager", "Save and load menu configuration presets"),
        ]
    },
    "L2.5.3": {
        "name": "Tutorial System Designer",
        "l3s": [
            ("L3.5.3.10", "Tutorial Progress Tracker", "Track player tutorial completion"),
            ("L3.5.3.11", "Contextual Tip Generator", "Show tips based on player actions"),
            ("L3.5.3.12", "Tutorial Skip Detection", "Detect if player skips tutorials"),
        ]
    },
    "L2.5.4": {
        "name": "Input/Control Mapper",
        "l3s": [
            ("L3.5.4.10", "Control Conflict Detector", "Detect input mapping conflicts"),
            ("L3.5.4.11", "Default Control Preset Manager", "Manage multiple default control schemes"),
            ("L3.5.4.12", "Control Sensitivity Calibrator", "Help players calibrate input sensitivity"),
        ]
    },
    "L2.5.5": {
        "name": "Accessibility Features Implementer",
        "l3s": [
            ("L3.5.5.10", "Screen Reader Integration", "Integrate screen reader support"),
            ("L3.5.5.11", "High Contrast Mode Designer", "Implement high contrast visual mode"),
            ("L3.5.5.12", "Motion Sickness Reducer", "Add options to reduce motion sickness"),
        ]
    },
    "L2.5.6": {
        "name": "UI Animation Specialist",
        "l3s": [
            ("L3.5.6.10", "UI Transition Choreographer", "Design smooth UI transitions"),
            ("L3.5.6.11", "Button Feedback Animator", "Create satisfying button press feedback"),
            ("L3.5.6.12", "UI Animation Performance Optimizer", "Optimize UI animations for performance"),
        ]
    },
    "L2.5.7": {
        "name": "Localization Manager",
        "l3s": [
            ("L3.5.7.10", "Text Overflow Handler", "Handle text overflow in translations"),
            ("L3.5.7.11", "Right-to-Left Language Support", "Support RTL languages (Arabic, Hebrew)"),
            ("L3.5.7.12", "Translation Placeholder Manager", "Manage missing translation placeholders"),
        ]
    },
    "L2.5.8": {
        "name": "UI Performance Optimizer",
        "l3s": [
            ("L3.5.8.10", "UI Draw Call Reducer", "Minimize UI rendering draw calls"),
            ("L3.5.8.11", "UI Asset Preloader", "Preload UI assets to prevent stuttering"),
            ("L3.5.8.12", "UI Memory Footprint Analyzer", "Analyze and reduce UI memory usage"),
        ]
    },
    "L2.5.9": {
        "name": "Input System Architect",
        "l3s": [
            ("L3.5.9.10", "Input Macro Recorder", "Record and playback input sequences"),
            ("L3.5.9.11", "Input Device Switcher", "Handle seamless switching between input devices"),
            ("L3.5.9.12", "Input Latency Measurer", "Measure and display input latency"),
        ]
    },

    # L1.6 Content Designer
    "L2.6.1": {
        "name": "Unit Stats Balancer",
        "l3s": [
            ("L3.6.1.10", "Unit Cost-Effectiveness Analyzer", "Ensure units are balanced for their cost"),
            ("L3.6.1.11", "Unit Counter Relationship Designer", "Design rock-paper-scissors unit counters"),
            ("L3.6.1.12", "Unit Power Curve Manager", "Balance unit power progression"),
        ]
    },
    "L2.6.2": {
        "name": "Mission Designer",
        "l3s": [
            ("L3.6.2.10", "Mission Pacing Analyzer", "Ensure missions have good pacing"),
            ("L3.6.2.11", "Mission Failure State Designer", "Design meaningful failure conditions"),
            ("L3.6.2.12", "Mission Branching Path Creator", "Create mission paths based on player choices"),
        ]
    },
    "L2.6.3": {
        "name": "Tech Tree Architect",
        "l3s": [
            ("L3.6.3.10", "Tech Tree Visualization Designer", "Design clear tech tree UI"),
            ("L3.6.3.11", "Technology Unlock Validator", "Verify tech unlocks are properly gated"),
            ("L3.6.3.12", "Tech Tree Balance Analyzer", "Balance technology research paths"),
        ]
    },
    "L2.6.4": {
        "name": "Economy Balancer",
        "l3s": [
            ("L3.6.4.10", "Inflation/Deflation Monitor", "Track in-game economic trends"),
            ("L3.6.4.11", "Price Elasticity Calculator", "Model player response to price changes"),
            ("L3.6.4.12", "Economic Exploit Detector", "Identify exploitable economic strategies"),
        ]
    },
    "L2.6.5": {
        "name": "Difficulty Curve Designer",
        "l3s": [
            ("L3.6.5.10", "Difficulty Spike Detector", "Identify and smooth difficulty spikes"),
            ("L3.6.5.11", "Player Skill Estimator", "Estimate player skill level"),
            ("L3.6.5.12", "Adaptive Difficulty Tuner", "Dynamically adjust difficulty"),
        ]
    },
    "L2.6.6": {
        "name": "Lore/Story Writer",
        "l3s": [
            ("L3.6.6.10", "Lore Consistency Checker", "Verify story consistency"),
            ("L3.6.6.11", "Character Arc Designer", "Design compelling character development"),
            ("L3.6.6.12", "Plot Twist Generator", "Create surprising but logical plot twists"),
        ]
    },
    "L2.6.7": {
        "name": "Ability/Spell Designer",
        "l3s": [
            ("L3.6.7.10", "Ability Cooldown Balancer", "Balance ability cooldowns"),
            ("L3.6.7.11", "Ability Combo Discoverer", "Identify potential ability combinations"),
            ("L3.6.7.12", "Ability Visual Clarity Enforcer", "Ensure abilities are visually distinct"),
        ]
    },
    "L2.6.8": {
        "name": "Progression System Architect",
        "l3s": [
            ("L3.6.8.10", "XP Curve Optimizer", "Design satisfying XP progression curves"),
            ("L3.6.8.11", "Reward Schedule Designer", "Schedule rewards to maintain engagement"),
            ("L3.6.8.12", "Prestige System Architect", "Design endgame prestige mechanics"),
        ]
    },
    "L2.6.9": {
        "name": "Narrative Designer",
        "l3s": [
            ("L3.6.9.10", "Dialogue Branch Mapper", "Map dialogue conversation trees"),
            ("L3.6.9.11", "Character Relationship Tracker", "Track relationships between characters"),
            ("L3.6.9.12", "Narrative Choice Consequencer", "Design meaningful choice consequences"),
        ]
    },

    # L1.7 Integration Agent
    "L2.7.1": {
        "name": "Asset Import Specialist",
        "l3s": [
            ("L3.7.1.10", "Asset Validation Pipeline", "Validate imported assets automatically"),
            ("L3.7.1.11", "Asset Metadata Extractor", "Extract and store asset metadata"),
            ("L3.7.1.12", "Asset Duplicate Detector", "Detect duplicate imported assets"),
        ]
    },
    "L2.7.2": {
        "name": "Version Control Manager",
        "l3s": [
            ("L3.7.2.10", "Binary File Conflict Resolver", "Handle binary file merge conflicts"),
            ("L3.7.2.11", "Commit Message Validator", "Enforce commit message standards"),
            ("L3.7.2.12", "Branch Strategy Enforcer", "Enforce branching workflows"),
        ]
    },
    "L2.7.3": {
        "name": "Build System Engineer",
        "l3s": [
            ("L3.7.3.10", "Build Cache Optimizer", "Optimize build caching for speed"),
            ("L3.7.3.11", "Incremental Build Manager", "Manage incremental build dependencies"),
            ("L3.7.3.12", "Build Artifact Archiver", "Archive and organize build artifacts"),
        ]
    },
    "L2.7.4": {
        "name": "CI/CD Pipeline Manager",
        "l3s": [
            ("L3.7.4.10", "Pipeline Failure Notifier", "Send notifications on pipeline failures"),
            ("L3.7.4.11", "Deployment Gate Controller", "Manage deployment approval gates"),
            ("L3.7.4.12", "Pipeline Performance Monitor", "Track pipeline execution times"),
        ]
    },
    "L2.7.5": {
        "name": "Dependency Manager",
        "l3s": [
            ("L3.7.5.10", "Dependency Vulnerability Scanner", "Scan for vulnerable dependencies"),
            ("L3.7.5.11", "Dependency Update Automator", "Automate safe dependency updates"),
            ("L3.7.5.12", "Dependency License Checker", "Verify dependency licenses"),
        ]
    },
    "L2.7.6": {
        "name": "Deployment Specialist",
        "l3s": [
            ("L3.7.6.10", "Deployment Health Checker", "Verify deployment health post-deploy"),
            ("L3.7.6.11", "Blue-Green Deployment Manager", "Manage blue-green deployments"),
            ("L3.7.6.12", "Canary Deployment Controller", "Control canary deployment rollouts"),
        ]
    },
    "L2.7.7": {
        "name": "Environment Configuration Manager",
        "l3s": [
            ("L3.7.7.10", "Environment Secrets Manager", "Securely manage environment secrets"),
            ("L3.7.7.11", "Configuration Drift Detector", "Detect configuration drift between environments"),
            ("L3.7.7.12", "Environment Provisioning Automator", "Automate environment setup"),
        ]
    },
    "L2.7.8": {
        "name": "Pipeline Monitoring Specialist",
        "l3s": [
            ("L3.7.8.10", "Pipeline Metrics Dashboard", "Display pipeline performance metrics"),
            ("L3.7.8.11", "Build Time Trend Analyzer", "Analyze build time trends over time"),
            ("L3.7.8.12", "Pipeline Cost Optimizer", "Optimize pipeline infrastructure costs"),
        ]
    },
    "L2.7.9": {
        "name": "Deployment Orchestrator",
        "l3s": [
            ("L3.7.9.10", "Multi-Environment Sync Coordinator", "Coordinate deployments across environments"),
            ("L3.7.9.11", "Deployment Rollback Automator", "Automate rollback procedures"),
            ("L3.7.9.12", "Deployment Verification Tester", "Run post-deployment verification tests"),
        ]
    },

    # L1.8 QA/Testing Agent
    "L2.8.1": {
        "name": "Automated Test Framework Developer",
        "l3s": [
            ("L3.8.1.10", "Test Flakiness Detector", "Identify and fix flaky tests"),
            ("L3.8.1.11", "Test Coverage Analyzer", "Analyze and improve test coverage"),
            ("L3.8.1.12", "Test Data Generator", "Generate realistic test data"),
        ]
    },
    "L2.8.2": {
        "name": "Manual Testing Coordinator",
        "l3s": [
            ("L3.8.2.10", "Test Case Priority Ranker", "Prioritize test cases by importance"),
            ("L3.8.2.11", "Exploratory Testing Guide", "Guide exploratory testing sessions"),
            ("L3.8.2.12", "Test Session Recorder", "Record and document test sessions"),
        ]
    },
    "L2.8.3": {
        "name": "Bug Reproduction Specialist",
        "l3s": [
            ("L3.8.3.10", "Minimal Reproduction Creator", "Create minimal bug reproductions"),
            ("L3.8.3.11", "Bug Environment Replicator", "Replicate exact bug environments"),
            ("L3.8.3.12", "Intermittent Bug Tracker", "Track patterns in intermittent bugs"),
        ]
    },
    "L2.8.4": {
        "name": "Performance Profiler",
        "l3s": [
            ("L3.8.4.10", "Performance Regression Detector", "Detect performance regressions"),
            ("L3.8.4.11", "Performance Baseline Manager", "Manage performance baselines"),
            ("L3.8.4.12", "Performance Report Generator", "Generate performance analysis reports"),
        ]
    },
    "L2.8.5": {
        "name": "Compatibility Tester",
        "l3s": [
            ("L3.8.5.10", "Device Farm Coordinator", "Coordinate testing across devices"),
            ("L3.8.5.11", "Browser Compatibility Matrix", "Track browser compatibility status"),
            ("L3.8.5.12", "OS Version Compatibility Tracker", "Track OS version compatibility"),
        ]
    },
    "L2.8.6": {
        "name": "Regression Test Manager",
        "l3s": [
            ("L3.8.6.10", "Regression Test Selector", "Select relevant regression tests"),
            ("L3.8.6.11", "Regression Suite Optimizer", "Optimize regression test suite runtime"),
            ("L3.8.6.12", "Regression Failure Analyzer", "Analyze regression test failures"),
        ]
    },
    "L2.8.7": {
        "name": "User Experience Tester",
        "l3s": [
            ("L3.8.7.10", "User Flow Tester", "Test critical user flows"),
            ("L3.8.7.11", "Accessibility Audit Conductor", "Conduct accessibility audits"),
            ("L3.8.7.12", "User Frustration Detector", "Identify frustrating UX patterns"),
        ]
    },
    "L2.8.8": {
        "name": "Security Tester",
        "l3s": [
            ("L3.8.8.10", "Penetration Test Coordinator", "Coordinate security penetration tests"),
            ("L3.8.8.11", "Security Vulnerability Prioritizer", "Prioritize security vulnerabilities"),
            ("L3.8.8.12", "Security Compliance Checker", "Check security compliance standards"),
        ]
    },
    "L2.8.9": {
        "name": "Security Tester",  # Duplicate from L2.8.8, but following existing structure
        "l3s": [
            ("L3.8.9.10", "API Security Tester", "Test API security vulnerabilities"),
            ("L3.8.9.11", "Authentication Flow Validator", "Validate authentication security"),
            ("L3.8.9.12", "Data Encryption Verifier", "Verify data encryption implementation"),
        ]
    },

    # L1.9 Analytics & Insights Agent
    "L2.9.1": {
        "name": "Player Behavior Analyst",
        "l3s": [
            ("L3.9.1.10", "Player Journey Mapper", "Map typical player journey paths"),
            ("L3.9.1.11", "Drop-off Point Identifier", "Identify where players quit"),
            ("L3.9.1.12", "Engagement Pattern Recognizer", "Recognize engagement patterns"),
        ]
    },
    "L2.9.2": {
        "name": "Performance Metrics Collector",
        "l3s": [
            ("L3.9.2.10", "FPS Statistics Aggregator", "Aggregate frame rate statistics"),
            ("L3.9.2.11", "Load Time Tracker", "Track loading times across sessions"),
            ("L3.9.2.12", "Crash Rate Monitor", "Monitor and report crash rates"),
        ]
    },
    "L2.9.3": {
        "name": "Balance Analytics Specialist",
        "l3s": [
            ("L3.9.3.10", "Win Rate Analyzer", "Analyze win rates by faction/unit"),
            ("L3.9.3.11", "Meta Strategy Detector", "Detect emerging meta strategies"),
            ("L3.9.3.12", "Balance Outlier Identifier", "Identify overpowered/underpowered elements"),
        ]
    },
    "L2.9.4": {
        "name": "A/B Testing Coordinator",
        "l3s": [
            ("L3.9.4.10", "Test Variant Designer", "Design A/B test variants"),
            ("L3.9.4.11", "Statistical Significance Calculator", "Calculate test result significance"),
            ("L3.9.4.12", "A/B Test Result Visualizer", "Visualize A/B test results"),
        ]
    },
    "L2.9.5": {
        "name": "Telemetry Data Processor",
        "l3s": [
            ("L3.9.5.10", "Data Pipeline Optimizer", "Optimize telemetry data pipelines"),
            ("L3.9.5.11", "Anomaly Detection System", "Detect anomalies in telemetry data"),
            ("L3.9.5.12", "Data Retention Policy Manager", "Manage telemetry data retention"),
        ]
    },
    "L2.9.6": {
        "name": "Dashboard & Reporting System",
        "l3s": [
            ("L3.9.6.10", "Custom Dashboard Builder", "Build custom analytics dashboards"),
            ("L3.9.6.11", "Automated Report Scheduler", "Schedule and send automated reports"),
            ("L3.9.6.12", "Data Export Formatter", "Format data for various export formats"),
        ]
    },
    "L2.9.7": {
        "name": "Predictive Analytics Engine",
        "l3s": [
            ("L3.9.7.10", "Churn Prediction Model", "Predict player churn probability"),
            ("L3.9.7.11", "Revenue Forecaster", "Forecast revenue trends"),
            ("L3.9.7.12", "Player Lifetime Value Estimator", "Estimate player LTV"),
        ]
    },
    "L2.9.8": {
        "name": "User Feedback Analyzer",
        "l3s": [
            ("L3.9.8.10", "Sentiment Analysis Engine", "Analyze feedback sentiment"),
            ("L3.9.8.11", "Common Issue Aggregator", "Aggregate common player issues"),
            ("L3.9.8.12", "Feature Request Prioritizer", "Prioritize feature requests by demand"),
        ]
    },
    "L2.9.9": {
        "name": "Insights & Recommendations Generator",
        "l3s": [
            ("L3.9.9.10", "Actionable Insight Identifier", "Identify actionable insights"),
            ("L3.9.9.11", "Recommendation Impact Estimator", "Estimate impact of recommendations"),
            ("L3.9.9.12", "Priority Insight Ranker", "Rank insights by business priority"),
        ]
    },
}

# New L2 agents to add (L2.10, L2.11, L2.12 for each existing L1)
NEW_L2_AGENTS = {
    "L1.1": [
        {
            "id": "L2.1.10",
            "name": "Texture Quality Specialist",
            "l3s": [
                ("L3.1.10.1", "Texture Resolution Optimizer", "Optimize texture resolutions for performance"),
                ("L3.1.10.2", "Texture Compression Selector", "Choose optimal texture compression"),
                ("L3.1.10.3", "Texture Mipmap Generator", "Generate texture mipmaps"),
                ("L3.1.10.4", "Texture Atlas Packer", "Pack textures into atlases"),
                ("L3.1.10.5", "Texture Tiling Validator", "Verify texture tiling seamlessness"),
                ("L3.1.10.6", "Texture Format Converter", "Convert textures between formats"),
                ("L3.1.10.7", "Texture Quality Scorer", "Score texture quality"),
                ("L3.1.10.8", "Texture Memory Analyzer", "Analyze texture memory usage"),
                ("L3.1.10.9", "Texture Streaming Manager", "Manage texture streaming"),
                ("L3.1.10.10", "Texture UV Unwrap Validator", "Validate UV unwrapping"),
                ("L3.1.10.11", "Texture Seam Fixer", "Fix visible texture seams"),
                ("L3.1.10.12", "Texture Detail Level Selector", "Select appropriate detail levels"),
            ]
        },
        {
            "id": "L2.1.11",
            "name": "Visual Effects Coordinator",
            "l3s": [
                ("L3.1.11.1", "VFX Timing Synchronizer", "Synchronize VFX with game events"),
                ("L3.1.11.2", "VFX Particle Budget Manager", "Manage particle effect budgets"),
                ("L3.1.11.3", "VFX Blend Mode Optimizer", "Optimize VFX blend modes"),
                ("L3.1.11.4", "VFX Scalability Designer", "Design VFX scalability settings"),
                ("L3.1.11.5", "VFX Audio Sync Manager", "Sync VFX with audio"),
                ("L3.1.11.6", "VFX Lifetime Optimizer", "Optimize effect lifetimes"),
                ("L3.1.11.7", "VFX Pooling System", "Implement VFX object pooling"),
                ("L3.1.11.8", "VFX Screen Coverage Monitor", "Monitor VFX screen coverage"),
                ("L3.1.11.9", "VFX Priority System", "Prioritize VFX rendering"),
                ("L3.1.11.10", "VFX Culling Optimizer", "Optimize VFX culling"),
                ("L3.1.11.11", "VFX Quality Tier Manager", "Manage VFX quality tiers"),
                ("L3.1.11.12", "VFX Performance Profiler", "Profile VFX performance"),
            ]
        },
        {
            "id": "L2.1.12",
            "name": "Asset Pipeline Automation Agent",
            "l3s": [
                ("L3.1.12.1", "Auto-Import Configurator", "Configure automatic asset import"),
                ("L3.1.12.2", "Asset Processing Queue Manager", "Manage asset processing queues"),
                ("L3.1.12.3", "Asset Validation Automator", "Automate asset validation"),
                ("L3.1.12.4", "Asset Optimization Pipeline", "Automated asset optimization"),
                ("L3.1.12.5", "Asset Metadata Tagger", "Automatically tag asset metadata"),
                ("L3.1.12.6", "Asset Dependency Resolver", "Resolve asset dependencies"),
                ("L3.1.12.7", "Asset Version Tracker", "Track asset versions"),
                ("L3.1.12.8", "Asset Build Integrator", "Integrate assets into builds"),
                ("L3.1.12.9", "Asset Error Reporter", "Report asset processing errors"),
                ("L3.1.12.10", "Asset Thumbnail Generator", "Generate asset thumbnails"),
                ("L3.1.12.11", "Asset Documentation Generator", "Generate asset documentation"),
                ("L3.1.12.12", "Asset Migration Automator", "Automate asset migrations"),
            ]
        },
    ],
    # Continue for L1.2 through L1.9...
    # (For brevity, I'll create a template that generates these)
}

def generate_new_l2_for_l1(l1_num, l1_name, l2_num, l2_name, l3_list):
    """Generate a new L2 agent section with 12 L3 agents."""
    section = f"\n## L2.{l1_num}.{l2_num}: {l2_name} → 12 L3 Micro-Agents\n\n"

    for l3_id, l3_name, l3_specialty in l3_list:
        section += f"### {l3_id}: **{l3_name}**\n"
        section += f"**Specialty:** {l3_specialty}\n\n"

    section += "---\n"
    return section

def generate_new_l1(l1_num, l1_name, l2_dict):
    """Generate a complete new L1 agent with 12 L2s, each with 12 L3s."""
    section = f"\n# L1.{l1_num} {l1_name.upper()} → 12 L2 SUB-AGENTS → 144 L3 MICRO-AGENTS\n\n"

    for l2_num in range(1, 13):
        l2_data = l2_dict.get(f"L2.{l1_num}.{l2_num}", {})
        l2_name = l2_data.get("name", f"Sub-Agent {l2_num}")
        l3s = l2_data.get("l3s", [])

        section += f"## L2.{l1_num}.{l2_num}: {l2_name} → 12 L3 Micro-Agents\n\n"

        for l3_id, l3_name, l3_specialty in l3s:
            section += f"### {l3_id}: **{l3_name}**\n"
            section += f"**Specialty:** {l3_specialty}\n\n"

        section += "---\n\n"

    return section

print("L3 Micro-Agent Architecture Expansion Script")
print("=" * 60)
print(f"Target: Expand from 729 to 1,728 L3 agents (999 new agents)")
print(f"Structure: 12 L1 × 12 L2 × 12 L3 = 1,728")
print("=" * 60)
print("\nThis script template is ready. Due to the massive scope,")
print("I'll need to generate the complete expansion systematically.")
print("\nNext step: Run expansion and update file...")
