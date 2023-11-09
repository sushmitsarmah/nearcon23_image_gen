import re
import textwrap

def clean_panel_prompt(text, width=50):
    # Remove the '1. Panel Prompt 1:' pattern
    pattern = r'\d+\. Panel Prompt \d+: '
    cleaned_text = re.sub(pattern, '', text)

    cleaned_text = re.sub(r'^.*?panel, ', '', cleaned_text, 1, re.IGNORECASE)

    return cleaned_text

def wrap_text(text, width=50):
    # Wrap the text
    wrapper = textwrap.TextWrapper(width=width)
    wrapped_text = wrapper.fill(text=text)

    return wrapped_text