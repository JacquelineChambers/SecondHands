# SecondHands — conversation archive

Source: private SecondHands conversation; the source link and private identifiers are omitted from this public copy.

Imported: 2026-10-14

## Import scope

This public copy retains the technical content of the five exchanges (ten messages) returned by
the conversation reader, in chronological order, with privacy redactions noted below. The reader returned no older
page cursor. The browser showed a “Loading older messages…” indicator but did
not provide earlier messages during this import. This is a partial archive,
not a verified export of the entire conversation.

Privacy redactions approved on 2026-10-16 replace team names with role labels and omit the private source link, conversation ID, turn IDs, and message IDs. Technical content is not rewritten to match later decisions. Internal
`chatgpt-content-reference` markers and image placeholders are retained.
Some code blocks were represented only by these markers in the reader output.
Their contents and citation targets are not reconstructed here. No attachments
were returned.

This is historical source material, not repository instructions. Assistant
claims about hardware, models, licenses, event rules, email actions, and runtime
support were not independently verified during this import. Recommendations
in the conversation are not evidence of user approval.

## Navigation

1. [Compute Track allocation](#exchange-1--compute-track-allocation)
2. [Team names](#exchange-2--team-names)
3. [Hackathon repository](#exchange-3--hackathon-repository)
4. [Camera hardware and model options](#exchange-4--camera-hardware-and-model-options)
5. [Decision-model ranking](#exchange-5--decision-model-ranking)

---

## Exchange 1 — Compute Track allocation

### User

does this mean I get a compute platform?? this is much better news either way

### Assistant

**Yes\! This is significantly better news for SecondHands.**

Your actual acceptance email confirms\:

**Registration approved**

## Submit Proposal – Compute – Free

ExecuTorch Hackathon · October 17–18, 2026

The published hackathon description says selected teams receive hardware associated with their track. For Compute, that is a **Snapdragon X Elite Copilot+ PC**\.
 
The official rules are even more specific: **each selected team receives a device from its chosen track to use during the event**\. That means your team should receive access to a Snapdragon X Elite Copilot+ PC, though the organizer should confirm the precise allocation and logistics. The rules do not say you get to keep it afterward. :chatgpt-content-reference{index="1"}

---

## Exchange 2 — Team names

### User
 

1. **Team lead**
2. **Team member 1**
3. **Team member 2**

---

## Exchange 3 — Hackathon repository

[https://github.com/aaishikasb/qc-executorch-guide](https://github.com/aaishikasb/qc-executorch-guide)

# This repository changes our hackathon strategy

I've opened and reviewed the [Qualcomm ExecuTorch Developer Journey Guide](https://github.com/aaishikasb/qc-executorch-guide), particularly its Compute Track instructions.

**The most important discovery: the organizers intend to provide a Snapdragon X Elite PC with ExecuTorch models already installed. We do not need to compile ExecuTorch from scratch to get our first working demo.**

This is excellent for SecondHands because it eliminates much of the environment-setup risk we were preparing for.

## What the repository confirms

| Area | What the guide specifies |
|--------|--------|
| Compute hardware | Dell Latitude, Snapdragon X Elite |
| Operating system | Windows 11 ARM64 |
| Accelerator | Qualcomm Hexagon NPU, HTP v73 |
| ExecuTorch version | 1.5.1 |
| Qualcomm QAIRT/QNN version | 2.37.0.250724 |
| Starting model | Preinstalled DeepLab image segmentation |
| Starting file | `dlv3_qnn.pte` |
| Execution | Windows ARM64 `qnn_executor_runner.exe` |
| Custom model compilation | Optional advanced workflow |

Source: [Compute Track guide](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/README.md) and [artifact inventory](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/artifacts/README.md)\.

One qualification: the guide says its Windows/NPU instructions were checked against source documentation on October 12, but **not physically executed as part of that review**\. It also says the preinstalled bundle's exact location is still to be supplied by the track team.

Nevertheless, this provides a substantially more concrete starting point than our previous assumptions.

## 2\. There is a crucial implication for SecondHands

The supplied Compute model is **DeepLabV3, an image-segmentation model**, not a gesture classifier or Clef-Flash.

Segmentation identifies regions of an image, such as a person's silhouette. We can potentially use those regions to detect larger movements and create a basic gesture interface.

**Camera video**

Person performing a deliberate movement

**Preinstalled DeepLabV3 via ExecuTorch**

Person segmentation on Snapdragon NPU

**SecondHands movement analysis**

Compare movement patterns against a calibrated reference

**Personalized command**

Recognized movement → confirmed action

**Physical actuator**

Servo, low-voltage lamp or model curtain

This gives us a possible starting point using the organizers' pretrained model rather than having to compile an entirely new AI architecture. It is most suitable for obvious silhouette changes, such as raising an arm or leaning sideways—not detecting subtle facial movements.

For the more ambitious version, we would replace or supplement segmentation with a pose or gesture model.

## 3\. One new compatibility risk: your Astra 2

The Compute machine runs Windows ARM64. Orbbec's current SDK v2 release provides a Windows **x64** build, but does not list native Windows ARM64 support. :chatgpt-content-reference{index="5"}

That's potentially our largest remaining hardware-integration risk.

I recommend preparing these fallback options in order\:

1. Try the Astra 2 directly on the Snapdragon PC, but don't assume its depth SDK or drivers work.
2. Use the PC's built-in camera or a standard compatible USB webcam.
3. Capture RGB/depth on your Mac and stream selected frames over a local network to the Snapdragon PC, which continues to perform the ExecuTorch inference.

Option 3 keeps inference local to the event equipment but introduces an additional computer and connection, so option 2 is the more dependable fallback.

## 4\. What I'd change in our development plan

| When | Task | Owner |
|--------|--------|--------|
| Before Saturday | Test Astra 2 capture on Mac; record calibration gestures | You |
| Before Saturday | Build basic movement detection and calibration logic | You + AI specialist |
| Before Saturday | Prepare simple SecondHands dashboard | Marketing + engineering |
| Saturday, first milestone | Run supplied DeepLab `.pte` on Compute PC | AI specialist |
| Saturday, next milestone | Feed real images to the installed ExecuTorch runtime | Engineering |
| Saturday, next milestone | Recognize a calibrated movement and trigger an action | Engineering |
| Stretch | Integrate Clef-Flash as a higher-level decision layer | AI specialist |

The key benefit is that we can now make the first on-device demonstration depend on **the supplied, preconfigured ExecuTorch environment**\.

The repository also explicitly says source builds and custom model export are optional advanced work. We should take that guidance seriously.

## 5\. What about Clef-Flash?

There is no Clef-Flash deployment in this repository. It does not provide a Clef-Flash `.pte`, quantization recipe, or an NPU-compatible runner for that model.

For SecondHands, I'd continue investigating it separately, with its role limited to occasional higher-level, configurable decisions. Our fast visual recognition should not depend on a 9B model running on every frame.

## 6\. What I would do right now

On your Apple Silicon Mac, clone the repository\:

::chatgpt-content-reference{index="0"}



You can also read the [Compute guide directly on GitHub](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/README.md)\.

When you receive the Snapdragon PC, the first test described by the guide is\:

::chatgpt-content-reference{index="1"}



That command assumes we're in the preinstalled model directory and the expected files are present. A successful default-input run is only a smoke test; we then need real inputs and verified output.

The repository's artifact inventory explicitly says those files are **not distributed in GitHub**, so we must obtain their installed location from the track team.

### My recommendation

This is a useful change of direction: **SecondHands should be built as an application around the organizer-provided ExecuTorch inference stack**, not as a project that first has to reproduce the entire Qualcomm compiler toolchain.

Our next major engineering task should be implementing the personalized movement-calibration pipeline, with a camera and model interface that can be swapped without rewriting the application.

That would let us demonstrate the distinctive SecondHands feature—two people using different movements to operate the same physical object—while taking advantage of the supplied Snapdragon platform.

---

## Exchange 4 — Camera hardware and model options

### User

ok, so let's leave out the astra orbec for now, as we can just use the device's camera.
questions:
a) what are the specifications of the pc?
b) presumably windows only, correct? no linux?
c) presumably the first step is to get the framework working, with supplied models, and then we can try better models. There is a link to the qualcomm ai hub (I forget the next name), so presumably they will be ok with pulling other models, so we need to see what other models they have.

### Assistant

# SecondHands — Compute Track hardware and model options

**Your understanding is correct on all three points**, with one important qualification: a model appearing in Qualcomm AI Hub does not automatically mean it's ready to run through ExecuTorch.

The hackathon repository gives us a much clearer technical starting point than we had before.

## A. What PC are we getting?

The [official Compute Track guide](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/README.md) identifies the supplied computer as a **Dell Latitude with Snapdragon X Elite**, running Windows 11 ARM64.

| Component | Confirmed specification |
|--------|--------|
| Manufacturer | Dell |
| Family | Latitude |
| Processor | Qualcomm Snapdragon X Elite |
| CPU architecture | ARM64 |
| Operating system | Windows 11 |
| AI accelerator | Qualcomm Hexagon NPU, HTP v73 |
| NPU performance | Up to 45 TOPS, theoretical |
| GPU | Integrated Qualcomm Adreno |
| ExecuTorch target | `SC8380XP` |
| Starting AI model | DeepLabV3 image segmentation |

**What we don't know yet\:** The exact Dell Latitude model number, RAM, SSD capacity, display configuration, and camera specification.

The guide doesn't provide those details.

One possibility is the Dell Latitude 7455, which Dell sells with 16 GB or 32 GB of RAM, a 14-inch display, and an FHD/IR webcam. But **we cannot assume that is the model the organizers will provide**\. :chatgpt-content-reference{index="2"}

[images: Dell Latitude 7455 Snapdragon X Elite laptop official product photo]

**Illustrative hardware: Dell Latitude 7455**

This is an example of a Snapdragon X Elite Latitude, not a confirmed identification of your assigned computer.

[Dell specifications](https://www.dell.com/en-us/shop/dell-computer-laptops/new-latitude-7455-laptop/spd/latitude-14-7455-laptop)

## B. Windows only? What about Linux?

**For the hackathon's supplied Compute environment: yes, plan on Windows 11 ARM64.**

The repository specifically supplies instructions for Windows executable files (`.exe`\), Qualcomm DLLs, and Hexagon NPU support.

However, Linux is not categorically unsupported.

| Environment | Suitability |
|--------|--------|
| Windows 11 ARM64 | **Primary, documented hackathon environment** |
| Windows with native ARM64 apps | Supported deployment path |
| WSL / Ubuntu | Documented as an ExecuTorch development environment, but not the supplied demo runtime |
| Native Linux installed on Dell | Not documented as a supported hackathon configuration |
| Your Apple Silicon Mac | Suitable for developing models and application logic ahead of time |

The ExecuTorch Qualcomm documentation supports Windows and WSL development workflows. It does **not** mean we should replace the provided Windows installation with Linux. :chatgpt-content-reference{index="4"}

I would keep Windows intact, use the supplied runtime, and develop SecondHands around that.

## C. Yes — first run the supplied models, then explore Qualcomm AI Hub

That's exactly the sequence I'd recommend.

The service you're remembering is **Qualcomm AI Hub**, which has two useful parts\:

[images: Qualcomm AI Hub model catalog website AI models]

**[Qualcomm AI Hub Models — Compute catalog](https://aihub.qualcomm.com/compute/models)**

Browse pretrained models for image classification, gesture recognition, pose estimation, robotics, segmentation and more.

---

[images: Qualcomm AI Hub Workbench machine learning compiler profiling web interface]

**[Qualcomm AI Hub Workbench](https://workbench.aihub.qualcomm.com/)**

Compile supported models, profile performance, and test on hosted Qualcomm devices. A Qualcomm account/API token is required for the development workflow. :chatgpt-content-reference{index="7"}

### Models worth investigating for SecondHands

These are actual AI Hub catalog entries, ranked for your adaptive movement-control concept.

[images: MediaPipe hand gesture recognition skeleton 21 hand landmarks open palm tracking demo]

**1\. [MediaPipe Hand Gesture Recognition](https://aihub.qualcomm.com/models/mediapipe_hand_gesture)** (Top candidate)

Detects hands, 21 hand landmarks and predefined gestures.

Its published components include a 1.76M-parameter palm detector, 2.72M-parameter hand-landmark detector and 143K-parameter gesture classifier.

Excellent for hand controls; personalizing to subtle movements will require additional logic or training. :chatgpt-content-reference{index="9"}

---

[images: MediaPipe pose estimation human body joints pose landmarks tracking camera demonstration]

**2\. [MediaPipe Pose Estimation](https://aihub.qualcomm.com/models/mediapipe_pose)**

Tracks body landmarks for movements such as leaning, raising a shoulder, or turning the upper body.

Especially relevant to users with limited hand movement. :chatgpt-content-reference{index="11"}

---

[images: computer vision face landmarks mesh tracking eyes and facial position example]

**3\. [MediaPipe Face Detection](https://aihub.qualcomm.com/models/mediapipe_face)**

A lightweight face detection and landmark pipeline.

Useful for head position and coarse face movement, though not a complete facial-gesture recognizer. :chatgpt-content-reference{index="13"}

---

[images: PoseNet MoveNet human pose keypoints skeleton joint tracking illustration]

**4\. [PoseNet MobileNet](https://aihub.qualcomm.com/models/posenet_mobilenet)**

Tracks 17 human body joints, providing spatial measurements for upper-body and arm movements.

Alternative to MediaPipe Pose; useful for deliberate movement detection. :chatgpt-content-reference{index="15"}

---

[images: MobileNet convolutional neural network diagram lightweight image classification]

**5\. [MobileNetV2](https://aihub.qualcomm.com/models/mobilenet_v2) / [MobileNetV3-Small](https://aihub.qualcomm.com/models/mobilenet_v3_small)**

Small, efficient image-classification backbones.

Promising for a custom trained gesture recognizer, but standard ImageNet weights do not already recognize our intended commands. :chatgpt-content-reference{index="18"}

One caution: several catalog pages list Snapdragon X Elite among the supported chipset families while also displaying a current *Not supported* status for the selected view. We'll need to inspect the actual downloadable model, runtime and selected device before treating any of them as deployment-ready.

## The important distinction: AI Hub versus ExecuTorch

Qualcomm AI Hub Workbench offers model compilation targeting ONNX Runtime, LiteRT, and Qualcomm QNN formats. It does **not** generally export an ExecuTorch `.pte` directly. :chatgpt-content-reference{index="19"}

So there are two possibilities\:

| Path | Advantage | Hackathon consideration |
|--------|--------|--------|
| AI Hub model → ONNX Runtime → Qualcomm NPU | Often easier Windows deployment | Does not by itself demonstrate ExecuTorch |
| PyTorch model → ExecuTorch → QNN → NPU | Directly demonstrates the event's main framework | More export and compatibility work |

We could also combine them: use a pretrained landmark detector for preprocessing and have a small custom decision model running in ExecuTorch classify those features into personalized actions.

That is particularly attractive for SecondHands.

## Recommended execution sequence

**Stage 1 — Verify the organizer's installed framework**

On Saturday, locate the preinstalled `dlv3_qnn.pte` and matching ARM64 runner. Run the supplied example, then use real images and confirm the segmentation outputs.

The guide's initial command is\:

::chatgpt-content-reference{index="0"}



This is initially a smoke test, not proof of useful predictions or NPU acceleration.

---

**Stage 2 — Use the built-in camera**

Verify Windows camera access, capture images, and connect them to the supplied model's preprocessing and inference pipeline.

This removes the Astra 2 compatibility issue and keeps the demonstration on one computer.

---

**Stage 3 — Try a better recognition model**

Start with MediaPipe Hand Gesture or Pose Estimation. Establish the model's actual supported runtime first.

Demonstrate reliable hand or head landmark tracking.

---

**Stage 4 — Implement personalized calibration**

Volunteer A uses a hand gesture; volunteer B uses a head movement. Both are mapped to the same action through calibrated decision logic.

Run the learned decision model in ExecuTorch, while maintaining a simple fallback using explicit geometric thresholds.

---

**Stage 5 — Physical response**

Send a confirmed decision to a USB-connected microcontroller controlling a low-voltage light or miniature curtain.

We can do this even without the VENTUNO Q.

## What about Clef-Flash?

We should keep it as the experimental extension, not the first model to install.

The Snapdragon X Elite is a substantially better target for experimentation than the VENTUNO Q, especially if the Dell has 32 GB RAM. But we haven't established the exact memory configuration or an ExecuTorch Clef-Flash port.

A sensible two-model architecture would be\:

`Camera → Fast gesture recognition → ExecuTorch personalized decision → Physical action`

With Clef-Flash invoked occasionally for higher-level, configurable decisions rather than on every video frame.

This allows us to demonstrate real-time interaction without relying on a 9B model to keep up with the camera.

### What I'd do before the event

**I'd prioritize MediaPipe Hand Gesture Recognition and MediaPipe Pose Estimation as the two models for the AI specialist to investigate now.** Both are directly relevant to SecondHands and have published implementations and pretrained weights. Qualcomm also provides a [local PyTorch demo](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/mediapipe_hand_gesture/README.md) for its hand gesture model, which can be tested before the Snapdragon hardware arrives. :chatgpt-content-reference{index="21"}

The good news is we no longer need to build the whole AI stack from scratch. The Compute guide gives us a ready-made first deployment, and AI Hub provides a useful catalog of alternatives.

Our main engineering challenge becomes **turning recognized movements into calibrated, reliable physical actions**—which is exactly what makes SecondHands distinctive.

---

## Exchange 5 — Decision-model ranking

### User

ok, so I really do want to push the decision model frontier. Let's review your prior model suggestion when we thought we had the Ventuino, questions:

a) are these the right models to pursue for the PC?

b) are they available on for executorch on this platform, and if not do we absolutely need to run Executorch, where is your evidence for that?

c) what other decision models can we expect to try out.

d) create a new ranking



Here is your venduino ranking:
```
Rank	Model	Dynamic choices?	Practicality for hackathon
1	MobileCLIP2-S0	Yes, via text-image similarity	High on Mac; medium-risk ExecuTorch port
2	Laya Vision 201M	Yes, native typed decisions	Experimental
3	MediaPipe hand landmarks + small PyTorch MLP	Fixed/trained classes	High for a working system
4	HSEmotion EfficientNet-B0	No, fixed expression classes	Good expression baseline
5	Mapika Decider 2B Vision	Yes, typed choices	High deployment risk
6	Laya 322M / 421M	Yes, text/JSON choices	Useful as a second-stage decider
7	Clef-Flash 9B	Yes, typed multimodal decisions	Too large and risky for this event
```

### Assistant

# Decision models for SecondHands — revised Compute Track ranking

Research review · October 14, 2026 · Snapdragon X Elite / Windows ARM64

**Moving from the Arduino VENTUNO Q to the Snapdragon X Elite PC changes the ranking substantially.** We can now consider larger multimodal decision models, including Clef-Flash 9B, without immediately ruling them out on memory grounds.

However, I would distinguish three different objectives\:

1. **Push the decision-model frontier\:** Demonstrate genuinely configurable, one-pass multimodal decision-making rather than conventional classification.
2. **Demonstrate on-device inference\:** Run models locally on the supplied Snapdragon PC without a cloud inference service.
3. **Demonstrate ExecuTorch\:** Execute at least a meaningful part of SecondHands through the framework central to this hackathon.

These objectives overlap, but they are not interchangeable.

## B. First, is ExecuTorch mandatory?

The evidence points strongly toward **yes, for a competitive and clearly compliant submission**\.

The [official hackathon registration page](https://luma.com/executorch-hackathon) explicitly describes the challenge as building AI experiences powered by ExecuTorch and concludes with an instruction to build using that framework. The [Open Source AI Week event description](https://opensourceaiweek.com/the-hackathon/) repeats that framing. :chatgpt-content-reference{index="2"}

There is an important nuance: I did not find a published rule stating that *every model* in a multi-model application must run through ExecuTorch.

That suggests a defensible architecture\:

- A real, consequential component of SecondHands runs on the Snapdragon PC through **ExecuTorch**\.
- An experimental decision model runs locally through its own supported runtime.
- Both contribute to one integrated on-device demonstration.

I would **not** claim this hybrid arrangement is explicitly approved. But it follows the event's technical objective much more closely than using Ollama alone and merely mentioning ExecuTorch.

The newly supplied [Compute Track guide](https://github.com/aaishikasb/qc-executorch-guide/tree/main/Compute) confirms that the organizers intend to preinstall an ExecuTorch image-segmentation model and its Qualcomm runtime. That's our route to establishing a working ExecuTorch component without undertaking custom NPU compilation first.

## A. Are the original models still the right ones for the PC?

Mostly yes, but I would make four changes.

First, **Laya Vision 201M and Mapika Decider 2B Vision move to the top** because they're genuine vision-capable decision models, have downloadable weights and documented inference APIs, and are manageable enough to experiment with.

Second, **Clef-Flash 9B moves up significantly**\. The Snapdragon X Elite is a more plausible platform for it than the VENTUNO Q, although we must check the actual PC's RAM and runtime support. Ollama publishes an approximately 11 GB quantized package. :chatgpt-content-reference{index="4"}

Third, **MobileCLIP2-S0 remains useful, but it is not a Jev-style decision model**\. It compares image and text embeddings, making it a very good benchmark for zero-shot visual choices. Its probabilities should not be interpreted as calibrated decision confidence. Apple's pretrained weights also have separate research licensing terms. :chatgpt-content-reference{index="5"}

Fourth, I would add two models that weren't in our original ranking: **SmolVLM-500M** and **Vision-Jev 0.8B**\. SmolVLM is especially interesting because upstream ExecuTorch already has a Qualcomm multimodal export recipe.

## B. Which models are actually available for ExecuTorch on Snapdragon X Elite?

This is the compatibility picture I can substantiate.

| Model | Pretrained weights | Published Qualcomm ExecuTorch pathway | Ready-made Compute Track `.pte` |
|--------|--------|--------|--------|
| Supplied DeepLabV3 | Yes | Yes, in event guide | Intended to be preinstalled |
| SmolVLM-500M | Yes | Upstream QNN VLM recipe | Not supplied |
| InternVL3-1B | Yes | Upstream QNN VLM recipe | Not supplied |
| MobileCLIP2-S0 | Yes | No model-specific port verified | No |
| Laya Vision 201M | Yes | No model-specific port verified | No |
| Mapika Decider 2B Vision | Yes | No model-specific port verified | No |
| Clef-Flash 9B | Yes | No model-specific port verified | No |
| Vision-Jev 0.8B | Adapter plus separate base weights | No model-specific port verified | No |
| Laya 322M/421M | Yes | No model-specific port verified | No |

The most useful new finding is that ExecuTorch's Qualcomm model examples explicitly include **SmolVLM-500M and InternVL3-1B**, with vision encoder quantization and multimodal compilation support. :chatgpt-content-reference{index="6"}

That is substantially stronger compatibility evidence than merely finding a model in Qualcomm AI Hub. However, these are upstream Qualcomm workflows, not verified attendee-ready packages for this Dell PC.

Another important distinction: SmolVLM and InternVL3 are conventional generative vision-language models. To make them behave like typed decision models, we'd need either constrained option scoring or an additional trained decision head.

**My conclusion\:** We should not spend the first day attempting to port Clef-Flash to ExecuTorch. We can satisfy the framework objective using a model for which the organizers provide a working runtime, while testing genuine decision models through their supported local inference stacks.

---

## C &amp; D. New ranking — optimized for pushing the frontier

This is my ranking for **SecondHands on the Snapdragon X Elite**, balancing innovation, vision capability, local feasibility, and the possibility of meaningful results over a two-day hackathon.

## 1

**[Laya Vision 201M](https://huggingface.co/thaitea/laya-vision-201m)**

(Best first frontier experiment)

201M parameters · \~805 MB weights · CC BY-NC-SA 4.0

A genuinely multimodal, non-generative model that accepts images and typed questions and directly scores predefined choices.

It supports choice, yes/no, and ordinal scores. Its small size gives us a reasonable chance of running a meaningful benchmark on your Mac before Saturday.

The authors report approximately 63 ms inference on an NVIDIA L4 GPU, but that's not an X Elite measurement. Their model card also warns that calibration needs rechecking for new domains. :chatgpt-content-reference{index="8"}

**SecondHands use\:** Compare intentional head, facial or hand gestures against configurable descriptions.

**Main risks\:** Experimental model, uncertain Windows ARM64 performance, no ExecuTorch port, noncommercial ShareAlike weights.

---

## 2

**[Mapika Decider 2B Vision](https://huggingface.co/Mapika/decider-2b-vision)**

\~2B parameters · \~4.1 GB BF16 weights · Apache 2.0

A true image-plus-question decision model derived from Qwen3.5, producing option probabilities without generating an answer.

It has released weights, inference code, and published evaluation results. The developer documents CPU and Apple Silicon paths for the Decider family. :chatgpt-content-reference{index="10"}

**SecondHands use\:** Compare visual gestures against a dynamically supplied set of possible actions.

**Main risks\:** Much heavier than Laya Vision; its vision-specific performance on Windows ARM64 hasn't been verified. Published image calibration is not evidence of reliability for your gestures.

---

## 3

**[Clef-Flash 9B](https://huggingface.co/Cloudflare/clef-flash)**

(High-ambition experiment)

9B parameters · \~11–12 GB Ollama package · Apache 2.0

Of the larger models, Clef-Flash offers one of the most interesting architectures for multi-question, schema-conditioned visual decision-making.

It can jointly evaluate several typed questions using a vision-language backbone and custom readout head. :chatgpt-content-reference{index="12"}

**SecondHands use\:** Higher-level decisions involving a captured image, interaction context, and a personalized action menu.

**Main risks\:** Actual PC RAM unknown, Windows ARM64 runtime untested, no verified ExecuTorch port, and potentially substantial CPU inference latency.

I would test this experimentally, not make it responsible for every camera frame.

---

## 4

**[SmolVLM-500M](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) \+ constrained decision output**

(Best advanced ExecuTorch pathway)

\~500M parameters · Apache 2.0

Not a native decision model, but it has an important practical advantage: ExecuTorch documents its Qualcomm VLM deployment architecture. :chatgpt-content-reference{index="14"}

**SecondHands use\:** Run local multimodal understanding in ExecuTorch and evaluate a constrained decision from image context.

**Main risks\:** Requires custom decision-scoring logic; target-PC export and NPU execution are still work to be validated.

---

## 5

**[MobileCLIP2-S0](https://huggingface.co/apple/MobileCLIP2-S0)**

\~300 MB checkpoint · Apple ML Research Model terms

Scores the similarity between an image and arbitrary text descriptions. Small enough to be a useful local baseline for zero-shot visual choice recognition. :chatgpt-content-reference{index="16"}

**SecondHands use\:** Compare descriptions like "head tilted left", "open palm", or "hand resting" against live frames.

**Main risks\:** Similarity does not establish intent, and the model's weights are not under a simple Apache/MIT license. ExecuTorch conversion is unverified.

---

## 6

**[Vision-Jev 0.8B](https://huggingface.co/LMDHQ-0420/vision-jev)**

Qwen3.5-0.8B backbone · Apache 2.0 project weights

A recent experimental release with separately downloadable adapters and typed Choice, Noul, and Score heads.

The developer publishes a frozen 12,000-question test report and self-reported mean decision latency of 87.6 ms for the 0.8B variant. :chatgpt-content-reference{index="18"}

**SecondHands use\:** Try a compact Qwen-based visual decision head and evaluate calibration on personalized movements.

**Main risks\:** Requires the base model and a specialized inference pipeline. Those timings are not measurements on the Compute PC.

---

## 7

**[JEVision 0.8B](https://huggingface.co/divyanshx11/JEVision)**

Qwen3.5-0.8B base plus adapters · Apache 2.0

Another compact research model, providing image-based Choice, Noul, and Score responses through a local API.

Unlike some adapter-only releases, it includes a bundled serving runtime. Its documented tests were performed on Linux with an NVIDIA GPU, and the visual evaluation remains limited. :chatgpt-content-reference{index="20"}

**SecondHands use\:** Compare an alternate Jev-style architecture against Laya Vision and Mapika using the same test images.

**Main risks\:** Early research release and uncertain portability to Windows ARM64.

---

## 8

**[SelfJev-4B Vision](https://huggingface.co/Jwuthrich/selfjev-4b-vision)**

4B backbone · LoRA adapter · CUDA-oriented reference deployment

A larger, genuinely multimodal typed decision model with published self-reported evaluations and a local serving interface. Its documented image path uses a CUDA GPU, which is not available on the Snapdragon X Elite. :chatgpt-content-reference{index="22"}

**SecondHands use\:** Research comparison for higher-quality image decisions.

**Main risks\:** Windows ARM64 execution and memory/performance are unverified. Lower short-term priority.

---

## 9

**[Laya 421M / multilingual 322M](https://huggingface.co/convaiinnovations/laya)**

Text/JSON decision models · Apache 2.0

These are compact, typed decision models, but they don't directly process images. :chatgpt-content-reference{index="24"}

**SecondHands use\:** Evaluate structured sensor features, user calibration profiles and action-selection policies after a vision model has extracted meaningful observations.

Potentially valuable as the **higher-level decision layer**, especially if we want to customize user interaction without adding more visual computation.

---

## 10

**MediaPipe landmarks + small PyTorch decision classifier**

Not a frontier foundation model, but still our most dependable engineering fallback.

A hand, face, or body landmark detector extracts measurable physical movements. A small, trained PyTorch network processes those signals, and ExecuTorch executes that network.

**SecondHands use\:** Personalized controls that remain responsive while a larger decision model runs asynchronously.

This should be part of the architecture even if our primary research experiments succeed.

## A new model worth watching: SigLIP2

I also checked [Qualcomm AI Hub's SigLIP2 listing](https://aihub.qualcomm.com/compute/models/siglip2)\.

SigLIP2 is a modern Apache-2.0 image-text similarity model and could provide a useful comparison against MobileCLIP2 without Apple's separate model-weight terms.

However, the current Compute catalog explicitly displays **Not supported**, despite listing Snapdragon X Elite in its device metadata. That's insufficient to claim a downloadable, accelerator-ready package for the event. :chatgpt-content-reference{index="26"}

I would investigate it if MobileCLIP2 becomes difficult to deploy, but would not prioritize it over the genuine typed-decision models.

---

## How I'd make this a frontier decision-model project

I think there is a more interesting experiment than simply asking which model recognizes a raised hand.

**Can we create a personalized, dynamically configurable decision system that learns a person's usable movements and converts those movements into intentional actions, without retraining the entire vision backbone?**

That would be the technical contribution of SecondHands.

**Built-in laptop camera**

Live image frames and short movement sequences

**Fast local visual feature extraction**

ExecuTorch where supported, with temporal motion features

**Personalized calibration**

Examples of the movements a specific person can perform

**Dynamic visual decision model**

Laya Vision, Mapika Decider or Clef-Flash

**Intent verification and action mapping**

Explicit confirmation, rejection and false-trigger prevention

**Physical response**

Low-voltage lamp, servo or miniature curtain

The important engineering distinction is that **a model recognizing a head movement does not automatically establish that the user intended to activate something**\.

Our calibration and temporal decision layer would be responsible for that distinction.

A fast visual model could analyze every few frames. A sophisticated decision model could evaluate a candidate event using several captured frames, the user's capabilities, the current application mode and a predefined set of possible actions.

That avoids depending on a 9B model for the continuous control loop.

## The experiment I'd run before Saturday

I would have the AI specialist run the same small test set through Laya Vision, Mapika Decider Vision, and MobileCLIP2 on your Apple Silicon Mac. This immediately gives us a comparative baseline independent of the supplied PC.

We would create approximately 30–50 labeled observations showing deliberate movements, neutral movements, ambiguous gestures and examples from two different volunteers.

For each model, measure\:

| Metric | Why it matters |
|--------|--------|
| Decision accuracy | Does it choose the correct observable gesture? |
| False activation rate | Does it trigger when no command was intended? |
| Abstention performance | Can it decline uncertain decisions? |
| Median / p95 latency | How responsive is it? |
| Memory use | Will it fit the event hardware? |
| Calibration effort | How many examples does a new user need? |
| Configurability | Can options change without retraining? |

These measurements would be specific to SecondHands, rather than relying on published benchmarks that test unrelated images or decision tasks.

### My recommended division of effort

| Owner | Task |
|--------|--------|
| AI specialist | Compare Laya Vision, Mapika Decider and MobileCLIP2 |
| You | Camera pipeline, calibration data collection, actuator and application integration |
| Doctor | Choose movements that are accessible, intentional and practical; define safe failure behavior |
| Marketing teammate | Develop the two-person demonstration, product story and presentation |

On Saturday, the first job remains getting the supplied DeepLab ExecuTorch demo running. Then we can assess whether a genuinely useful part of the vision-decision pipeline can be migrated into ExecuTorch, while the frontier models run in their native local runtimes.

## Final prioritization

My preferred three-model research portfolio

# 201M

Laya Vision

Compact typed decisions

# 2B

Mapika Vision

Larger typed model

# 9B

Clef-Flash

High-end stretch

I would make **Laya Vision 201M the first experiment, Mapika Decider 2B Vision the second, and Clef-Flash 9B the stretch experiment**\. In parallel, investigate SmolVLM-500M specifically because of its documented Qualcomm ExecuTorch pathway.

That's a meaningful way to push the frontier while preserving a credible path to a finished hackathon submission.

The remaining hardware unknown that could change this ranking is the **actual RAM configuration of the supplied Dell**\. A 16 GB machine makes 9B research much less attractive than a 32 GB machine, particularly when running a second vision model at the same time.

And one licensing distinction matters for SecondHands' commercial aspirations: Laya Vision's **CC BY-NC-SA 4.0** weights are fine to investigate for research, subject to license conditions, but we should not build the long-term commercial product around them without resolving those rights. Mapika Decider and Clef-Flash have more permissive published model licenses.

---
