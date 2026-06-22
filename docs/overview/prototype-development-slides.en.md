# Bridge AI Development Process

## Slide 1: Development Goal

**Bridge AI** should be developed as a **usable decision-support prototype** for pediatric knee growth-plate injury analysis.

- Input: knee X-ray + structured clinical data
- Core function: detect the relevant growth-plate region and combine it with clinical factors
- Output: visual overlay, explainable risk summary, and simple growth-impact projection

**Prototype focus**

- Build a credible internal prototype
- Demonstrate practical workflow and interpretable output
- Avoid overclaiming full diagnostic or long-term predictive accuracy

## Slide 2: Prototype Development Approach

The project should be developed in **two connected layers**:

**1. Vision Layer**

- Use a pre-trained detection model and fine-tune it on pediatric knee X-rays
- Detect the physis or injury region
- Produce bounding box or heatmap output for the dashboard

**2. Prognosis Layer**

- Transform clinical data into structured features
- Combine image findings with rule-based growth logic
- Estimate damage severity, risk direction, and 1-, 3-, and 5-year impact

**Why this approach**

- More realistic than training a full end-to-end prognosis model now
- Better aligned with the limited data currently available
- Easier to explain, validate, and demonstrate

## Slide 3: Practical Development Process

**Step 1: Prepare the foundation**

- Confirm prototype scope and expected outputs
- Clean the dataset and verify labels
- Standardize the clinical input structure

**Step 2: Build the product shell**

- Keep the current React + FastAPI structure
- Add database storage for cases and results
- Add object storage for X-rays and generated overlays

**Step 3: Add the first real model**

- Train a localization model for the growth-plate region
- Integrate inference into the backend API
- Replace metadata-only visual output with model-generated output

**Step 4: Connect the full prototype flow**

- Combine model output with clinical and growth logic
- Display the result in one dashboard workflow
- Test the flow with sample and uploaded cases

## Slide 4: Final Prototype Deliverables

At the end of the prototype phase, the team should have:

- a deployed dashboard
- a deployed backend API
- a first trained localization model
- a hybrid prognosis engine
- persistent case and image storage
- curated sample cases for stable demos
- documentation, validation notes, and clear limitations

**Key message**

The right first milestone is not a full multimodal medical AI system.
It is a **hybrid prototype** with:

- one real vision model
- one explainable prognosis workflow
- one usable dashboard
