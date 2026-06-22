# Bridge AI Prototype Development Process

## Introduction

This document describes how the Bridge AI project can be developed from its current concept into a usable prototype with a practical starting model. It is written for a multidisciplinary delivery team and focuses on product direction, system structure, data flow, model strategy, and execution phases rather than low-level source code.

The current repository already contains a working demo application, sample X-ray assets, synthetic clinical bias data, and a deterministic scoring pipeline. That existing work is useful as a reference implementation for the user interface, API shape, and demo workflow. However, the current demo is metadata-driven and does not yet represent a true machine learning prototype. This document therefore explains how to move from the current facade toward a first real prototype without overcommitting to a clinically unrealistic AI scope.

## Assumptions

- The project is intended as an early decision-support prototype, not a clinical-grade diagnostic system.
- Available data is limited and currently includes open or synthetic pediatric knee X-ray assets, bounding box labels, synthetic clinical bias records, and research-based growth formulas.
- There is no sufficiently large longitudinal dataset yet to train a trustworthy end-to-end prognosis model for long-term bone growth outcomes.
- The team needs a prototype that is credible, explainable, demonstrable, and buildable within a limited time frame.

## 1. Project Overview

Bridge AI is intended to support early assessment of pediatric knee growth-plate injury after trauma. The core problem is that a single X-ray at the time of injury shows current structural damage, but it does not directly tell clinicians how strongly that injury may affect later growth, angular deformity, or limb-length discrepancy. In practice, that uncertainty delays intervention and shifts decision-making toward observation rather than early risk stratification.

The primary target users for the prototype are pediatric orthopedic clinicians, radiology-adjacent clinical teams, and innovation reviewers who need to understand how the system could assist decision-making. Secondary users include researchers and product stakeholders who need a testbed for validating feature design, data workflow, and model feasibility.

The prototype should demonstrate three things clearly:

1. The system can accept a knee X-ray plus structured clinical inputs.
2. The system can identify the relevant growth-plate region and generate interpretable output.
3. The system can combine image-derived findings with clinical factors to produce a transparent risk-oriented prognosis view, even if long-term outcome prediction remains approximate in the first phase.

## 2. Prototype Goal

A usable prototype for this project should not be defined as a fully autonomous medical AI system. It should be defined as a reliable internal prototype that allows a clinician or evaluator to upload or select a case, review the detected region of interest, inspect structured risk factors, and receive a reproducible prognosis-oriented output with enough interpretability to discuss next steps.

The first prototype should include:

- X-ray input through file upload and curated sample cases.
- Structured clinical input such as age, bone age, sex, weight, height, injury side or location, and relevant medical-history modifiers.
- A starting vision model that localizes the growth-plate region and, if feasible, predicts a coarse injury class or damage proxy.
- A rule-based or hybrid prognosis engine that combines image features and clinical factors into damage severity, growth-risk estimates, and simple 1-, 3-, and 5-year projections.
- A dashboard that shows the overlay, key metrics, risk explanation, and trend visualization.
- Persistent storage for case metadata, uploaded assets, and generated outputs.

The first prototype should explicitly exclude:

- Clinical deployment or treatment recommendation automation.
- Full PACS integration, authentication for hospital-wide rollout, and enterprise audit controls.
- A custom end-to-end multimodal deep model trained to predict long-term clinical outcomes directly from raw X-rays.
- Claims of diagnostic accuracy beyond the limited prototype evaluation set.

Those items belong to later phases because they require larger datasets, stronger governance, and external validation.

## 3. Recommended Tech Stack

The recommended stack should stay close to what already works in the repository, while replacing only the parts that would block a real prototype.

### Frontend

Use React with Vite and Tailwind CSS.

This stack is already present in the repository and is well suited to a dashboard-style prototype. It supports fast iteration, lightweight deployment, and a clean separation between input flow, visual overlay, and analytical sections. There is no strong reason to replace it at this stage.

### Backend

Use FastAPI with Python.

The current backend already exposes a clean analysis endpoint and aligns well with data processing, image handling, and ML inference workflows. FastAPI is a strong fit because the same language can be used for API logic, inference orchestration, preprocessing, and research scripts.

### Database

Use PostgreSQL for the hosted prototype and SQLite for local development only.

The current demo does not persist analysis history. A real prototype should store cases, inputs, run metadata, and generated outputs. PostgreSQL is a practical choice because it supports structured clinical fields, model-run metadata, and future auditability without introducing unnecessary complexity. SQLite is acceptable for local development but should not be treated as the main hosted data store.

### Object Storage

Use S3-compatible storage such as Supabase Storage, Cloudflare R2, or AWS S3.

X-ray uploads, overlay images, and derived artifacts should not be stored directly inside the API container or database. Object storage is the simplest durable path and prepares the project for later dataset versioning.

### AI and Data Tooling

Use PyTorch, Ultralytics YOLO for the first vision model, scikit-learn for lightweight tabular baselines, and NumPy, Pandas, Pillow, and OpenCV for preprocessing.

This is a deliberately pragmatic choice. The project needs visible localization output quickly, and YOLO-style detection is simpler to train and demonstrate than a custom medical segmentation stack. Scikit-learn is sufficient for early tabular baselines or probability calibration. The current repository already uses Python-based image and numeric tooling, so this path minimizes friction.

If the team later moves into heavier medical imaging workflows or DICOM-intensive pipelines, MONAI can be added in a later phase rather than at the start.

### Cloud and Deployment

Use Vercel for the frontend and Render, Railway, or Fly.io for the FastAPI backend with model files.

The current repo documents Vercel deployment for both apps, which is acceptable for a pure demo. Once real model inference is added, a Python host with stable filesystem access, larger memory headroom, and predictable runtime behavior becomes more appropriate for the backend. A split deployment is the safer practical choice.

### External Services and APIs

No external medical API is required for the first prototype.

Optional additions for later phases include:

- `pydicom` for DICOM ingestion.
- Orthanc or PACS-facing integration if hospital workflows become in scope.
- Analytics or monitoring tools such as Sentry and PostHog for internal validation.

## 4. System Architecture

The recommended architecture is a hybrid application composed of five practical layers.

### Presentation Layer

The frontend provides a single workflow-oriented dashboard. Users upload an image or select a sample case, enter structured clinical values, submit the analysis, and receive a result view that contains the image overlay, risk metrics, explanatory factors, and projection charts.

### API Layer

The FastAPI backend exposes endpoints for sample retrieval, case submission, analysis execution, and result retrieval. In the first prototype, inference can remain synchronous if runtime is short. If model runtime becomes noticeable, the analysis endpoint can evolve into an asynchronous job flow later.

### Data Layer

The data layer stores:

- Case metadata and clinical inputs in PostgreSQL.
- Uploaded X-rays and derived overlay images in object storage.
- Model artifacts and version metadata in a controlled file or storage location.

### Model Layer

The model layer should be split rather than end-to-end:

- A vision component localizes the physis region and, if feasible, predicts coarse fracture or damage features.
- A prognosis component combines those outputs with clinical inputs and research-based logic to generate risk-oriented projections.

This separation keeps the system explainable and matches the reality of the current dataset.

### User Interaction Flow

The intended high-level flow is:

1. User provides image and clinical inputs.
2. Backend validates and preprocesses the submission.
3. Vision model produces region and feature outputs.
4. Prognosis engine converts model outputs plus clinical data into structured risk results.
5. Result is stored and returned to the frontend.
6. Frontend displays the overlay, scores, factors, and projected trend.

## 5. Data Flow

Data should enter the system through a controlled submission path rather than through direct model access. A prototype that is explainable and testable needs a clean data pipeline even more than it needs a complex model.

The recommended flow is:

1. **Input capture**
   The user submits a knee X-ray together with structured fields such as age, bone age, sex, weight, height, location, and selected medical-history modifiers.

2. **Validation**
   The backend validates file type, file size, image readability, required fields, value ranges, and enum consistency. Invalid submissions should fail before any model execution.

3. **Preprocessing**
   The image is normalized into a standard working format. For the first prototype, PNG or JPEG is acceptable. If DICOM support is added later, windowing and metadata extraction should happen at this stage. Images should also be resized consistently for inference while preserving a traceable original.

4. **Feature extraction**
   The vision model produces at least one spatial output, such as a bounding box around the growth-plate region. If the model is trained for more than localization, it may also output Salter-Harris class probabilities or a coarse damage proxy.

5. **Clinical transformation**
   Clinical inputs are transformed into model-ready and logic-ready features. This includes BMI calculation, age normalization, clinical bias lookup, and structured encoding of medication or pathology modifiers. The repo already contains synthetic clinical bias generation logic and WHO reference tables that can seed this step.

6. **Fusion and prognosis**
   The system combines image-derived features with clinical features and rule-based growth logic to compute the prototype output. This is the most appropriate place for formulas related to remaining growth, mechanical bias, and deformity direction.

7. **Persistence**
   The raw input metadata, transformed features, result payload, model version, and timestamps should be stored. The raw image and overlay asset should be stored in object storage with linked references in the database.

8. **Display**
   The frontend renders the processed image, structured metrics, risk explanations, and projections in a clinician-readable format.

## 6. AI/ML Model Approach

This project does require machine learning, but not in the form of a fully custom end-to-end prognosis model in the first prototype.

### What the model is expected to do

The first practical model should do one focused job well: identify or localize the relevant growth-plate injury region on a pediatric knee X-ray and optionally predict a coarse injury class or damage severity proxy.

That is the part of the pipeline where machine learning adds the most immediate value because:

- it creates visible, interpretable output for the user interface;
- it reduces dependence on manually prepared labels for each demo case;
- it produces structured features that can feed a prognosis engine.

### What input data is required

The starting model requires:

- Pediatric knee X-rays in a consistent view, ideally with separate train and validation sets.
- Bounding box annotations for the physis or injury region.
- Optional labels for Salter-Harris type, laterality, bar location, or damage severity proxy.

For the full prototype pipeline, additional structured input is required:

- Age and bone age.
- Sex.
- Weight and height.
- Clinical history or pathology modifiers relevant to bone growth.

### What output the model should produce

The first model should output:

- Bounding box or localization map for the relevant physis region.
- Confidence score.
- Optional coarse class such as normal versus injury, or Salter-Harris group if the dataset supports it.

The system-level output should then include:

- Damage estimate or injury severity proxy.
- Varus, valgus, or growth-arrest tendency using the prognosis engine.
- Simple projected growth-impact metrics for 1, 3, and 5 years.

### What type of approach should be used

The recommended first-phase approach is a hybrid stack:

- A pre-trained object detection model fine-tuned on the available X-ray dataset.
- A rule-based prognosis layer informed by clinical formulas and structured bias tables.
- An optional lightweight tabular model later, once enough structured records exist.

This is preferable to training a custom multimodal deep prognosis model because the repository does not yet show evidence of a sufficiently large, real longitudinal ground-truth dataset. Training an end-to-end long-term prognosis model on synthetic or weakly labeled outcome data would create fragile results and misleading confidence.

### Basic training and evaluation process

The recommended starting process is:

1. Prepare and clean the labeled image dataset.
2. Train a detector to localize the physis or injury region.
3. Evaluate localization quality using standard detection metrics and visual review.
4. Freeze that model as the image feature generator for the prototype.
5. Use rule-based prognosis logic for the first integrated release.
6. Collect structured usage data and expert review feedback.
7. Add a tabular baseline later only if the team accumulates enough outcome-linked records.

### Basic improvement path

Model evolution should follow this order:

1. Better detection and annotation quality.
2. Better structured outcome definitions.
3. Small tabular or calibration model on top of image-derived features.
4. True multimodal prognosis model only after dataset maturity is proven.

## 7. Main Feature Flows

The prototype should support a small number of strong flows rather than many weak ones.

### Analysis Submission Flow

The user opens the dashboard, uploads an X-ray or selects a sample, enters structured clinical inputs, and submits the case. The system validates the submission, runs inference, and returns a result set in one coherent response.

### Clinical Review Flow

The user reviews the overlay to confirm that the system focused on the relevant region, checks the damage or injury metrics, and reads the factor list that explains why the system produced the current risk profile. This flow is critical because trust depends on visibility and not only on numbers.

### Growth Projection Flow

The user views the projected trend section, which translates the image and clinical findings into a simple future-oriented interpretation. In the first prototype, this should remain clearly framed as a model-assisted estimate rather than a definitive clinical prediction.

### Sample Demonstration Flow

The system should include curated sample cases with reliable outputs. This is essential for demos, stakeholder reviews, and regression testing even after real model inference is introduced.

### Data Capture and Iteration Flow

Each run should create a traceable stored record. That gives the team a feedback loop for later model improvement, error analysis, and dataset growth.

## 8. Development Process

The recommended path from zero to usable prototype should proceed in controlled layers.

### Project setup

Begin by confirming the product scope, accepted clinical inputs, intended user flow, and prototype claims. The current repository already provides a useful UI and API baseline, so the first practical setup task is to keep that structure and separate demo-only logic from future real inference logic.

### Tech stack setup

Initialize local environments for the React frontend and FastAPI backend. Add PostgreSQL and object storage configuration early even if the first runs still use local files. This prevents the prototype from becoming trapped in a non-persistent demo architecture.

### Data structure design

Define clear entities such as case, uploaded image, clinical input set, model run, result summary, and overlay artifact. The current metadata-driven format in the repo is a good seed, but it should become a database-backed case schema rather than remain a static JSON-only pattern.

### Core feature implementation

Keep the current dashboard pattern: sample selection, manual upload, structured form, submission, and combined result page. Add persistence, result history for internal review, and basic status handling around model execution.

### Model or logic implementation

Implement the first vision model for localization and replace the current label-only overlay generation path with inference-generated output. Keep the prognosis logic hybrid and explicit. The repository’s existing growth and scoring formulas are a practical starting engine for this layer.

### API integration

Expose endpoints for sample retrieval, analysis submission, and case retrieval. Keep the request and response contract stable so the frontend can evolve without constant backend churn.

### UI development

Preserve the existing visual strengths of the current demo, especially the single-screen dashboard and visible overlay section. Refine the language so the UI clearly distinguishes image findings, estimated risk, and projected outlook.

### Testing

Testing should include:

- Input validation tests.
- API contract tests.
- Inference smoke tests.
- Visual regression checks for sample cases.
- Human review of overlay correctness and result plausibility.

Heavy testing infrastructure is not necessary at the start. A reliable small suite around the main flow is enough.

### Deployment

Deploy the frontend and backend separately. Store images in object storage and point the backend to the model artifact location. Use a small set of seeded sample cases in production so demos are deterministic even if user-uploaded inference occasionally fails.

### Prototype validation

Prototype validation should not rely only on technical metrics. It should include:

- Successful end-to-end runs.
- Correct localization on a held-out validation set.
- Clinical face-validity review of the risk output.
- Internal agreement that the system demonstrates the intended concept without overclaiming.

## 9. Development Phases

### Phase 1: Scope and Data Audit

Goal: define what the first prototype can honestly claim.

Main tasks:

- Review existing repo assets, labels, and formulas.
- Standardize the clinical input schema.
- Audit image labeling quality and dataset splits.
- Decide the exact starting model target.

Expected output:

- Finalized prototype scope.
- Cleaned dataset inventory.
- Stable case schema and result schema.

### Phase 2: Product Skeleton and Persistence

Goal: turn the current demo into a durable prototype shell.

Main tasks:

- Keep the React and FastAPI structure.
- Add PostgreSQL-backed case storage.
- Add object storage for uploads and overlays.
- Refactor static metadata flows into database-backed records where appropriate.

Expected output:

- Deployable application shell with persistent case handling.

### Phase 3: Starting Vision Model

Goal: replace metadata-only visual output with real model inference.

Main tasks:

- Prepare training data and annotation format.
- Fine-tune a pre-trained detector.
- Add model inference service to the backend.
- Validate localization quality visually and quantitatively.

Expected output:

- First trained model that produces a usable box or localization output.

### Phase 4: Prognosis Engine Integration

Goal: combine image features and clinical logic into a meaningful prototype output.

Main tasks:

- Map detector outputs into structured features.
- Integrate growth formulas and clinical bias logic.
- Define output metrics and explanatory factors.
- Keep the system deterministic where possible for repeatability.

Expected output:

- End-to-end hybrid analysis pipeline.

### Phase 5: UI and User Flow Refinement

Goal: make the system usable for review, demo, and feedback.

Main tasks:

- Improve result clarity and section ordering.
- Add stronger status and error handling.
- Ensure sample cases remain available.
- Review language for interpretability and caution.

Expected output:

- Usable analyst-facing prototype dashboard.

### Phase 6: Validation and Hosted Prototype

Goal: produce a stable hosted prototype for team review.

Main tasks:

- Deploy frontend and backend.
- Seed sample cases.
- Run smoke tests and clinical plausibility checks.
- Document limitations and known gaps.

Expected output:

- Shareable prototype environment and validation notes.

## 10. Risks and Considerations

### Technical risks

The current architecture is simple, but model inference adds runtime, storage, and artifact-management concerns. If the team tries to add too many backend patterns at once, the prototype may become harder to stabilize than the model itself.

### Data risks

The most serious risk is dataset quality. Synthetic fractures, limited pediatric samples, inconsistent views, weak annotations, and absent longitudinal labels can all produce visually convincing but clinically weak models. This is why the first prototype should use a narrow model scope and explicit hybrid logic.

### Model limitations

A detector can localize an injury region without proving true prognostic validity. The system must not imply that it has learned long-term biological growth behavior from limited data if that has not actually been demonstrated.

### User experience risks

If the interface presents probabilities without explanation, users may overtrust or dismiss the output. The prototype must clearly show what was detected, which inputs were used, and why the result was produced.

### Clinical and governance considerations

Any use of patient data requires consent, governance, and proper storage controls. Even if the prototype uses open or synthetic data, the architecture should not assume permanent use of unsecured image handling.

### Scalability concerns

The first hosted prototype does not need distributed inference or complex orchestration. However, the data model and storage decisions should avoid locking the team into a static-demo architecture that cannot later support real case history, versioned models, or validation workflows.

## 11. Final Prototype Deliverables

At the end of the prototype phase, the team should have:

- A deployed frontend dashboard.
- A deployed FastAPI backend.
- A persistent case and result store.
- Object storage for uploaded and generated images.
- A first trained vision model for physis-region localization.
- A hybrid prognosis engine that combines model output and clinical logic.
- A stable analysis API contract.
- Sample demo cases for deterministic walkthroughs.
- Basic technical documentation for setup, deployment, and limitations.
- A validation summary describing what the prototype does and does not prove.

## Conclusion

The most practical path for Bridge AI is not to jump directly from a mock demo to a full multimodal medical prognosis model. The repository already suggests a better route: keep the existing dashboard and API structure, introduce one real vision model first, and pair it with an explicit prognosis engine that uses image-derived features plus structured clinical logic. That approach creates a prototype that is usable, explainable, and technically honest.

Once the team has stronger labeled data, especially real longitudinal outcome data, Bridge AI can evolve into a more sophisticated multimodal learning system. Until then, the right move is to build a high-quality hybrid prototype that demonstrates credible clinical assistance without pretending to solve the hardest prediction problem too early.
