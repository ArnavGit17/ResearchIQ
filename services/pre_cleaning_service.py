import re

class PreCleaningService:
    """
    Handles initial cleaning and normalization of raw text extracted from documents.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Removes excessive whitespace, normalizes line breaks, and removes invisible characters.
        """
        if not text:
            return ""

        # Remove null bytes and zero-width spaces
        text = text.replace('\x00', '')
        text = text.replace('\u200b', '')
        
        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Replace 3 or more consecutive newlines with exactly 2 (preserves paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove consecutive spaces but preserve newlines
        # This regex replaces multiple horizontal spaces (spaces/tabs) with a single space
        text = re.sub(r'[ \t]+', ' ', text)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        
        # Rejoin lines
        text = '\n'.join(lines)
        
        # Final cleanup to remove leading/trailing whitespace from the whole document
        return text.strip()

    @staticmethod
    def calculate_statistics(text: str) -> dict:
        """
        Calculates basic statistics (words, sentences, characters) from the cleaned text.
        """
        if not text:
            return {"word_count": 0, "sentence_count": 0, "character_count": 0}

        # Character count
        character_count = len(text)

        # Word count (split by whitespace)
        words = text.split()
        word_count = len(words)

        # Sentence count (very basic approximation based on punctuation)
        # Matches [.!?] followed by whitespace or end of string
        sentences = re.split(r'[.!?]+(?:\s+|$)', text)
        # Filter out empty strings that may occur from splitting
        sentence_count = len([s for s in sentences if s.strip()])

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "character_count": character_count
        }
