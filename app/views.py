from django.shortcuts import render
from django.views.generic import TemplateView

import openai
import os
import environ

env = environ.Env()
env.read_env(os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), '.env'))


class IndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = {
            'response': "返信をここに表示します",
        }
        return render(request, 'index.html', context)
    def post(self, request, *args, **kwargs):
        openai.api_key = env('GPT3_KEY')
        input_text = request.POST['input-text']
        #engine_type = request.POST['engine type']

        integrated_text = ""
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="私: " + input_text + "\n松下幸之助: ",
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=1,
            presence_penalty=0,

        )

        response_text = response['choices'][0]['text']

        sentence_list = response_text.split("。")
        sentence_list.pop(-1)
        poped_sentence = "。".join(sentence_list)
        poped_sentence += "。"
        integrated_text += poped_sentence

        context = {
            'response': integrated_text,
            'input_text': input_text,
        }
        return render(request, 'index.html', context)