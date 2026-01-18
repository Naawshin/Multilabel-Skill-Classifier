import gradio as gr
import onnxruntime as rt
from transformers import AutoTokenizer
import torch
import json

print("ONNX Runtime loaded:", rt.__version__)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilroberta-base")

# Load skill mapping
with open("skill_mapping.json", "r") as f:
    skill_id = json.load(f)

skills = list(skill_id.keys())

# Load ONNX model
inf_session = rt.InferenceSession('skill-classifier.onnx')
input_name = inf_session.get_inputs()[0].name
output_name = inf_session.get_outputs()[0].name

def classify_job_skills(job_description, threshold=0.5):
    """
    Classify skills from a job description
    
    Args:
        job_description: Text of the job posting
        threshold: Minimum confidence score (0-1)
    
    Returns:
        Dictionary of skill -> probability for skills above threshold
    """
    if not job_description.strip():
        return {}
    
    # Tokenize input (truncate to 512 tokens)
    input_ids = tokenizer(job_description, truncation=True, max_length=512)['input_ids']
    
    # Run inference
    logits = inf_session.run([output_name], {input_name: [input_ids]})[0]
    
    # Convert to probabilities
    probs = torch.sigmoid(torch.FloatTensor(logits))[0]
    
    # Filter by threshold and return top skills
    results = {
        skill: float(prob) 
        for skill, prob in zip(skills, probs) 
        if prob >= threshold
    }
    
    # Sort by probability (highest first)
    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

# Example job descriptions
examples = [
    [
        """We're looking for a Senior Machine Learning Engineer to join our team. 
        Responsibilities include building ML pipelines, training deep learning models, 
        and deploying models to production using AWS and Docker. Strong Python skills required, 
        along with experience in PyTorch or TensorFlow. Knowledge of MLOps practices and 
        CI/CD pipelines is a plus.""",
        0.5
    ],
    [
        """Full Stack Developer needed! Must have strong JavaScript, React, and Node.js experience. 
        You'll be building responsive web applications, working with REST APIs, and managing 
        databases (SQL/NoSQL). Familiarity with Git, Docker, and cloud platforms (AWS/Azure) 
        is required. Great communication and teamwork skills essential.""",
        0.5
    ],
    [
        """Data Analyst position available. Looking for someone skilled in SQL, Python, and 
        Excel for data analysis and visualization. Experience with Tableau or Power BI required. 
        You'll perform EDA, create dashboards, and communicate insights to stakeholders. 
        Strong attention to detail and problem-solving skills needed.""",
        0.5
    ]
]

# Create Gradio interface
with gr.Blocks(title="Job Skills Classifier") as iface:
    gr.Markdown(
        """
        # 🎯 Job Skills Classifier
        
        Extract required skills from job descriptions using AI. 
        Powered by DistilRoBERTa fine-tuned on 21k+ job postings.
        """
    )
    
    with gr.Row():
        with gr.Column():
            job_input = gr.Textbox(
                lines=8,
                placeholder="Paste a job description here...",
                label="Job Description"
            )
            threshold_slider = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.5,
                step=0.05,
                label="Confidence Threshold",
                info="Only show skills with probability above this value"
            )
            classify_btn = gr.Button("Classify Skills", variant="primary")
        
        with gr.Column():
            output_label = gr.Label(
                num_top_classes=20,
                label="Detected Skills"
            )
    
    gr.Markdown("### 💡 Try these examples:")
    gr.Examples(
        examples=examples,
        inputs=[job_input, threshold_slider],
        outputs=output_label,
        fn=classify_job_skills,
        cache_examples=False
    )
    
    gr.Markdown(
        """
        ---
        ### 📊 About
        
        This model detects **technical skills** (Python, Machine Learning, AWS, etc.) and 
        **soft skills** (Communication, Leadership, Problem Solving, etc.) from job descriptions.
        
        **Skills covered:** 80+ technical and soft skills across software development, 
        data science, cloud computing, and more.
        
        """
    )
    
    # Connect button to function
    classify_btn.click(
        fn=classify_job_skills,
        inputs=[job_input, threshold_slider],
        outputs=output_label
    )

# Launch
iface.launch()