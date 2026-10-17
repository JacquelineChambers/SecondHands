# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
#   "decider-ai @ git+https://github.com/Mapika/decider.git@d6fc522aed7fc392576a9b66a330409bc6c382bd",
#   "torch==2.14.1", "torchvision==0.29.1", "transformers==5.20.1", "pillow==13.0.0",
# ]
# ///
"""Run the pinned Mapika vision experiment in its own dependency environment."""

from secondhands.recognition.decision_experiments import main

if __name__ == "__main__":
    main("mapika")
