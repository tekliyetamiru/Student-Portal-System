from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia

def home(request):
    return render(request,'dashboard/home.html')


def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} successfully")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('notes')

class NotesDetail(generic.DetailView):
    model=Notes

def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished =="on":
                    finished = True
                else:
                    finished = False
            except:
                finished=False
            homework=Homework(user=request.user,subject=request.POST['subject'],title=request.POST['title'],description=request.POST['description'],due=request.POST['due'],is_finished=finished)
            homework.save()
            messages.success(request,f"Home is Add to")
    else:
        form=HomeworkForm() 

    homework=Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    return render(request,'dashboard/homework.html',locals())

def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    print("homework is finished or not finished :",homework.is_finished)
    homework.save()
    return redirect('homework')

def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')

def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']   
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description']=desc
            print("r")
            result_list.append(result_dict)
            contexts= {'form':form,'results':result_list}
        return render(request,"dashboard/youtube.html",contexts)

    else:
        form=DashboardForm()

    return render(request,'dashboard/youtube.html',{'form':form})


def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos=Todo(user=request.user,title=request.POST['title'],is_finished=finished)
            todos.save()
            messages.success(request,f"Add new Todo {request.user.username} to list")
    else:
        form=TodoForm()
    todolist=Todo.objects.filter(user=request.user)
    if len(todolist) == 0:
        todos_done =True
    else:
        todos_done = False
    return render(request,'dashboard/todo.html',locals())

def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')
def update_todo(request,pk=None):
    data = Todo.objects.get(id=pk)
    if data.is_finished == True:
        data.is_finished = False
    else:
        data.is_finished = True
    data.save()
    return redirect('todo')

def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer= r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'), 
                'count':answer['items'][i]['volumeInfo'].get('pagecount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
            
            result_list.append(result_dict)
            contexts= {'form':form,'results':result_list}
        return render(request,"dashboard/books.html",contexts)

    else:
        form=DashboardForm()

    return render(request,'dashboard/books.html',{'form':form})


def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer= r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
        except: 
            return render(request,'dashboard/dictionary.html',locals())
    else:
        form = DashboardForm()
    
    return render(request,'dashboard/dictionary.html',locals())



def wiki(request):
    if request.method=='POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context={
           'form':form,
           'title':search.title,
           'link':search.url,
           'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form = DashboardForm()
    
    return render(request,'dashboard/wiki.html',locals())


def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            input =True
            m_form=measurement_form
            if'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'yard' and second =='foot':
                        answer = f'{input} yard ={int(input)*3} foot'
                    if first == 'foot' and second =='yard':
                        answer = f'{input} foot ={int(input)*3} yard'
                
       
        
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            input =True
            m_form=measurement_form
            if'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'pound' and second =='kilogram':
                        answer = f'{input} pound ={int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second =='pound':
                        answer = f'{input} kilogram ={int(input)*2.20462} pound'
                
       

    else:
        form = ConversionForm()
        input = False
    return render(request,'dashboard/conversion.html',locals())

def register(request):
    if request.method=="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username}")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request,'dashboard/register.html',locals())

def login(request):
    return render(request,'dashboard/login.html',locals())

# Create your views here.
