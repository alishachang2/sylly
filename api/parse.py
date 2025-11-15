# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("numind/NuExtract", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("numind/NuExtract", trust_remote_code=True)
messages = [
    {"role": "user", "content": "Who are you?"},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=40)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))

import torch
from transformers import AutoProcessor, AutoModelForVision2Seq

model_name = "numind/NuExtract-2.0-2B"
# model_name = "numind/NuExtract-2.0-8B"

model = AutoModelForVision2Seq.from_pretrained(model_name, 
                                               trust_remote_code=True, 
                                               torch_dtype=torch.bfloat16,
                                               attn_implementation="flash_attention_2",
                                               device_map="auto")
processor = AutoProcessor.from_pretrained(model_name, 
                                          trust_remote_code=True, 
                                          padding_side='left',
                                          use_fast=True)

# You can set min_pixels and max_pixels according to your needs, such as a token range of 256-1280, to balance performance and cost.
# min_pixels = 256*28*28
# max_pixels = 1280*28*28
# processor = AutoProcessor.from_pretrained(model_name, min_pixels=min_pixels, max_pixels=max_pixels)

class Returnvalues:
    def __init__(event_name, date, time):
        self.event_name = event_name
        self.date = date
        self.time = time