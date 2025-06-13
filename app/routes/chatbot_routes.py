# from flask import Blueprint, request, jsonify
# from transformers import GPT2Tokenizer, GPT2LMHeadModel
# import torch

# chatbot_bp = Blueprint("chatbot", __name__)
# tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
# model = GPT2LMHeadModel.from_pretrained('distilgpt2')

# @chatbot_bp.route("/inquiry", methods=["POST"])
# def inquiry():
#     try:
#         data = request.json
#         text = data.get("input", "")
#         if not text:
#             return jsonify({"status": False, "message": "No text provided"}), 400

#         # Tokenize input
#         input_ids = tokenizer.encode(text, return_tensors="pt")

#         # Generate output (max 50 tokens total)
#         output_ids = model.generate(input_ids, max_length=50, do_sample=True, top_k=50)

#         # Decode output tokens to text
#         generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

#         return jsonify({
#             "input": text,
#             "response": generated_text
#         })

#     except Exception as e:
#         return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
