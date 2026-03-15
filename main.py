import os
import tempfile
import subprocess
import shutil
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from utils.file_parser import build_project_context
from utils.ai_generator import generate_documentation

app = FastAPI(title="AI Documentation Generator API")

# Setup CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Mount static files to serve the frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class GenerateRequest(BaseModel):
    source_type: str  # "github" or "local"
    source_path: str  # URL or local filesystem path

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serves the main frontend HTML file."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Welcome to AI Doc Generator</h1><p>Frontend not found. Please create static/index.html.</p>")

@app.post("/api/generate")
async def api_generate_docs(request: GenerateRequest):
    """
    Endpoint that accepts a local project path or GitHub URL and returns AI-generated markdown documentation.
    """
    path = request.source_path.strip()
    source_type = request.source_type.strip().lower()

    if not path:
        raise HTTPException(status_code=400, detail="Path or URL cannot be empty.")
        
    temp_dir = None
    target_path = path

    try:
        if source_type == "github":
            # Clone the repo securely to a temporary directory
            temp_dir = tempfile.mkdtemp(prefix="ai_doc_gen_")
            print(f"Cloning {path} into temporary directory {temp_dir}...")
            
            # Run git clone. We use subprocess to call the system git.
            result = subprocess.run(
                ["git", "clone", "--depth", "1", path, temp_dir],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise ValueError(f"Failed to clone GitHub repository. Make sure the URL is correct and public. Error: {result.stderr}")
            
            target_path = temp_dir
            
        elif source_type == "local":
            if not os.path.exists(path) or not os.path.isdir(path):
                raise HTTPException(status_code=400, detail=f"Invalid local directory path: {path}")
        else:
            raise HTTPException(status_code=400, detail="Invalid source_type. Must be 'github' or 'local'.")

        # 1. Parse Directory
        print(f"Parsing directory: {target_path}")
        contextStr = build_project_context(target_path)
        
        # 2. Call Gemini API
        print("Sending codebase to Gemini for documentation generation...")
        markdown_doc = generate_documentation(contextStr)
        
        return {
            "status": "success",
            "documentation": markdown_doc
        }
            
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    finally:
        # Clean up the temporary directory if it was created
        if temp_dir and os.path.exists(temp_dir):
            try:
                # On Windows, sometimes shutil.rmtree on a git repo needs special handling for read-only files,
                # but for now we try a basic rmtree.
                def remove_readonly(func, path, excinfo):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(temp_dir, onerror=remove_readonly)
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up temp directory {temp_dir}: {cleanup_error}")

# Added for running directly from python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
