# ComfyUI IP-Adapter + ControlNet for Equipment Variations

**Source:** InstaSD
**Video ID:** E2E_TEST_001
**URL:** https://www.youtube.com/watch?v=E2E_TEST_001
**Added:** 2025-11-07 11:48
**Confidence:** 95%

---

## Topic: IP-Adapter ControlNet

## Key Insights

1. IP-Adapter at weights above 0.70 locks both face consistency and colors, preventing equipment color variations
2. Reducing IP-Adapter weight to 0.40 while maintaining ControlNet at 0.60 allows color flexibility while preserving pose and face recognition
3. ControlNet handles pose locking independently, eliminating need for high IP-Adapter weights in character variation workflows

## Technical Settings

```
denoise: 0.40
ip_adapter_weight: 0.40
controlnet_strength: 0.60
```

## Workflow Steps

- Step 1: Set Denoise parameter to 0.40 in ComfyUI workflow
- Step 2: Configure IP-Adapter weight to 0.40 (not above 0.70)
- Step 3: Set ControlNet strength to 0.60 for pose consistency
- Step 4: Generate equipment variations while maintaining character face recognition

## Tools & Technologies

ComfyUI, IP-Adapter, ControlNet

## Key Takeaways

- IP-Adapter color locking behavior can be controlled by weight adjustment for equipment variation workflows
- Optimal parameter combination enables same character across different equipment tiers for game asset pipelines

---

## Metadata

- **Category:** ip-adapter-knowledge
- **Model:** claude-sonnet-4-20250514
- **Analyzed:** 2025-11-07 11:48:01
