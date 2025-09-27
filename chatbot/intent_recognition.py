import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

from chatbot.config import UserIntent, ChatbotConfig, ChatStage

class IntentRecognizer:
    """Advanced intent recognition for chatbot interactions"""
    
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name="openai/gpt-oss-20b",
            temperature=0.1,
            max_tokens=500
        ) if self.groq_api_key else None
        
        self.patterns = ChatbotConfig.INTENT_PATTERNS
    
    def recognize_intent(self, user_input: str, current_stage: ChatStage = ChatStage.INITIAL, 
                        context: Dict = None) -> UserIntent:
        """Recognize user intent with context awareness"""
        
        # First try pattern-based recognition (fast)
        pattern_intent = self._pattern_based_recognition(user_input, current_stage)
        
        # If pattern matching is confident enough, return it
        if pattern_intent.confidence >= 0.8:
            return pattern_intent
        
        # Otherwise, use LLM-based recognition for better accuracy
        if self.llm:
            llm_intent = self._llm_based_recognition(user_input, current_stage, context)
            return llm_intent if llm_intent.confidence > pattern_intent.confidence else pattern_intent
        
        return pattern_intent
    
    def _pattern_based_recognition(self, user_input: str, current_stage: ChatStage) -> UserIntent:
        """Pattern-based intent recognition using keywords and stage context"""
        
        user_input_lower = user_input.lower().strip()
        
        # Stage-specific intent detection
        if current_stage == ChatStage.AWAITING_FEEDBACK:
            return self._detect_feedback_intent(user_input_lower)
        
        elif current_stage == ChatStage.PRESENTING_DRAFT:
            return self._detect_draft_response_intent(user_input_lower)
        
        # File upload detection
        if self._is_file_reference(user_input):
            return UserIntent(
                intent_type="file_upload",
                confidence=0.9,
                entities={"file_path": self._extract_file_path(user_input)}
            )
        
        # General intent detection
        intent_scores = {}
        
        for intent, keywords in self.patterns.items():
            score = self._calculate_keyword_score(user_input_lower, keywords)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return UserIntent(
                intent_type=best_intent[0],
                confidence=min(best_intent[1], 0.85),  # Cap pattern-based confidence
                entities=self._extract_entities(user_input, best_intent[0])
            )
        
        # Default fallback
        return UserIntent(
            intent_type="ask_question",
            confidence=0.3,
            entities={}
        )
    
    def _llm_based_recognition(self, user_input: str, current_stage: ChatStage, 
                             context: Dict = None) -> UserIntent:
        """LLM-based intent recognition for complex cases"""
        
        system_prompt = f"""You are an intent classifier for a LinkedIn blog creation chatbot.

Current conversation stage: {current_stage}
Context: {context or {}}

Analyze the user's message and classify the intent. Respond with JSON:
{{
  "intent_type": "one of: file_upload, start_blog, provide_feedback, approve_draft, start_over, ask_question",
  "confidence": 0.0-1.0,
  "entities": {{"key": "value"}},
  "feedback_type": "if providing feedback: content, style, tone, structure, or general",
  "specific_requests": ["list of specific changes requested"]
}}

Intent types:
- file_upload: User wants to upload/process a file
- start_blog: User wants to create a new blog post
- provide_feedback: User is giving feedback to improve current draft
- approve_draft: User approves the current draft
- start_over: User wants to start completely over
- ask_question: User is asking for help/information

User message: "{user_input}"
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ])
            
            # Parse JSON response
            import json
            result_text = response.content.strip()
            
            # Clean JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            result = json.loads(result_text)
            
            return UserIntent(
                intent_type=result.get("intent_type", "ask_question"),
                confidence=result.get("confidence", 0.5),
                entities=result.get("entities", {}),
                feedback_type=result.get("feedback_type"),
                specific_requests=result.get("specific_requests", [])
            )
            
        except Exception as e:
            print(f"LLM intent recognition error: {e}")
            return UserIntent(intent_type="ask_question", confidence=0.4, entities={})
    
    def _detect_feedback_intent(self, user_input: str) -> UserIntent:
        """Detect feedback-specific intents"""
        
        # Approval indicators
        approval_words = ["good", "great", "perfect", "approve", "accept", "ready", "publish", "done"]
        if any(word in user_input for word in approval_words):
            return UserIntent(
                intent_type="approve_draft",
                confidence=0.85,
                entities={}
            )
        
        # Feedback type detection
        feedback_types = {
            "content": ["content", "information", "facts", "data", "details"],
            "style": ["style", "tone", "voice", "writing", "sound"],
            "structure": ["structure", "organization", "flow", "order", "format"],
            "engagement": ["engagement", "hook", "attention", "catchy", "interesting"]
        }
        
        detected_type = "general"
        for ftype, keywords in feedback_types.items():
            if any(keyword in user_input for keyword in keywords):
                detected_type = ftype
                break
        
        # Extract specific requests
        specific_requests = self._extract_change_requests(user_input)
        
        return UserIntent(
            intent_type="provide_feedback",
            confidence=0.9,
            entities={"feedback_focus": detected_type},
            feedback_type=detected_type,
            specific_requests=specific_requests
        )
    
    def _detect_draft_response_intent(self, user_input: str) -> UserIntent:
        """Detect response to draft presentation"""
        
        # Strong approval indicators
        strong_approval = ["perfect", "excellent", "love it", "publish", "ready", "approve"]
        if any(phrase in user_input for phrase in strong_approval):
            return UserIntent(
                intent_type="approve_draft",
                confidence=0.95,
                entities={}
            )
        
        # Mild approval
        mild_approval = ["good", "nice", "okay", "fine"]
        if any(word in user_input for word in mild_approval) and "but" not in user_input:
            return UserIntent(
                intent_type="approve_draft",
                confidence=0.7,
                entities={}
            )
        
        # Change requests
        change_indicators = ["change", "modify", "different", "improve", "better", "more", "less"]
        if any(word in user_input for word in change_indicators):
            return self._detect_feedback_intent(user_input)
        
        return UserIntent(
            intent_type="ask_question",
            confidence=0.5,
            entities={}
        )
    
    def _is_file_reference(self, user_input: str) -> bool:
        """Check if user input contains file reference"""
        file_indicators = [
            "file", "document", "upload", "attach", "pdf", "docx", "pptx", 
            "image", "code", ".pdf", ".docx", ".txt", ".py", ".js"
        ]
        
        return any(indicator in user_input.lower() for indicator in file_indicators)
    
    def _extract_file_path(self, user_input: str) -> Optional[str]:
        """Extract file path from user input"""
        # Look for common file path patterns
        path_patterns = [
            r'["\']([^"\']+\.[a-zA-Z]{2,4})["\']',  # Quoted paths
            r'(\S+\.[a-zA-Z]{2,4})',  # Simple paths
            r'([A-Za-z]:\\[^\\/:*?"<>|\r\n]+)',  # Windows paths
            r'(/[^\\/:*?"<>|\r\n]+)',  # Unix paths
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, user_input)
            if match:
                potential_path = match.group(1)
                if Path(potential_path).suffix.lower() in ChatbotConfig.SUPPORTED_FILE_TYPES:
                    return potential_path
        
        return None
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword matching score"""
        matches = sum(1 for keyword in keywords if keyword in text)
        return matches / len(keywords) if keywords else 0
    
    def _extract_entities(self, text: str, intent_type: str) -> Dict[str, str]:
        """Extract relevant entities based on intent type"""
        entities = {}
        
        if intent_type == "file_upload":
            file_path = self._extract_file_path(text)
            if file_path:
                entities["file_path"] = file_path
        
        elif intent_type == "start_blog":
            # Extract topic if mentioned
            topic_patterns = [
                r"about (.+?)(?:\.|$)",
                r"on (.+?)(?:\.|$)",
                r"regarding (.+?)(?:\.|$)"
            ]
            for pattern in topic_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities["topic"] = match.group(1).strip()
                    break
        
        return entities
    
    def _extract_change_requests(self, feedback: str) -> List[str]:
        """Extract specific change requests from feedback"""
        requests = []
        
        # Pattern-based extraction
        change_patterns = [
            r"make it (.+?)(?:\.|$)",
            r"add (.+?)(?:\.|$)",
            r"remove (.+?)(?:\.|$)",
            r"change (.+?)(?:\.|$)",
            r"improve (.+?)(?:\.|$)"
        ]
        
        for pattern in change_patterns:
            matches = re.findall(pattern, feedback, re.IGNORECASE)
            requests.extend([match.strip() for match in matches])
        
        return requests[:5]  # Limit to 5 requests
    
    def get_confidence_explanation(self, intent: UserIntent) -> str:
        """Get explanation for confidence level"""
        if intent.confidence >= 0.9:
            return "Very confident"
        elif intent.confidence >= 0.7:
            return "Confident"
        elif intent.confidence >= 0.5:
            return "Moderate confidence"
        else:
            return "Low confidence"

class ContextualIntentRecognizer(IntentRecognizer):
    """Enhanced intent recognizer with conversational context"""
    
    def __init__(self, groq_api_key: str = None):
        super().__init__(groq_api_key)
        self.conversation_context = []
    
    def update_context(self, user_message: str, bot_response: str, stage: ChatStage):
        """Update conversational context"""
        self.conversation_context.append({
            "user": user_message,
            "bot": bot_response,
            "stage": stage,
            "timestamp": datetime.now()
        })
        
        # Keep only recent context
        if len(self.conversation_context) > 5:
            self.conversation_context = self.conversation_context[-5:]
    
    def recognize_intent_with_context(self, user_input: str, current_stage: ChatStage) -> UserIntent:
        """Recognize intent with full conversational context"""
        context = {
            "previous_messages": self.conversation_context[-3:],
            "stage_history": [ctx["stage"] for ctx in self.conversation_context],
            "recent_topics": self._extract_recent_topics()
        }
        
        return self.recognize_intent(user_input, current_stage, context)
    
    def _extract_recent_topics(self) -> List[str]:
        """Extract topics from recent conversation"""
        topics = []
        for ctx in self.conversation_context[-3:]:
            # Simple topic extraction from user messages
            user_msg = ctx["user"].lower()
            if len(user_msg) > 20:
                # Extract first few words as potential topic
                words = user_msg.split()[:5]
                topic = " ".join(words)
                topics.append(topic)
        
        return topics