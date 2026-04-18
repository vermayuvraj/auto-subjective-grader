# Auto Subjective Grader — Absolute First-Principles Technical Encyclopedia

> **Purpose:** Guide meeting preparation — every concept explained from scratch  
> **Author:** Yuvraj Verma  
> **Note:** Every term in every heading and subheading is explained. No assumed knowledge beyond school mathematics.

---

# TABLE OF CONTENTS

## PART A — THE PROBLEM OF REPRESENTING LANGUAGE AS NUMBERS
- A.1 Why Computers Need Numbers
- A.2 Binary Representation & Bits
- A.3 ASCII and Unicode: Characters as Numbers
- A.4 The Problem of Representing Words
- A.5 One-Hot Encoding — Definition, Construction, Failure
- A.6 Vector Spaces — What They Are and Why They Matter
- A.7 Dense Vectors — The Solution
- A.8 Distributional Semantics — The Core Hypothesis
- A.9 Word2Vec: Training Words to Encode Meaning
- A.10 GloVe: Global Co-occurrence Statistics

## PART B — NEURAL NETWORKS: THE BUILDING BLOCK
- B.1 What is a Neuron?
- B.2 Activation Functions — Why Non-Linearity is Essential
- B.3 Layers and Deep Networks
- B.4 Loss Functions — Measuring Error
- B.5 Backpropagation — How Networks Learn
- B.6 Gradient Descent Variants
- B.7 Overfitting, Underfitting, and Regularization

## PART C — WHY RNNS FAILED AND TRANSFORMERS WON
- C.1 Sequences in NLP
- C.2 Recurrent Neural Networks (RNN) — Architecture
- C.3 The Vanishing Gradient Problem — Mathematical Proof
- C.4 LSTM: The Gated Solution
- C.5 Why LSTMs Are Still Not Enough

## PART D — THE TRANSFORMER ARCHITECTURE (COMPLETE)
- D.1 The "Attention is All You Need" Insight
- D.2 Tokenization — Turning Words into Indices
- D.3 Token Embeddings — The Lookup Table
- D.4 Positional Encoding — Injecting Order
  - D.4.1 Sinusoidal Positional Encoding — Mathematical Derivation
  - D.4.2 Learnable Positional Embeddings
- D.5 Query, Key, Value — The Core Abstraction
  - D.5.1 The Database Analogy
  - D.5.2 Linear Projection Matrices Wq, Wk, Wv
  - D.5.3 Computing Raw Attention Scores (QKᵀ)
  - D.5.4 The Scaling Factor √d_k — Why and How
  - D.5.5 Softmax — Converting Scores to Probabilities
  - D.5.6 Weighted Sum of Values
  - D.5.7 The Complete Attention Formula
- D.6 Multi-Head Attention — Purpose and Mechanics
  - D.6.1 Why Multiple Heads?
  - D.6.2 Concatenation and Output Projection
  - D.6.3 Computational Cost
- D.7 The Feed-Forward Sub-layer
  - D.7.1 Architecture and Dimensions
  - D.7.2 GELU vs ReLU — Detailed Comparison
- D.8 Residual Connections (Skip Connections)
  - D.8.1 The Vanishing Gradient Problem Revisited
  - D.8.2 How Residuals Solve It
  - D.8.3 Identity Initialization Principle
- D.9 Layer Normalization
  - D.9.1 The Problem Without Normalization
  - D.9.2 Layer Norm Formula — Every Symbol Explained
  - D.9.3 Layer Norm vs Batch Norm — Key Differences
- D.10 The Complete Encoder Block — Putting It Together

## PART E — BERT AND SENTENCE-BERT (COMPLETE)
- E.1 What is BERT?
- E.2 WordPiece Tokenization — Full Algorithm
  - E.2.1 Why Not Word-Level Tokenization?
  - E.2.2 Why Not Character-Level?
  - E.2.3 The BPE Family — Byte Pair Encoding
  - E.2.4 WordPiece Selection Criterion
  - E.2.5 Special Tokens: [CLS], [SEP], [MASK], [PAD]
- E.3 BERT's Three Input Embeddings
  - E.3.1 Token Embedding
  - E.3.2 Segment Embedding
  - E.3.3 Positional Embedding
  - E.3.4 Summing the Three Embeddings
- E.4 BERT Pre-Training
  - E.4.1 Masked Language Modeling (MLM) — Full Explanation
  - E.4.2 Why 80/10/10 Masking Split?
  - E.4.3 Next Sentence Prediction (NSP)
  - E.4.4 Pre-Training Scale and Hardware
- E.5 Sentence-BERT
  - E.5.1 The N² Problem with Vanilla BERT
  - E.5.2 Siamese Network — Architecture and Intuition
  - E.5.3 Natural Language Inference Fine-tuning
  - E.5.4 Triplet Loss — Full Derivation
  - E.5.5 Multiple Negative Ranking Loss
- E.6 all-MiniLM-L6-v2: Knowledge Distillation
  - E.6.1 What is Knowledge Distillation?
  - E.6.2 Teacher-Student Framework
  - E.6.3 KL Divergence — What It Measures
  - E.6.4 MiniLM: Attention Distillation
  - E.6.5 Model Architecture Comparison Table
- E.7 Mean Pooling — Sentence to Single Vector
  - E.7.1 Why Not Use the [CLS] Token?
  - E.7.2 The Pooling Formula
  - E.7.3 Attention Masking for Padding
- E.8 Cosine Similarity — Complete Analysis
  - E.8.1 Dot Product — Definition and Geometry
  - E.8.2 L2 Norm — Definition
  - E.8.3 The Cosine Formula Derived from Law of Cosines
  - E.8.4 Why Not Euclidean Distance?
  - E.8.5 High-Dimensional Geometry Intuition
  - E.8.6 The Leniency Curve — Why 0.6 Threshold?

## PART F — VISION MODELS (COMPLETE)
- F.1 Convolutional Neural Networks — From Pixels to Features
  - F.1.1 What is a Convolution?
  - F.1.2 Stride, Padding, and Output Size
  - F.1.3 Max Pooling — Spatial Downsampling
  - F.1.4 Batch Normalization
  - F.1.5 VGG Architecture — Depth Through Simplicity
  - F.1.6 ResNet — Skip Connections in CNNs
- F.2 Vision Transformer (ViT)
  - F.2.1 The Core Idea: Image as Sequence of Patches
  - F.2.2 Patch Splitting and Flattening
  - F.2.3 Linear Patch Embedding
  - F.2.4 Class Token in ViT
  - F.2.5 2D Positional Embeddings
  - F.2.6 ViT Encoder Blocks
  - F.2.7 Output: The Image Embedding
- F.3 CLIP — Contrastive Language-Image Pre-training
  - F.3.1 The Dual-Encoder Design
  - F.3.2 Shared Embedding Space
  - F.3.3 The Contrastive Learning Framework
  - F.3.4 InfoNCE Loss — Full Mathematical Derivation
  - F.3.5 Temperature Parameter τ
  - F.3.6 Why 400 Million Image-Text Pairs?
  - F.3.7 How CLIP Encodes Diagram Images in the Project
  - F.3.8 L2 Normalization Before Cosine Similarity

## PART G — OCR ENGINES (COMPLETE)
- G.1 What is OCR and Why is it Hard?
- G.2 EasyOCR — Text Detection with CRAFT
  - G.2.1 CRAFT Overview
  - G.2.2 VGG-16 Backbone — Block by Block
  - G.2.3 Feature Pyramid Network (FPN) — Multi-Scale Fusion
  - G.2.4 U-Net Decoder — Skip Connections for Resolution Recovery
  - G.2.5 Region Score Heatmap
  - G.2.6 Affinity Score Heatmap
  - G.2.7 Post-Processing: Heatmap → Bounding Boxes
- G.3 EasyOCR — Text Recognition with CRNN
  - G.3.1 CRNN Overview
  - G.3.2 CNN Feature Extractor — Feature Columns
  - G.3.3 Bidirectional LSTM — Architecture
  - G.3.4 LSTM Cell Equations — Every Symbol Explained
  - G.3.5 Why Bidirectional?
  - G.3.6 CTC: Connectionist Temporal Classification
  - G.3.7 The Blank Token
  - G.3.8 CTC Collapse Rules
  - G.3.9 CTC Training Loss — Dynamic Programming
  - G.3.10 Greedy CTC Decoding vs Beam Search
- G.4 Google Vision AI
  - G.4.1 API hierarchy: Page → Block → Paragraph → Word → Symbol
  - G.4.2 Language Hints and the BCP-47 Handwriting Tag
  - G.4.3 Image Size Constraints and Compression
- G.5 Azure Document Intelligence
  - G.5.1 Prebuilt-Read Model
  - G.5.2 Polygon Bounding Boxes
  - G.5.3 Multi-Page PDF Processing

## PART H — FORMULA PIPELINE (COMPLETE)
- H.1 Why Formulas Need Special Treatment
- H.2 Formula Region Detection — Heuristics
  - H.2.1 Y-Coordinate Block Grouping
  - H.2.2 The `_looks_formula_like` Function
  - H.2.3 Signal Character Density
- H.3 pix2tex (LatexOCR) — Image to LaTeX
  - H.3.1 The Encoder-Decoder Paradigm
  - H.3.2 ResNet Encoder — Feature Grid
  - H.3.3 Autoregressive Decoding
  - H.3.4 Cross-Attention — Q from Decoder, K/V from Encoder
  - H.3.5 Masked Self-Attention in Decoder
  - H.3.6 The Complete Decoder Block
- H.4 SymPy — Computer Algebra System
  - H.4.1 Symbolic vs Numeric Computation
  - H.4.2 Expression Trees — Abstract Syntax Trees
  - H.4.3 Core SymPy Classes
  - H.4.4 The ANTLR4 Parser and Formal Grammar
  - H.4.5 LaTeX → SymPy Conversion
- H.5 Formula Equivalence Checking
  - H.5.1 Method 1: Algebraic Simplification — `simplify(A - B) == 0`
  - H.5.2 Simplification Algorithms: Expand, Factor, Trigsimp
  - H.5.3 Method 2: Numerical Equality — `.equals()`
  - H.5.4 Method 3: SequenceMatcher — Ratcliff/Obershelp Algorithm
  - H.5.5 Score Mapping Table

## PART I — DIAGRAM EXTRACTION (COMPLETE)
- I.1 Digital Images as Data Structures
  - I.1.1 Grayscale Images: 2D Matrices
  - I.1.2 Color Images: 3D Tensors (H×W×C)
  - I.1.3 BGR vs RGB: OpenCV Convention
  - I.1.4 Bit Depth and Pixel Value Range
- I.2 Image Binarization — Thresholding
  - I.2.1 What is Thresholding?
  - I.2.2 Binary Inverse Threshold — Used in Project
  - I.2.3 Why Threshold at 245?
  - I.2.4 Otsu's Method — Automatic Threshold Selection
  - I.2.5 Adaptive Thresholding (Alternative)
- I.3 Morphological Image Processing
  - I.3.1 Structuring Elements
  - I.3.2 Dilation — Set Theory Definition and Visual Effect
  - I.3.3 Erosion — Set Theory Definition and Visual Effect
  - I.3.4 Opening vs Closing — Which One and Why?
  - I.3.5 Morphological Closing in the Project
- I.4 Connected Components Analysis
  - I.4.1 Graphs — Formal Definition
  - I.4.2 Connectivity: 4-connectivity vs 8-connectivity
  - I.4.3 Connected Component — Formal Definition
  - I.4.4 BFS Algorithm — Step-by-Step with Pseudocode
  - I.4.5 Two-Pass Labelling Algorithm
  - I.4.6 Union-Find Data Structure — Path Compression
  - I.4.7 Stats Array: Area, Bounding Box, Centroid
  - I.4.8 Area Filtering: Why 0.3% of Page Area?
  - I.4.9 Position Filtering: Why 45% Height?

## PART J — SCORING, LLM EVALUATION, AND SYSTEM
- J.1 The Rubric System
  - J.1.1 Max Marks and Per-Question Configuration
  - J.1.2 Weight Normalization — Full Formula
  - J.1.3 Missing Components — Penalty vs Redistribution
  - J.1.4 Complete Scoring Walk-through with Numbers
- J.2 Gemini 2.5 Flash — Multimodal LLM
  - J.2.1 Foundation Models vs Specialized Models
  - J.2.2 Decoder-Only Transformers (GPT architecture)
  - J.2.3 Autoregressive Text Generation
  - J.2.4 RLHF: Reinforcement Learning from Human Feedback
  - J.2.5 Multimodal Input: Text + Image Tokens
  - J.2.6 Prompt Engineering and JSON Output
  - J.2.7 Parsing the JSON Response Robustly
  - J.2.8 SBERT+CLIP vs Gemini: Trade-offs
- J.3 FastAPI Backend
  - J.3.1 WSGI vs ASGI
  - J.3.2 How FastAPI Works
  - J.3.3 Async Job Architecture
  - J.3.4 Threading and Mutex Locks
  - J.3.5 Cloud Run: Ephemeral Filesystem Problem
  - J.3.6 GCS (Google Cloud Storage) for Durability
- J.4 Report Generation with fpdf2
- J.5 Complete End-to-End Pipeline Walkthrough

---

---

# PART A — THE PROBLEM OF REPRESENTING LANGUAGE AS NUMBERS

---

## A.1 Why Computers Need Numbers

A computer processor (CPU/GPU) can only perform mathematical operations: addition, multiplication, comparison. It has no inherent understanding of letters, words, sentences, or meaning. Everything — images, audio, text — must ultimately be converted to numbers before a computer can work with it.

**Real-world analogy:** A weighing scale doesn't care whether you put apples or oranges on it — it measures in kilograms. You must convert your problem ("how much does this fruit weigh?") into the scale's language (kilograms). Similarly, you must convert your problem ("how similar are these two sentences?") into the computer's language (numbers and algebra).

**The deeper challenge with language:** Numbers like 42 and 43 are close together — their difference is 1. But words like "cat" and "dog" are semantically related (both are animals), while "cat" and "democracy" are unrelated. We need a number representation where the *numeric distance* reflects *semantic distance*. This is the fundamental problem that the entire field of NLP (Natural Language Processing) has been trying to solve.

---

## A.2 Binary Representation & Bits

At the lowest level, every number in a computer is stored as **bits** — binary digits that are either 0 or 1 (off or on, no voltage or full voltage in the circuit).

A **byte** is 8 bits. With 8 bits you can represent 2⁸ = 256 distinct values (0 to 255).

```
Binary:  1   0   1   1   0   1   0   0
Power:  2⁷  2⁶  2⁵  2⁴  2³  2²  2¹  2⁰
Value: 128  +0  +32  +16  +0  +4  +0  +0  = 180
```

Why does this matter for us? Because every pixel in an image is stored as one byte (0–255), and understanding this helps us understand image thresholding later (Part I).

---

## A.3 ASCII and Unicode: Characters as Numbers

**ASCII (American Standard Code for Information Interchange)** assigns a number 0–127 to every common English character:

| Character | ASCII Decimal | Binary |
|---|---|---|
| 'A' | 65 | 01000001 |
| 'a' | 97 | 01100001 |
| '0' | 48 | 00110000 |
| ' ' (space) | 32 | 00100000 |
| 'E' | 69 | 01000101 |

So the string `"Ohm"` becomes `[79, 104, 109]`.

**Unicode** extends this to 1,114,112 code points, covering every script in the world (Arabic, Hindi, Chinese, math symbols like ∑, ∫, ≠, and even emoji 🔬). Python's `str` type is Unicode by default. This is how the formula pipeline handles symbols like `∑`, `∫`, `√`, `π`, `θ`.

**UTF-8** is a variable-length encoding for Unicode: common ASCII characters use 1 byte; less common characters use 2–4 bytes. This is the encoding used in JSON files output by the OCR pipeline.

**The fundamental limitation:** Character-level numbers tell us nothing about meaning. `"resistance"` and `"current"` are physics concepts that appear together in the same textbook chapters, but as ASCII arrays they are completely unrelated sequences of integers.

---

## A.4 The Problem of Representing Words

We now move from characters to words. A **word** is the smallest unit of meaning in most NLP tasks (though subword units are sometimes better, as we'll see in Part E).

A **vocabulary** V is the set of all unique words in your corpus (collection of text). In English, common vocabularies have 30,000–100,000 words.

The question is: **how do you turn a word into a number (or numbers) such that the numbers capture meaning?**

Three attempts, in order of sophistication:
1. Integer index (fails — arbitrary ordering)
2. One-hot vector (fails — no semantic information)
3. Dense vector (succeeds — encodes meaning in geometry)

---

## A.5 One-Hot Encoding — Definition, Construction, Failure

### Definition
A **one-hot vector** for word `w` with vocabulary index `i` in vocabulary of size V is a vector of length V where position `i` is 1 and all others are 0.

### Construction Example
```
Vocabulary (4 words): {"current": 0, "voltage": 1, "resistance": 2, "elephant": 3}

v("current")    = [1, 0, 0, 0]
v("voltage")    = [0, 1, 0, 0]
v("resistance") = [0, 0, 1, 0]
v("elephant")   = [0, 0, 0, 1]
```

### Why It Fails — Three Reasons

**Reason 1: No Semantic Information**
```
dot( v("current"), v("voltage") )    = 1×0 + 0×1 + 0×0 + 0×0 = 0
dot( v("current"), v("elephant") )  = 1×0 + 0×0 + 0×0 + 0×1 = 0
```
Every pair of different words is orthogonal (dot product = 0). The model cannot distinguish related from unrelated words.

**Reason 2: Memory Explosion**
If V = 50,000 words, each word vector has 50,000 dimensions. A single sentence of 10 words needs 10 × 50,000 = 500,000 numbers — mostly zeros. This is called a **sparse representation**.

**Reason 3: No Generalization**
If the model learns something about `"current"`, it cannot transfer that knowledge to `"voltage"` because they are in completely different, perpendicular directions in the vector space.

---

## A.6 Vector Spaces — What They Are and Why They Matter

A **vector space** ℝⁿ is the set of all possible n-dimensional vectors. Think of ℝ² as a flat 2D plane, ℝ³ as 3D space. ℝ³⁸⁴ is the 384-dimensional space used by Sentence-BERT — impossible to visualize, but mathematically well-defined.

**Key operations:**
- **Addition**: `a + b` = sum element-wise. Geometrically: place vectors tip-to-tail.
- **Scalar multiplication**: `λa` = scale each element by λ. Geometrically: stretch/shrink the vector.
- **Dot product**: `a · b = Σᵢ aᵢbᵢ`. Measures how much two vectors "agree" in direction.
- **Norm (length)**: `‖a‖ = √(Σᵢ aᵢ²)`. Euclidean distance from origin.

**Why vector spaces for words?** Because we can do *algebra with meanings*:
```
vec("king") - vec("man") + vec("woman") ≈ vec("queen")
```
This famous Word2Vec result shows that gender relationships are encoded as parallel vectors in the space. You can compute with meaning.

---

## A.7 Dense Vectors — The Solution

Instead of a sparse 50,000-dim vector with one 1, represent each word as a **dense d-dimensional vector** (d = 50–300 typically) where every element is a real number:

```
v("current")    = [0.32, -0.15,  0.87,  0.21, -0.43, ...]   dim: 300
v("voltage")    = [0.29, -0.12,  0.84,  0.18, -0.40, ...]   dim: 300
v("elephant")   = [-0.71, 0.56, -0.23,  0.39,  0.61, ...]   dim: 300
```

**Properties of a good dense representation:**
- `‖v("current") - v("voltage")‖` is small (electrically related)
- `‖v("current") - v("elephant")‖` is large (completely unrelated)
- The direction of the vector encodes *type* of concept (physics terms cluster together)
- Arithmetic relations emerge: `v("V") - v("I") + v("Amps") ≈ v("Volts")`

**How are these numbers determined?** Through training on large text corpora, using Word2Vec or later BERT.

---

## A.8 Distributional Semantics — The Core Hypothesis

> **"You shall know a word by the company it keeps."** — J. R. Firth, 1957

This is the foundational hypothesis of all modern NLP:

**Distributional Hypothesis:** Words that appear in similar contexts tend to have similar meanings.

**Evidence:**
- `"current"` and `"voltage"` both appear near words like `"resistor"`, `"circuit"`, `"Ohm"`, `"ampere"`.
- `"dog"` and `"cat"` both appear near words like `"pet"`, `"food"`, `"animal"`, `"fur"`.
- Therefore `"current"` and `"voltage"` should have similar vectors, as should `"dog"` and `"cat"`.

This hypothesis is the basis for Word2Vec, GloVe, and ultimately BERT — all of which learn representations by predicting words from their contexts.

---

## A.9 Word2Vec: Training Words to Encode Meaning

**Word2Vec** (Mikolov et al., Google, 2013) was the practical breakthrough in dense word embeddings. It trains a shallow neural network to predict words from their context, and the learned weights become the word embeddings.

### A.9.1 Two Training Modes

**Skip-gram:** Given a centre word → predict surrounding context words.
**CBOW (Continuous Bag of Words):** Given context words → predict the centre word.

Skip-gram is more commonly used because it learns better representations for rare words.

### A.9.2 Skip-gram Training Objective

Given a corpus, go through each word as centre word `w_c`. For each centre word, define a context window of size `k` (e.g., k=2 means look at 2 words before and after).

**Goal:** maximize the probability of seeing the actual context words given the centre word:

```
Maximize: Σ_{t=1}^{T} Σ_{-k≤j≤k, j≠0} log P(w_{t+j} | w_t)
```

Where `T` = total number of words in corpus.

```
P(w_context | w_centre) = exp(v'_{w_context} · v_{w_centre}) / Σ_{w∈V} exp(v'_w · v_{w_centre})
```

This is a **softmax** over the entire vocabulary — the probability that word `w_context` appears as context, given centre word `w_centre`.

There are two sets of embedding vectors:
- `v_w` — input embedding for word w (when it is the centre word)
- `v'_w` — output embedding for word w (when it is a context word)

Training adjusts both sets to maximize the above probability.

### A.9.3 Negative Sampling (Practical Speed-up)

Computing softmax over 50,000 words is slow. **Negative sampling** instead treats it as a binary classification:
- Is `(w_centre, w_context)` a real pair? → label 1
- Is `(w_centre, w_random)` a fake pair? → label 0

For each real pair, sample k negative (random) words and train the model to distinguish real from fake.

### A.9.4 The Embedding Matrix

After training, the embedding matrix `W ∈ ℝ^{V×d}` is the word embedding lookup table. The row at index i is the embedding for vocabulary word i.

```python
embedding = W[word_index]   # shape: (d,)
```

This lookup table becomes the foundation for BERT's token embedding (Part E.3.1).

---

## A.10 GloVe: Global Co-occurrence Statistics

**GloVe** (Global Vectors for Word Representation, Pennington et al., Stanford, 2014) takes a different approach: instead of a predictive local window model, it directly factorizes the global co-occurrence matrix.

### A.10.1 The Co-occurrence Matrix

For a corpus with vocabulary V, build matrix `X ∈ ℝ^{V×V}` where:
```
X[i][j] = number of times word j appears in the context window of word i
```

### A.10.2 The GloVe Objective

GloVe learns vectors u_i (for word i as centre) and v_j (for word j as context) such that:
```
u_i · v_j + b_i + b_j ≈ log(X[i][j])
```

Where `b_i, b_j` are bias terms. The loss:
```
L = Σ_{i,j} f(X[i][j]) × (u_i·v_j + b_i + b_j - log(X[i][j]))²
```

`f(X)` is a weighting function that downweights very frequent co-occurrences.

### A.10.3 Relation to the Project

BERT and Sentence-BERT build on distributional semantics (same core hypothesis as Word2Vec/GloVe) but capture *contextual* word meaning — the same word `"current"` gets different embeddings in `"electrical current"` vs `"current events"`. This is the key advance over Word2Vec's static embeddings.

---

---

# PART B — NEURAL NETWORKS: THE BUILDING BLOCK

---

## B.1 What is a Neuron?

A **neuron** (also called a **perceptron** or **node**) is the fundamental computational unit:

```
Inputs:   x₁, x₂, x₃  (numbers from previous layer or raw data)
Weights:  w₁, w₂, w₃  (learnable parameters)
Bias:     b             (learnable offset)

Pre-activation: z = w₁x₁ + w₂x₂ + w₃x₃ + b
Output:         a = σ(z)
```

In vector notation:
```
z = w^T · x + b     (dot product of weight vector and input vector, plus bias)
a = σ(z)
```

**Intuition:** Each weight `wᵢ` controls how much input `xᵢ` influences the output. If `wᵢ` is large and positive, input `xᵢ` strongly activates the neuron. If `wᵢ` is negative, it inhibits it. The bias `b` shifts the activation threshold — allowing the neuron to fire even when all inputs are 0 (or vice versa).

**Biological inspiration:** Real neurons receive electrical signals from many other neurons via synapses. If the total incoming signal exceeds a threshold, the neuron "fires" — sending a signal to the next neurons. The weights model synapse strengths.

---

## B.2 Activation Functions — Why Non-Linearity is Essential

Without activation functions, the output of any network would be:
```
output = W_n × W_{n-1} × ... × W_1 × input = W_combined × input
```
No matter how many layers you stack, it collapses to a single linear transformation. A linear model can only learn linear relationships — useless for complex data.

**Non-linear activation functions** break this collapse. With non-linearity between layers, deeper networks can approximate any continuous function (the Universal Approximation Theorem).

### B.2.1 Sigmoid / Logistic

```
σ(x) = 1 / (1 + e^(-x))    Output range: (0, 1)
```

**Properties:**
- Squashes any real number into (0, 1) — interpretable as probability.
- Smooth and differentiable everywhere.
- **Gradient vanishes** for |x| >> 0 (σ'(x) = σ(x)(1-σ(x)) → 0 for large |x|).
- Used in LSTM gates (values must be in (0,1) for gates to open/close).

```
   x:   -6    -4    -2     0     2     4     6
σ(x):  0.002  0.02  0.12  0.5   0.88  0.98  0.998
```

### B.2.2 Tanh (Hyperbolic Tangent)

```
tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))    Output range: (-1, 1)
```

**Properties:**
- Zero-centered (output mean ≈ 0), which helps gradient flow.
- Also suffers from vanishing gradients at extremes.
- Used in LSTM cell state update.

### B.2.3 ReLU (Rectified Linear Unit)

```
ReLU(x) = max(0, x)    Output range: [0, ∞)
```

**Properties:**
- Computationally trivial (just a comparison).
- **No vanishing gradient** for positive inputs (gradient = 1 exactly).
- **Dead neurons**: if x < 0, gradient = 0 — neurons can permanently stop learning ("die"). Solved by LeakyReLU.
- Dominant activation in CNNs (VGG, ResNet).

### B.2.4 GELU (Gaussian Error Linear Unit)

```
GELU(x) = x × Φ(x)

Where Φ(x) = P(X ≤ x) for X ~ N(0,1)  (CDF of standard normal distribution)

Approximation: GELU(x) ≈ 0.5x × (1 + tanh(√(2/π) × (x + 0.044715x³)))
```

**Properties:**
- Smooth approximation to ReLU — avoids the "kink" at 0.
- Allows small negative values through (gates based on probability), unlike ReLU which hard-zeros.
- Standard in Transformers (BERT, GPT, etc.).
- Empirically outperforms ReLU on language tasks.

```
ReLU vs GELU at x=0: 
  ReLU(0) = 0 (hard boundary)
  GELU(0) = 0×0.5 = 0 (same, but smooth approach)

At x=-1:
  ReLU(-1) = 0 (completely dead)
  GELU(-1) ≈ -0.17 (small negative — some signal passes through)
```

### B.2.5 Softmax (Used in Attention)

```
softmax(z)_i = e^{z_i} / Σ_{j=1}^{K} e^{z_j}    Output: K values in (0,1) summing to 1
```

**Properties:**
- Converts a vector of arbitrary real numbers into a probability distribution.
- Emphasizes the largest value (the `e^x` function grows exponentially).
- The denominator `Σe^{z_j}` is called the partition function.

**Numerical stability note:** Computing `e^x` for large x overflows float32. In practice, we subtract max before exponentiating:
```
softmax(z)_i = e^{z_i - max(z)} / Σ_j e^{z_j - max(z)}
```
This is mathematically identical but numerically stable.

---

## B.3 Layers and Deep Networks

A **layer** is a collection of neurons all taking the same input and producing parallel outputs:

```
Layer with n neurons, input dim d:
  Weight matrix W ∈ ℝ^{n×d}
  Bias vector b ∈ ℝ^n

  z = Wx + b     ∈ ℝ^n   (matrix-vector multiplication)
  a = σ(z)       ∈ ℝ^n   (element-wise activation)
```

A **deep network** stacks multiple layers:
```
input x → [Layer 1] → a₁ → [Layer 2] → a₂ → ... → aₙ → output
```

Each layer learns increasingly abstract features:
- Layer 1: raw input patterns (edges in images, character n-grams in text)
- Layer 2: combinations of patterns (shapes, morphemes)
- Layer 3+: high-level concepts (faces, syntax, semantics)

---

## B.4 Loss Functions — Measuring Error

A **loss function** L(y, ŷ) measures how wrong the model's prediction `ŷ` is compared to the true label `y`.

### Mean Squared Error (MSE) — for regression
```
L = (1/n) × Σᵢ (yᵢ - ŷᵢ)²
```

### Cross-Entropy — for classification
```
L = -Σᵢ yᵢ × log(ŷᵢ)
```
Where `yᵢ` is the true probability (0 or 1) and `ŷᵢ` is the predicted probability.

**Why log?** If the model predicts ŷ = 0.001 for the correct class (very wrong), log(0.001) = -7 → large penalty. If ŷ = 0.999 (very right), log(0.999) ≈ 0 → small penalty. This matches our intuition about errors.

### KL Divergence — Used in Knowledge Distillation
```
KL(P || Q) = Σᵢ P(i) × log(P(i) / Q(i))
```
Measures how distribution Q differs from reference distribution P. Always ≥ 0. Equals 0 iff P = Q everywhere.

---

## B.5 Backpropagation — How Networks Learn

Training aims to minimize the loss by adjusting all weights. This is done via **backpropagation** — efficient computation of gradients using the chain rule.

### The Chain Rule
If `y = f(g(x))`, then `dy/dx = (dy/dg) × (dg/dx)`.

For a network: `L = loss(output(layer_n(...(layer_1(x))...)))`:
```
∂L/∂w₁ = (∂L/∂aₙ) × (∂aₙ/∂aₙ₋₁) × ... × (∂a₁/∂w₁)
```

This chain of products is computed backward from the loss, layer-by-layer — hence "back"propagation.

### Why Backprop is Efficient
Computing all gradients naively would require O(W²) operations (W = number of weights). Backprop computes all gradients in O(W) by reusing intermediate computations (dynamic programming).

---

## B.6 Gradient Descent Variants

After computing gradients, we update weights:
```
w ← w - α × ∂L/∂w
```
Where `α` is the **learning rate** — a hyperparameter controlling step size.

| Variant | Uses | Update frequency |
|---|---|---|
| **Batch GD** | Entire dataset | Once per epoch |
| **SGD** | One sample at a time | Every sample |
| **Mini-batch SGD** | Batch of 32–256 samples | Every batch |
| **Adam** | Adaptive learning rates | Every batch |

**Adam (Adaptive Moment Estimation)** is the standard optimizer for transformers:
```
m_t = β₁×m_{t-1} + (1-β₁)×g_t        (1st moment = mean of gradients)
v_t = β₂×v_{t-1} + (1-β₂)×g_t²       (2nd moment = variance of gradients)
ŵ ← ŵ - α × m̂_t / (√v̂_t + ε)
```
Adam adapts the learning rate per-parameter, converging faster than plain SGD.

---

## B.7 Overfitting, Underfitting, and Regularization

**Underfitting:** Model is too simple, can't capture the data's complexity. High training error.

**Overfitting:** Model memorizes training data, fails on new data. Low training error, high test error.

**Solutions:**
- **Dropout:** Randomly set some neuron outputs to 0 during training (prevents co-adaptation). At test time, scale outputs by the dropout probability.
- **Weight decay (L2 regularization):** Add `λ‖w‖²` to loss, penalizing large weights.
- **More data:** The best solution.
- **Early stopping:** Stop training when validation loss stops improving.

---

---

# PART C — WHY RNNS FAILED AND TRANSFORMERS WON

---

## C.1 Sequences in NLP

Text is inherently sequential — word order matters. `"current through resistor"` ≠ `"resistor through current"`.

**The challenge:** how do you design a model that:
1. Handles sequences of variable length (sentences can be 5 to 500 words).
2. Captures long-range dependencies ("The theory that **Einstein** proposed in 1905, which described the relationship between mass and energy, was named special relativity by **him**.").
3. Can be trained efficiently (parallelism).

---

## C.2 Recurrent Neural Networks (RNN) — Architecture

An RNN processes tokens one at a time, maintaining a **hidden state** that accumulates information from all previous tokens.

### The Recurrence Equation
```
h₀ = zeros(d_hidden)    (initial hidden state, all zeros)
hₜ = tanh(Wₕ · hₜ₋₁ + Wₓ · xₜ + b)

Where:
  hₜ ∈ ℝ^{d_h}           current hidden state
  hₜ₋₁ ∈ ℝ^{d_h}         previous hidden state
  xₜ ∈ ℝ^{d_x}            current input (word embedding)
  Wₕ ∈ ℝ^{d_h × d_h}      recurrent weight matrix
  Wₓ ∈ ℝ^{d_h × d_x}      input weight matrix
```

**How it works:** At each time step t, the model takes the new input `xₜ` and the **previous hidden state** `hₜ₋₁` (which summarizes everything seen before now), and produces a new hidden state `hₜ`. This chain continues until the end of the sequence.

```
x₁ → [RNN] → h₁ ─────────────────────────────┐
                        x₂ → [RNN] → h₂       │
   (h₁ is passed     (hₜ₋₁ = h₁)        x₃ → [RNN] → h₃ → output
    as hₜ₋₁)
```

---

## C.3 The Vanishing Gradient Problem — Mathematical Proof

The critical failure of RNNs is the **vanishing gradient problem**. Here's why it happens mathematically:

During backpropagation through time (BPTT), the gradient of loss with respect to an early hidden state involves multiplying weight matrices many times:

```
∂L/∂h₁ = (∂L/∂hₜ) × ∏_{k=2}^{t} (∂hₖ/∂hₖ₋₁)

∂hₖ/∂hₖ₋₁ = diag(1 - hₖ²) × Wₕ    [for tanh activation]
```

The product `∏_{k=2}^{t} (∂hₖ/∂hₖ₋₁)` is a product of t-1 matrices. If the eigenvalues of `Wₕ` are less than 1, this product shrinks exponentially → **gradients vanish**: early tokens receive no gradient signal, so the model doesn't learn to depend on distant context.

If eigenvalues > 1 → gradients **explode** (overflow), causing training instability.

**Concrete example:** In a 100-token sequence, the gradient for token 1 is the product of 99 matrix multiplications. If each factor reduces the gradient by just 0.9, the final gradient is `0.9^99 ≈ 5×10⁻⁵` — 20,000× smaller than at the output. The model effectively ignores tokens more than ~20 positions away.

---

## C.4 LSTM: The Gated Solution

**LSTM (Long Short-Term Memory)** (Hochreiter & Schmidhuber, 1997) introduces a second state — the **cell state Cₜ** — which can carry information for long distances without multiplying through many weight matrices. Gates control what information flows into, out of, and gets erased from the cell state.

### C.4.1 Four LSTM Equations (Every Symbol Explained)

```
fₜ = σ(Wf · [hₜ₋₁, xₜ] + bf)    ← Forget Gate
iₜ = σ(Wi · [hₜ₋₁, xₜ] + bi)    ← Input Gate
C̃ₜ = tanh(Wc · [hₜ₋₁, xₜ] + bc) ← Candidate Cell State
oₜ = σ(Wo · [hₜ₋₁, xₜ] + bo)    ← Output Gate

Cₜ = fₜ ⊙ Cₜ₋₁ + iₜ ⊙ C̃ₜ         ← Cell State Update
hₜ = oₜ ⊙ tanh(Cₜ)                 ← Hidden State Output
```

**Symbol explanations:**
- `σ` → sigmoid function, output ∈ (0,1) — values near 0 = gate closed (block), near 1 = gate open (pass through)
- `⊙` → element-wise (Hadamard) product: [a,b]⊙[c,d] = [a×c, b×d]
- `[hₜ₋₁, xₜ]` → **concatenation**: stack the two vectors end-to-end, making a longer vector
- `Wf, Wi, Wc, Wo` → learnable weight matrices for each gate
- `bf, bi, bc, bo` → learnable bias vectors

**Intuition for each gate:**
- **Forget gate fₜ**: "What fraction of the old cell state should I keep?" values near 1 = keep completely, near 0 = forget completely.
- **Input gate iₜ**: "How much of the new candidate information should I add to the cell?"
- **Candidate C̃ₜ**: "What new information do I want to potentially add?" (tanh squashes to (-1,1))
- **Output gate oₜ**: "What part of the cell state should I output as the hidden state?"
- **Cell update**: New cell = (what we kept from old cell) + (what we decided to add)
- **Hidden output**: Filtered cell state passed through tanh → output

### C.4.2 Why LSTMs Work Better

The cell state update `Cₜ = fₜ ⊙ Cₜ₋₁ + iₜ ⊙ C̃ₜ` propagates information **by addition**, not multiplication. The gradient through this path:
```
∂Cₜ/∂Cₜ₋₁ = fₜ   (element-wise, values between 0 and 1)
```
This avoids the repeated matrix multiplication that caused vanishing gradients. Information can flow for hundreds of steps.

---

## C.5 Why LSTMs Are Still Not Enough

Even LSTMs have two remaining problems:

1. **Sequential dependency**: `hₜ` depends on `hₜ₋₁` which depends on `hₜ₋₂`... You cannot compute all hidden states in parallel. Training is slow — O(sequence_length) sequential steps.

2. **Fixed-size hidden state**: The entire history of a potentially 500-word sentence is compressed into a single fixed d_h-dimensional vector. Information is lost for long sequences.

**The Transformer solution:** Instead of one hidden state that sees the whole past, every token directly attends to **every other token** simultaneously. No sequential bottleneck. No compression bottleneck. 

---

---

# PART D — THE TRANSFORMER ARCHITECTURE

---

## D.1 The "Attention is All You Need" Insight

The 2017 paper from Google Brain (Vaswani et al.) proposed discarding RNNs entirely and relying solely on **attention mechanisms** to model relationships between tokens.

**Key insight:** "Attention" in neural networks means weighted aggregation — instead of passing information through a chain of states, allow each position to directly attend to *all* other positions and compute a weighted blend. If attention weights correctly capture dependency strength, a single attention pass replaces an entire chain of recurrent steps.

The Transformer does this:
- In **parallel** (all positions attend to all positions simultaneously via matrix operations)
- With **no sequential dependency** (position 50 can attend to position 1 directly, without going through positions 2–49)
- **Multiple times** (deep layers refine representations progressively)

This enabled training on orders of magnitude larger datasets, leading to GPT, BERT, and eventually Gemini.

---

## D.2 Tokenization — Turning Words into Indices

Before any math, text must become numbers. **Tokenization** splits text into **tokens** (units) and maps each to an integer index in a vocabulary.

Different from Word2Vec which used whole words as tokens, BERT uses **subword tokenization** (covered fully in Part E.2). For now, understand:

```
"Ohm's Law states V = IR"
     ↓ tokenize
["oh", "##m", "'", "s", "law", "states", "v", "=", "ir"]
     ↓ map to vocab indices
[3421, 892, 29, 7, 2391, 4821, 153, 85, 7241]
```

These integer indices are the actual input to the transformer's embedding layer.

---

## D.3 Token Embeddings — The Lookup Table

The **token embedding layer** is a matrix `W_emb ∈ ℝ^{V×d}` where:
- V = vocabulary size (30,000 for BERT)
- d = embedding dimension (768 for BERT-base, 384 for MiniLM)

Looking up token index `i` returns the `i`-th row: `W_emb[i] ∈ ℝ^d`.

```
Input: integer index 3421
Output: W_emb[3421] = [0.32, -0.15, 0.87, ...] ∈ ℝ^384
```

These embedding vectors are **learnable parameters** — they are initialized randomly and updated during training/fine-tuning to encode semantic meaning.

The full input sequence of n tokens becomes the matrix `X ∈ ℝ^{n×d}` where row i is the embedding for token i.

---

## D.4 Positional Encoding — Injecting Order

### The Problem of Permutation Invariance

Self-attention (next section) computes attention scores between all pairs of tokens. This operation is **permutation invariant** — shuffling the order of tokens gives the same set of attention scores (just in different positions of the output matrix). The model has no idea that "A follows B" vs "B follows A".

We must inject positional information somehow.

### D.4.1 Sinusoidal Positional Encoding — Full Derivation

The original Transformer paper uses:
```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

Where:
- `pos` ∈ {0, 1, 2, ...} — the position of the token in the sequence
- `i` ∈ {0, 1, ..., d_model/2 - 1} — the dimension index pair
- `d_model` — embedding dimension (e.g., 512)

**Intuition through analogy:** Think of a clock. The hour hand position tells you coarsely what time it is; the minute hand gives finer detail; the second hand gives finest detail. Different sinusoidal frequencies provide different "resolutions" of position:

- When i=0: frequency = 1/10000⁰ = 1 → one full cycle every 2π ≈ 6 positions (fast, fine-grained)
- When i=d/2: frequency = 1/10000¹ = 0.0001 → one cycle every 62,832 positions (slow, coarse)

Together, the 512-dim positional encoding vector uniquely encodes every position up to ~10,000 tokens.

**Mathematical property that makes relative positions learnable:**
```
PE(pos+k) = linear_transform(PE(pos))
```

This means the model can learn to compute relative distances from absolute positions — the attention mechanism can figure out "this token is 3 positions after that token" from the positional embeddings.

**Adding to embeddings:**
```
Z₀ = X + PE    (element-wise addition, shapes must match: both ∈ ℝ^{n×d})
```

### D.4.2 Learnable Positional Embeddings (Used in BERT)

BERT instead uses a **learnable positional embedding table** — a matrix `P ∈ ℝ^{L_max × d}` where `L_max` = maximum sequence length (512 for BERT). The i-th row is the positional embedding for position i:

```
Z₀ = X + P[0:n]   (slice first n rows for a sequence of length n)
```

These are randomly initialized and learned during pre-training, allowing the model to capture language-specific positional patterns (not just abstract mathematical ones). Empirically performs similarly to sinusoidal but slightly better for tasks the model was pre-trained on.

---

## D.5 Query, Key, Value — The Core Abstraction

This is **the most important concept** in the entire project. Everything from BERT to CLIP to Gemini to pix2tex uses this.

### D.5.1 The Database Analogy

Imagine you're looking up information in a soft (fuzzy) key-value store:

| Key | Value |
|---|---|
| "electrical property" | (information about voltage) |
| "circuit element" | (information about resistor) |
| "unit of measurement" | (information about Ohm) |

You have a **query**: "what is the unit of electrical resistance?"

A hard lookup finds the exact key match. A **soft (attention) lookup** computes a similarity score between your query and every key, then returns a *weighted blend* of all values — more weight to higher-similarity keys:

```
result = (0.1 × value_A) + (0.05 × value_B) + (0.85 × value_C)
                                                ↑ this key matched best
```

In the transformer, every token is simultaneously a query (what it's looking for), a key (what it has to offer), and a value (what information it contains).

### D.5.2 Linear Projection Matrices Wq, Wk, Wv

Given input matrix `X ∈ ℝ^{n×d_model}` (n tokens, d_model dimensions each):

```
Q = X × Wq      Wq ∈ ℝ^{d_model × d_k}      Q ∈ ℝ^{n × d_k}
K = X × Wk      Wk ∈ ℝ^{d_model × d_k}      K ∈ ℝ^{n × d_k}
V = X × Wv      Wv ∈ ℝ^{d_model × d_v}      V ∈ ℝ^{n × d_v}
```

**What does "linear projection" mean?**
- It's a matrix multiplication — the linear map taking each d_model-dim embedding to a d_k-dim query/key space.
- The purpose: project the embedding into a specialized subspace (different subspace for Q, K, V) optimized for attention computation.
- Wq, Wk, Wv are **learnable** — the model discovers during training what projections make attention most useful.

**Why separate projections?**
- The query subspace should capture "what I'm looking for" — a question-like representation.
- The key subspace should capture "what I can answer" — a label-like representation.
- These need not be the same transformation of the same embedding.

### D.5.3 Computing Raw Attention Scores (QKᵀ)

```
Scores = Q × Kᵀ     ∈ ℝ^{n×n}
```

`Scores[i][j]` = how much token i should attend to token j.

**How this is computed:**
```
Scores[i][j] = Q[i] · K[j] = Σ_{d=1}^{d_k} Q[i,d] × K[j,d]
```

This is the dot product between the query vector of token i and the key vector of token j.

**Why dot product measures relevance:** If Q[i] and K[j] are parallel (pointing in the same direction), their dot product is large (= `‖Q[i]‖ × ‖K[j]‖`). If perpendicular, dot product = 0. The model learns projections where related tokens produce parallel Q and K vectors.

**Matrix illustration for 3 tokens:**
```
     Q[1]·K[1]  Q[1]·K[2]  Q[1]·K[3]
     Q[2]·K[1]  Q[2]·K[2]  Q[2]·K[3]
     Q[3]·K[1]  Q[3]·K[2]  Q[3]·K[3]
```
This is a 3×3 matrix where Scores[i][j] tells us how much token i attends to token j.

### D.5.4 The Scaling Factor √d_k — Why and How

**The Problem:**
When d_k is large (e.g., 64), dot products `Q[i] · K[j]` become large in magnitude. WHY?

If Q[i] and K[j] are random vectors with each dimension drawn from N(0,1) (standard normal), then their dot product:
```
Q[i]·K[j] = Σ_{d=1}^{d_k} Q[i,d] × K[j,d]
```
is a sum of `d_k` independent N(0,1) random variables. By the variance addition rule for independent variables:

```
Var(Q[i]·K[j]) = Σ_{d=1}^{d_k} Var(Q[i,d] × K[j,d]) = d_k × 1 = d_k

Std(Q[i]·K[j]) = √d_k
```

So dot products have standard deviation `√d_k`. For d_k=64, std=8.

**The Consequence:**
When inputs to softmax are large (magnitude ~ 8), one element dominates strongly:
```
softmax([8, 0.1, -0.2]) ≈ [0.9997, 0.0002, 0.0001]
```
Softmax has become **nearly one-hot** → gradient of softmax is essentially zero almost everywhere → **vanishing gradient problem inside attention**.

**The Fix:**
Divide by √d_k to normalize the dot products back to unit standard deviation:
```
Scores_scaled = Q × Kᵀ / √d_k      std ≈ 1 after scaling
```

Now softmax gets mild inputs → the gradient flows well → training is stable.

### D.5.5 Softmax — Converting Scores to Probabilities

```
A = softmax(Scores_scaled)     A ∈ ℝ^{n×n}

A[i][j] = exp(Scores_scaled[i][j]) / Σ_{k=1}^{n} exp(Scores_scaled[i][k])
```

Applied **row-by-row**: each row i is normalized independently.

**What A means:** Row A[i] is a probability distribution over all tokens — how much token i pays attention to each other token. All entries in row i sum to 1.

**The exp function:** Even a small difference in score becomes a large difference in attention weight (e.g., scores (2.0, 1.0, 0.5) → exp(2.0)=7.39, exp(1.0)=2.72, exp(0.5)=1.65 → after normalization ≈ (0.63, 0.23, 0.14)). This makes attention decisions sharper than linear scaling.

### D.5.6 Weighted Sum of Values

```
Output = A × V     ∈ ℝ^{n×d_v}
```

For each token i:
```
Output[i] = Σ_{j=1}^{n} A[i][j] × V[j]
```

This is a **weighted average of all value vectors**, where the weights are the attention probabilities. High attention → high contribution to output.

**Physical meaning:** Token i's new representation is a blend of information from all other tokens, weighted by how relevant each is. `"flows"` in `"current flows"` gets a representation enriched with information from `"current"` and the other nearby tokens.

### D.5.7 The Complete Attention Formula

```
              ⎛  Q · Kᵀ  ⎞
Attention =  softmax ⎜ ────── ⎟ · V
              ⎝   √d_k   ⎠
```

This single formula is replicated (with different learned Wq, Wk, Wv) in BERT, CLIP, pix2tex, and conceptually in Gemini.

---

## D.6 Multi-Head Attention — Purpose and Mechanics

### D.6.1 Why Multiple Heads?

A single attention head computes one kind of relationship between tokens. But language has many simultaneous relationships:

- **Syntactic**: verb agrees with subject (grammatical role)
- **Semantic**: `"it"` refers to `"the resistor"` mentioned earlier (coreference)
- **Positional**: adjacent words form phrases (n-grams)
- **Long-range**: `"theory"` connects to `"proved"` 30 words later

No single attention head can efficiently capture all these simultaneously. **Multi-head attention** runs h independent attention mechanisms in parallel, each in a lower-dimensional subspace.

### D.6.2 Concatenation and Output Projection

```
head_i = Attention(X·Wq_i, X·Wk_i, X·Wv_i)    each ∈ ℝ^{n × d_k}

MultiHead(X) = Concat(head₁, ..., headₕ) · Wo

              ↑ Concat: stack head outputs column-wise: ℝ^{n × (h × d_k)}
              · Wo: project back: Wo ∈ ℝ^{(h × d_k) × d_model}
              output ∈ ℝ^{n × d_model}
```

**Standard settings in BERT-base**: h=12 heads, d_model=768, d_k = d_model/h = 64
**In MiniLM-L6-v2**: h=12 heads, d_model=384, d_k = 32

### D.6.3 Computational Cost

Self-attention costs O(n² × d) in time and O(n²) in memory (the attention matrix A ∈ ℝ^{n×n}). For long sequences (n=4096), this becomes prohibitive — a known limitation of the original Transformer, addressed by modern variants (FlashAttention, sparse attention). In this project, max sequence length is 256 tokens (MiniLM), so this is not a problem.

---

## D.7 The Feed-Forward Sub-layer

### D.7.1 Architecture and Dimensions

After attention aggregates information across positions, a per-position feedforward network processes each token's aggregated representation independently:

```
FFN(xᵢ) = W₂ · GELU(W₁ · xᵢ + b₁) + b₂

W₁ ∈ ℝ^{d_ff × d_model}    (expand)
W₂ ∈ ℝ^{d_model × d_ff}    (contract)
d_ff = 4 × d_model          (standard: 4× expansion)
```

**Example:** d_model=384 → d_ff=1536. Each token goes from 384 → 1536 → 384.

**Why expand then contract?** The wider intermediate layer gives the network more capacity to learn complex non-linear transformations. The expansion creates a richer feature space; the contraction projects back to the standard dimension for the next layer.

**"Per-position" means**: W₁ and W₂ are the **same** matrices for every position (parameter sharing) — applied independently to each token. This is different from attention which mixes information between positions.

### D.7.2 GELU vs ReLU — Detailed Comparison

| Property | ReLU `max(0,x)` | GELU `x·Φ(x)` |
|---|---|---|
| Below 0 | Hard zero | Small negative value |
| At 0 | Kink (non-smooth) | Smooth transition |
| Gradient | 0 or 1 exactly | Continuous, smooth |
| Dead neurons | Yes (can occur) | No (always non-zero grad) |
| Computation | `if x>0: x else 0` (fast) | Requires tanh approximation (slower) |
| Used for | CNNs, image models | Transformers, BERT, GPT |

The smooth gradient of GELU is important for stable training of deep transformers where gradient signal must propagate through many layers.

---

## D.8 Residual Connections (Skip Connections)

### D.8.1 The Vanishing Gradient Problem Revisited

Even without recurrence, deep networks (many transformer layers) suffer when gradients must travel from the output back through many non-linear transformations to early layers. Each transformation can diminish the gradient.

### D.8.2 How Residuals Solve It

He et al. (2016, ResNet) introduced: instead of learning `y = F(x)`, the layer learns the **residual** `F(x)` and adds the input directly:

```
y = F(x) + x    ← residual connection
```

**Why this helps gradients:** The gradient through this addition:
```
∂L/∂x = ∂L/∂y × ∂y/∂x = ∂L/∂y × (∂F(x)/∂x + 1)
```

The `+1` term means gradient always has a component that doesn't vanish — it can flow directly from output to input through the shortcut path. No matter how bad F's gradient is, the `+1` ensures at least the raw gradient reaches earlier layers.

### D.8.3 Identity Initialization Principle

If we initialize all F's weights close to zero, then `y = F(x) + x ≈ 0 + x = x`. The network starts as an **identity function** — it literally does nothing. Training then gradually adds refinements on top of the identity. This is much easier to optimize than a network that starts doing something random.

---

## D.9 Layer Normalization

### D.9.1 The Problem Without Normalization

As data passes through many non-linear layers, the distribution of activations changes dramatically. Later layers receive inputs with wildly different means and variances depending on what the previous layer computed. This makes learning unstable and slow — the layer must constantly adapt to a shifting input distribution (called **covariate shift**).

### D.9.2 Layer Norm Formula — Every Symbol Explained

```
LayerNorm(x) = γ × (x - μ) / √(σ² + ε) + β
```

**Symbol-by-symbol:**

| Symbol | Type | Meaning |
|---|---|---|
| `x ∈ ℝ^d` | Input | The vector we're normalizing (one token's representation) |
| `μ = (1/d) Σᵢ xᵢ` | Scalar | Mean of all d elements of x |
| `σ² = (1/d) Σᵢ (xᵢ - μ)²` | Scalar | Variance of all d elements of x |
| `ε` (epsilon) | Constant | Small value (1e-6) added to denominator to prevent division by zero |
| `√(σ² + ε)` | Scalar | Standard deviation (with stability fix) |
| `(x - μ) / √(σ² + ε)` | Normalized | Re-centered and re-scaled to mean≈0, std≈1 |
| `γ ∈ ℝ^d` | **Learnable** | Scale parameter (element-wise). Initialized to all 1s |
| `β ∈ ℝ^d` | **Learnable** | Shift parameter (element-wise). Initialized to all 0s |

After normalization, the output has approximately zero mean and unit variance, computed **per token** (across the d feature dimensions).

**Note:** γ and β are learned by the model — it can learn to "undo" normalization in specific dimensions if that's useful. The normalization ensures initial training stability; the model gradually adapts.

### D.9.3 Layer Norm vs Batch Norm — Key Differences

| | Layer Norm | Batch Norm |
|---|---|---|
| Computes stats over | Feature dimension (d) per sample | Batch dimension (N) per feature |
| Depends on batch size? | No | Yes (fails for batch size 1) |
| Works for variable-length sequences? | Yes | No |
| Used for | Transformers (NLP) | CNNs (image) |

Layer norm is preferred in transformers because NLP has variable-length sequences — you can't normalize across a batch of differently-lengthed sentences. Layer norm normalizes each token's d-dimensional vector independently.

---

## D.10 The Complete Transformer Encoder Block

Combining everything, one full encoder block:

```
Input:  x ∈ ℝ^{n × d}
         │
         ▼
════════════════════════════════════════════
Step 1: MULTI-HEAD SELF-ATTENTION
  Q = x·Wq,  K = x·Wk,  V = x·Wv         (project)
  A = softmax(QKᵀ/√d_k)                   (attention weights)
  attn_out = A·V                            (weighted sum)
  attn_out = Concat(heads) · Wo             (multi-head)
════════════════════════════════════════════
         │ attn_out
         ▼
Step 2: RESIDUAL + LAYER NORM
  x' = LayerNorm(x + attn_out)             (residual add, then normalize)
════════════════════════════════════════════
         │ x'
         ▼
Step 3: FEED-FORWARD NETWORK (per position)
  ffn_out = W₂·GELU(W₁·x' + b₁) + b₂
════════════════════════════════════════════
         │ ffn_out
         ▼
Step 4: RESIDUAL + LAYER NORM
  x'' = LayerNorm(x' + ffn_out)
════════════════════════════════════════════
Output: x'' ∈ ℝ^{n × d}   (same shape as input)
```

This block is stacked:
- 6 times in **all-MiniLM-L6-v2**
- 12 times in **BERT-base**
- 24 times in **BERT-large**
- 12 times in **CLIP's ViT-B/32 image encoder**

---

---

# PART E — BERT AND SENTENCE-BERT

---

## E.1 What is BERT?

**BERT** (Bidirectional Encoder Representations from Transformers, Devlin et al., Google, 2018) was the first model to apply a deep bidirectional transformer to language understanding, and it achieved state-of-the-art results on 11 NLP benchmarks simultaneously upon release.

**"Bidirectional"** means each token's representation is computed using context from both the left and the right simultaneously — unlike GPT (which is left-to-right only) or ELMo (which was two separate LSTMs). This bidirectionality is achieved by the self-attention mechanism, which has no inherent direction.

**"Encoder"** means BERT produces representations of input text (it doesn't generate text — that's what GPT decoder models do).

---

## E.2 WordPiece Tokenization — Full Algorithm

### E.2.1 Why Not Word-Level Tokenization?

If your vocabulary is all words in English:
- Vocabulary size = 500,000+
- Words like `"resistivity"`, `"superconductivity"` are rare → embedding is poorly trained
- New words (invented after training) → **out-of-vocabulary (OOV)**: must be represented as `[UNK]` → information lost
- Different forms of same word are unrelated: `"resist"`, `"resistor"`, `"resistance"`, `"resisting"` all have separate unrelated vectors

### E.2.2 Why Not Character-Level?

- Sequences become very long: `"superconductivity"` = 20 tokens → attention cost O(20²) instead of O(1²)
- Characters carry little individual meaning
- Very long sequences strain the model's memory capacity

### E.2.3 The BPE Family — Byte Pair Encoding

WordPiece is based on **BPE (Byte Pair Encoding)** — originally a text compression algorithm, adapted for NLP tokenization.

**Core idea of BPE:**
1. Start with individual characters as the vocabulary.
2. Count all pairs of consecutive tokens.
3. Merge the most frequent pair into a new token.
4. Repeat until vocabulary size reaches target (e.g., 30,000).

```
Initial vocab: {t, h, e, space, c, u, r, n, ...}
Most frequent pair: ('t','h') → merge to 'th'
Next: ('th','e') → 'the'
Next: ('c','u') → 'cu'
...
Eventually: 'current', 'voltage' become single tokens (very common)
            'resistor' → ['resist','##or'] (moderate frequency)
            'superconductivity' → ['super','##con','##duct','##ivity']
```

### E.2.4 WordPiece Selection Criterion

WordPiece differs from standard BPE in the **merge criterion**: instead of merging the most frequent pair, it merges the pair that **maximizes the language model likelihood**:

```
Score(A,B) = count(AB) / (count(A) × count(B))
```

This prefers merges where the combination is much more likely than the parts individually — i.e., where `AB` is a genuine linguistic unit, not just a frequent accident.

### E.2.5 Special Tokens: [CLS], [SEP], [MASK], [PAD]

| Token | Index | Purpose |
|---|---|---|
| `[CLS]` | 101 | Classification token — always prepended. Final hidden state used for sentence-level tasks |
| `[SEP]` | 102 | Separator — between sentence A and B, and at end of input |
| `[MASK]` | 103 | Masking — replaces tokens during MLM pre-training |
| `[PAD]` | 0 | Padding — fills sequences to equal length in a batch |
| `[UNK]` | 100 | Unknown — for characters not in vocabulary (very rare) |

---

## E.3 BERT's Three Input Embeddings

BERT's input to the transformer is the **element-wise sum** of three separate embedding vectors for each token position.

### E.3.1 Token Embedding

Standard embedding lookup: vocabulary index → d-dimensional vector. Table size: 30,000 × 768 = 23M parameters for BERT-base.

### E.3.2 Segment Embedding

For tasks involving two sentences (e.g., NSP, question-answering), BERT needs to know which sentence each token belongs to. Only two possible values:

- **Segment A embedding**: `E_A ∈ ℝ^768` (learnable) — added to all tokens in sentence A (including [CLS] and [SEP] after A)
- **Segment B embedding**: `E_B ∈ ℝ^768` (learnable) — added to all tokens in sentence B (including [SEP] after B)

For single-sentence input (like answer similarity), all tokens get segment A embedding.

### E.3.3 Positional Embedding

Learnable positional table: 512 × 768 = 393K parameters. Row i is added to the token at position i.

### E.3.4 Summing the Three Embeddings

```
Position: 0       1         2       3       4        5       6
Token:   [CLS]  "the"   "current" [SEP]  "the"  "voltage" [SEP]
Segment:    A     A         A       A       B        B       B

Final_emb[0] = W_emb[[CLS]] + E_A + P[0]
Final_emb[1] = W_emb["the"] + E_A + P[1]
Final_emb[2] = W_emb["current"] + E_A + P[2]
Final_emb[3] = W_emb[[SEP]] + E_A + P[3]
Final_emb[4] = W_emb["the"] + E_B + P[4]
Final_emb[5] = W_emb["voltage"] + E_B + P[5]
```

All three are ∈ ℝ^768, so their sum is ∈ ℝ^768. The combined vector encodes: what word (token emb) + which sentence (segment emb) + what position (pos emb).

---

## E.4 BERT Pre-Training

### E.4.1 Masked Language Modeling (MLM) — Full Explanation

**Why self-supervised?** Labeled data (human-annotated) is expensive. The cleverness of MLM is using the text itself as supervision — no human labels needed.

**Procedure:**
1. Start with a sentence: `"The current flows through the resistor"`
2. Randomly select 15% of tokens: say `"current"` (pos 2) and `"resistor"` (pos 6) are selected.
3. Apply the 80/10/10 strategy to each selected token (details in E.4.2).
4. Feed the modified sentence to BERT.
5. For each masked position, predict the original token.

**The training signal:** For position 2 (masked), BERT sees context on both sides:
- Left: `"The [MASK] flows through the [MASK]"`
- But also sees the right side of position 2: `"flows through"`

The model learns that `"[MASK] flows through"` → `"current"`, developing deep contextual understanding.

### E.4.2 Why 80/10/10 Masking Split?

For each selected token, the 80/10/10 rule applies:
- **80% replace with [MASK]**: the primary learning signal
- **10% replace with a random word**: crucial for this reason — if every selected token became [MASK], the model at inference time (fine-tuning) never sees [MASK] tokens, creating a train/test mismatch. The random word teaches the model to maintain good representations for *all* tokens (even non-masked ones), since any token might be "secretly" selected.
- **10% kept unchanged**: also helps the model maintain good representations for unmasked tokens.

**Result:** The model learns to produce a contextually appropriate representation for every token in every context, whether masked or not.

### E.4.3 Next Sentence Prediction (NSP)

**Task:** Given [CLS] + Sentence A + [SEP] + Sentence B + [SEP], predict: does B follow A in the original text?

- 50% of the time: B is the actual next sentence (positive)
- 50% of the time: B is a random sentence from the corpus (negative)

The [CLS] token's final hidden state is passed to a binary classifier:
```
logit = MLP([CLS]_output)
P(IsNext) = sigmoid(logit)
```

**The purpose:** Forces BERT to learn **discourse coherence** — understanding whether one sentence follows from another, which is crucial for tasks like question answering (does the answer actually address the question?).

### E.4.4 Pre-Training Scale and Hardware

- **Dataset:** BooksCorpus (800M words) + English Wikipedia (2,500M words) = 3.3B words
- **BERT-base:** 12 layers, 768 hidden, 12 heads, 110M parameters
- **Training time:** 4 days on 4 Cloud TPU pods (64 TPUs total) — thousands of dollars of compute
- **Result:** A model that deeply understands English text, freely available for fine-tuning on specific tasks

---

## E.5 Sentence-BERT

### E.5.1 The N² Problem with Vanilla BERT

Suppose you want to find which of 100 student answers is most similar to the ideal answer.

With **vanilla BERT**, to compare student answer i with the ideal, you must run: `[CLS] ideal [SEP] student_i [SEP]` through the full 12-layer BERT model. To compare all 100 students: **100 forward passes** = ~10 seconds.

If you want to find all similar pairs in a dataset of 10,000 sentences: 10,000²/2 = 50,000,000 forward passes = **months of compute**.

Each BERT forward pass is expensive: O(n² × d × 12 layers) ≈ 10M operations.

### E.5.2 Siamese Network — Architecture and Intuition

**Sentence-BERT** fine-tunes BERT so that each sentence can be independently encoded into a single fixed-size embedding. Then comparison is just cosine similarity — an O(d) operation.

```
    Sentence A                   Sentence B
        ↓                             ↓
  [BERT Encoder]             [BERT Encoder]    ← SHARED WEIGHTS
        ↓                             ↓
  [Mean Pool →]              [Mean Pool →]
        ↓                             ↓
      u ∈ ℝ^d                      v ∈ ℝ^d
                    ↓
          cos_sim(u, v) ∈ [-1, 1]
```

**"Siamese" network**: In Greek mythology, Siamese twins share the same body. Here, the two branches share the same BERT weights — they are one BERT model applied twice. This ensures both embeddings live in the same vector space (otherwise cosine similarity is meaningless).

**Pre-computation advantage:** Encode the ideal answer once → u. Encode each student answer once → v₁...v₁₀₀. Then compare: `cos_sim(u, v₁), cos_sim(u, v₂), ...` — just 100 vector operations, not 100 BERT forward passes.

### E.5.3 Natural Language Inference Fine-tuning

NLI datasets (SNLI, MultiNLI) contain sentence pairs labeled with one of three relations:
- **Entailment**: "A cat is sleeping in the sun" → "An animal is resting"
- **Contradiction**: "A cat is sleeping" → "A cat is running"
- **Neutral**: "A cat is sleeping" → "The weather is nice"

SBERT is fine-tuned with a 3-way classification loss:
```
features = [u, v, |u-v|]    concat of both embeddings + element-wise absolute difference
logits = W_class · features  (W_class ∈ ℝ^{3×3d})
loss = CrossEntropy(softmax(logits), label)
```

The `|u-v|` term captures the absolute difference between the two embeddings, which is informative for whether they're similar or contradictory.

After training, entailing pairs have high cosine similarity; contradicting pairs have low similarity — exactly what we need for grading.

### E.5.4 Triplet Loss — Full Derivation

An alternative training objective using triplets (anchor a, positive p, negative n):

```
L = max(0,  ‖f(a) - f(p)‖²  -  ‖f(a) - f(n)‖²  +  margin)
         ↑ dist(anchor,positive)   ↑ dist(anchor,negative)
```

Where `f(x)` is the SBERT embedding of sentence x, `margin` is a hyperparameter (e.g., 1.0).

**What this loss does:**
- If `dist(a,p) > dist(a,n) - margin` (positive is farther than negative), the loss is positive → we penalize.
- If `dist(a,n) > dist(a,p) + margin` (negative is sufficiently farther than positive), loss = 0 → no penalty.

**Training effect:** Positive pairs (same meaning) are pulled together in embedding space; negative pairs (different meaning) are pushed apart, with a margin gap between them.

**In terms of cosine similarity:**
```
L = max(0,  margin  -  cos_sim(f(a), f(p))  +  cos_sim(f(a), f(n)))
```

Higher similarity to positive (+cos_sim(a,p)) and lower similarity to negative (-cos_sim(a,n)) both reduce the loss.

### E.5.5 Multiple Negative Ranking Loss

The actual training of `all-MiniLM-L6-v2` uses **Multiple Negative Ranking Loss (MNRL)** — a more data-efficient approach:

In a batch of N pairs `{(a₁,p₁), (a₂,p₂), ..., (aₙ,pₙ)}`:
- For anchor aᵢ, the positive is pᵢ, and **all other pⱼ (j≠i) in the batch** are used as negatives.
- Loss: InfoNCE-like cross-entropy over N choices

```
L = -1/N × Σᵢ log( exp(cos_sim(aᵢ,pᵢ)/τ) / Σⱼ exp(cos_sim(aᵢ,pⱼ)/τ) )
```

A batch of 64 pairs gives 63 negatives per anchor — very efficient.

---

## E.6 all-MiniLM-L6-v2: Knowledge Distillation

### E.6.1 What is Knowledge Distillation?

**Knowledge Distillation** (Hinton et al., 2015) is a training technique where a smaller **"student"** model is trained to mimic a larger **"teacher"** model, rather than learning from raw data alone.

**Motivation:** Large models (teacher) are accurate but slow. Small models (student) are fast but less accurate. Distillation gets you most of the accuracy with much less computation.

### E.6.2 Teacher-Student Framework

```
Teacher (large, pre-trained, frozen):
  ┌─────────────────────┐
  │ BERT-large (340M)   │
  │ 24 layers, 1024-dim │ → produces "soft targets": attention matrices,
  └─────────────────────┘   probability distributions (not just hard labels)

Student (small, being trained):
  ┌─────────────────────┐
  │ MiniLM-L6 (22M)     │
  │ 6 layers, 384-dim   │ → must match teacher's behavior
  └─────────────────────┘

Training data: same sentences fed to both
Loss: student must match teacher's intermediate representations
```

**Why "soft targets" are better than hard labels:**
- Hard label: `"cat" → [0,0,0,1,0,...]` (one-hot, 99.99% certainty)
- Soft target (teacher output): `"cat" → [0.001, 0.003, 0.002, 0.85, 0.05, ...]` (probabilities)

The soft targets carry information about *which wrong answers are least wrong* — the teacher's uncertainty encodes relationships between classes, providing richer training signal.

### E.6.3 KL Divergence — What It Measures

KL (Kullback-Leibler) Divergence measures how one probability distribution P differs from another Q:

```
KL(P || Q) = Σᵢ P(i) × log(P(i) / Q(i))
```

**Properties:**
- Always ≥ 0
- = 0 iff P = Q (identical distributions)
- Not symmetric: KL(P||Q) ≠ KL(Q||P)
- Convention: P = reference (teacher), Q = approximation (student)

**In distillation:** minimize `KL(A_teacher || A_student)` — make the student's distribution match the teacher's as closely as possible.

### E.6.4 MiniLM: Attention Distillation

**Standard distillation** transfers knowledge by matching output logits or hidden states. **MiniLM** specifically distills the **self-attention distributions** of the teacher's last layer:

```
L_distill = KL( softmax(A_teacher_last / τ)  ||  softmax(A_student_last / τ) )
```

Where `τ` (temperature) > 1 softens the distributions.

**Why attention specifically?** Attention matrices encode what each token looks at — essentially the model's internal reasoning about which tokens are related. Transferring this teaches the student *how* to reason about relationships, not just *what* the final outputs are.

The teacher's attention tells the student: "When processing the word 'voltage', look closely at 'current' and 'resistance' — that's where the relevant context is." The student learns this behavior.

### E.6.5 Model Architecture Comparison Table

| Property | BERT-base | BERT-large | all-MiniLM-L6-v2 |
|---|---|---|---|
| Transformer layers | 12 | 24 | 6 |
| Hidden dimension | 768 | 1024 | 384 |
| Attention heads | 12 | 16 | 12 |
| FFN size (d_ff) | 3072 | 4096 | 1536 |
| Total parameters | 110M | 340M | ~22M |
| Max sequence length | 512 | 512 | 256 |
| Output embedding dim | 768 | 1024 | 384 |
| Inference speed | 1× | 0.5× | ~5× |
| Sentence similarity quality | baseline | +1-2% | -1-3% |

---

## E.7 Mean Pooling — Sentence to Single Vector

### E.7.1 Why Not Use the [CLS] Token?

Vanilla BERT's [CLS] token was optimized during pre-training for **sentence-pair classification** (NSP task). Without further fine-tuning, the [CLS] representation is not a good general-purpose sentence embedding — it doesn't capture the full meaning of the sentence evenly.

**Empirical evidence** (from SBERT paper): On Semantic Textual Similarity benchmarks:
- BERT [CLS] (no fine-tuning): Pearson r = 0.20 (barely better than random)
- BERT mean pooling (no fine-tuning): Pearson r = 0.54
- SBERT mean pooling (with fine-tuning): Pearson r = 0.85

Mean pooling outperforms [CLS] even before fine-tuning.

### E.7.2 The Pooling Formula

```
h₁, h₂, ..., hₙ ∈ ℝ^384  are the final-layer hidden states for n tokens

sentence_embedding = (1/n) × (h₁ + h₂ + ... + hₙ)
                   = (1/n) × Σᵢ₌₁ⁿ hᵢ     ∈ ℝ^384
```

**Geometric interpretation:** The mean pooled vector is the centroid (center of mass) of the n token vectors in 384-dimensional space.

### E.7.3 Attention Masking for Padding

When processing a batch of sentences with different lengths, shorter sequences are **padded** with [PAD] tokens to match the longest sequence. We must not include padding tokens in the mean:

```python
# token_embeddings: shape (batch_size, max_seq_len, 384)
# attention_mask:   shape (batch_size, max_seq_len), 1=real token, 0=padding

# Expand mask to feature dimension:
mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

# Zero out padding positions:
masked_embeddings = token_embeddings * mask

# Sum real token embeddings:
sum_emb = masked_embeddings.sum(dim=1)    # shape: (batch_size, 384)

# Count real tokens per sentence:
count = mask.sum(dim=1).clamp(min=1e-9)  # prevent division by zero

# Mean:
sentence_embedding = sum_emb / count      # shape: (batch_size, 384)
```

The `.clamp(min=1e-9)` prevents division by zero for sentences that are entirely padding (edge case).

---

## E.8 Cosine Similarity — Complete Analysis

### E.8.1 Dot Product — Definition and Geometry

The **dot product** (also called inner product or scalar product) of two vectors a and b in ℝⁿ is:

```
a · b = Σᵢ₌₁ⁿ aᵢ × bᵢ = a₁b₁ + a₂b₂ + ... + aₙbₙ    (scalar result)
```

**Geometric meaning:** `a · b = ‖a‖ × ‖b‖ × cos(θ)` where θ is the angle between the two vectors.

- If θ = 0° (parallel): a · b = ‖a‖ × ‖b‖ (maximum, positive)
- If θ = 90° (perpendicular): a · b = 0 (orthogonal = no similarity)
- If θ = 180° (anti-parallel): a · b = -‖a‖ × ‖b‖ (maximum negative)

This follows from the **Law of Cosines** applied to the parallelogram of vectors.

### E.8.2 L2 Norm — Definition

The **L2 norm** (Euclidean length) of vector a:

```
‖a‖₂ = √(Σᵢ aᵢ²) = √(a₁² + a₂² + ... + aₙ²)
```

This is simply the Pythagorean theorem extended to n dimensions. It measures the "length" of the vector from the origin.

### E.8.3 The Cosine Formula Derived from Law of Cosines

Rearranging the geometric dot product formula:

```
a · b = ‖a‖ × ‖b‖ × cos(θ)

cos(θ) = (a · b) / (‖a‖ × ‖b‖)

cos_sim(a, b) = cos(θ) = (Σᵢ aᵢbᵢ) / (√Σᵢaᵢ² × √Σᵢbᵢ²)
```

**Range:** cos(θ) ∈ [-1, 1]. For SBERT embeddings in practice, values fall in [0, 1] (embeddings rarely point in opposite directions).

### E.8.4 Why Not Euclidean Distance?

**Euclidean distance:** `‖a - b‖ = √(Σᵢ(aᵢ - bᵢ)²)`

**Problem:** Two semantically identical sentences might have different embedding magnitudes (norms) if one is tokenized into more tokens and the mean pooling produces a longer vector. Euclidean distance conflates direction (meaning) and magnitude (scale of activations).

**Cosine similarity is magnitude-invariant:** If b = 2×a (same direction, double magnitude):
```
cos_sim(a, b) = (a · 2a) / (‖a‖ × ‖2a‖) = 2‖a‖² / (‖a‖ × 2‖a‖) = 1.0
```
So `cos_sim(a, 2a) = 1.0` — correctly identifies identical direction despite different magnitudes.

### E.8.5 High-Dimensional Geometry Intuition

In 384 dimensions, **almost all random vectors are roughly orthogonal** to each other (cos_sim ≈ 0). The curse of dimensionality means the "volume" of the space is concentrated near the equator (90°) in high dimensions.

This means:
- Random (unrelated) sentence pairs get cos_sim ≈ 0–0.3
- Loosely related pairs: 0.3–0.6
- Domain-related but different answers: 0.5–0.7
- Similar answers in different words: 0.7–0.85
- Near-identical answers: 0.85–1.0

The **0.6 threshold** in the project accounts for the fact that even unrelated academic text gets 0.5–0.6 (because they share domain vocabulary and structure — all physics answers contain words like "force", "energy", "equation", etc.).

### E.8.6 The Leniency Curve — Why 0.6 Threshold?

The raw cosine similarity `sim ∈ [0, 1]` is mapped to a fraction:

```python
if sim <= 0.6:
    text_fraction = 0.0
else:
    text_fraction = min(1.0, (sim - 0.6) / 0.4)
```

**Why 0.6?** Experimenting on sample answers showed that:
- An answer about a completely different topic in the same subject gets sim ≈ 0.5–0.6 (shared academic vocabulary)
- A vaguely relevant but incorrect answer gets sim ≈ 0.6–0.7
- A partially correct answer gets sim ≈ 0.7–0.85
- A complete correct answer gets sim ≈ 0.85–1.0

The threshold at 0.6 eliminates the "background noise" from shared vocabulary, making only genuinely relevant answers earn marks.

**Linear rescaling:** The interval `[0.6, 1.0]` is mapped linearly to `[0.0, 1.0]`:
```
fraction = (sim - 0.6) / (1.0 - 0.6) = (sim - 0.6) / 0.4
```

At sim=0.6: fraction = 0. At sim=1.0: fraction = 1.0. At sim=0.8: fraction = (0.8-0.6)/0.4 = 0.5.

---

---

# PART F — VISION MODELS

---

## F.1 Convolutional Neural Networks — From Pixels to Features

### F.1.1 What is a Convolution?

A **convolution** comes from mathematics: `(f * g)(t) = ∫ f(τ)g(t-τ)dτ`. In discrete 2D image processing:

```
Output[i][j] = Σ_{p=0}^{k-1} Σ_{q=0}^{k-1} Kernel[p][q] × Input[i+p][j+q]
```

A **kernel** (also called filter or weight matrix) is a small matrix (e.g., 3×3) that slides over the input image, computing a **weighted sum** at each position.

**Concrete example — Edge detection kernel:**
```
Kernel K = [[-1, -1, -1],    (detects horizontal edges: +8 at center,
             [-1,  8, -1],     -1 at all 8 neighbors)
             [-1, -1, -1]]

At position (i,j):
Output[i][j] = -1×I[i-1,j-1] - 1×I[i-1,j] - 1×I[i-1,j+1]
             - 1×I[i,j-1]   + 8×I[i,j]   - 1×I[i,j+1]
             - 1×I[i+1,j-1] - 1×I[i+1,j] - 1×I[i+1,j+1]
```

If the center pixel is much brighter than neighbors (edge) → Output > 0. If uniform region → cancel out → Output ≈ 0.

**In a CNN,** the kernel values are **not hand-designed** — they are **learned parameters** that automatically discover useful features (edges, curves, colors, textures) through training.

### F.1.2 Stride, Padding, and Output Size

**Stride `s`**: how many pixels the kernel moves at each step. Default: 1 (move one pixel at a time). Stride 2 halves the output size (downsampling).

**Padding `p`**: how many zeros are added around the border of the input. Padding=0 → output shrinks. Padding=(k-1)/2 → output same size as input ("same" padding).

**Output size formula:**
```
Output_height = floor((H + 2p - k) / s) + 1

For H=32, k=3, p=1, s=1:
  (32 + 2×1 - 3) / 1 + 1 = 32/1 + 1 = 32   (same size! "same" padding)

For H=32, k=3, p=0, s=2:
  (32 + 0 - 3) / 2 + 1 = 29/2 + 1 = 15   (roughly halved)
```

### F.1.3 Max Pooling — Spatial Downsampling

**Max pooling** takes the maximum value in each non-overlapping `k×k` window:
```
MaxPool output[i][j] = max of Input[ki:ki+k, kj:kj+k]
```

For a 2×2 max pool:
```
Input:  [3, 7]    Output: max(3,7,1,8) = 8
        [1, 8]
```

**Purpose:**
1. **Downsampling**: reduces spatial size by factor k, reducing computation for subsequent layers.
2. **Translation invariance**: if a feature shifts by 1 pixel, max pooling often produces the same output — the feature is still "present" regardless of exact location.

### F.1.4 Batch Normalization

**Batch Normalization** (Ioffe & Szegedy, 2015) normalizes activations across the batch dimension (N) for each feature map:

```
For feature channel c:
  μ_c = (1/N) Σᵢ feature_maps[i,c,:,:]     (mean over batch × spatial dims)
  σ²_c = (1/N) Σᵢ (feature_maps[i,c,:,:] - μ_c)²
  z_c = (x_c - μ_c) / √(σ²_c + ε)
  y_c = γ_c × z_c + β_c    (learn per-channel scale and shift)
```

Batch norm ensures each feature map has consistent mean and variance statistics, stabilizing training. It also acts as a regularizer (the noise from batch statistics discourages overfitting). Used in VGG-16 (inside CRAFT) and ResNet.

### F.1.5 VGG Architecture — Depth Through Simplicity

**VGG** (Simonyan & Zisserman, Oxford, 2014) achieved great depth (up to 19 layers) through one insight: use only **3×3 convolutions** (the smallest filter that can capture spatial relationships), stacked many times.

**Why 3×3?** Two stacked 3×3 conv layers have the same receptive field as one 5×5 layer (a 3×3 over a 3×3 output covers a 5×5 input area), but fewer parameters (2×3²×C² = 18C² vs 5²×C² = 25C²) and two non-linearities instead of one.

VGG-16 specifically (used in CRAFT):
```
Block 1: Conv3×3-64, Conv3×3-64, MaxPool → H/2 × W/2
Block 2: Conv3×3-128, Conv3×3-128, MaxPool → H/4 × W/4
Block 3: Conv3×3-256, Conv3×3-256, Conv3×3-256, MaxPool → H/8 × W/8
Block 4: Conv3×3-512, Conv3×3-512, Conv3×3-512, MaxPool → H/16 × W/16
Block 5: Conv3×3-512, Conv3×3-512, Conv3×3-512, MaxPool → H/32 × W/32
```
Total parameters: 138M (mostly in final FC layers).

### F.1.6 ResNet — Skip Connections in CNNs

ResNet (He et al., 2016) added skip connections to CNNs, enabling training of 50–152+ layer deep networks:

```
ResNet block:
  x ── F(x) = Conv→BN→ReLU→Conv→BN ─── (+) ── ReLU ──→
  └─────────────────────────────────────┘ ↑
                                     residual add
```

`output = F(x) + x`.  If F = 0 (early training), output = x (identity). Network gradually learns refinements F on top of identity.

ResNet-50 is used inside **pix2tex** as the formula image encoder.

---

## F.2 Vision Transformer (ViT)

### F.2.1 The Core Idea: Image as Sequence of Patches

The transformer expects a sequence of vectors. The clever idea of ViT (Dosovitskiy et al., Google, 2020): **divide the image into a grid of patches, each patch becomes a "token"**, then run a standard transformer encoder.

**Why patches instead of pixels?** At 224×224 pixels, treating each pixel as a token gives 50,176 tokens → attention cost O(50176²) — completely infeasible. Patches of 32×32 give 49 tokens → manageable.

### F.2.2 Patch Splitting and Flattening

```
Image I ∈ ℝ^{H×W×C}    (H=W=224, C=3 for RGB, P=32 for ViT-B/32)

Number of patches: N = (H/P) × (W/P) = (224/32)² = 7×7 = 49

Patch p_{i,j} = I[i×P:(i+1)×P, j×P:(j+1)×P, :]   ∈ ℝ^{P×P×C}

Flattened: p_{i,j} ∈ ℝ^{P²×C} = ℝ^{32×32×3} = ℝ^{3072}
```

Now we have 49 vectors, each ℝ^{3072}. This is the "sequence" input to the transformer.

### F.2.3 Linear Patch Embedding

Each 3072-dim patch vector is linearly projected to d-dim:
```
patch_embedding = E_patch × patch + e_cls_bias?

E_patch ∈ ℝ^{d × 3072}    (learnable projection matrix)
output ∈ ℝ^d               (d=768 for ViT-B/32)
```

This is exactly analogous to the token embedding matrix in BERT (maps a token index to a d-dim vector), but here we map a pixel patch to a d-dim vector.

### F.2.4 Class Token in ViT

Before the transformer, a learnable **class token** `x_cls ∈ ℝ^d` is prepended:

```
z₀ = [x_cls; patch_emb₁; patch_emb₂; ...; patch_emb₄₉]  ∈ ℝ^{50×d}
```

After the transformer, `z_L[0]` (the CLS position's output) aggregates information from all 50 positions via self-attention through L layers. It is used as the image embedding.

**Why prepend [CLS]?** Without it, we'd need to pool over all patch positions (like mean pooling in BERT). The [CLS] token learns to be where global image information accumulates through attention — like a "summary token."

### F.2.5 2D Positional Embeddings

49 patches have 2D spatial positions (row/column in the 7×7 grid). Standard 1D positional embeddings are used (positions 0–48, with 0 for [CLS]):

```
z₀ ← z₀ + E_pos    where E_pos ∈ ℝ^{50×d} (learnable table)
```

More sophisticated variants use 2D sinusoidal or factored row+column embeddings, but 1D learned embeddings work well empirically.

### F.2.6 ViT Encoder Blocks

The 50 "patch tokens" (1 CLS + 49 patches) go through L transformer encoder blocks — identical to the BERT encoder block (multi-head self-attention → residual+LN → FFN → residual+LN).

**Key property:** In self-attention, every patch can attend to every other patch. The model learns to relate, e.g., the top-left patch of a resistor symbol to the bottom-right patch to recognize the complete component.

For **ViT-B/32** (used in CLIP):
- L = 12 transformer layers
- d = 768 (hidden size)
- h = 12 attention heads
- d_k = 64
- d_ff = 3072 (4× expansion)

### F.2.7 Output: The Image Embedding

```
image_embedding = z_L[0]    ∈ ℝ^768    (CLS position output)
```

But CLIP adds an additional linear projection:
```
image_embedding_clip = image_embedding × W_proj_image + b_proj    ∈ ℝ^512
```

This 512-dim vector is the final image embedding used for similarity comparison.

---

## F.3 CLIP — Contrastive Language-Image Pre-training

### F.3.1 The Dual-Encoder Design

CLIP (Radford et al., OpenAI, 2021) trains two encoders jointly:

```
Image Encoder: ViT-B/32 → 512-dim
Text Encoder:  12-layer Transformer, max 77 tokens → 512-dim
```

Both produce 512-dimensional embeddings in the **same shared vector space**.

### F.3.2 Shared Embedding Space

"Shared space" means: if you input `(photo of a circuit diagram)` to the image encoder and the text `"circuit diagram"` to the text encoder, both produce vectors that **point in similar directions** in ℝ^512.

This was not explicitly programmed — it emerged from training with the contrastive loss.

After training, the model can perform:
- **Zero-shot image classification**: compare image to text prompts ("a photo of a cat", "a photo of a dog"), pick highest similarity.
- **Image retrieval**: find images matching a text query.
- **Diagram comparison** (our use case): compare two images and see if they show the same thing.

### F.3.3 The Contrastive Learning Framework

**Contrastive learning** is a self-supervised framework: no explicit labels are needed. Instead, define:
- **Positive pairs**: inherently similar inputs
- **Negative pairs**: inherently dissimilar inputs

And train the model to produce **similar embeddings for positive pairs** and **dissimilar embeddings for negative pairs**.

For CLIP, positives = (image, its caption text). Negatives = (image, a different image's caption).

The key insight: with 400 million captioned images from the internet, you have 400 million positive pairs — no human labeling needed. And every batch of N pairs contains N²-N implicit negatives for free.

### F.3.4 InfoNCE Loss — Full Mathematical Derivation

**InfoNCE** (Van den Oord et al., 2018) stands for Information Noise-Contrastive Estimation.

Given a batch of N image-text pairs `{(I₁,T₁), ..., (Iₙ,Tₙ)}`, compute 2N embeddings:
```
iᵢ = Image_encoder(Iᵢ) / ‖Image_encoder(Iᵢ)‖   ∈ ℝ^512 (L2 normalized)
tⱼ = Text_encoder(Tⱼ) / ‖Text_encoder(Tⱼ)‖     ∈ ℝ^512 (L2 normalized)
```

Compute the N×N similarity matrix (dot product = cosine similarity after L2 normalization):
```
S[i][j] = iᵢ · tⱼ / τ      (τ = temperature, learnable scalar)
```

**Image-to-text loss** (for each image, find its matching text):
```
L_i2t = -1/N × Σᵢ log( exp(S[i][i]) / Σⱼ exp(S[i][j]) )
```

This is cross-entropy where the "labels" are the diagonal (correct pairs are labels 0,1,...,N-1).

**Text-to-image loss** (for each text, find its matching image):
```
L_t2i = -1/N × Σⱼ log( exp(S[j][j]) / Σᵢ exp(S[i][j]) )
```

**Total CLIP loss:**
```
L_CLIP = (L_i2t + L_t2i) / 2
```

**Gradient intuition:** For image I₁ and its correct caption T₁:
- We want `S[1][1]` (I₁-T₁ similarity) to be high → gradient pushes i₁ and t₁ closer.
- We want `S[1][2], S[1][3], ...` (I₁-T₂, I₁-T₃, ...) to be low → gradient pushes i₁ away from t₂, t₃, etc.

### F.3.5 Temperature Parameter τ

The temperature `τ` controls the sharpness of the softmax distribution:
- Small τ (e.g., 0.07): distribution is **sharp** — one correct pair dominates, hard negatives punished heavily. Fast learning but can be unstable.
- Large τ (e.g., 1.0): distribution is **flat** — all pairs treated nearly equally. Training signal is weaker.

CLIP learns `τ` as a parameter: `τ = exp(log_τ)` where `log_τ` is initialized to `log(1/0.07) ≈ 2.66`.

### F.3.6 Why 400 Million Image-Text Pairs?

CLIP's power comes from scale. A model trained on 400M pairs from the internet learns representations that cover essentially any visual concept humans talk about — including hand-drawn circuit diagrams, biology diagrams, flowcharts, and other academic diagrams that appear in study materials online.

This is why CLIP can meaningfully compare student-drawn diagrams to ideal diagrams — it has semantic understanding of visual concepts, not just pixel similarity.

### F.3.7 How CLIP Encodes Diagram Images in the Project

```python
# evaluation_core.py
inputs = self.processor(
    images=[img_ideal_rgb, img_student_rgb],   # Two PIL images
    return_tensors="pt"
)
# processor resizes to 224×224, normalizes pixel values to [-1,1]

with torch.no_grad():
    feats = self.model.get_image_features(**inputs)
    # feats.shape = (2, 512)
    # feats[0] = ideal diagram embedding
    # feats[1] = student diagram embedding
```

### F.3.8 L2 Normalization Before Cosine Similarity

```python
feats = feats / feats.norm(dim=-1, keepdim=True)
```

**Why normalize?** After normalization:
- `‖feats[0]‖ = 1` and `‖feats[1]‖ = 1` (unit vectors)
- `feats[0] · feats[1] = ‖feats[0]‖ × ‖feats[1]‖ × cos(θ) = 1×1×cos(θ) = cos(θ)`

So the dot product **equals** cosine similarity for unit vectors. This is computationally cheaper than computing cosine similarity (divide by both norms separately) and numerically identical.

---

---

# PART G — OCR ENGINES

---

## G.1 What is OCR and Why is it Hard?

**OCR (Optical Character Recognition)** is the task of converting images of text (scanned documents, photos) into machine-readable strings.

**Why it's hard:**
1. **Handwriting variability**: every person's handwriting is unique — same letter `'a'` can look completely different
2. **Noise**: paper texture, scanning artifacts, folds, smudges
3. **Varying scale and rotation**: text may be tilted, zoomed
4. **Overlapping characters**: cursive handwriting has connected letters
5. **Domain-specific symbols**: math formulas have special symbols (∑, ∫, ∂) not in standard text datasets

---

## G.2 EasyOCR — Text Detection with CRAFT

### G.2.1 CRAFT Overview

**CRAFT** (Character Region Awareness For Text detection, Baek et al., 2019) reformulates text detection as a pixel-level prediction problem: instead of predicting bounding boxes directly, it generates probability heatmaps that indicate where characters are.

**The key insight:** Detecting characters (smaller units) is more generalizable than detecting words or lines — you can then merge characters into words using the affinity map.

### G.2.2 VGG-16 Backbone — Block by Block

CRAFT uses VGG-16 as a pretrained feature extractor (initialized with ImageNet-pretrained weights):

```
Input: RGB image ∈ ℝ^{3×H×W}

Block 1: (stride=1, no maxpool initially)
  Conv2d(3, 64, 3×3, pad=1) → BN → ReLU
  Conv2d(64, 64, 3×3, pad=1) → BN → ReLU
  MaxPool2d(2, stride=2) → ℝ^{64×H/2×W/2}    [feature map 1: H/2 resolution]

Block 2:
  Conv2d(64, 128, 3×3, pad=1) → BN → ReLU  (×2)
  MaxPool2d(2, stride=2) → ℝ^{128×H/4×W/4}  [feature map 2: H/4]

Block 3:
  Conv2d(128, 256, 3×3, pad=1) → BN → ReLU  (×3)
  MaxPool2d(2, stride=2) → ℝ^{256×H/8×W/8}  [feature map 3: H/8]

Block 4:
  Conv2d(256, 512, 3×3, pad=1) → BN → ReLU  (×3)
  MaxPool2d(2, stride=2) → ℝ^{512×H/16×W/16} [feature map 4: H/16]

Block 5:
  Conv2d(512, 512, 3×3, pad=1) → BN → ReLU  (×3)
  MaxPool2d(2, stride=2) → ℝ^{512×H/32×W/32} [feature map 5: H/32]
```

**Key observation:** Each block doubles the depth of features while halving the spatial resolution. The features at different levels capture different scales:
- Block 1 features (H/2): fine detail, edge information
- Block 3 features (H/8): characters and strokes
- Block 5 features (H/32): large text regions, global layout

### G.2.3 Feature Pyramid Network (FPN) — Multi-Scale Fusion

FPN (Lin et al., 2017) combines features from multiple VGG levels using a top-down pathway:

**Why multi-scale?** Small characters require fine-resolution features; large headings require coarse-resolution features (which have large receptive fields). FPN gets both.

The bottom-up path is the VGG backbone (above). The top-down path:

```
Feature level 5 (H/32, 512 features)
  ↓ Upsample 2× (bilinear interpolation or transposed conv) → H/16
  + Feature level 4 (H/16, 512 features) added via skip connection
  ↓ Conv → 256 features → H/16
  ↓ Upsample 2× → H/8
  + Feature level 3 (H/8, 256 features) added
  ↓ Conv → 128 features → H/8
  ↓ Upsample 2× → H/4
  + Feature level 2 (H/4, 128 features) added
  ↓ Conv → 64 features → H/4
  ↓ Upsample 2× → H/2
  Final: 64 features → H/2 resolution
```

**Bilinear upsampling:** For each position (i,j) in the upsampled image, linearly interpolate the four nearest neighbors in the lower-resolution feature map.

### G.2.4 U-Net Decoder — Skip Connections for Resolution Recovery

The architecture mirrors **U-Net** (Ronneberger et al., 2015), originally designed for biomedical image segmentation. The key contribution: **skip connections** that directly copy fine-resolution features from the encoder (VGG backbone) to the decoder (top-down path).

This prevents the loss of fine spatial detail during downsampling — the decoder can access both high-level semantic features (from deep layers) and fine spatial detail (from shallow layers via skip connections).

### G.2.5 Region Score Heatmap

The final 2-channel output of CRAFT includes:
**Channel 1 — Region score:** probability that pixel (i,j) is near the center of a character.

```
region_score[i][j] = P(pixel (i,j) belongs to a character center)
```

Characters have a Gaussian-shaped activation peak at their centroid. This is generated by training with **Gaussian ground truth maps** (soft labels) centered on character bounding box centers — rather than hard 0/1 labels, the model learns to produce smooth probability maps.

### G.2.6 Affinity Score Heatmap

**Channel 2 — Affinity score:** probability that pixel (i,j) lies between two adjacent characters that belong to the same word.

```
affinity_score[i][j] = P(pixel is between adjacent same-word characters)
```

This allows CRAFT to detect word boundaries: high affinity = same word; low affinity = word boundary.

**How affinity GT is generated during training:** For each consecutive character pair (c_i, c_{i+1}), place an affinity box at the center point between their bounding boxes.

### G.2.7 Post-Processing: Heatmap → Bounding Boxes

1. **Threshold** region score at 0.7 to get binary character mask.
2. **Threshold** affinity score at 0.4 to get binary affinity mask.
3. **Connected components** on combined mask → identify character groups.
4. **Minimum area rectangle** (rotated rect) fitted to each component group.
5. The result: rotated bounding boxes that can handle text at any angle.

```python
# EasyOCR code conceptually:
result = reader.readtext(image)
# result: list of (bbox, text, confidence)
# bbox: 4 corner points [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
```

---

## G.3 EasyOCR — Text Recognition with CRNN

### G.3.1 CRNN Overview

**CRNN** (Convolutional Recurrent Neural Network, Shi et al., 2015) recognizes the text in each detected bounding box crop. It converts a word image to a string by:
1. **CNN**: extract visual features (left-to-right columns)
2. **BiLSTM**: model sequential character context
3. **CTC decoder**: convert per-frame character probabilities to final string

### G.3.2 CNN Feature Extractor — Feature Columns

The CNN processes a height-normalized word crop (all crops resized to height=32 px, width varies):

```
Input: 32×W×1 (grayscale)

CNN (VGG variant, no final pooling on height dimension):
  ConvBlock1 → 32×W/4×64
  ConvBlock2 → 16×W/8×128
  ConvBlock3 → 8×W/16×256
  ConvBlock4 → 4×W/32×512
  ConvBlock5 → 1×W/32×512   (height collapsed to 1!)
```

The key: **the height dimension is pooled down to 1** by the end of the CNN. What remains is effectively a sequence of T = W/32 columns, each 512-dimensional.

**Why columns?** Text reads left-to-right; each column of the output corresponds approximately to one horizontal slice of the original word image, which corresponds to portions of characters.

**Visualization:**
```
"OHM" word image (32×90px)
After CNN → 1×3×512 (if W/32=3)
Column 0: features from region covering 'O'
Column 1: features from region covering 'H'
Column 2: features from region covering 'M'
```

(In practice, T ≈ W/4 due to actual implementation details, giving more columns for finer resolution.)

### G.3.3 Bidirectional LSTM — Architecture

The sequence of T=W/32 feature columns `[f₁, f₂, ..., fᵀ]` is fed to a 2-layer bidirectional LSTM:

```
Layer 1:
  Forward LSTM:  f₁ → rnn_f → h₁_f, f₂ → rnn_f → h₂_f, ..., fᵀ → h^T_f
  Backward LSTM: fᵀ ← rnn_b → h^T_b, fᵀ₋₁ ← h^{T-1}_b, ..., f₁ ← h₁_b
  Concat: h₁ = [h₁_f; h₁_b] ∈ ℝ^{2×d_lstm}

Layer 2:
  same structure, takes Layer 1 output as input

Final output: sequence [g₁, g₂, ..., gᵀ], each gₜ ∈ ℝ^{d_lstm}
```

### G.3.4 LSTM Cell Equations — Every Symbol Explained

```
At time step t, for one LSTM cell:

Inputs:  xₜ ∈ ℝ^d     (current feature column)
         hₜ₋₁ ∈ ℝ^h   (previous hidden state)
         Cₜ₋₁ ∈ ℝ^h   (previous cell state)

Gates:

  f_t = σ(Wf · concat(hₜ₋₁, xₜ) + bf)
       ↑σ = sigmoid gates always output (0,1)
       ↑Wf ∈ ℝ^{h×(h+d)} learnable weights, bf ∈ ℝ^h bias
       → f stands for "forget", controls what % of Cₜ₋₁ to keep

  i_t = σ(Wi · concat(hₜ₋₁, xₜ) + bi)
       → i stands for "input", controls what % of new info to add

  C̃_t = tanh(Wc · concat(hₜ₋₁, xₜ) + bc)
       → tanh outputs (-1,1), this is the "candidate" new cell state

  o_t = σ(Wo · concat(hₜ₋₁, xₜ) + bo)
       → o stands for "output", controls visibility of cell state

State updates:

  C_t = f_t ⊙ C_{t-1}  +  i_t ⊙ C̃_t
        ↑ keep this much   ↑ add this much of new candidate
        fraction of old    weighted by input gate

  h_t = o_t ⊙ tanh(C_t)
        ↑ output gate  ↑ squash cell state through tanh → (-1,1)
```

**Detailed symbol explanations:**
- `⊙` (Hadamard product / element-wise multiply): `[a,b]⊙[c,d] = [a×c, b×d]`. This is different from matrix multiply. It applies gate values independently to each feature dimension.
- `concat(h,x)`: vector concatenation, `[1,2] concat [3,4] = [1,2,3,4]`. The W matrices are applied to the full concatenated vector.
- `tanh`: hyperbolic tangent — squashes to (-1,1). Used for cell state and candidate because cell state can represent absence (negative) or presence (positive) of a feature.

### G.3.5 Why Bidirectional?

**Forward LSTM**: at step t, sees characters at positions 1, 2, ..., t. The `'H'` in `'OHM'` knows about 'O' before it.

**Backward LSTM**: processed from right to left. At step t (3rd position from end), has seen characters at positions T, T-1, ..., t. The `'H'` now also knows about the `'M'` after it.

**Concatenation**: `h_t = [h_t_forward; h_t_backward]`. Now the representation for 'H' has seen both 'O' (from the left) and 'M' (from the right) — full bidirectional context, crucial for correctly disambiguating characters that look similar out of context.

### G.3.6 CTC: Connectionist Temporal Classification

**The problem:** The LSTM outputs T vectors, one per time step (one per feature column). We want a string of L characters where L < T (the string is shorter than the sequence). How do we align them?

**CTC** (Graves et al., 2006) adds an extra blank character `-` (represented as ε or _) and defines a mapping from sequences of length T to strings of length L.

### G.3.7 The Blank Token

The blank token `-` has a specific index in the character set (usually the last index: if charset = {A,B,...,Z,a,...,z,0,...,9,...}, blank is the N+1th entry).

**Purpose:** Act as a spacer between repeated characters and fill "empty" time steps where no new character is being predicted.

### G.3.8 CTC Collapse Rules

Given a T-length output sequence (one character label per timestep, may include blanks):

**Two rules:**
1. **Merge consecutive identical labels** (including blank)
2. **Remove blank tokens**

```
Raw output (T=10):  O O O - - H - M M M
After rule 1:       O     - -  H   M
After rule 2:       O           H   M
Final string: "OHM"
```

The same final string "OHM" arises from many different alignments:
```
O - - H - M - - - -
O O - H H M M - - -
O - H - M - - - - -
... (many more)
```
CTC sums the probabilities of ALL valid alignments.

### G.3.9 CTC Training Loss — Dynamic Programming

The CTC loss for training: given the model's per-timestep character probabilities and the true label string, compute:

```
L_CTC = -log P(y | x) = -log Σ_{π: B(π)=y} P(π | x)
```

Where:
- `y` = target string (e.g., "OHM")
- `B(π)` = CTC collapse of alignment π
- Sum is over **all valid alignments** that collapse to y

Computing this naively is exponential (all possible alignments). **Dynamic programming** (forward-backward algorithm) computes it in O(T × L) time:

```
α_t(s) = P(first t characters produce prefix y[1:s] via CTC)
β_t(s) = P(last T-t characters produce suffix y[s+1:L] via CTC)

P(y|x) = Σ_s α_T(s) × β_T(s)    (sum over all positions)
```

This is analogous to the forward-backward algorithm in Hidden Markov Models.

### G.3.10 Greedy CTC Decoding vs Beam Search

**Greedy decoding:** At each timestep, pick the most probable character. Apply CTC collapse.
```
Argmax over char at each t: O O - H - M - - - -
Collapse: "OHM"
```
This is fast but suboptimal — the globally best sequence may not start with the locally best character at each step.

**Beam search decoding:** Maintain B candidate sequences at each step, expanding each with top characters. More accurate, higher computational cost. EasyOCR defaults to greedy for speed.

---

## G.4 Google Vision AI

### G.4.1 API Hierarchy

Google Vision's `document_text_detection` returns a hierarchical structure:
```
FullTextAnnotation
  └── pages: [Page, ...]
       └── blocks: [Block, ...]           (text blocks: paragraphs, tables, etc.)
            └── paragraphs: [Paragraph, ...]
                 └── words: [Word, ...]
                      └── symbols: [Symbol, ...]   (individual chars + confidence)
                           └── confidence: float
```

Each element has `bounding_poly` with `vertices` — 4 corner points `{x, y}` in pixel coordinates.

In the code, the system reconstructs the full text and bounding boxes at the paragraph level (combining all words in a paragraph):

```python
for block in page.blocks:
    for para in block.paragraphs:
        para_text = ' '.join(
            ''.join(s.text for s in word.symbols)
            for word in para.words
        )
        # bbox from para.bounding_poly.vertices
```

### G.4.2 Language Hints and the BCP-47 Handwriting Tag

```python
image_context = vision.ImageContext(
    language_hints=["en-t-i0-handwrit"]
)
```

`"en-t-i0-handwrit"` is a BCP-47 language tag with extension subtags:
- `en` — English
- `-t-` — transformation tag (indicates the content type differs from the language)
- `i0` — unnamed category
- `-handwrit` — handwritten content

This tells the Vision API to use its **handwriting-specialized** recognition model rather than the printed text model. The handwriting model has learned from millions of handwritten English samples and handles variable letter forms, slant, ligatures, etc.

### G.4.3 Image Size Constraints and Compression

Google Vision API accepts images up to **10 MB** per call. For high-DPI (300 DPI) A4 scans, a single page PNG can be 15–30 MB. The code handles this:

```python
img_bytes = to_jpeg_bytes(pil_img, quality=90)
if len(img_bytes) > 9 * 1024 * 1024:   # > 9 MB
    img_bytes = to_jpeg_bytes(pil_img, quality=80)
if still_too_large:
    scale = 0.85  # downscale by 15%
    pil_img = pil_img.resize((int(W*0.85), int(H*0.85)))
    # retry...
```

JPEG compression works by discarding high-frequency components (fine detail). Quality 90 preserves most detail; quality 45 is noticeable degradation. The tradeoff: smaller file → faster API call, but slightly lower OCR accuracy for fine script.

---

## G.5 Azure Document Intelligence

### G.5.1 Prebuilt-Read Model

Azure's `prebuilt-read` model is optimized for reading text from arbitrary documents. Like Google Vision, the underlying architecture is proprietary but follows the general pattern of:
- Transformer-based layout analysis (where are text regions?)
- Transformer-based text recognition (what does each region say?)

### G.5.2 Polygon Bounding Boxes

Azure returns bounding polygons as 8 floats `[x0,y0, x1,y1, x2,y2, x3,y3]` representing 4 corner points in order (top-left, top-right, bottom-right, bottom-left).

```python
polygon = line.polygon   # [x0,y0,x1,y1,x2,y2,x3,y3]
bbox = [
    [polygon[0], polygon[1]],   # TL
    [polygon[2], polygon[3]],   # TR
    [polygon[4], polygon[5]],   # BR
    [polygon[6], polygon[7]]    # BL
]
```

The coordinates are in **inches** (not pixels!), so must be converted to pixels using DPI:
`pixel_x = inch_x × DPI`

### G.5.3 Multi-Page PDF Processing

Unlike Google Vision (which processes one page at a time), Azure DI can process multi-page PDFs in one call. The whole PDF bytes are sent, and the response includes `document.pages[i]` for each page.

The code converts the entire PDF to bytes: `open(pdf_path, 'rb').read()` and sends it as `raw_document = documentai.RawDocument(content=pdf_bytes, mime_type="application/pdf")`.

---

---

# PART H — FORMULA PIPELINE

---

## H.1 Why Formulas Need Special Treatment

Standard OCR returns `"E = mc^2"` as a plain text string. This is useful for display but breaks mathematical comparison:

| Student writes | OCR returns | SymPy reads |
|---|---|---|
| `E = mc²` | `"E = mc^2"` | `Eq(E, m*c**2)` |
| `mc² = E` | `"mc^2 = E"` | `Eq(m*c**2, E)` |
| `mc² - E = 0` | `"mc^2 - E = 0"` | equivalent |

All three are mathematically equivalent but string comparison would mark them all as different. For fair grading, we need mathematical equivalence checking, which requires a symbolic representation — and pix2tex converts the formula image to LaTeX for SymPy to parse.

---

## H.2 Formula Region Detection — Heuristics

### H.2.1 Y-Coordinate Block Grouping

OCR blocks from the same text line have approximately the same Y-coordinate (vertical center). The code groups blocks that are within `tolerance_px` (typically 10 pixels) of each other:

```python
def _group_blocks_into_lines(blocks, tolerance_px=10):
    sorted_by_y = sorted(blocks, key=lambda b: center_y(b))
    lines = []
    current_line = [sorted_by_y[0]]
    for block in sorted_by_y[1:]:
        if abs(center_y(block) - center_y(current_line[-1])) <= tolerance_px:
            current_line.append(block)
        else:
            lines.append(current_line)
            current_line = [block]
    lines.append(current_line)
    return lines
```

**Why group by Y?** A formula like `∑_{n=1}^{∞} 1/n²` might span multiple OCR blocks on the same line (the summation sign, the subscript, the superscript, and the fraction might be separate blocks). Grouping by Y-coordinate reunites them before deciding if the line is formula-like.

### H.2.2 The `_looks_formula_like` Function

The function applies several heuristic tests to the text of a block/line. If any test passes, the line is flagged as formula-like:

```python
MATH_KEYWORDS = {'sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'sum',
                 'int', 'pi', 'theta', 'alpha', 'beta', 'gamma', ...}

MATH_OPERATORS = set('=+-×÷*/^_{}()[]∑∫√≈±∞∂∇')

def _looks_formula_like(text):
    lower = text.lower()
    # Test 1: contains math keywords
    if any(kw in lower for kw in MATH_KEYWORDS):
        return True
    # Test 2: high density of math operators and digits
    signal_chars = sum(1 for c in text if c in MATH_OPERATORS or c.isdigit())
    if signal_chars / max(len(text), 1) > 0.15:   # >15% are math chars
        return True
    # Test 3: contains Unicode math symbols
    if any(ord(c) > 127 and c in '∑∫√≈±∞∂∇θπ' for c in text):
        return True
    # Test 4: letter-digit pattern (e.g., "V=IR", "3x+4y=12")
    if re.search(r'[A-Za-z]\s*=\s*[A-Za-z0-9]', text):
        return True
    return False
```

### H.2.3 Signal Character Density

The 0.15 (15%) threshold for signal characters means: for a text like `"V = 3I + 2R"` (10 chars), signal chars are `=`, `3`, `+`, `2`, = 4 chars → 40% > 15% → formula-like.

For normal text like `"Ohm's Law states that the"` (25 chars), very few signal chars → not formula-like.

---

## H.3 pix2tex (LatexOCR) — Image to LaTeX

### H.3.1 The Encoder-Decoder Paradigm

**Encoder-Decoder** is a foundational architecture for sequence-to-sequence (seq2seq) tasks: given an input of one format (image), generate an output of another format (text sequence).

The encoder compresses the input into a rich "context" representation. The decoder reads this context and generates the output sequence, one element at a time.

**Applications of this paradigm:**
- Machine translation: source language → target language
- Summarization: long document → short summary
- Image captioning: image → text description
- Formula OCR: formula image → LaTeX string (our case)

### H.3.2 ResNet Encoder — Feature Grid

pix2tex uses a ResNet (ResNet-31 in some versions, ResNet-50 in others) to encode the formula crop:

```
Input: grayscale formula image ∈ ℝ^{1×H×W}   (e.g., 128×512)

ResNet:
  Conv7×7 (stride 2) → ℝ^{64×H/2×W/2}
  MaxPool (stride 2) → ℝ^{64×H/4×W/4}
  ResBlock×3 → ℝ^{64×H/4×W/4}
  ResBlock×4 (stride 2) → ℝ^{128×H/8×W/8}
  ResBlock×6 (stride 2) → ℝ^{256×H/16×W/16}
  ResBlock×3 (stride 2) → ℝ^{512×H/32×W/32}

Output shape: (512, H/32, W/32) e.g., (512, 4, 16)
```

This 2D feature grid is then **flattened** into a sequence:
```
Reshape: (512, 4, 16) → (512, 4×16) = (512, 64)
Transpose: → (64, 512)
```

Now we have 64 "visual tokens", each 512-dimensional. This is the encoder output / memory for the decoder.

**Why flatten a 2D grid to 1D sequence?** The decoder's attention mechanism operates on a 1D sequence of key-value pairs from the encoder. The spatial 2D structure is not needed — the decoder learns to spatially navigate the formula image via attention weights over this 1D sequence.

### H.3.3 Autoregressive Decoding

**"Autoregressive"** means: the output is generated one token at a time, and each new token depends on all previously generated tokens.

```
Step 1: Input = [<start>]
        Decoder attends to encoder memory
        Output: P(next_token | <start>, memory) → sample: "\"
Step 2: Input = [<start>, "\"]
        Output: P(next_token | <start>, "\", memory) → sample: "f"
Step 3: Input = [<start>, "\", "f"]
        Output: P(next_token | ...) → sample: "r"
...
Until <end> token is generated
Final: "\" + "f" + "r" + "a" + "c" + "{" + "1" + "}" + "{" + "2" + "}" = "\frac{1}{2}"
```

This models the conditional distribution `P(y₁, y₂, ..., yₗ | x) = Π_t P(yₜ | y₁,...,yₜ₋₁, x)` (chain rule of probability).

**Greedy decoding:** At each step, pick the highest-probability token.
**Beam search:** Maintain B candidates, pick the one with highest overall sequence probability.

### H.3.4 Cross-Attention — Q from Decoder, K/V from Encoder

The critical mechanism that connects decoder to encoder. In each decoder transformer block, after masked self-attention, there is a **cross-attention** sub-layer:

```
Q = decoder_hidden_state × Wq    (queries: what does the decoder want to know?)
K = encoder_output × Wk          (keys: what does each encoder position have?)
V = encoder_output × Wv          (values: what information is at each encoder position?)

CrossAttn = softmax(QKᵀ / √d_k) × V
```

**The key insight:** Q comes from the decoder (what the decoder is currently generating), but K and V come from the encoder (the formula image features). The cross-attention weight `A[i][j]` tells us: when generating decoder token at position i, how much should we attend to encoder position j (visual region j of the formula image)?

**Visual example:** When generating `\frac` (fraction command):
- The decoder query Q asks for "what's the main structure of this formula?"
- The encoder key K[j] for the fraction bar region has high similarity to this query
- Cross-attention weight is high for the fraction bar region
- The decoder "looks at" the fraction bar to confirm it should generate `\frac`

This is a learned, soft, differentiable version of "look at the relevant part of the image to decide what to write."

### H.3.5 Masked Self-Attention in Decoder

**The decoder cannot look at future tokens** — at inference time, future tokens don't exist yet. During training, future tokens exist (we have the complete target), but we must prevent cheating.

**Causal mask (upper triangular mask):**
```
Mask for sequence [t1, t2, t3, t4]:
     t1   t2   t3   t4
t1 [ 1    0    0    0  ]   ← t1 can only attend to t1
t2 [ 1    1    0    0  ]   ← t2 can attend to t1, t2
t3 [ 1    1    1    0  ]   ← t3 can attend to t1, t2, t3
t4 [ 1    1    1    1  ]   ← t4 can attend to everything
```

Value 0 → fill with -∞ before softmax → after softmax → attention weight = 0 (effectively masked).

This ensures: during training, when computing the loss for position t, the model only sees tokens 1...t-1 (same as what it would see at inference time).

### H.3.6 The Complete Decoder Block

```
Input: previous tokens (so far generated)
         │
    [Token Embedding + Positional Encoding]
         │
         ▼
 ════════════════════════════════════
 Step 1: MASKED SELF-ATTENTION
   same as encoder attention BUT with causal mask
   prevents attending to future tokens
 ════════════════════════════════════
         │ + Residual → LayerNorm
         ▼
 ════════════════════════════════════
 Step 2: CROSS-ATTENTION
   Q from decoder hidden state
   K, V from encoder output (formula image features)
   "looks at" relevant image regions
 ════════════════════════════════════
         │ + Residual → LayerNorm
         ▼
 ════════════════════════════════════
 Step 3: FEED-FORWARD NETWORK
 ════════════════════════════════════
         │ + Residual → LayerNorm
         ▼
 Linear(d_model → vocab_size) + Softmax
         │
 P(next LaTeX token) over whole vocabulary
```

---

## H.4 SymPy — Computer Algebra System

### H.4.1 Symbolic vs Numeric Computation

**Numeric computation:** `1/3 = 0.3333...` (floating point, approximate, has precision errors)

**Symbolic computation:** `1/3 = Rational(1, 3)` (exact fraction, can be manipulated algebraically)

SymPy represents mathematics exactly. `sp.sqrt(2) = √2` (symbolic), not `1.41421356...` (numeric). This allows exact algebraic manipulation:

```python
import sympy as sp
x = sp.Symbol('x')
expr = sp.expand((x + 1)**2)
# Result: x**2 + 2*x + 1   (exact, symbolic)

sp.simplify(expr - x**2 - 2*x - 1)
# Result: 0   (exactly zero, not 0.0000000001 from floating point)
```

This exactness is why SymPy can definitively prove mathematical equivalence — numeric methods would only check approximate equality.

### H.4.2 Expression Trees — Abstract Syntax Trees

Every SymPy expression is internally stored as a **tree** where:
- Leaf nodes are atoms (symbols, numbers)
- Internal nodes are operations (Add, Mul, Pow, Function, etc.)

```
Expression: (a + b) ** 2

Tree:
     Pow
    /   \
  Add    2
 /   \
a     b

Python: sp.Pow(sp.Add(a, b), 2)
```

**Simplification = tree transformation:**
```
Pow(Add(a,b), 2)
  → expand → Add(Mul(a,a), Mul(2,Mul(a,b)), Mul(b,b))
             = a² + 2ab + b²
```

Trees can be traversed, matched, and rewritten by applying algebraic identities.

### H.4.3 Core SymPy Classes

| SymPy Class | Mathematical concept | Example |
|---|---|---|
| `Symbol('x')` | Variable (unknown) | `x`, `y`, `E`, `m`, `c` |
| `Integer(3)` | Exact integer | `3`, `-5` |
| `Rational(1,3)` | Exact fraction | `1/3`, `p/q` |
| `Float('3.14')` | Floating-point (careful!) | `3.14` |
| `Add(a,b)` | Sum a+b | `x + y + 2` |
| `Mul(a,b)` | Product a×b | `3*x*y` |
| `Pow(b,e)` | Power b^e | `x**2`, `e**x` |
| `sin(x)`, `cos(x)` | Trig functions | standard functions |
| `E` | Euler's number e ≈ 2.718 | `sp.E` |
| `pi` | π ≈ 3.14159 | `sp.pi` |
| `Eq(lhs, rhs)` | Equation lhs = rhs | `Eq(E, m*c**2)` |
| `Equality` | Same as Eq | |

**Automatic simplification happens inline:** `sp.Integer(2) + sp.Integer(3)` immediately gives `sp.Integer(5)`, not `Add(2,3)`.

### H.4.4 The ANTLR4 Parser and Formal Grammar

SymPy's `parse_latex()` function uses **ANTLR4** — a parser generator framework — to parse LaTeX strings into SymPy expression trees.

**What is a formal grammar?** A grammar defines the legal structure of a language. For LaTeX math:
```
expression := term (('+' | '-') term)*
term       := factor (('*' | '/') factor)*
factor     := atom ('^' atom)?
atom       := NUMBER | SYMBOL | '(' expression ')' | FUNCTION '{' expression '}'
FUNCTION   := '\frac' | '\sqrt' | '\sin' | ...
```

ANTLR4 generates a parser from this grammar that:
1. **Tokenizes** the LaTeX string: `"\frac{1}{2}"` → `[FRAC, LBRACE, 1, RBRACE, LBRACE, 2, RBRACE]`
2. **Parses** the token sequence: `FRAC(1, 2)` → `Rational(1,2)`
3. **Builds AST**: SymPy expression tree

### H.4.5 LaTeX → SymPy Conversion

```python
from sympy.parsing.latex import parse_latex

parse_latex(r"\frac{1}{2}mv^2")
# → Mul(Rational(1,2), m, Pow(v, 2))
# → ½mv²

parse_latex(r"E = mc^2")
# → Eq(E, Mul(m, Pow(c, 2)))
# → E = mc²

parse_latex(r"\sin^2\theta + \cos^2\theta")
# → Add(Pow(sin(theta), 2), Pow(cos(theta), 2))
# → sin²θ + cos²θ
```

The manual converter `_latexish_to_sympy()` in the code handles cases where `parse_latex` fails:
```
\frac{a}{b} → (a)/(b)       (replace with division)
\sqrt{x}    → sqrt(x)       (Python function)
^           → **            (Python exponentiation)
\times      → *             (multiplication)
\cdot       → *
```

---

## H.5 Formula Equivalence Checking

### H.5.1 Method 1: Algebraic Simplification

```python
sp.simplify(expr_a - expr_b) == 0
```

**`sp.simplify`** applies a cascade of simplification algorithms:

1. **Rational simplification**: Cancel common factors in fractions.
   - `(a²-b²)/(a-b)` → `a+b`

2. **Polynomial normal form**: Expand everything, collect like terms.
   - `(x+1)² - x² - 2x` → `x²+2x+1 - x² - 2x` → `1` (not 0, so not equivalent)

3. **Trigonometric simplification** (`trigsimp`):
   - `sin²(x) + cos²(x)` → `1`
   - `2sin(x)cos(x)` → `sin(2x)`

4. **Exponential/logarithm simplification** (`logcombine`):
   - `log(a) + log(b)` → `log(ab)`

5. **Groebner bases** (for complex polynomial systems):
   Checks polynomial equivalence via algebraic elimination.

**The `== 0` check:** In SymPy, `expr == 0` checks symbolic identity (the expression is the zero expression), not numeric floating-point equality. `sp.simplify(x + 1 - x - 1) == 0` → `True` because simplification produces `sp.Integer(0)` which symbolically equals 0.

### H.5.2 Simplification Algorithms: Expand, Factor, Trigsimp

**`sp.expand`**: Distributes multiplication over addition.
```python
sp.expand((x + 1)**3)
# → x³ + 3x² + 3x + 1
```

**`sp.factor`**: Factors polynomials into irreducible factors.
```python
sp.factor(x**2 - 1)
# → (x-1)(x+1)
```

**`sp.trigsimp`**: Applies trig identities.
```python
sp.trigsimp(sp.sin(x)**2 + sp.cos(x)**2)
# → 1
```

**`sp.cancel`**: Cancels common factors in rational expressions.
```python
sp.cancel((x**2 - 1) / (x - 1))
# → x + 1
```

`sp.simplify` tries all of the above and picks the simplest result.

### H.5.3 Method 2: Numerical Equality — `.equals()`

```python
expr_a.equals(expr_b)
```

This method **substitutes random numerical values** for all symbols and checks if both expressions produce the same result:

```python
# Internal logic (conceptual):
test_values = {sym: random.uniform(-5, 5) for sym in expr_a.free_symbols}
n_tests = 5
for _ in range(n_tests):
    a_val = complex(expr_a.subs(test_values).evalf())   # evaluate numerically
    b_val = complex(expr_b.subs(test_values).evalf())
    if abs(a_val - b_val) > 1e-6:                       # not equal
        return False
return True
```

**When used:** For transcendental expressions (involving sin, cos, exp, log) that algebraic simplification can't easily handle:
```
sin(2x) == 2*sin(x)*cos(x)?
```
Algebraic simplification might struggle, but numerical evaluation easily confirms equality.

**Risk:** Accidentally equal at test points (false positive). Multiple random test points reduce this risk. Mathematically pathological cases exist (Risch decision procedure needed for provably correct answer), but rare in practice for student formulas.

### H.5.4 Method 3: SequenceMatcher — Ratcliff/Obershelp Algorithm

When SymPy parsing fails (e.g., formula contains undefined symbols or unusual LaTeX commands), the code falls back to string similarity:

```python
from difflib import SequenceMatcher
ratio = SequenceMatcher(None, ideal_norm, student_norm).ratio()
```

**Ratcliff/Obershelp Algorithm:**
1. Find the **longest common substring** (LCS) of both strings.
2. Recursively apply to the portions before and after the LCS match.
3. Keep counting matched characters until all sub-problems are empty.
4. Final ratio = `2 × total_matched / (len(s1) + len(s2))`

**Example:**
```
ideal:   "E=mc^{2}"   (normalized, 8 chars)
student: "E=mc^2"     (normalized, 6 chars)

LCS: "E=mc^" (5 chars)
  Remaining: "{2}" vs "2"
  LCS of "{2}" and "2": "2" (1 char)
    Remaining: "{" vs "" → 0 chars
    Remaining: "}" vs "" → 0 chars

Total matched: 5 + 1 = 6
Ratio: 2×6 / (8+6) = 12/14 = 0.857
```

0.857 is high → these formulas are very similar string-wise.

### H.5.5 Score Mapping Table

| Condition | Formula score fraction |
|---|---|
| SymPy: `simplify(A-B)==0` | 1.0 (perfect) |
| SymPy: `A.equals(B)` | 1.0 (perfect) |
| String ratio ≥ 0.90 | 0.8 (very close) |
| String ratio ≥ 0.75 | 0.6 (partial) |
| String ratio ≥ 0.55 | 0.35 (partly right) |
| String ratio < 0.55 | 0.0 (wrong) |

---

---

# PART I — DIAGRAM EXTRACTION

---

## I.1 Digital Images as Data Structures

### I.1.1 Grayscale Images: 2D Matrices

A grayscale image is a 2D array (matrix) of integers:
```
image ∈ ℤ^{H×W}      where each element ∈ {0, 1, 2, ..., 255}

0   = no light = black
255 = maximum light = white
128 = 50% gray
```

For a 300 DPI A4 page (297mm × 210mm):
```
H = 297mm × (300 pixels/25.4mm) = 3508 pixels
W = 210mm × (300 pixels/25.4mm) = 2480 pixels
Total pixels = 3508 × 2480 = 8,699,840 ≈ 8.7 megapixels
Array size = 8.7M × 1 byte = 8.7 MB
```

### I.1.2 Color Images: 3D Tensors (H×W×C)

A color image has C=3 channels (Red, Green, Blue), each a grayscale matrix:
```
image ∈ ℤ^{H×W×3}

image[:,:,0] → Red channel   (all pixel's red intensities)
image[:,:,1] → Green channel
image[:,:,2] → Blue channel

Pixel (i,j) color = (image[i,j,0], image[i,j,1], image[i,j,2])
                  = (R, G, B) where each ∈ {0,...,255}

Examples:
  (255, 0, 0) = pure red
  (0, 255, 0) = pure green
  (0, 0, 255) = pure blue
  (255, 255, 255) = white
  (0, 0, 0) = black
  (100, 100, 100) = gray
```

### I.1.3 BGR vs RGB: OpenCV Convention

**OpenCV** (`cv2`) loads and stores images in **BGR** (Blue-Green-Red) order — the reverse of the standard **RGB** (Red-Green-Blue) order. This is a historical artifact from early video processing hardware.

```python
img_bgr = cv2.imread("image.png")    # BGR: (B, G, R)
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)   # convert to RGB

# Access pixel at (row=10, col=20):
img_bgr[10, 20] = [B, G, R]   # OpenCV order
img_rgb[10, 20] = [R, G, B]   # standard order
```

**PIL/Pillow** uses RGB order. When converting between OpenCV and PIL:
```python
pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
```

The CLIP processor expects RGB images, hence the conversion in `DiagramSimilarityModel.similarity()`.

### I.1.4 Bit Depth and Pixel Value Range

**8-bit grayscale:** 2⁸ = 256 values (0–255). Standard for most images. Each pixel = 1 byte.

**16-bit grayscale:** 2¹⁶ = 65,536 values. Used for medical imaging (CT scans, microscopy) where fine gray-level distinction matters. Not used in this project.

**1-bit (binary):** Only 0 or 1. Smallest possible. Used after thresholding in this project — each pixel is either ink (1) or background (0).

---

## I.2 Image Binarization — Thresholding

### I.2.1 What is Thresholding?

Thresholding converts a grayscale image (0–255 per pixel) into a binary image (0 or 255 per pixel) by applying a threshold T:

```
Threshold T:
  if pixel_value < T:  output = 255  (or 0, depending on type)
  if pixel_value > T:  output = 0    (or 255)
```

**Purpose:** Separate foreground (ink) from background (paper) to get a clean black-and-white image where we can confidently say "this pixel is ink, that pixel is background."

### I.2.2 Binary Inverse Threshold — Used in Project

```python
_, ink_mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)
```

**`cv2.THRESH_BINARY_INV`**: inverted binary threshold.
```
For each pixel (i,j):
  if gray[i,j] <= 245:
    ink_mask[i,j] = 255   (ink pixel → white in mask)
  else:
    ink_mask[i,j] = 0     (background pixel → black in mask)
```

**Why "inverted"?** We want ink pixels to be "active" (white = 1 in the binary mask). Paper is bright (gray value ~250), ink is dark (gray value ~30). Inverting makes ink=white, paper=black.

### I.2.3 Why Threshold at 245?

On a well-scanned white A4 paper:
- Pure white paper background: gray ≈ 250–255
- Yellowish/aged paper: gray ≈ 230–250
- Very faint pencil: gray ≈ 200–240
- Normal pencil: gray ≈ 100–200
- Dark pen: gray ≈ 20–100

By thresholding at 245:
- Everything darker than 245 (= any marks, even faint pencil) → ink = 255 in mask
- Only truly white background (245–255) → background = 0

If we used 128 (midpoint), we'd miss faint pencil marks (gray 100–180 would pass, but faint 200–240 might not). 245 is more inclusive of faint marks.

**Tradeoff:** Too high (e.g., 254) → captures noise, paper texture → many false ink pixels. Too low (e.g., 180) → misses faint marks → diagram fragments. 245 is empirically good for standard 300 DPI A4 scans.

### I.2.4 Otsu's Method — Automatic Threshold Selection

Otsu's method (Nobuyuki Otsu, 1979) automatically finds the optimal threshold by maximizing **inter-class variance** (also equivalent to minimizing intra-class variance):

**The idea:** A good threshold separates pixels into two classes (background and ink) such that the two classes are as different as possible from each other, and as similar as possible within themselves.

**Mathematical derivation:**

For a threshold t, define:
```
w₀(t) = probability of class 0 (background, pixel value ≤ t) = Σ_{i=0}^{t} h[i]
w₁(t) = probability of class 1 (ink, pixel value > t) = Σ_{i=t+1}^{255} h[i]

where h[i] = normalized histogram: h[i] = count(pixels with value i) / total_pixels

μ₀(t) = mean value of class 0 = (Σ_{i=0}^{t} i×h[i]) / w₀(t)
μ₁(t) = mean value of class 1 = (Σ_{i=t+1}^{255} i×h[i]) / w₁(t)

μ_total = w₀(t)×μ₀(t) + w₁(t)×μ₁(t)    (total mean, constant for all t)
```

**Between-class variance** (what Otsu maximizes):
```
σ²_B(t) = w₀(t) × w₁(t) × (μ₀(t) - μ₁(t))²
           ↑ weights ↑       ↑ class separation ↑
```

**Algorithm:** Compute `σ²_B(t)` for all t ∈ {0,...,255} (from histogram, O(256) time), pick t* = argmax.

**Why not in this project:** Fixed threshold 245 is simpler and works for consistent scan quality. Otsu would be better for variable-quality scans.

### I.2.5 Adaptive Thresholding (Alternative)

For non-uniform illumination (shadows, uneven scanner light), a global threshold fails — the same shadow region might need threshold 150 while a bright region needs threshold 245.

**Adaptive thresholding** computes a local threshold for each pixel based on its neighborhood:
```
T(i,j) = mean(neighborhood(i,j)) - C    (adaptive mean)
or
T(i,j) = Gaussian_weighted_mean(neighborhood) - C
```

The neighborhood is typically a 11×11 or 31×31 window. C is a small constant (e.g., 5).

Not used in this project (assuming uniform scan quality), but worth knowing.

---

## I.3 Morphological Image Processing

### I.3.1 Structuring Elements

A **structuring element** (SE) B is a small binary pattern (usually 3×3 or 5×5) that defines the neighborhood for morphological operations:

```
3×3 square (flat):
B = [[1,1,1],
     [1,1,1],    ← 1 = part of SE, 0 = not part
     [1,1,1]]

3×3 cross:
B = [[0,1,0],
     [1,1,1],
     [0,1,0]]

5×5 circle:
B = [[0,0,1,0,0],
     [0,1,1,1,0],
     [1,1,1,1,1],
     [0,1,1,1,0],
     [0,0,1,0,0]]
```

The project uses: `kernel = np.ones((3,3), np.uint8)` — a 3×3 all-ones (flat square) SE.

### I.3.2 Dilation — Set Theory Definition and Visual Effect

**Set theory definition:** Let A = set of foreground (ink) pixels, B = structuring element.

```
Dilation:  A ⊕ B = { z : (B)_z ∩ A ≠ ∅ }

"z is in the dilation if, when we place B centered at z, at least one part of B overlaps with A"
```

Equivalently: shift B to be centered at each point in A, and add all covered positions to the output.

**Visual effect:** A grows outward by the shape of B.
```
Before dilation (3×3 square SE, 1-pixel gap):
  0 0 0 0 0 0 0 0
  0 1 1 1 0 1 1 0   ← gap between the two blobs
  0 1 1 1 0 1 1 0
  0 1 1 1 0 1 1 0
  0 0 0 0 0 0 0 0

After dilation:
  0 1 1 1 1 1 1 0
  1 1 1 1 1 1 1 1   ← gap filled! blobs merged
  1 1 1 1 1 1 1 1
  1 1 1 1 1 1 1 1
  0 1 1 1 1 1 1 0
```

### I.3.3 Erosion — Set Theory Definition and Visual Effect

```
Erosion:  A ⊖ B = { z : B_z ⊆ A }

"z is in the erosion if, when we place B centered at z, B fits completely inside A"
```

**Visual effect:** A shrinks inward by the shape of B. Small protruding parts that B can't fit inside are removed.

```
Before erosion:
  1 1 1 1 1 1   (blob width=6)
  1 1 1 1 1 1
  
After erosion (3×3 SE):
  0 1 1 1 1 0   (width reduced by 1 on each side = 4)
  0 1 1 1 1 0
```

### I.3.4 Opening vs Closing — Which One and Why?

**Opening = Erosion then Dilation:**
```
A ∘ B = (A ⊖ B) ⊕ B
```
Effect: **removes small objects** (smaller than B). Large objects survive erosion and are restored by dilation.

**Closing = Dilation then Erosion:**
```
A • B = (A ⊕ B) ⊖ B
```
Effect: **fills small holes and gaps** (smaller than B). External boundaries are restored after dilation by erosion.

**The project uses Closing** (`cv2.MORPH_CLOSE`): fills small breaks in pencil/pen strokes so the diagram is treated as one connected region, not fragmented pieces.

**Why not Opening?** Opening would remove small isolated marks — but we want to keep ALL ink, even isolated points (which might be dots marking important positions in diagrams).

### I.3.5 Morphological Closing in the Project

```python
kernel = np.ones((3, 3), np.uint8)    # 3×3 flat square structuring element
closed = cv2.morphologyEx(ink_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
```

**With `iterations=1`:** Apply the closing once (dilation + erosion once each).

**Effect on answer sheets:** A hand-drawn resistor symbol typically drawn with a pen might have tiny 1–2 pixel breaks where the pen lifted slightly. These breaks would wrongly split the symbol into multiple connected components. Closing fills these gaps, keeping the symbol as one component.

**Scale of effect:** A 3×3 SE fills gaps up to ~2 pixels wide. For larger gaps, you'd need a larger kernel (5×5 fills ~4-pixel gaps). The 3×3 is appropriate for minor pen gaps without merging genuinely separate elements.

---

## I.4 Connected Components Analysis

### I.4.1 Graphs — Formal Definition

A **graph** G = (V, E) consists of:
- **V** (Vertices / Nodes): a set of objects
- **E** (Edges): pairs of vertices representing connections

**Undirected graph**: edges have no direction — (u,v) = (v,u).
**Unweighted graph**: edges have no numeric weight.

For our image: V = all foreground pixels, E = pairs of adjacent pixels.

### I.4.2 Connectivity: 4-connectivity vs 8-connectivity

**4-connectivity:** A pixel is connected to 4 neighbors (up, down, left, right):
```
  □ ■ □
  ■ X ■   ← X is 4-connected to the 4 highlighted ■ neighbors
  □ ■ □
```

**8-connectivity:** A pixel is connected to 8 neighbors (including diagonals):
```
  ■ ■ ■
  ■ X ■   ← X is 8-connected to all 8 surrounding ■ neighbors
  ■ ■ ■
```

**The project uses 8-connectivity** (`connectivity=8`): diagonal connections are recognized. This is more appropriate for hand-drawn diagrams where diagonal strokes should connect to adjacent pixels.

### I.4.3 Connected Component — Formal Definition

A **connected component** is a **maximal connected subgraph** of G:
- **Connected**: there exists a path (sequence of edges) between every pair of vertices in the component.
- **Maximal**: you cannot add any more vertices while maintaining connectivity (each component is as large as possible).

In image terms: a connected component is a group of ink pixels where you can travel from any pixel to any other pixel by stepping through adjacent (8-directionally) ink pixels, and no ink pixel adjacent to the group is excluded.

```
Binary image (■=ink, □=background):
  □ □ □ □ □ □ □ □
  □ ■ ■ ■ □ ■ ■ □    ← Two separate components
  □ ■ □ ■ □ □ ■ □
  □ ■ ■ ■ □ □ □ □
  □ □ □ □ □ □ □ □

Component 1: {(1,1),(1,2),(1,3),(2,1),(2,3),(3,1),(3,2),(3,3)}  (the left blob, 8 pixels)
Component 2: {(1,5),(1,6),(2,6)}                                  (the right small shape, 3 pixels)
```

### I.4.4 BFS Algorithm — Step-by-Step with Pseudocode

**BFS (Breadth-First Search)** explores all pixels at distance k from the start before exploring distance k+1 — it expands in a "wave" pattern.

```
Algorithm: Connected_Components_BFS(binary_image)

label = 0
label_map = all zeros (same size as image)

For each pixel (r,c) in raster scan order:
  If binary_image[r,c] == 1 AND label_map[r,c] == 0:
    # Unvisited foreground pixel → start new component
    label += 1
    queue = [(r,c)]
    label_map[r,c] = label
    
    While queue is not empty:
      (y,x) = queue.dequeue()    (FIFO — BFS)
      
      For each neighbor (ny,nx) in 8-neighbors(y,x):
        If binary_image[ny,nx] == 1 AND label_map[ny,nx] == 0:
          label_map[ny,nx] = label
          queue.enqueue((ny,nx))
    # End: all pixels in this component have label
    
Return label_map, label (total count)
```

**Time complexity:** O(H × W) — each pixel is visited at most once.

### I.4.5 Two-Pass Labelling Algorithm

OpenCV uses a more efficient **two-pass algorithm** that avoids the queue entirely:

**Pass 1 (left-to-right, top-to-bottom):**
```
For each pixel (r,c):
  If foreground:
    neighbors = already-labeled 8-neighbors of (r,c) (only top & left half)
    If no neighbors: assign new label L
    Else if all same label L: assign L
    Else (multiple different labels): assign min label, record equivalences
```

**Pass 2 (resolve equivalences):**
```
Apply Union-Find to collapse equivalent labels
(all pixels that should be the same component get the same final label)
```

**Why faster?** Avoids the overhead of a queue data structure; works with sequential memory access patterns (cache-friendly).

### I.4.6 Union-Find Data Structure — Path Compression

**Union-Find** (also called Disjoint Set Union / DSU) manages a collection of disjoint sets with two operations:
- **Find(x)**: returns the representative (root) of the set containing x
- **Union(x, y)**: merges the sets containing x and y

**Naive implementation:** O(N) per Find (walk up a chain of parents). 

**With Path Compression:** During Find, make every node on the path directly point to the root:
```
Find(x):
  if parent[x] != x:
    parent[x] = Find(parent[x])   ← path compression!
  return parent[x]

Union(x, y):
  rx = Find(x), ry = Find(y)
  if rx == ry: return   (already same set)
  parent[ry] = rx       (merge: make ry's root point to rx)
```

**With Union by Rank + Path Compression:** amortized O(α(N)) ≈ O(1) per operation, where α is the inverse Ackermann function (grows so slowly it's effectively constant for all practical N).

**In connected components:** each label is a set; Union is called when two neighboring pixels have different provisional labels (they should be the same component); Find resolves what the final label is.

### I.4.7 Stats Array: Area, Bounding Box, Centroid

```python
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
    ink_mask, connectivity=8
)
```

**Return values:**
- `num_labels` (int): total number of components including background (label 0)
- `labels` (H×W int array): label map — `labels[r,c]` is the component index for pixel (r,c)
- `stats` (num_labels × 5 array): for each component: `[left, top, width, height, area]`
  - `left` (x): leftmost x-coordinate of bounding box
  - `top` (y): topmost y-coordinate of bounding box
  - `width`, `height`: bounding box dimensions
  - `area`: count of pixels in component (not bounding box area!)
- `centroids` (num_labels × 2 array): `[cx, cy]` — center of mass of each component

**Label 0** is always the background (all non-foreground pixels). Real components start at label 1.

### I.4.8 Area Filtering: Why 0.3% of Page Area?

```python
page_area = H × W    # e.g., 3508 × 2480 = 8,699,840 pixels
min_area = 0.003 × page_area    # = 26,100 pixels

if stats[label, cv2.CC_STAT_AREA] < min_area:
    continue   # skip this component (too small = noise or individual character)
```

**Why 0.3%?**
- A typical handwritten character on a 300 DPI A4 page: ~6mm tall, ~4mm wide. In pixels: 71px × 47px = 3,337 pixels = 0.038% of page. Much smaller than 0.3%.
- A typical diagram (e.g., resistor symbol): ~30mm × 20mm → 354px × 236px = 83,544 pixels = 0.96% of page. Well above 0.3%.

So 0.3% comfortably separates individual characters from diagrams, with a good safety margin.

**Why not 1% or 5%?** A small but significant diagram element (e.g., an arrow or label box) might only be 0.5% of page area. Setting min_area too high would miss these. 0.3% preserves multi-component diagrams where each element is independently filtered.

### I.4.9 Position Filtering: Why 45% Height?

```python
cy = centroids[label, 1]    # y-coordinate of centroid (0=top, H=bottom)
if cy < 0.45 * H:
    continue   # centroid in top 45% of page → skip (likely text)
```

**Rationale:**
In standard Indian engineering/science exam answer sheets:
- **Top ~40%**: written answer text (paragraphs, definitions, derivations)
- **Bottom ~60%**: diagrams, figures, circuit drawings

Students typically write text first, then draw the diagram below. The 0.45 (45%) threshold ensures we capture diagrams that might appear in the upper part of the "diagram zone" (which starts at ~40% of page height) with a 5% safety margin.

**Limitation acknowledged:** This fails if students draw a diagram in the middle of their text. A more robust system would use layout analysis to find diagram regions regardless of position. This heuristic works typically for structured answer booklets.

---

---

# PART J — SCORING, LLM EVALUATION, AND SYSTEM

---

## J.1 The Rubric System

### J.1.1 Max Marks and Per-Question Configuration

The `rubric.json` file defines evaluation parameters per question/page:

```json
{
  "1": {
    "max_marks": 10,
    "text_weight": 0.6,
    "diagram_weight": 0.4,
    "formula_weight": 0.2,
    "penalize_missing_diagram": true,
    "penalize_missing_formula": false
  },
  "2": {
    "max_marks": 5,
    "text_weight": 1.0,
    "diagram_weight": 0.0,
    "formula_weight": 0.0,
    "penalize_missing_diagram": false,
    "penalize_missing_formula": false
  }
}
```

The key `"1"` maps to page 1 (first question). Questions with no diagram or formula simply set those weights to 0.

### J.1.2 Weight Normalization — Full Formula

Raw weights `w_t, w_d, w_f` are normalized so they sum to 1:

```
Step 1: Adjust for missing components
  if ideal has no diagram:   w_d = 0
  if ideal has no formula:   w_f = 0 (or keep it — both options exist)
  if student has no diagram AND penalize_missing is True:  keep w_d (student gets 0)
  if student has no diagram AND penalize_missing is False: set w_d = 0 (redistribute)

Step 2: Normalize
  total_w = w_t + w_d + w_f
  w_t_norm = w_t / total_w
  w_d_norm = w_d / total_w
  w_f_norm = w_f / total_w

  (w_t_norm + w_d_norm + w_f_norm = 1.0 always)
```

**Example:** Question 1: text=0.6, diagram=0.4, formula=0.2, total=1.2
```
w_t_norm = 0.6/1.2 = 0.500
w_d_norm = 0.4/1.2 = 0.333
w_f_norm = 0.2/1.2 = 0.167
Sum: 0.500 + 0.333 + 0.167 = 1.000 ✓
```

### J.1.3 Missing Components — Penalty vs Redistribution

**Case A: Student doesn't draw a diagram, `penalize_missing_diagram: true`**
```
w_d is NOT zeroed out → w_d_norm = 0.333 (as above)
diagram_fraction = 0.0 (no diagram → no similarity)
contribution: 0.0 × 0.333 = 0.0
Student loses 0.333 × max_marks = 3.33 marks for not drawing the diagram
```

**Case B: Student doesn't draw a diagram, `penalize_missing_diagram: false`**
```
w_d IS zeroed out → redistribute to remaining modalities
new weights: text=0.6, diagram=0, formula=0.2, total=0.8
w_t_norm = 0.6/0.8 = 0.75
w_f_norm = 0.2/0.8 = 0.25
No marks are "wasted" — text and formula get more weight
```

**Which to use?** For questions explicitly requiring a diagram (marked in the rubric), penalty mode is appropriate. For optional diagrams or when it's unclear, redistribution is fairer.

### J.1.4 Complete Scoring Walk-through with Numbers

**Setup:**
- Question 1, max_marks = 10
- Weights: text=0.6, diagram=0.4, formula=0.2 → normalized: 0.5, 0.333, 0.167
- Student has both text, diagram, and formula

**Similarity scores:**
- SBERT cosine similarity: 0.78
  - text_fraction = max(0, (0.78 - 0.6)/0.4) = max(0, 0.18/0.4) = max(0, 0.45) = 0.45
- CLIP cosine similarity: 0.75
  - diagram_fraction = min(1.0, 0.75 × 1.2) = min(1.0, 0.90) = 0.90
- SymPy: equivalent formula
  - formula_fraction = 1.0

**Final score:**
```
weighted_sum = 0.45 × 0.500 + 0.90 × 0.333 + 1.0 × 0.167
             = 0.225        + 0.300        + 0.167
             = 0.692

score = 0.692 × 10 = 6.92 / 10
```

---

## J.2 Gemini 2.5 Flash — Multimodal LLM

### J.2.1 Foundation Models vs Specialized Models

**Specialized model:** Trained for one task.
- SBERT: only sentence similarity
- CLIP: only image-text matching
- pix2tex: only formula recognition

A **foundation model** (also called large language model / LLM): trained on diverse data across many tasks, capable of many things.

- GPT-4: text understanding, generation, reasoning, code
- Gemini 2.5: text, images, video, audio, code — all in one model

Foundation models achieve this by training on **internet-scale** data (trillions of text tokens, billions of images) with a single unified architecture (transformer), letting the model learn task-agnostic representations.

### J.2.2 Decoder-Only Transformers (GPT Architecture)

Gemini uses a **decoder-only** transformer (like GPT), in contrast to BERT which is **encoder-only**.

| Encoder-only (BERT) | Decoder-only (GPT/Gemini) |
|---|---|
| Full self-attention (all positions → all) | Causal self-attention (each position → only past) |
| Produces representations of input | Generates output text autoregressively |
| Used for: classification, similarity | Used for: text generation, chat, reasoning |

In a decoder-only transformer:
- Attention is **causal (masked)**: position t can only attend to positions 1...t
- This allows autoregressive generation: generate token t using context 1...t-1

### J.2.3 Autoregressive Text Generation

```
Prompt: "Grade this answer: [ideal_text]... [student_text]... Return JSON:"
         ↓
Gemini processes all prompt tokens, generates one token at a time:

Step 1: P(token | prompt) → "{" (27% probability, highest → output "{")
Step 2: P(token | prompt + "{") → '"' (token "quote", highest)
Step 3: P(token | prompt + '{"') → 't' → ... → "text_score"
...
Until: "}" is generated (end of JSON)

Full output: {"text_score": 7, "diagram_score": 3, "score": 8.5, "feedback": "Good explanation of Ohm's Law but missing derivation."}
```

### J.2.4 RLHF: Reinforcement Learning from Human Feedback

**Problem:** Training a model on text prediction makes it good at generating plausible text — but not necessarily helpful, harmless, or honest text.

**RLHF** is a post-training technique (after regular supervised training) that aligns the model with human values:

1. **Supervised Fine-Tuning (SFT):** Train on human-written examples of good responses.

2. **Reward Model Training:** Show humans pairs of model responses. Humans rank which is better. Train a **reward model** to predict human preference scores.

3. **RL Fine-tuning:** Use the reward model as a reward signal in Reinforcement Learning (typically PPO — Proximal Policy Optimization). The LLM is the "policy"; it generates text; the reward model evaluates it; RL updates the LLM to generate higher-reward text.

**Result:** A model that follows instructions, gives helpful responses, and is less likely to produce harmful content. This is why Gemini reliably follows the JSON output instruction in our grading prompt.

### J.2.5 Multimodal Input: Text + Image Tokens

Gemini accepts "parts" — a list of mixed text strings and PIL images:

```python
parts = [prompt_string, ideal_diagram_PIL, student_diagram_PIL]
response = model.generate_content(parts)
```

**Internally:** Each PIL image is passed through a Vision Encoder (similar to ViT) to produce a sequence of visual tokens. These tokens are interleaved with text tokens in the full context:

```
[text token]×N_prompt  [visual token]×N_image1  [visual token]×N_image2
```

The decoder transformer processes ALL tokens together — every text token can attend to every image token and vice versa. This allows Gemini to say "the student's diagram (image 2) is missing the arrow that exists in the ideal (image 1)."

### J.2.6 Prompt Engineering and JSON Output

The system prompt is carefully engineered:

```
You are an expert professor grading a student's answer.

Maximum marks: {max_marks}
Text component max: {text_max}
Diagram component max: {diagram_max}

IDEAL ANSWER (text):
{ideal_text}

STUDENT ANSWER (text):
{student_text}

[ideal diagram image]
[student diagram image]

Grade strictly and fairly. Return ONLY valid JSON:
{{"text_score": <0 to {text_max}>, "diagram_score": <0 to {diagram_max}>, "score": <0 to {max_marks}>, "feedback": "<brief feedback>"}}
```

**Engineering choices:**
- "Return ONLY valid JSON": reduces probability of preamble text before the JSON.
- Double braces `{{` and `}}` in Python f-strings: escape literal `{` and `}` (Python f-strings use single braces for variables).
- Giving exact ranges: prevents out-of-range scores. Gemini still might generate slightly invalid scores → clamping in code.

### J.2.7 Parsing the JSON Response Robustly

Sometimes Gemini adds text before or after the JSON:
```
"Here is my evaluation:\n{\"text_score\": 7, ...}\n\nI hope this helps."
```

Robust parsing:
```python
raw_text = response.text

# Find outermost JSON object:
start = raw_text.find("{")
end   = raw_text.rfind("}")

if start == -1 or end == -1 or start >= end:
    raise ValueError("No JSON found in response")

json_str = raw_text[start:end+1]
data = json.loads(json_str)

# Clamp to valid range:
text_score  = max(0, min(text_max,    data.get("text_score", 0)))
diag_score  = max(0, min(diagram_max, data.get("diagram_score", 0)))
total_score = max(0, min(max_marks,   data.get("score", 0)))
feedback    = data.get("feedback", "No feedback provided")
```

`rfind` finds the LAST `}` — handles nested JSON (if Gemini outputs nested JSON for some reason, `rfind` gets the outer closing brace).

### J.2.8 SBERT+CLIP vs Gemini: Trade-offs

| Aspect | SBERT + CLIP + SymPy | Gemini LLM |
|---|---|---|
| **Speed** | 5–30 seconds total | 10–60 seconds (API latency) |
| **Cost** | Free (local GPU) | ~$0.001–0.01 per grading |
| **Privacy** | All local | Student data sent to Google |
| **Explainability** | Numbers (similarity %) | Natural language feedback |
| **Formula math** | Exact (SymPy) | Qualitative only |
| **Reasoning** | No (pattern matching) | Yes (concept coverage) |
| **Internet needed** | Only for cloud OCR | Always |
| **Consistency** | Deterministic | Slight randomness (temperature > 0) |
| **Error mode** | Fails on unusual answers | Can confabulate (hallucinate) |

**When to use Gemini:** When detailed feedback is needed, or SBERT similarity is borderline (e.g., student's answer is correct but uses very different terminology from the ideal answer).

---

## J.3 FastAPI Backend

### J.3.1 WSGI vs ASGI

**WSGI (Web Server Gateway Interface):** Traditional synchronous Python web interface. Each HTTP request blocks a thread until the response is ready. Under high concurrency (many simultaneous requests), runs out of threads → requests queue up → timeouts.

**ASGI (Asynchronous Server Gateway Interface):** Async interface supporting concurrent I/O. Event-loop based: when one request is waiting for I/O (file read, API call, database query), the event loop switches to handling another request. Much higher concurrency with fewer threads.

**FastAPI is ASGI-based**, running on `uvicorn` (ASGI server). Even when the grading pipeline is running in a background thread, uvicorn continues serving other HTTP requests (status polls, downloads).

### J.3.2 How FastAPI Works

FastAPI uses Python **type hints** to automatically:
1. Validate request data (Pydantic models)
2. Generate API documentation (Swagger UI at /docs)
3. Create OpenAPI schema

```python
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()

class JobStatus(BaseModel):
    run_id: str
    status: str    # "queued" | "running" | "completed" | "failed"
    progress_percent: int
    message: str

@app.post("/api/jobs", response_model=JobStatus)
async def create_job(
    ideal_pdf: UploadFile = File(...),         # required file upload
    student_pdfs: list[UploadFile] = File(...), # multiple files
    rubric: UploadFile = File(...)
) -> JobStatus:
    # FastAPI automatically validates: ideal_pdf is an UploadFile with PDF content
    # Saves files, creates job, returns immediately
    ...
```

### J.3.3 Async Job Architecture

**The problem:** A full grading run (OCR + evaluation for 10 students) may take 3–10 minutes. HTTP connections time out after ~60 seconds. We cannot block the HTTP response while running the pipeline.

**Solution:** The job creation endpoint (`POST /api/jobs`) immediately returns a `run_id`, then the pipeline runs in a background thread. The frontend polls `GET /api/jobs/{run_id}` every few seconds.

```
Time:  0s    2s     60s    180s    370s
       │      │      │      │       │
POST ──┘      │      │      │       │  (immediate response, run_id returned)
              │ poll │      │       │
GET ──────────┘      │      │       │  (status: "running", progress: 15%)
                     │ poll │       │
GET ──────────────────┘      │       │  (status: "running", progress: 60%)
                             │ poll  │
GET ──────────────────────────┘       │  (status: "completed", reports: [...])
                                      │
[download report PDFs]
```

**Background thread:**
```python
import threading

def _run_pipeline_in_background(run_id, ...):
    try:
        with PIPELINE_RUN_LOCK:     # ensures only one pipeline at a time
            _update_status(run_id, "running", 0)
            run_ocr(...)
            _update_status(run_id, "running", 30)
            run_diagram_extraction(...)
            _update_status(run_id, "running", 50)
            run_evaluation(...)
            _update_status(run_id, "running", 80)
            generate_reports(...)
            _update_status(run_id, "completed", 100)
    except Exception as e:
        _update_status(run_id, "failed", -1, str(e))

t = threading.Thread(target=_run_pipeline_in_background, args=(run_id,...), daemon=True)
t.start()
```

`daemon=True` means the thread is killed when the main process exits — no lingering background threads if the server crashes.

### J.3.4 Threading and Mutex Locks

**What is a thread?** A thread is a separate sequence of execution within the same process. Multiple threads share the same memory (same Python objects, same variables). This allows true parallelism (on different CPU cores) for CPU-bound tasks, but Python's GIL (Global Interpreter Lock) limits true parallel CPU execution for pure Python code. However, for I/O-bound threads (waiting for API calls, file reads), GIL doesn't block — threads can be truly concurrent.

**What is a Mutex (Mutual Exclusion Lock)?**

A mutex is a synchronization primitive that ensures only one thread can execute a **critical section** (protected code) at a time.

```python
PIPELINE_RUN_LOCK = threading.Lock()

# Thread A:                      # Thread B:
with PIPELINE_RUN_LOCK:          # simultaneously tries to acquire:
    # Thread A holds the lock    #   BLOCKS here until Thread A releases
    run_pipeline(...)
    # Thread A releases lock     # Thread B acquires lock and runs
```

**Why needed?** If two grading pipelines ran simultaneously:
- Both would try to write to the same `results/` directory → race condition → corrupted files
- Both would load large models to GPU → out of memory → crash
- CPU/GPU would be overwhelmed → both slower or crashing

The lock serializes pipeline runs: second job queues up and starts after first finishes.

### J.3.5 Cloud Run: Ephemeral Filesystem Problem

**Google Cloud Run** is a serverless container platform. Containers are **ephemeral**: when a request finishes (or after some idle time), the container may be destroyed. A new container starts fresh for the next request — no persistent disk. Any files written during one container's lifetime are lost for the next.

**Problem:** Report PDFs generated during a grading run would be lost when the container restarts:
```
Request 1: POST /api/jobs → generates report.pdf (saved to /tmp/)
Container idle → Container killed
New container starts
Request 2: GET /api/jobs/{run_id}/reports → tries to read /tmp/report.pdf → FILE NOT FOUND
```

### J.3.6 GCS (Google Cloud Storage) for Durability

**Solution:** After generating each report PDF, immediately upload it to **Google Cloud Storage (GCS)** — a persistent, globally accessible object store:

```python
class RunArtifactStore:
    def __init__(self, gcs_bucket_name):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket = self.client.bucket(gcs_bucket_name)

    def save_report(self, run_id, report_filename, local_path):
        blob_name = f"runs/{run_id}/reports/{report_filename}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(local_path)

    def get_signed_url(self, run_id, report_filename, expiry=3600):
        blob = self.bucket.blob(f"runs/{run_id}/reports/{report_filename}")
        return blob.generate_signed_url(expiration=expiry)  # URL valid for 1 hour
```

**Signed URLs** allow the frontend to directly download files from GCS without going through the FastAPI server — reducing server load and bypassing the ephemeral filesystem issue.

---

## J.4 Report Generation with fpdf2

**fpdf2** is a pure-Python library that constructs PDF files from scratch:

```python
from fpdf import FPDF

class ReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 8, 'Automated Answer Sheet Evaluation Report', align='C', ln=1)
        self.ln(3)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 5, f'Page {self.page_no()}')

pdf = ReportPDF()
pdf.add_page()   # triggers header()

pdf.set_font('Helvetica', size=12)
pdf.cell(0, 8, f'Student: {student_name}', ln=1)
pdf.cell(0, 8, f'Total Score: {total:.2f} / {max_total}', ln=1)

pdf.ln(5)    # vertical space

for q in questions:
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 7, f"Q{q.id}: {q.score:.2f} / {q.max_marks}", ln=1)
    pdf.set_font('Helvetica', size=10)
    pdf.multi_cell(0, 6, f"Feedback: {q.feedback}")  # auto word-wrap

pdf.output(output_path)   # writes PDF binary to disk
```

**How fpdf2 generates a PDF:**
1. PDF is a text-based format (with binary streams for compressed content).
2. fpdf2 maintains an internal buffer of PDF commands.
3. `cell()` and `multi_cell()` add text-drawing commands at current position.
4. `output()` finalizes: adds cross-reference table, page tree, serializes to PDF binary.

---

## J.5 Complete End-to-End Pipeline Walkthrough

Let's follow one complete grading run — teacher uploads `ideal.pdf` + `student_Arush.pdf` + `rubric.json`:

```
=== PHASE 0: Job Creation ===
Client → POST /api/jobs (multipart: ideal.pdf, student.pdf, rubric.json)
FastAPI:
  - Validate files (check PDF mime type, JSON validity)
  - Generate run_id = uuid4() → e.g., "a3b8c1d2-..."
  - Save to disk: /data/runs/{run_id}/uploads/ideal.pdf, student.pdf, rubric.json
  - Write /data/runs/{run_id}/run_meta.json = {"status":"queued","progress":0}
  - Spawn Thread(target=_run_pipeline, args=(run_id,...))
  - Return 200 OK: {"run_id":"a3b8c1d2","status":"queued","progress":0}

=== PHASE 1: OCR (thread runs) ===
Acquire PIPELINE_RUN_LOCK → no other pipeline running
Update status: "running", progress: 10%

For ideal.pdf:
  pdf2image.convert_from_path(ideal.pdf, dpi=300) → [page1_PIL, page2_PIL]
  
  For page 1 (page1_PIL):
    Gray = convert(page1_PIL, 'L')
    img_bytes = encode_as_jpeg(page1_PIL, quality=90)
    if size > 9MB: compress more
    response = google_vision.document_text_detection(img_bytes)
    blocks = parse_annotation(response.full_text_annotation)
    → [{bbox:[[x1,y1],...], text:"Ohm's Law states V=IR...", conf:0.97}, ...]
    Save: results/ocr/Ideal_page1.json

For student_Arush.pdf:
  Similar process, save: results/ocr/Student_Arush_page1.json

Update status: progress 30%

=== PHASE 2: Diagram Extraction ===
For each page, ideal and student:
  gray_img = cv2.cvtColor(page_img_bgr, cv2.COLOR_BGR2GRAY)   (H×W, uint8)
  _, ink_mask = cv2.threshold(gray_img, 245, 255, cv2.THRESH_BINARY_INV)
  closed = cv2.morphologyEx(ink_mask, cv2.MORPH_CLOSE, np.ones((3,3)))
  n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, 8)
  
  good_boxes = []
  for label in range(1, n_labels):
    area = stats[label, cv2.CC_STAT_AREA]
    cy   = centroids[label, 1]
    if area >= 0.003 * H*W and cy >= 0.45*H:
      good_boxes.append(stats[label, :4])   # [x, y, w, h]
  
  if good_boxes:
    x_min = min(b[0] for b in good_boxes)
    y_min = min(b[1] for b in good_boxes)
    x_max = max(b[0]+b[2] for b in good_boxes)
    y_max = max(b[1]+b[3] for b in good_boxes)
    diagram_crop = page_img_bgr[y_min:y_max, x_min:x_max]
    cv2.imwrite("results/diagrams/Ideal_page1_diagram.png", diagram_crop)

Update status: progress 45%

=== PHASE 2.5: Formula Extraction ===
Load Ideal_page1.json blocks
Group blocks by Y-coordinate (lines)
For each line: check _looks_formula_like()
If formula-like: crop region, run LatexOCR

formula_reader = LatexOCR()   (loads pix2tex model)
crop = page_img[y1:y2, x1:x2, :]   (formula region)
pil_crop = Image.fromarray(crop)
latex = str(formula_reader(pil_crop))   (ResNet encoder + Transformer decoder)
→ "V = IR"  or "\frac{1}{2}mv^{2}" etc.

Save: results/formulas/Ideal_page1_formulas.json

Repeat for student page.

Update status: progress 60%

=== PHASE 3: Evaluation ===
Load rubric.json for question 1: {"max_marks":10, "text_weight":0.6, "diagram_weight":0.4, "formula_weight":0.2, ...}

TEXT SIMILARITY:
  ideal_text = Ideal_page1.json['text']       → "Ohm's Law states that V=IR..."
  student_text = Student_Arush_page1.json['text'] → "According to Ohm V = IR..."
  
  sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
  emb_ideal   = sbert_model.encode(ideal_text)    → ℝ^384
  emb_student = sbert_model.encode(student_text)  → ℝ^384
  raw_sim = util.cos_sim(emb_ideal, emb_student).item()   → 0.81
  text_fraction = max(0, (0.81 - 0.6) / 0.4) = 0.525

DIAGRAM SIMILARITY:
  ideal_img   = Image.open("results/diagrams/Ideal_page1_diagram.png").convert("RGB")
  student_img = Image.open("results/diagrams/Student_Arush_page1_diagram.png").convert("RGB")
  
  clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
  clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
  
  inputs = clip_processor(images=[ideal_img, student_img], return_tensors="pt")
  feats = clip_model.get_image_features(**inputs)   → shape (2, 512)
  feats = feats / feats.norm(dim=-1, keepdim=True)  (L2 normalize)
  raw_diag_sim = (feats[0] @ feats[1]).item()   → 0.77
  diagram_fraction = min(1.0, 0.77 × 1.2) = min(1.0, 0.924) = 0.924

FORMULA SIMILARITY:
  ideal_latex   = "V = IR"   (from formula pipeline)
  student_latex = "V=IR"     (student's formula)
  
  ideal_expr   = parse_latex("V = IR") → Eq(V, I*R)
  student_expr = parse_latex("V=IR")   → Eq(V, I*R)
  diff = sp.simplify(ideal_expr.rhs - student_expr.rhs) = sp.simplify(I*R - I*R) = 0
  formula_fraction = 1.0   (mathematically equivalent!)

SCORE:
  w_total = 0.6 + 0.4 + 0.2 = 1.2
  score = (0.525 × 0.6/1.2 + 0.924 × 0.4/1.2 + 1.0 × 0.2/1.2) × 10
        = (0.525 × 0.500 + 0.924 × 0.333 + 1.0 × 0.167) × 10
        = (0.2625 + 0.3077 + 0.1670) × 10
        = 0.737 × 10
        = 7.37 / 10

Save: results/eval/Student_Arush_eval.json

Update status: progress 80%

=== PHASE 4: Report Generation ===
pdf = ReportPDF()
pdf.add_page()
pdf.cell(0, 8, "Student: Arush")
pdf.cell(0, 8, "Total Score: 7.37 / 10")
pdf.cell(0, 6, "Q1: 7.37/10 | Text: 52.5% | Diagram: 92.4% | Formula: 100%")
pdf.multi_cell(0, 6, "Feedback: Good explanation. Diagram well drawn.")
pdf.output("results/reports/Student_Arush_report.pdf")

Upload to GCS: gs://{bucket}/runs/{run_id}/reports/Student_Arush_report.pdf

=== PHASE 5: Completion ===
Update run_meta.json:
{
  "status": "completed",
  "progress_percent": 100,
  "summary": [{"name":"Student_Arush","score":7.37,"max":10,"pct":73.7}],
  "report_urls": [{"name":"Student_Arush", "url":"https://storage.googleapis.com/...signed_url..."}]
}

Release PIPELINE_RUN_LOCK

=== CLIENT POLLING ===
GET /api/jobs/{run_id} → reads run_meta.json → returns completed status + download URLs
Frontend downloads PDFs, displays leaderboard table
```

---

# Summary Reference Table

| Technology | Category | Role | Key Math |
|---|---|---|---|
| EasyOCR / CRAFT | Text detection | Finds text bounding boxes in images | VGG-16 + FPN heatmap prediction |
| CRNN + CTC | Text recognition | Reads detected text crops | BiLSTM + CTC dynamic programming |
| Google Vision AI | Cloud OCR | Handwritten text recognition | Proprietary transformer model |
| Azure Document Intelligence | Cloud OCR | Handwritten text recognition | prebuilt-read model |
| Connected Components (OpenCV) | CV | Extracts diagram regions | Graph BFS/two-pass, Union-Find |
| Morphological Closing | CV | Fills gaps in diagram strokes | Dilation ⊕ B then Erosion ⊖ B |
| Regex heuristics | Formula detect | Identifies formula lines | Character density analysis |
| pix2tex (LatexOCR) | Formula OCR | Formula image → LaTeX | ResNet encoder + Transformer decoder + cross-attention |
| SymPy CAS | Formula eval | Mathematical equivalence | Expression trees, algebraic simplification |
| Word2Vec / GloVe | NLP foundation | Dense word vectors | Skip-gram, co-occurrence matrix |
| BERT (architecture) | Transformer | Bidirectional text encoder | 12-layer transformer, MLM pre-training |
| Sentence-BERT (all-MiniLM-L6-v2) | Text similarity | Semantic sentence embeddings | Siamese network, mean pooling, cosine similarity |
| Knowledge Distillation (MiniLM) | Compression | Faster student model | KL divergence on attention matrices |
| Cosine Similarity | Similarity metric | Compare text/image vectors | `(a·b)/(‖a‖‖b‖)` |
| ViT-B/32 | Vision | Image patch encoder | Patch splitting, 12 transformer layers |
| CLIP | Diagram similarity | Visual semantic similarity | InfoNCE contrastive loss, shared embedding space |
| Gemini 2.5 Flash | LLM evaluation | Holistic grading + feedback | Decoder transformer, RLHF, multimodal |
| Rubric system | Scoring | Weighted multi-modal scoring | Weight normalization, leniency curve |
| fpdf2 | Reporting | PDF report generation | PDF command stream generation |
| FastAPI + uvicorn | Backend | REST API + async jobs | ASGI, threading, mutex lock |
| Google Cloud Storage | Storage | Durable artifact store | Blob storage, signed URLs |

---

*End of document. This document covers every fundamental, algorithm, model, and technique used in the Auto Subjective Grader project from first principles.*
