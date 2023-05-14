from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.urls import reverse_lazy

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage


from .form import AuthorForm
from . models import AuthorInfo, BookInfo

import openai
import random
import csv
import os


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

def csv_to_array(file):
    # CSVファイルを読み込む
    csv_data = file.read().decode('utf-8').splitlines()
    # CSVファイルを配列に変換する
    data_array = []
    for row in csv.reader(csv_data):
        data_array.append(row)
    return data_array

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
        selected_author_name = selected_author_info.author_name
        selected_author_type = selected_author_info.author_type

        book_name_list = [selected_author_info.book_name1, 
                          selected_author_info.book_name2, 
                          selected_author_info.book_name3]
        chatbot_response = ""

        # 著書要約返信機能（最終的に、複数の章の要約をDBに保存でき、その中からランダムに返答できるようにする）
        # part_content_sum_listをカンマで分割し、乱数を生成してリクエスト毎にランダムに返す
        for i, book_name in enumerate(book_name_list):
            if has_common_string(book_name, input_text):
                sum_contents = BookInfo.objects.get(book_name=book_name).part_content_sum_list
                print(sum_contents)
                chatbot_response = random.choice(sum_contents.split(',')[:-1])
                break
            elif "自己紹介" in input_text:
                chatbot_response = selected_author_info.intoroduction
            else:
                integrated_text = ""
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    # UIで選択した著者ジャンルに応じて切り替わるようにpromptを設計済み
                    prompt="私: " + input_text + "\n"+ selected_author_name +":"+selected_author_type+"として回答します。 ",
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
        book_content1, book_content2, book_content3 = "", "", ""
        request_data = request.POST
        if "book_content1" in request.FILES:
            book_content1 = request.FILES["book_content1"]
        if "book_content2" in request.FILES:
            book_content2 = request.FILES["book_content2"]
        if "book_content3" in request.FILES:
            book_content3 = request.FILES["book_content3"]

        author_info_model = AuthorInfo(author_name=request_data["author_name"],
                                       intoroduction=request_data["intoroduction"],
                                       author_type=request_data["author_type"],
                                       book_name1=request_data["book_name1"],
                                       book_content1=book_content1,
                                       book_name2=request_data["book_name2"],
                                       book_content2=book_content2,
                                       book_name3=request_data["book_name3"],
                                       book_content3=book_content3)
        author_info_model.save()

        book_contents = []
        # 済　book_nameのいずれかに入力があることを検出し、Trueの場合contentを配列に追加する
        if request_data["book_name1"]:
            book_contents.append([request_data["book_name1"]])
        if request_data["book_name2"]:
            book_contents.append([request_data["book_name2"]])
        if request_data["book_name3"]:
            book_contents.append([request_data["book_name3"]])

        new_author = AuthorInfo.objects.all().last()
        # 済　配列の数だけAPIを叩いて要約を作成し、それをもとにbook_infoモデルのレコードを作成する
        for i, book_content in enumerate(book_contents):
            # print(request.FILES["book_content"+str(i+1)])
            file = None
            if i==0:
                file = AuthorInfo.objects.get(pk=author_info_model.pk).book_content1
            elif i==1:
                file = AuthorInfo.objects.get(pk=author_info_model.pk).book_content2
            elif i==2:
                file = AuthorInfo.objects.get(pk=author_info_model.pk).book_content3

            # dfを行単位で分割して、２列目の章内容だけ扱う。行の数だけループさせて、複数の要約テキストをカンマで連結して取得する
            book_content_parts = [row[1] for row in csv_to_array(file)]
            
            part_content_sum_list = ""
            for book_content_part in book_content_parts:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=book_content_part+ "\n\nまとめ:\n",
                    temperature=0.7,
                    max_tokens=int(300),
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                part_content_sum_list += response['choices'][0]['text'] + ","
            book_info_model = BookInfo(book_name=book_content[0], author=new_author, part_content_sum_list=part_content_sum_list)
            book_info_model.save()
        return redirect("app:author_create")
            
        