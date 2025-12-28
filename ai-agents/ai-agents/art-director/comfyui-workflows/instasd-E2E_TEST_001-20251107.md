# ComfyUI IP-Adapter + ControlNet for Equipment Variations

**Source:** InstaSD
**Video ID:** E2E_TEST_001
**URL:** https://www.youtube.com/watch?v=E2E_TEST_001
**Added:** 2025-11-07 12:15
**Confidence:** 90%

---

## Topic: ComfyUI Workflows

## Key Insights

1. IP-Adapter at weights above 0.70 locks both face consistency and colors, preventing equipment color variations
2. Reducing IP-Adapter weight to 0.40 while maintaining ControlNet at 0.60 allows color flexibility while preserving pose and face recognition
3. ControlNet can handle pose locking independently, reducing the need for high IP-Adapter strength in character variation workflows

## Technical Settings

```
denoise: 0.40
ip_adapter_weight: 0.40
controlnet_strength: 0.60
```

## Workflow Steps

- Step 1: Set Denoise parameter to 0.40 for optimal variation control
- Step 2: Configure IP-Adapter weight to 0.40 to maintain face similarity without color constraints
- Step 3: Set ControlNet strength to 0.60 to preserve pose consistency
- Step 4: Generate equipment variations while maintaining character recognition

## Tools & Technologies

ComfyUI, IP-Adapter, ControlNet

## Key Takeaways

- Balanced IP-Adapter and ControlNet settings enable efficient game asset pipelines for character equipment variations
- Lower IP-Adapter weights (0.40) combined with moderate ControlNet strength (0.60) provide optimal flexibility for equipment tier generation while maintaining character consistency

---

## Metadata

- **Category:** comfyui-workflows
- **Model:** claude-sonnet-4-20250514
- **Analyzed:** 2025-11-07 12:15:29
