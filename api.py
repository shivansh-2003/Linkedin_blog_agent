"""
Minimal FastAPI app exposing a single ingestion endpoint that processes any file
via the ingestion UnifiedProcessor.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
import shutil
import sys

# Ensure ingestion modules are importable when running API from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INGESTION_DIR = os.path.join(BASE_DIR, "ingestion")
if INGESTION_DIR not in sys.path:
    sys.path.insert(0, INGESTION_DIR)

from ingestion.unified_processor import UnifiedProcessor

# Helper to make nested structures JSON-safe (e.g., remove bytes)
def _sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items() if k != "image_bytes"}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, (bytes, bytearray)):
        return {"bytes_len": len(obj)}
    return obj

app = FastAPI(title="Ingestion API", version="1.0.0")

ingestion_processor = UnifiedProcessor()

@app.post("/api/ingest")
async def ingest_any_file(file: UploadFile = File(...)):
    """Process any supported document through the ingestion pipeline and return a JSON payload."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            result = ingestion_processor.process_file(tmp_path)
            structured_data_safe = None
            if result.extracted_content and result.extracted_content.structured_data is not None:
                structured_data_safe = _sanitize_for_json(result.extracted_content.structured_data)

            payload = {
                "success": result.success,
                "error": result.error_message,
                "source_file": result.source_file,
                "content_type": result.content_type.value,
                "ai_analysis": result.ai_analysis,
                "key_insights": result.key_insights,
                "metadata": result.metadata.dict() if result.metadata else None,
                "extracted_content": {
                    "content_type": result.extracted_content.content_type.value if result.extracted_content else None,
                    "file_path": result.extracted_content.file_path if result.extracted_content else None,
                    "raw_text": result.extracted_content.raw_text[:2000] + ("..." if result.extracted_content and len(result.extracted_content.raw_text) > 2000 else "") if result.extracted_content else None,
                    "structured_data": structured_data_safe,
                    "metadata": result.extracted_content.metadata if result.extracted_content else None,
                    "processing_model": result.extracted_content.processing_model.value if result.extracted_content else None,
                    "processing_time": result.extracted_content.processing_time if result.extracted_content else None,
                } if result.extracted_content else None,
            }
            return JSONResponse(content=payload)
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 