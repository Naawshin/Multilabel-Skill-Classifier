# Multilabel Skill Classifier & Job-Resume Skill Matcher

<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Transformers](https://img.shields.io/badge/Transformers-orange?style=for-the-badge)
![ONNX](https://img.shields.io/badge/ONNX-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
[![Hugging Face Spaces](https://img.shields.io/badge/HuggingFace%20Spaces-blue?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/goldphish2209/multilabel-skill-classifier)

**Multilabel skill classifier from tech job descriptions + Resume-Job matching system**

</div>

This project features a multilabel text classification model to extract hard and soft skills from tech job descriptions. The model was trained using data scraped from [Indeed](https://www.indeed.com/). The data was collected in two steps:
1. **Job URL collection:** Due to limitations I could only scrape 26k job links scraped from the first page of various job locations. The URL scraper can be found in `scraper\link_scraper.py` .
2. **Job Description Scraping:** Using the job URLs, the job descriptions were scraped with `scraper\job_description_scraper.py`.
All the scraped data can be found in the `data` folder.
## Key Features

- Detects **83 different skills** (hard + soft skills)
  - **Hard skills**: Python, SQL, JavaScript, React, Node.js, AWS, Docker, Git, Java, C++, etc.
  - **Soft skills**: Teamwork, Collaboration, Communication, Critical Thinking, Problem Solving, Leadership, Adaptability, etc.
- State-of-the-art transformer-based multilabel classification
- Best performing model: **ModernBERT** — near-perfect results
- Fast inference using **ONNX** runtime
- Live interactive demo on **Hugging Face Spaces**
- Full-featured **Flask web application** including:
  - Job Description → Skills Extraction
  - Resume ↔ Job Description → Skill Matching (shows matching & missing skills + confidence scores)

## Automated Labeling Pipeline
It seemed like a big task to manually label all 22k job descriptions. Hence, I used a rule-based multi-labeling system using regex.
### Here's how the labeling works:
1. **Comprehensive Skills Dictionary**  
   A total of **83 target skills** (hard + soft) were defined covering the most frequently mentioned competencies in tech job postings.

2. **Regex-Based Pattern Matching**  
   Each skill is associated with a carefully crafted regular expression that captures:
   - Common abbreviations used to define the skills
   - Different spellings & variations
   - Full names and short forms
   - Case-insensitive matching

3. **One-Hot Encoding**  
   For every job description, it was checked if the text contains any of the defined patterns for each skill. 
## Model Training and ONNX Inference
I initally started out with distilroberta-base. Then I explored 3 more transformer-based models and found modernbert to be the best among them with an accuracy score of 0.99. Finally, I converted the trained model into ONNX.
## Model Performance Comparison

| Model                  | Accuracy | F1-Samples | F1-Macro | F1-Micro |
|------------------------|----------|------------|----------|----------|
| distilroberta-base     | 0.9700   | 0.9446     | 0.9243   | 0.9498   |
| **modernbert** (best)  | **0.9996** | **0.9928** | **0.9969** | **0.9990** |
| all-MiniLM-L6-v2       | 0.9700   | 0.9028     | 0.8782   | 0.9081   |
| bert-base-uncased      | 0.9800   | 0.9304     | 0.9110   | 0.9348   |

## Model Deployment
The model was depployed in HugginFace Spaces Gradio App. You'll get the implementation in the `deployment` folder or in the [gradio app](https://huggingface.co/spaces/goldphish2209/multilabel-skill-classifier)
<div align="center">
<img src="https://github.com/user-attachments/assets/21903490-1e7a-48d8-bf52-a52ea2519ac9"
 alt="Gradio App Demo"/>
<br/>
<small>Fig: HuggingFace Spaces Gradio App Demo</small>
</div>

## Web Deployment
The Flask-based web app lets user extract skills from job descriptions and also match their resume with the required skills. Try the [Skill Extractor and Resume-Matcher](https://multilabel-skill-classifier.onrender.com) on Render.
<div align="center">
<img src="https://github.com/user-attachments/assets/af548153-6095-4cfa-a2d4-be26aae48906" width= 800 alt="Resume-Matcher App Demo"/>
<br/>
<small>Fig: Skill Analyzer and Resume-Matcher App Homepage</small>
</div>
<div align="center">
<img src="https://github.com/user-attachments/assets/56ceb40f-96e3-44c6-9b40-e820bd3862f8" width= 800 alt="Resume-Matcher App Demo"/>
<br/>
<small>Fig: Skill Analyzer Demo</small>
</div>

### Run Locally

```bash
# Clone the repo
git clone https://github.com/Naawshin/Multilabel-Skill-Classifier.git

# Switch to flask
git switch flask

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the app
python app.py
```

Feedback, feature requests, bug reports, and pull requests are **very welcome**!

Feel free to reach out:

- ✉️ Email: nawshintabassum88@gmail.com
- 🔗 LinkedIn: https://www.linkedin.com/in/nowshin-tabasum/

---

If this project helped you or you just found it interesting, please consider giving it a star ⭐ It really helps the project grow!

