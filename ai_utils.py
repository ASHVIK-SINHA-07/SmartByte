"""
AI Utilities for Smart Study Assistant
Handles all Gemini API interactions
"""

import os
from dotenv import load_dotenv
from logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# Try to import Gemini API
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True

    GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Gemini API configuration failed: {e}")
            GENAI_AVAILABLE = False
    else:
        logger.warning("GEMINI_API_KEY not found")
        GENAI_AVAILABLE = False
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai package not installed")


def _get_model():
    """Get Gemini model instance with fallback"""
    if not GENAI_AVAILABLE:
        return None

    model_names = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.0-flash-exp",
    ]

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            logger.info(f"Using Gemini model: {model_name}")
            return model
        except Exception as e:
            logger.debug(f"Model {model_name} not available: {e}")
            continue

    return None


def summarize_text(text, max_sentences=6):
    """Summarize text using Gemini API"""
    if not text or not text.strip():
        return "No text to summarize."

    if not GENAI_AVAILABLE:
        return "Error: Gemini API not available"

    try:
        model = _get_model()
        if not model:
            return "Error: No Gemini model available"

        prompt = f"""Please summarize the following text concisely in {max_sentences} bullet points or less. 
Make it clear and informative. End with a brief TL;DR.

Text to summarize:
{text[:10000]}"""

        logger.info("Sending summarization request to Gemini API")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text") and response.text:
            summary = response.text.strip()
            logger.info(f"Received summary ({len(summary)} chars)")
            return summary
        elif response and hasattr(response, "candidates"):
            for candidate in response.candidates:
                if hasattr(candidate, "content") and hasattr(
                    candidate.content, "parts"
                ):
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            summary = part.text.strip()
                            logger.info(
                                f"Received summary from candidate ({len(summary)} chars)"
                            )
                            return summary

        return "Error: Could not extract summary from API response"

    except Exception as e:
        error_msg = f"Summarization error: {str(e)}"
        logger.error(error_msg)
        return error_msg


def generate_flashcards(text, num_cards=5):
    """Generate flashcards from text using Gemini API"""
    if not text or not text.strip():
        return []

    if not GENAI_AVAILABLE:
        logger.warning("Gemini API not available for flashcard generation")
        return []

    try:
        model = _get_model()
        if not model:
            return []

        prompt = f"""Generate exactly {num_cards} flashcard question-answer pairs from this text.
Format each flashcard as:
Q: [question]
A: [answer]

Make questions clear, specific, and test key concepts. Keep answers concise but complete.

Text:
{text[:5000]}"""

        logger.info(f"Generating {num_cards} flashcards")
        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text"):
            return []

        # Parse flashcards from response
        flashcards = []
        lines = response.text.strip().split("\n")
        current_q = None

        for line in lines:
            line = line.strip()
            if line.startswith("Q:"):
                current_q = line[2:].strip()
            elif line.startswith("A:") and current_q:
                current_a = line[2:].strip()
                flashcards.append({"question": current_q, "answer": current_a})
                current_q = None

        logger.info(f"Generated {len(flashcards)} flashcards")
        return flashcards

    except Exception as e:
        logger.error(f"Flashcard generation error: {e}")
        return []


def rewrite_text(text, style="paraphrase"):
    """Rewrite/paraphrase text using Gemini API

    Args:
        text: Text to rewrite
        style: 'paraphrase', 'simplify', 'formal', 'casual'
    """
    if not text or not text.strip():
        return text

    if not GENAI_AVAILABLE:
        return "Error: Gemini API not available"

    try:
        model = _get_model()
        if not model:
            return "Error: No Gemini model available"

        style_prompts = {
            "paraphrase": "Rewrite the following text using different words while keeping the same meaning:",
            "simplify": "Simplify the following text to make it easier to understand:",
            "formal": "Rewrite the following text in a more formal, academic style:",
            "casual": "Rewrite the following text in a more casual, conversational style:",
        }

        prompt = f"""{style_prompts.get(style, style_prompts['paraphrase'])}

{text[:3000]}

Provide only the rewritten text without any explanations."""

        logger.info(f"Rewriting text with style: {style}")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text") and response.text:
            rewritten = response.text.strip()
            logger.info(f"Text rewritten ({len(rewritten)} chars)")
            return rewritten

        return "Error: Could not generate rewritten text"

    except Exception as e:
        error_msg = f"Rewrite error: {str(e)}"
        logger.error(error_msg)
        return error_msg


def extract_keywords(text, max_keywords=10):
    """Extract key terms/concepts from text"""
    if not text or not text.strip():
        return []

    if not GENAI_AVAILABLE:
        return []

    try:
        model = _get_model()
        if not model:
            return []

        prompt = f"""Extract the {max_keywords} most important keywords or key concepts from this text.
Provide only the keywords, separated by commas, without numbering or explanations.

Text:
{text[:3000]}"""

        logger.info("Extracting keywords")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text") and response.text:
            keywords_text = response.text.strip()
            keywords = [k.strip() for k in keywords_text.split(",")]
            logger.info(f"Extracted {len(keywords)} keywords")
            return keywords[:max_keywords]

        return []

    except Exception as e:
        logger.error(f"Keyword extraction error: {e}")
        return []


def generate_quiz_questions(text, num_questions=5):
    """Generate intelligent quiz questions from text using Gemini AI
    
    Args:
        text: The content to generate questions from
        num_questions: Number of questions to generate
        
    Returns: list of dicts with 'question' and 'answer' keys
    """
    if not text or not text.strip():
        return []

    if not GENAI_AVAILABLE:
        logger.warning("Gemini API not available for quiz generation")
        return []

    try:
        model = _get_model()
        if not model:
            logger.error("No Gemini model available")
            return []

        prompt = f"""Based on the following study notes, generate {num_questions} intelligent quiz questions that test understanding of the key concepts.

Requirements:
- Create questions that test comprehension, not just memorization
- Mix question types: fill-in-the-blank, short answer, and conceptual questions
- Provide clear, concise answers
- Focus on the most important concepts in the text

Format your response EXACTLY as follows (one question per block):

Q1: [Your first question here]
A1: [Answer to first question]

Q2: [Your second question here]
A2: [Answer to second question]

[Continue for all {num_questions} questions]

Study Notes:
{text[:8000]}"""

        logger.info(f"Generating {num_questions} quiz questions using Gemini AI")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text") and response.text:
            response_text = response.text.strip()
            questions = []
            
            # Parse the response
            lines = response_text.split('\n')
            current_question = None
            current_answer = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for question (Q1:, Q2:, etc.)
                if line.startswith('Q') and ':' in line:
                    # Save previous Q&A if exists
                    if current_question and current_answer:
                        questions.append({
                            "question": current_question,
                            "answer": current_answer
                        })
                    # Start new question
                    current_question = line.split(':', 1)[1].strip()
                    current_answer = None
                    
                # Check for answer (A1:, A2:, etc.)
                elif line.startswith('A') and ':' in line:
                    current_answer = line.split(':', 1)[1].strip()
            
            # Don't forget the last Q&A pair
            if current_question and current_answer:
                questions.append({
                    "question": current_question,
                    "answer": current_answer
                })
            
            logger.info(f"Successfully generated {len(questions)} quiz questions")
            return questions[:num_questions]  # Ensure we don't exceed requested number

        logger.warning("No text in Gemini response")
        return []

    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        return []


def assess_difficulty(text):
    """Assess difficulty level of text content

    Returns: dict with 'level' (Easy/Medium/Hard) and 'explanation'
    """
    if not text or not text.strip():
        return {"level": "Unknown", "explanation": "No text provided"}

    if not GENAI_AVAILABLE:
        return {"level": "Unknown", "explanation": "API not available"}

    try:
        model = _get_model()
        if not model:
            return {"level": "Unknown", "explanation": "Model not available"}

        prompt = f"""Assess the difficulty level of this educational content.
Provide:
1. Difficulty Level: Easy, Medium, or Hard
2. Brief explanation (one sentence)

Format your response as:
Level: [Easy/Medium/Hard]
Explanation: [brief explanation]

Text:
{text[:2000]}"""

        logger.info("Assessing content difficulty")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text") and response.text:
            result_text = response.text.strip()
            level = "Medium"
            explanation = ""

            for line in result_text.split("\n"):
                if line.startswith("Level:"):
                    level = line.split(":", 1)[1].strip()
                elif line.startswith("Explanation:"):
                    explanation = line.split(":", 1)[1].strip()

            logger.info(f"Difficulty assessed: {level}")
            return {"level": level, "explanation": explanation}

        return {"level": "Unknown", "explanation": "Could not assess"}

    except Exception as e:
        logger.error(f"Difficulty assessment error: {e}")
        return {"level": "Unknown", "explanation": str(e)}
