# text-2-cad
Early attempt to create an engine able to generate steerable CAD from text input. Most of the solutions to this problem use Gaussian Splatting and large image generative models. This project aims to create a more lightweight and steerable solution. LLMs proved to be very effective in writing high-resource languages, such as Python. For CAD, one of the most used scripting languages is OpenSCAD. What if we ask LLMs to generate OpenSCAD code? This is the main idea behind this project.
After the generation, this solution would also allow the user to tweak parameters and re-generate the CAD model. This would allow the user to steer the generation process and obtain the desired CAD model. With Gaussian Splatting, this is not possible, as the generation process is not steerable.

Currently, it is a naive implementation, leveraging vanilla OpenAI API, or augmented via RAG, using a vector DB of the OpenSCAD documentation. This works only for very simple shapes. The next step is to gather a dataset of OpenSCAD scripts and the corresponding textual descriptions, to fine-tune an LLM. This would allow the model to generate more complex shapes, and to be more robust to the user input.

## Usage
Being a flask app, it can be run locally with:
```
python app.py
```
or deployed on a server, such as Heroku.

You need an environment variable called `OPENAI_API_KEY` containing your OpenAI API key.
