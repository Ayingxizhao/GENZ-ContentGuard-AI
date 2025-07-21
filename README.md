# HAI_project

# conference: ICML, ICLR, Neurips, AAAI, CVPR

# 1. Papers to Read
some good papers to read:
https://arxiv.org/pdf/2311.03449

hate speech in multi-modal [https://proceedings.neurips.cc/paper_files/paper/2024/file/586640cda3db2dc77349013dcefee456-Paper-Datasets_and_Benchmarks_Track.pdf]

# 2. Project Description
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
