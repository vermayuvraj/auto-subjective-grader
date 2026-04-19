import os

os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
import easyocr
from pix2tex.cli import LatexOCR


def main() -> None:
    print("Preloading SentenceTransformer model cache...")
    SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

    print("Preloading CLIP model cache...")
    CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    print("Preloading EasyOCR model cache...")
    easyocr.Reader(["en"], gpu=False)

    print("Preloading pix2tex model cache...")
    LatexOCR()


if __name__ == "__main__":
    main()
