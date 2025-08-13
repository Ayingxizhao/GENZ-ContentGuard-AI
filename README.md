# HAI_project - ContentGuard AI

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

## 🚀 Web Application

We've developed a **ContentGuard AI** web application that provides real-time malicious content detection through a modern web interface.

### Features
- **Real-time Analysis**: Instant AI-powered content analysis
- **Modern UI**: Clean, responsive web interface
- **Gen Z Language Support**: Optimized for internet slang and modern language patterns
- **API Integration**: Uses OpenAI's GPT models for accurate detection

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with your OpenAI API key
3. Run the application: `python run.py`
4. Open browser to: `http://localhost:5001`

### Files
- `app.py` - Main Flask application
- `templates/index.html` - Web interface
- `static/css/style.css` - Styling
- `static/js/script.js` - Interactive functionality
- `config.py` - Configuration management
- `run.py` - Application launcher

For detailed setup instructions, see [SETUP.md](SETUP.md).
