import os
import json
import requests
import modules.scripts as scripts
import gradio as gr
from modules.shared import opts, OptionInfo
from modules import shared

class DeepseekPrompts(scripts.Script):
    def __init__(self):
        super().__init__()
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.default_system_prompt = """You are an expert prompt engineer for Stable Diffusion. 
        Generate creative, detailed prompts that will produce high-quality images. 
        Include relevant artistic styles, composition details, and quality modifiers."""
        shared.log.info("DeepseekPrompts: Initializing plugin")
        
    def title(self):
        return "Deepseek Prompts"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def ui(self, is_img2img):
        shared.log.info("DeepseekPrompts: Building UI components")
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
        
        shared.log.info("DeepseekPrompts: UI setup complete")
        return [prompt_input, output]
    
    def generate_prompts(self, prompt, num_variations, creativity, system_prompt):
        shared.log.info(f"DeepseekPrompts: generate_prompts called with: prompt='{prompt}' variations={num_variations} creativity={creativity}")
        
        if not prompt.strip():
            shared.log.error("DeepseekPrompts: Empty prompt received")
            return "Please enter a prompt first."
        
        api_key = self.get_api_key()
        if not api_key:
            shared.log.error("DeepseekPrompts: No API key configured")
            return "Error: No Deepseek API key configured. Please set your API key in settings."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        user_prompt = f"""Generate {num_variations} distinct variations of this Stable Diffusion prompt. 
        Each variation should maintain the core concept but explore different styles, details, and enhancements.
        Return each variation on a new line with a number prefix (1., 2., etc.).
        
        Original prompt: {prompt}"""
        
        payload = {
            "model": opts.data.get("deepseek_default_model", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": creativity,
            "max_tokens": 2000
        }
        
        shared.log.debug(f"DeepseekPrompts: API request payload: {json.dumps(payload, indent=2)}")
        
        try:
            shared.log.info("DeepseekPrompts: Sending request to Deepseek API")
            response = requests.post(self.api_url, headers=headers, json=payload)
            shared.log.debug(f"DeepseekPrompts: API response status: {response.status_code}")
            shared.log.debug(f"DeepseekPrompts: API response headers: {response.headers}")
            
            response.raise_for_status()
            
            response_json = response.json()
            shared.log.debug(f"DeepseekPrompts: API response body: {json.dumps(response_json, indent=2)}")
            
            if 'choices' not in response_json or len(response_json['choices']) == 0:
                shared.log.error("DeepseekPrompts: Invalid response format - no choices")
                return "Error: Invalid response format from API"
                
            content = response_json['choices'][0]['message']['content']
            shared.log.info(f"DeepseekPrompts: Successfully generated prompts: {content[:100]}...")
            return content
            
        except requests.exceptions.RequestException as e:
            shared.log.error(f"DeepseekPrompts: API request failed: {str(e)}")
            return f"API Error: {str(e)}"
        except json.JSONDecodeError as e:
            shared.log.error(f"DeepseekPrompts: Failed to parse API response: {str(e)}")
            return f"Error parsing API response: {str(e)}"
        except Exception as e:
            shared.log.error(f"DeepseekPrompts: Unexpected error: {str(e)}", exc_info=True)
            return f"Unexpected error: {str(e)}"
    
    def enhance_prompt(self, prompt, creativity, system_prompt):
        shared.log.info(f"DeepseekPrompts: enhance_prompt called with: prompt='{prompt}' creativity={creativity}")
        
        if not prompt.strip():
            shared.log.error("DeepseekPrompts: Empty prompt received")
            return "Please enter a prompt first."
            
        api_key = self.get_api_key()
        if not api_key:
            shared.log.error("DeepseekPrompts: No API key configured")
            return "Error: No Deepseek API key configured. Please set your API key in settings."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        user_prompt = f"""Improve this Stable Diffusion prompt by adding more detail, better structure, 
        and quality modifiers while keeping the original meaning. Return only the enhanced prompt.
        
        Original prompt: {prompt}"""
        
        payload = {
            "model": opts.data.get("deepseek_default_model", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": creativity,
            "max_tokens": 500
        }
        
        shared.log.debug(f"DeepseekPrompts: API request payload: {json.dumps(payload, indent=2)}")
        
        try:
            shared.log.info("DeepseekPrompts: Sending enhancement request to Deepseek API")
            response = requests.post(self.api_url, headers=headers, json=payload)
            shared.log.debug(f"DeepseekPrompts: API response status: {response.status_code}")
            
            response.raise_for_status()
            
            response_json = response.json()
            shared.log.debug(f"DeepseekPrompts: API response body: {json.dumps(response_json, indent=2)}")
            
            content = response_json['choices'][0]['message']['content']
            shared.log.info(f"DeepseekPrompts: Successfully enhanced prompt: {content}")
            return content
            
        except Exception as e:
            shared.log.error(f"DeepseekPrompts: Error enhancing prompt: {str(e)}", exc_info=True)
            return f"Error enhancing prompt: {str(e)}"
    
    def use_prompt(self, generated_prompts):
        shared.log.info(f"DeepseekPrompts: use_prompt called with: generated_prompts='{generated_prompts[:50]}...'")
        
        if not generated_prompts.strip():
            shared.log.warning("DeepseekPrompts: No generated prompts to use")
            return ""
            
        if "\n" in generated_prompts:
            prompt = generated_prompts.split("\n")[0].split(". ", 1)[-1]
            shared.log.info(f"DeepseekPrompts: Selected first prompt: {prompt}")
            return prompt
        shared.log.info(f"DeepseekPrompts: Using single prompt: {generated_prompts}")
        return generated_prompts
    
    def get_api_key(self):
        api_key = opts.data.get("deepseek_api_key", os.getenv("DEEPSEEK_API_KEY", ""))
        if api_key:
            shared.log.debug("DeepseekPrompts: API key found in configuration")
        else:
            shared.log.warning("DeepseekPrompts: No API key configured")
        return api_key
    
    @staticmethod
    def on_ui_settings():
        shared.log.info("DeepseekPrompts: Registering UI settings")
        section = ("deepseek", "Deepseek")
        opts.add_option("deepseek_api_key", OptionInfo(
            "", "API Key", section=section
        ))
        opts.add_option("deepseek_default_model", OptionInfo(
            "deepseek-chat", "Default Model", section=section
        ))
