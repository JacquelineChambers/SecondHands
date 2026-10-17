# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
#   "torch==2.14.1", "torchvision==0.29.1", "transformers==4.57.6", "pillow==13.0.0",
# ]
# ///
"""Run the pinned SmolVLM experiment in its own dependency environment."""

from secondhands.recognition.decision_experiments import main

if __name__ == "__main__":
    main("smolvlm")
