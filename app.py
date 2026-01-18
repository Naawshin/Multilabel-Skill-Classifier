from flask import Flask, render_template, request
from gradio_client import Client

app = Flask(__name__)

# Initialize Gradio client
client = Client("goldphish2209/multilabel-skill-classifier")

def parse_skills(result):
    """Parse skills from Gradio/HuggingFace result"""
    skills = []
    
    print("DEBUG - Result type:", type(result))
    print("DEBUG - Result content:", result)
    
    # The API returns: {"label": "...", "confidences": [{"label": "...", "confidence": ...}, ...]}
    if isinstance(result, dict) and 'confidences' in result:
        confidences_list = result['confidences']
        
        if isinstance(confidences_list, list):
            for item in confidences_list:
                if isinstance(item, dict):
                    skill_name = item.get('label', 'Unknown')
                    confidence = item.get('confidence', 0)
                    
                    try:
                        skills.append({
                            'skill': str(skill_name).strip(),
                            'confidence': round(float(confidence), 2)
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing skill: {e}")
                        continue
    
    # Sort by confidence descending
    return sorted(skills, key=lambda x: x['confidence'], reverse=True)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        action = request.form.get('action')
        
        if action == 'analyze_job':
            job_description = request.form['job_description']
            threshold = float(request.form.get('threshold', 0.5))
            
            # Get predictions from Hugging Face Space
            result = client.predict(
                job_description=job_description,
                threshold=threshold,
                api_name="/classify_job_skills"
            )

            print("RAW RESULT:", result)
            
            skills = parse_skills(result)
            
            print("PARSED SKILLS:", skills)
            
            return render_template(
                "index.html",
                show_job_results=True,
                job_description=job_description,
                skills=skills,
                total_skills=len(skills),
                threshold=threshold
            )
        
        elif action == 'match_resume':
            resume_text = request.form['resume_text']
            job_text = request.form['job_text']
            threshold = float(request.form.get('threshold', 0.5))
            
            # Get skills from job description
            job_result = client.predict(
                job_description=job_text,
                threshold=threshold,
                api_name="/classify_job_skills"
            )
            
            # Get skills from resume
            resume_result = client.predict(
                job_description=resume_text,  # Using same parameter name
                threshold=threshold,
                api_name="/classify_job_skills"
            )
            
            # Parse results
            job_skills = parse_skills(job_result)
            resume_skills = parse_skills(resume_result)
            
            print("JOB SKILLS:", job_skills)
            print("RESUME SKILLS:", resume_skills)
            
            # Create sets for comparison (case-insensitive)
            job_skill_set = {skill['skill'].lower() for skill in job_skills}
            resume_skill_set = {skill['skill'].lower() for skill in resume_skills}
            
            # Find matches and missing
            matching = job_skill_set & resume_skill_set
            missing = job_skill_set - resume_skill_set
            
            # Calculate match percentage
            if len(job_skill_set) == 0:
                match_percentage = 0
            else:
                match_percentage = round((len(matching) / len(job_skill_set)) * 100, 1)
            
            # Get full skill objects
            matching_skills = [
                s for s in job_skills if s['skill'].lower() in matching
            ]
            missing_skills = [
                s for s in job_skills if s['skill'].lower() in missing
            ]
            
            return render_template(
                "index.html",
                show_resume_results=True,
                match_percentage=match_percentage,
                matching_skills=matching_skills,
                missing_skills=missing_skills,
                total_matching=len(matching_skills),
                total_missing=len(missing_skills),
                resume_text=resume_text,
                job_text=job_text,
                threshold=threshold
            )
    
    # GET request - show landing page
    return render_template("index.html")


if __name__ == "__main__":
    print("Starting Skill Analyzer...")
    print("Connecting to Hugging Face Space: goldphish2209/multilabel-skill-classifier")
    app.run(debug=True)