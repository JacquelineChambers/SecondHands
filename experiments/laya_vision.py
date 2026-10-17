# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
#   "laya @ git+https://github.com/r33drichards/laya-vision.git@9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c",
#   "torch==2.14.1", "torchvision==0.29.1", "transformers==5.17.0", "pillow==13.0.0",
# ]
# ///
"""Run with the root justfile to install the local package into this isolated environment."""

from secondhands.recognition.decision_experiments import main

if __name__ == "__main__":
    main("laya")
