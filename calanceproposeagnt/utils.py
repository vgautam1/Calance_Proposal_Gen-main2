import json
import logging
from langchain.output_parsers import StructuredOutputParser

class CustomOutputParser(StructuredOutputParser):
    def parse(self, text):
        try:
            return super().parse(text)
        except json.JSONDecodeError as e:
            # Handle invalid escape characters by replacing them
            text = text.replace('\\', '\\\\')
            return super().parse(text)
