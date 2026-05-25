import os
import sys
import re
import webbrowser
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import markdown

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Path to the markdown file passed via CLI
TARGET_FILE = None

def parse_opencode_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into structural blocks using the horizontal line separator
    raw_blocks = re.split(r'^---+\s*$', content, flags=re.MULTILINE)
    
    session_meta = {"title": "OpenCode Session Viewer", "id": "Unknown", "created": "", "updated": ""}
    parsed_turns = []

    # First block contains global file header details
    header_block = raw_blocks[0]
    title_match = re.search(r'^#\s*(.*)', header_block, re.MULTILINE)
    if title_match:
        session_meta["title"] = title_match.group(1).strip()
    
    id_match = re.search(r'\*\*Session ID:\*\*\s*([^\n\r]+)', header_block)
    if id_match: session_meta["id"] = id_match.group(1).strip()

    # Process turns sequentially
    for block in raw_blocks[1:]:
        block = block.strip()
        if not block:
            continue

        turn = {"role": "", "mode": "", "model": "", "time": "", "thought": "", "body": ""}

        # Case 1: Parse User Turns
        if block.startswith("## User"):
            turn["role"] = "user"
            # Strip out the header line to leave pure body text
            turn["body"] = markdown.markdown(re.sub(r'^## User\s*', '', block))
            parsed_turns.append(turn)
            
        # Case 2: Parse Assistant Turns
        elif block.startswith("## Assistant"):
            turn["role"] = "assistant"
            
            # Extract Meta parameters via strict pattern tracking
            meta_header_match = re.match(r'## Assistant\s*\(([^·]+)·\s*([^·]+)·\s*([^)]+)\)', block)
            if meta_header_match:
                turn["mode"] = meta_header_match.group(1).strip()
                turn["model"] = meta_header_match.group(2).strip()
                turn["time"] = meta_header_match.group(3).strip()
            
            # Isolate and pull out the inner thinking section blocks
            body_content = re.sub(r'## Assistant\s*\([^)]+\)', '', block).strip()
            
            # Matches strings starting with _Thinking:_ or wrapped in underscores
            thought_match = re.search(r'(_Thinking:_|__Thinking:__)\s*(.*?)(?=\n\n\*\*Tool:|\n\n[A-Za-z]|\Z)', body_content, re.DOTALL)
            if thought_match:
                turn["thought"] = markdown.markdown(thought_match.group(2).strip())
                # Strip out the thought section from main body rendering loop
                body_content = body_content.replace(thought_match.group(0), "").strip()
            
            # Convert remaining output data text chunks / table tools into HTML standard patterns
            turn["body"] = markdown.markdown(body_content, extensions=['fenced_code', 'tables'])
            parsed_turns.append(turn)

    return session_meta, parsed_turns

@app.get("/", response_class=HTMLResponse)
async def render_dashboard(request: Request):
    meta, turns = parse_opencode_markdown(TARGET_FILE)
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "meta": meta, 
            "turns": turns, 
            "filename": os.path.basename(TARGET_FILE)
        }
    )

def main():
    global TARGET_FILE
    if len(sys.argv) < 2:
        print("Usage: python viewer.py <path_to_session_markdown.md>")
        sys.exit(1)
        
    TARGET_FILE = os.path.abspath(sys.argv[1])
    if not os.path.exists(TARGET_FILE):
        print(f"Error: Target export file not found at {TARGET_FILE}")
        sys.exit(1)

    # Fire open a local web browser instance right before launching server
    webbrowser.open("http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    main()