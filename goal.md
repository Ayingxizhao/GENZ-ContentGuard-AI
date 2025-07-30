goal: develop and deploy a AI-powered system that 
can accurtately idnetify and guard against 
malicious language used by GENZ on

problem: 
1. dynamic nature of language
2. contextual understanding
3. ethical
4. implications
5. data scarcity //synthetic data generation

propose pipeline:
1. data collection:
    - define what are genz language and define what are the malicious language
    - collect data. scraping publicly available data. reddit.
    - synetic data generation: 
2. data annotation:
    - high quality annotation
3. processing
    - raw data involve with emojis, tokenization, lowercasing, removal of urls,
    handling of common internet abbreviations, handling of common internet slang
4. base llm selction: chatgpt, llama, etc.
5. fine-tuning: Pytorch 
classification and prediction: 

Curren step:
- have the data 
- letting LLM to determine the malicous 
    - we need human-in-the-loop system # 20 (10/malicious, 10/nonmalicious), 20 
    - Gen Z slang changes rapidly. An LLM, even a large one, might not be up-to-date with the very latest terms or how existing terms are being used in new, malicious ways. Its knowledge is based on its last training data.
- we need examples and non-examples of whats maclious
    - define categories: hate-speech, harassment, threats of violence, misinformation.
    - we need context nuances. 
        1. data annotation
        2. Data processing
            a. cleaning + normalization + tokenization