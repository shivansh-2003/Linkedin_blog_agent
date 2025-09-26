# Ingestion Subsystem

End-to-end, multi-format content ingestion for the LinkedIn Blog Agent. Supports PDFs, Word, PowerPoint, text, code, and images with AI-enabled analysis and standardized outputs.

## Overview

- Unified entrypoint: `unified_processor.UnifiedProcessor`
- Format-specific extractors: `pdf_processor`, `word_processor`, `ppt_processor`, `text_processor`, `code_processor`, `image_processor`
- AI analysis: `ai_analyzer.AIAnalyzer` (Groq for text/code docs, Gemini for vision)
- Prompt templates: `prompt_templates.py` (centralized, easy to tune)
- Batch operations: `batch_processor.BatchProcessor`
- File detection/validation: `file_detection.FileDetector`
- Shared models/config: `config.py`

## Data Models (Pydantic)

Defined in `config.py`:
- `ContentType`: pdf, word, powerpoint, code, image, text
- `ProcessingModel`: Groq and Gemini model IDs
- `ExtractedContent`: unified extraction payload per file (raw text, structured data, metadata, processing_model, processing_time)
- `DocumentMetadata`: generic metadata (file size, page/word counts)
- `ProcessedContent`: final standardized result (source_file, content_type, extracted_content, ai_analysis, key_insights, metadata, success, error)

## Processing Flow

1. Validate + detect file type via `FileDetector`
2. Extract using the appropriate processor:
   - `PDFProcessor`: text via LangChain `PyPDFLoader`
   - `WordProcessor`: text via LangChain `Docx2txtLoader`
   - `PPTProcessor`: text, slide structure, and embedded image bytes + mime types
   - `TextProcessor`: plain/markdown text parsing
   - `CodeProcessor`: reads code, light static structure analysis (functions/classes/imports)
   - `ImageProcessor`: reads image bytes and mime type
3. AI analysis via `AIAnalyzer`:
   - Images: Gemini 2.0 Flash vision
   - PowerPoint: Gemini generates per-image captions, then Groq (Llama 3.3 70B) aggregates text + captions into a long summary
   - Code/Text/PDF/Word: Groq models (configurable per `ProcessingModel`)
   - Robust Groq fallbacks (e.g., 8B, Gemma) if a model is decommissioned or errors
4. Build `ProcessedContent` with `ai_analysis` and `key_insights`

## Model Selection

`config.Config.MODEL_MAPPING` maps content types to default models:
- `POWERPOINT`: `llama-3.3-70b-versatile` (Groq)
- `CODE`: `openai/gpt-oss-20b` (Groq)
- `WORD`: `llama-3.1-8b-instant` (Groq)
- `PDF`: `llama-3.3-70b-versatile` (Groq)
- `TEXT`: `gemma2-9b-it` (Groq)
- `IMAGE`: `gemini-1.5-flash` (Gemini; analyzer uses `gemini-2.0-flash`)

Environment override (optional):
- `GROQ_FALLBACK_MODELS`: comma-separated list of alternative Groq model IDs to try if the primary fails

Reference: Groq Supported Models: `https://console.groq.com/docs/models`

## Prompt Templates

`prompt_templates.py` centralizes templates for consistent style:
- `CODE_SYSTEM_PROMPT` + `build_code_user_prompt(...)`
- `PPT_SYSTEM_PROMPT` + `build_ppt_user_prompt(...)`

`ai_analyzer.AIAnalyzer` imports and uses these for CODE and POWERPOINT.

## PPT Multimodal Orchestration

- `ppt_processor` embeds `images` per slide as `{ mime_type, bytes_len, image_bytes }`
- `ai_analyzer`:
  - Runs Gemini 2.0 Flash on each image → compact `image_captions` [{ slide, caption }]
  - Builds a compact slide image summary and truncated captions to keep prompts within limits
  - Calls Groq LLM with both slide text and Gemini captions for a long, LinkedIn-optimized summary
- The API response includes `extracted_content.structured_data.image_captions` to verify vision usage

## API Usage

A minimal FastAPI app exposes ingestion as one endpoint in project root `api.py`:
- `POST /api/ingest` with `multipart/form-data` file
- Returns JSON with `ProcessedContent`

Example:
```bash
curl -F "file=@/path/to/file.pptx" http://localhost:8000/api/ingest | jq
```

Response fields of interest:
- `success`: boolean
- `ai_analysis`: long-form LLM output
- `key_insights`: extracted bullet points (top 5)
- `extracted_content.structured_data`: format-specific details
  - For PPT: `slides`, `presentation_metadata`, `image_captions` (vision verification)

## Environment Variables

- `GROQ_API_KEY` (required)
- `GOOGLE_API_KEY` (required for Gemini)
- `GROQ_FALLBACK_MODELS` (optional)

## Dependencies (subset)

- `groq`
- `google-generativeai`
- `python-pptx`
- `langchain-community`
- `pydantic`
- `fastapi`, `uvicorn` (API)

See project `requirements.txt` for the full list.

## Batch Processing

- `batch_processor.BatchProcessor` supports concurrent ingestion for multiple files or directories
- Provides aggregate summaries and can write results to a text file

## Extending

- Add a new processor: Implement `extract_content(file_path) -> ExtractedContent`, then register in `UnifiedProcessor.processors`
- Update model choice: adjust `config.Config.MODEL_MAPPING`
- Tune prompts: edit `prompt_templates.py`
- Enhance fallbacks/rate-limiting: update `ai_analyzer.AIAnalyzer`

## Error Handling

- Validation errors yield `success=false` with an `error_message`
- Groq decommissioned-model or length errors are handled via model fallbacks and prompt compaction (particularly for PPT)
- API strips raw `image_bytes` before JSON serialization (reports `bytes_len` only)

## Known Limits / Notes

- PPT prompts are compacted (limited slides and truncated captions) to avoid token overflow
- Code structure analysis is heuristic; deep static analysis is out of scope
- Vision captions are brief; for heavy vision tasks, consider per-slide detailed captioning then aggregation
