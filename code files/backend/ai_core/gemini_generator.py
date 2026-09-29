import os
import time
from textwrap import dedent

from dotenv import load_dotenv

load_dotenv()


SYSTEM_INSTRUCTION = dedent("""
You are LegalEase, an AI assistant for drafting legal-document drafts.

Produce a professional, structured DRAFT based only on the user's supplied facts.

Do not invent names, dates, money, addresses, governing laws, rights, or
obligations.

If an important legal fact is missing, use a clearly marked placeholder such as
[TO BE COMPLETED] instead of guessing.

Output plain text only.

Use:
- A clear title
- Numbered sections
- Appropriate headings
- Professional legal wording
- A signature section where appropriate

Include this notice at the end:

"This document is an AI-generated draft and is not legal advice. Have it reviewed
by a qualified lawyer before signing or relying on it."

Do not claim that the document is legally valid or enforceable.
""").strip()


class GeminiDocumentGenerator:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.1-flash-lite"
        ).strip()

        self.fallback_model = "gemini-3.5-flash-lite"

        self.mock_mode = (
            os.getenv("MOCK_MODE", "false").lower() == "true"
        )

        self.client = None

        if not self.mock_mode and self.api_key:
            try:
                from google import genai

                self.client = genai.Client(
                    api_key=self.api_key
                )

            except Exception as exc:
                raise RuntimeError(
                    f"Could not initialize Gemini SDK: {exc}"
                ) from exc

    def generate_document(
        self,
        document_type,
        parties,
        terms,
        effective_date
    ):

        if self.mock_mode:
            return self._mock_document(
                document_type,
                parties,
                terms,
                effective_date
            )

        if not self.client:
            raise RuntimeError(
                "Gemini is not configured. "
                "Set GEMINI_API_KEY in .env "
                "or set MOCK_MODE=true for local testing."
            )

        prompt = dedent(f"""
        Draft a {document_type}.

        PARTIES:
        {parties}

        EFFECTIVE DATE:
        {effective_date}

        USER-SUPPLIED TERMS:
        {terms}

        Requirements:

        - Preserve all supplied facts exactly.
        - Do not invent missing legal facts.
        - Use [TO BE COMPLETED] for important missing information.
        - Organize the draft into logical numbered clauses.
        - Include definitions only when necessary.
        - Include signatures appropriate to the identified parties.
        - Keep the wording editable and professional.
        """).strip()

        # ---------------------------------------------------------
        # First attempt: configured model
        # ---------------------------------------------------------

        try:
            return self._generate_with_retry(
                self.model_name,
                prompt
            )

        except Exception as first_error:

            # -----------------------------------------------------
            # If the first model is unavailable, try fallback model
            # -----------------------------------------------------

            if self.model_name != self.fallback_model:

                try:
                    return self._generate_with_retry(
                        self.fallback_model,
                        prompt
                    )

                except Exception as fallback_error:

                    raise RuntimeError(
                        "Gemini generation failed.\n"
                        f"Primary model ({self.model_name}): "
                        f"{first_error}\n"
                        f"Fallback model ({self.fallback_model}): "
                        f"{fallback_error}"
                    ) from fallback_error

            raise

    def _generate_with_retry(
        self,
        model_name,
        prompt,
        max_retries=3
    ):

        last_error = None

        for attempt in range(max_retries + 1):

            try:

                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "system_instruction": SYSTEM_INSTRUCTION,
                        "temperature": 0.2,
                        "max_output_tokens": 6000,
                    },
                )

                text = getattr(response, "text", None)

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text.strip()

            except Exception as exc:

                last_error = exc

                error_text = str(exc).upper()

                # Retry only temporary/server errors.
                is_retryable = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "500" in error_text
                    or "502" in error_text
                    or "504" in error_text
                )

                # Do not retry invalid API keys,
                # bad requests, etc.
                if not is_retryable:
                    raise

                # Stop after the final attempt.
                if attempt >= max_retries:
                    break

                # Exponential backoff:
                # 2 seconds, 4 seconds, 8 seconds
                wait_time = 2 ** (attempt + 1)

                print(
                    f"Gemini temporary error with "
                    f"{model_name}. "
                    f"Retry {attempt + 1}/{max_retries} "
                    f"in {wait_time} seconds..."
                )

                time.sleep(wait_time)

        raise RuntimeError(
            f"Gemini model '{model_name}' remained unavailable "
            f"after {max_retries + 1} attempts: {last_error}"
        )

    def _mock_document(
        self,
        document_type,
        parties,
        terms,
        effective_date
    ):

        return dedent(f"""
        {document_type.upper()}

        Effective Date: {effective_date}

        1. PARTIES

        {parties}

        2. TERMS AND CONDITIONS

        {terms}

        3. ADDITIONAL INFORMATION

        [TO BE COMPLETED]

        4. SIGNATURES

        Party 1 Signature: __________________________

        Party 2 Signature: __________________________

        Date: __________________________


        This document is an AI-generated draft and is not legal advice.
        Have it reviewed by a qualified lawyer before signing or relying on it.
        """).strip()