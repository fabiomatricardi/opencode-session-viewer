# OpenCode Session Viewer

A lightweight, terminal-faithful Python web application designed to parse raw Markdown session logs exported by the **OpenCode CLI LLM agent harness** and render them into a high-fidelity, high-contrast browser UI.

This tool preserves the authentic low-lit terminal aesthetic of OpenCode—complete with collapsible agent reasoning logs (`_Thinking:_` blocks), syntax-highlighted tool executions, clear role separation, and model execution metadata.

---

## 🚀 Features

* **Zero-Config CLI Entry:** Simply pass your exported session file path directly to the script to launch your browser dashboard.
* **Faithful Terminal UI Aesthetics:** Native implementation of the dark OpenCode theme palette utilizing custom monospaced styling.
* **Collapsible Thought Architecture:** Dynamically converts inline LLM `_Thinking:_` blocks into functional HTML accordions, keeping long session trails scannable.
* **Isolated User Context Blocks:** Full-width container partitioning to easily separate raw user inputs from system agent actions.
* **Robust Component Isolation:** Seamless parsing of technical tool blocks (e.g., JSON schemas inside `edit`, `bash`, and `glob` actions) using standard Python Markdown extensions.

---

## 🏗️ Core Concept & Architectural Flow

The core design philosophy of this tool revolves around **Dynamic Token Extraction**. Instead of relying on a generalized Markdown parser that treats all headers uniformly, this application treats the exported file as a structured chronological execution state log.

```
       [ Raw Markdown Export ]
                  │
                  ▼
         [ Multi-Line Split ] 
           Divided by `---`
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
 [ User Block ]      [ Assistant Block ]
       │                     │
       │                     ├─► RegEx Meta-Tag Capture
       │                     │   (Mode, Model, Performance)
       │                     │
       │                     └─► State Extraction
       │                         (Isolate `_Thinking:_`)
       ▼                     ▼
 [ HTML Component ]  [ HTML Components + Collapsible Logs ]
       │                     │
       └──────────┬──────────┘
                  ▼
      [ High-Contrast Web UI ]

```

---

## 📂 Project Structure

```text
opencode-session-viewer/
│
├── view.py                # Main CLI framework, custom parser, and FastAPI application
├── README.md              # Project documentation and specifications
└── templates/
    └── index.html         # Monospaced OpenCode retro terminal theme template

```

---

## ⚙️ Detailed Code Implementation

### 1. State Log Parsing (`view.py`)

The logic uses regular expressions to fragment the markdown file based on the horizontal rules (`---`) separating turns.

* **Turn Separation & Typing:** The parser scans for explicit block prefixes (`## User` vs `## Assistant`).
* **Metadata Extraction:** When an assistant turn is found, a regular expression targets the performance signature:
```python
meta_header_match = re.match(r'## Assistant\s*\(([^·]+)·\s*([^·]+)·\s*([^)]+)\)', block)

```


This extracts the engine execution mode (e.g., *Build* or *Plan*), the base model name (*Qwen3.6 Plus Free*), and processing time constraints (*8.5s*) on the fly.
* **Thinking Block Separation:** To prevent raw internal thoughts from muddying up the timeline, the engine isolates any blocks flagged with the `_Thinking:_` token using text segment clipping before forwarding the remaining payload code tables to the layout renderer.

### 2. High-Fidelity Rendering UI (`templates/index.html`)

The frontend leverages a custom **Tailwind CSS** layout locked into the monospaced `JetBrains Mono` font stack.

* **Collapsible Accordions:** Handled natively in HTML5 via the `<details>` and `<summary>` components to provide lightning-fast log expanding toggles with zero heavy JavaScript overhead:
```html
<details class="group" {% if loop.last %}open{% endif %}>
    <summary>+ Thought · {{ turn.time }}</summary>
    <div>{{ turn.thought | safe }}</div>
</details>

```


* **Asynchronous Local Orchestration:** When initiated via terminal, the app maps your target session file path globally, queries system browser channels using Python's native `webbrowser` library to initialize local viewing routing, and kicks off an isolated ASGI server instance over `uvicorn`.

---

## 🛠️ Installation & Getting Started

### Prerequisites

Ensure your Python virtual environment is active, then install the required dependencies:

```powershell
pip install fastapi uvicorn markdown jinja2

```

### Execution Command

Pass your target OpenCode Markdown export file path as a direct script parameter argument:

```powershell
python .\view.py .\session-ses_1b5e_makeOfProject.md

```

The tool will immediately read the file, mount the processing backend server at `http://127.0.0.1:8000`, and launch your local default browser tab automatically.

---

## 🎨 Theme Palette Specification

For developers looking to extend the visual stylesheets, the UI implements a tight high-contrast aesthetic mapping:

* **Background Canvas:** `#0b0c10` (Ultra Deep Black Carbon)
* **Prompt Blocks:** `#1a1c23` (High Contrast Muted Slate)
* **Thought Toggles:** `#ff9e3b` (OpenCode Amber Alert Yellow)
* **Status Tags:** `#7aa2f7` (Terminal Console Soft Blue)

---

Enjoy reviewing your agentic workflow history in a clean, professional web console! Feel free to open an issue or submit a pull request if you want to extend the syntax parsing engine.
