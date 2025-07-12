import os
import json
import requests
import modules.scripts as scripts
import gradio as gr
from modules.shared import opts, OptionInfo

class DeepseekPrompts(scripts.Script):
    def __init__(self):
        super().__init__()
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.default_system_prompt = """You are an expert prompt engineer for Stable Diffusion. 
        Generate creative, detailed prompts that will produce high-quality images. 
        Include relevant artistic styles, composition details, and quality modifiers."""
        
    def title(self):
        return "Deepseek Prompts"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def ui(self, is_img2img):
        with gr.Accordion("Deepseek Prompt Generator", open=False):
            with gr.Row():
                with gr.Column(scale=3):
                    prompt_input = gr.Textbox(label="Initial Prompt", lines=3, placeholder="Enter your base prompt here...")
                    with gr.Row():
                        num_variations = gr.Slider(1, 10, value=3, step=1, label="Number of Variations")
                        creativity = gr.Slider(0.1, 1.0, value=0.7, step=0.1, label="Creativity")
                    with gr.Row():
                        enhance_btn = gr.Button("Enhance Prompt", variant="primary")
                        generate_btn = gr.Button("Generate Variations", variant="primary")
                    system_prompt = gr.Textbox(label="System Prompt", value=self.default_system_prompt, lines=2)
                with gr.Column(scale=2):
                    output = gr.Textbox(label="Generated Prompts", lines=8, interactive=True)
                    with gr.Row():
                        use_btn = gr.Button("Use Selected", variant="secondary")
                        clear_btn = gr.Button("Clear", variant="secondary")
        
        generate_btn.click(
            fn=self.generate_prompts,
            inputs=[prompt_input, num_variations, creativity, system_prompt],
            outputs=[output]
        )
        
        enhance_btn.click(
            fn=self.enhance_prompt,
            inputs=[prompt_input, creativity, system_prompt],
            outputs=[output]
        )
        
        use_btn.click(
            fn=self.use_prompt,
            inputs=[output],
            outputs=[self.prompt_textbox]
        )
        
        clear_btn.click(
            fn=lambda: "",
            inputs=[],
            outputs=[output]
        )
        
        return [prompt_input, output]
    
    def generate_prompts(self, prompt, num_variations, creativity, system_prompt):
        if not prompt.strip():
            return "Please enter a prompt first."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_api_key()}"
        }
        
        user_prompt = f"""Generate {num_variations} distinct variations of this Stable Diffusion prompt. 
        Each variation should maintain the core concept but explore different styles, details, and enhancements.
        Return each variation on a new line with a number prefix (1., 2., etc.).
        
        Original prompt: {prompt}"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": creativity,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating prompts: {str(e)}"
    
    def enhance_prompt(self, prompt, creativity, system_prompt):
        if not prompt.strip():
            return "Please enter a prompt first."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_api_key()}"
        }
        
        user_prompt = f"""Improve this Stable Diffusion prompt by adding more detail, better structure, 
        and quality modifiers while keeping the original meaning. Return only the enhanced prompt.
        
        Original prompt: {prompt}"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": creativity,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error enhancing prompt: {str(e)}"
    
    def use_prompt(self, generated_prompts):
        # Get the first prompt if multiple are generated
        if "\n" in generated_prompts:
            return generated_prompts.split("\n")[0].split(". ", 1)[-1]
        return generated_prompts
    
    def get_api_key(self):
        # Get from settings or environment variable
        return opts.data.get("deepseek_api_key", os.getenv("DEEPSEEK_API_KEY", ""))
    
    @staticmethod
    def on_ui_settings():
        section = ("deepseek", "Deepseek")
        opts.add_option("deepseek_api_key", OptionInfo(
            "", "API Key", section=section
        ))
        opts.add_option("deepseek_default_model", OptionInfo(
            "deepseek-chat", "Default Model", section=section
        ))
