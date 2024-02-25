from flask import Flask, render_template, request
import pandas as pd
import google.generativeai as genai
import google.ai.generativelanguage as glm
# import API_KEY
import numpy as np
import os

app = Flask(__name__)

embeddings_df = pd.read_json("book_embeddings.json")

# genai.configure(api_key=API_KEY.api_key().GOOGLE_API_KEY)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def do_dot(x,y):
    return np.dot(x,y)

def format_lists(text):
    return text.split("\n")

def get_best_match(text,best_num):
    model = 'models/embedding-001'
    embedding_Q = genai.embed_content(model=model,
                                content="i want recipe of " + text,
                                task_type="RETRIEVAL_QUERY")['embedding']
    e_df = embeddings_df.copy()
    e_df['score'] = embeddings_df.apply(lambda x:do_dot(x['embeddings'],embedding_Q),axis=1)
    e_df.sort_values(by=['score'],ascending=False,inplace=True)
    relevant_text = ''
    for i in range(0,best_num):
        relevant_text = relevant_text + str(e_df.iloc[i]['text'])
    return relevant_text

def make_prompt(query, relevant_text):
  prompt = '''
    You are an informative bot and please use the relevant text provided and answer the question.
    Please provide only the recipe. The question is ''' + query + ''' The relevant text is ''' + relevant_text
  return prompt

# Simulated function to get recipe details
def get_recipe_details(recipe_name):
    # In a real application, this function would fetch recipe details based on the recipe name.
    # Here, we're just simulating a response.
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                pass
    except:
        return ["Error in Connecting Gemini API"]
    
    try:
        query = "i want recipe of " + recipe_name
        prompt = make_prompt(query=query,relevant_text=get_best_match(query,5))
        gen_model = genai.GenerativeModel('gemini-1.0-pro')
        answer = gen_model.generate_content(prompt)
        return format_lists(answer.text)
    except Exception as e:
        print(e)
        return ["Error in API"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        recipe_name = request.form['recipeName']
        recipe_details = get_recipe_details(recipe_name)
        return render_template('index.html', recipe=recipe_details)
    return render_template('index.html', recipe=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)