from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .form import AuthorForm
from . models import AuthorInfo, BookInfo

import openai
import os
# pythonanywhereにデプロイするときは以下は消すこと
#import environ

# env = environ.Env()
# env.read_env(os.path.join(os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__))), '.env'))

# .envファイルをpushしない！！！

def has_common_string(str1, str2):
    """
    2つの文字列に、3文字以上の共通の文字列があるかどうかを判定する関数。
    """
    common = set(str1) & set(str2)
    for c in common:
        if len(c.encode('utf-8')) >= 3:
            return True
    return False

class IndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        author_info_model = AuthorInfo.objects.all()
        context = {
            'response': "返信をここに表示します",
            'author_infos': author_info_model,
        }
        return render(request, 'index.html', context)
    def post(self, request, *args, **kwargs):
        openai.api_key = os.environ['GPT3_KEY']
        author_info_model = AuthorInfo.objects.all()
        input_text = request.POST['input-text']
        selected_author_id = request.POST['author_id']
        selected_author_info = AuthorInfo.objects.get(id=int(selected_author_id))
        book_name_list = [selected_author_info.book_name1, 
                          selected_author_info.book_name2, 
                          selected_author_info.book_name3]
        
        # 著書要約返信機能（最終的に、複数の章の要約をDBに保存でき、その中からランダムに返答できるようにする）
        for i, book_name in enumerate(book_name_list):
            if has_common_string(book_name, input_text):
                chatbot_response = BookInfo.objects.get(book_name=book_name).part_content_sum_list
                break
            elif "自己紹介" in input_text:
                chatbot_response = selected_author_info.intoroduction
            else:
                integrated_text = ""
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    # UIで選択した著者ジャンルに応じて切り替わるようにpromptを設計！
                    prompt="私: " + input_text + "\n松下幸之助:社長として回答します。 ",
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
                chatbot_response += poped_sentence

        context = {
            'response': chatbot_response,
            'input_text': input_text,
            'author_infos': author_info_model,
        }
        return render(request, 'index.html', context)
    
class AuthorCreateView(CreateView):
    model = AuthorInfo
    template_name = "post_author.html"
    form_class = AuthorForm
    success_url = reverse_lazy("app:author_create")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    # BookInfoに要約を登録する処理を書く
    def post(self, request):
        openai.api_key = os.environ['GPT3_KEY']
        request_data = request.POST

        author_info_model = AuthorInfo(author_name=request_data["author_name"],
                                       intoroduction=request_data["intoroduction"],
                                       author_type=request_data["author_type"],
                                       book_name1=request_data["book_name1"],
                                       book_content1=request_data["book_content1"],
                                       book_name2=request_data["book_name2"],
                                       book_content2=request_data["book_content2"],
                                       book_name3=request_data["book_name3"],
                                       book_content3=request_data["book_content3"])
        author_info_model.save()

        book_contents = []
        # book_nameのいずれかに入力があることを検出し、Trueの場合contentを配列に追加する
        if request_data["book_name1"]:
            book_contents.append([request_data["book_name1"], request_data["book_content1"]])
        if request_data["book_name2"]:
            book_contents.append([request_data["book_name2"], request_data["book_content2"]])
        if request_data["book_name3"]:
            book_contents.append([request_data["book_name3"], request_data["book_content3"]])

        new_author = AuthorInfo.objects.all().last()
        # 配列の数だけAPIを叩いて要約を作成し、それをもとにbook_infoモデルのレコードを作成する
        for book_content in book_contents:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=book_content[1]+ "\n\nまとめ:\n",
                temperature=0.7,
                max_tokens=int(300),
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            part_content_sum_list = response['choices'][0]['text']
            book_info_model = BookInfo(book_name=book_content[0], author=new_author, part_content_sum_list=part_content_sum_list)
            book_info_model.save()
        return redirect("app:author_create")
            
        