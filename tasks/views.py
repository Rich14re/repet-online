# views.py
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm, TaskForm, AnswerForm, CourseForm, ExplainForm, ExplanationTitleForm, ComputerScienceTaskForm , CustomAuthenticationForm, ComputerScienceTaskForm, ComputerScienceTaskDetailForm
from .models import Class, Course, Task, UserTaskStatus, Course, Profile, Explanation, Explain, ComputerScienceTask, ComputerScienceTask, ComputerScienceTaskDetail, Status

def home_view(request):
    return render(request, 'tasks/home.html')

@login_required
def payment_success(request, status_name):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    status, created = Status.objects.get_or_create(name=status_name)
    profile.statuses.add(status)
    profile.save()

    return render(request, 'tasks/payment_success.html', {'user': user})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})

@login_required
def account_view(request):
    user_statuses = request.user.profile.statuses.all()
    users = User.objects.all()
    user_answers = {}
    
    for user in users:
        incorrect_answers = UserTaskStatus.objects.filter(user=user, is_correct=False)
        if incorrect_answers.exists():
            user_answers[user] = incorrect_answers
    
    
    context = {
        'user_statuses': user_statuses,
        'user_answers': user_answers if request.user.is_superuser else None,
    }
    return render(request, 'tasks/account.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def course_view(request):
    tasks = Task.objects.all()
    explainses = Explanation.objects.all()
    user_status = {status.task_id: status.status for status in UserTaskStatus.objects.filter(user=request.user)}

    context = {
        'tasks': tasks,
        'explainses': explainses,
        'user_status': user_status,
    }
    return render(request, 'tasks/course.html', context)

@login_required
def task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user_status, created = UserTaskStatus.objects.get_or_create(user=request.user, task=task)
    
    if request.method == 'POST':
        print("Form submission detected.")
        form = AnswerForm(request.POST, instance=user_status)
        if form.is_valid():
            user_status = form.save(commit=False)
            user_status.is_correct = (user_status.answer == task.correct_answer)
            print("User's answer:", user_status.answer)  # Debug print
            print("Correct answer:", task.correct_answer)  # Debug print
            print("Is correct:", user_status.is_correct)  # Debug print
            if not user_status.is_correct:
                user_status.total_answer = user_status.answer
                print("Stored incorrect answer:", user_status.total_answer)  # Debug print
            user_status.save()
            return redirect('task', task_id=task.id)
    else:
        form = AnswerForm(instance=user_status)
    
    return render(request, 'tasks/task_detail.html', {'task': task, 'user_status': user_status, 'form': form})


def check_answer(task, answer):
    correct_answer = "правильный ответ"
    return answer == correct_answer

@user_passes_test(lambda u: u.is_superuser)
def add_explanation(request):
    if request.method == 'POST':
        title_form = ExplanationTitleForm(request.POST)
        explanation_forms = [ExplainForm(request.POST, request.FILES, prefix=str(i)) for i in range(1, 16)]

        if title_form.is_valid():
            title_instance = title_form.save()  # Сохраняем объект Explain
            for form in explanation_forms:
                if form.is_valid() and form.cleaned_data.get('description'):
                    explanation = form.save(commit=False)
                    explanation.explain = title_instance  # Устанавливаем связь с Explain
                    explanation.save()
            return redirect('course_list')

    else:
        title_form = ExplanationTitleForm()
        explanation_forms = [ExplainForm(prefix=str(i)) for i in range(1, 16)]

    context = {
        'title_form': title_form,
        'explanation_forms': explanation_forms,
    }
    return render(request, 'tasks/add_explanation.html', context)

@login_required
def course_list(request):
    courses = Course.objects.all()
    explains = Explain.objects.all()
    user_statuses = request.user.profile.statuses.all()

    # Создаем словарь с информацией о доступности каждого курса для пользователя
    course_access = {course: course.required_status in user_statuses for course in courses}

    # Проверка наличия конкретных статусов
    has_advanced_access = user_statuses.filter(name='advanced').exists()
    has_premium_access = user_statuses.filter(name='premium').exists()
    has_gold_access = user_statuses.filter(name='gold').exists()
    has_platinum_access = user_statuses.filter(name='platinum').exists()
    
    course_tasks = {
        1: Task.objects.filter(course_id=1),
        2: Task.objects.filter(course_id=2),
        3: Task.objects.filter(course_id=3),
        4: Task.objects.filter(course_id=4),
    }

    return render(request, 'tasks/course_list.html', {
        'courses': courses,
        'explains': explains,
        'course_access': course_access,
        'has_advanced_access': has_advanced_access,
        'has_premium_access': has_premium_access,
        'has_gold_access': has_gold_access,
        'has_platinum_access': has_platinum_access,
        'course_tasks': course_tasks,
    })

@user_passes_test(lambda u: u.is_superuser)
def add_task(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        task_forms = [TaskForm(request.POST, request.FILES, prefix=str(i)) for i in range(25)]

        if course_form.is_valid():
            # Сохраняем курс, используя данные из формы
            course = course_form.save()

            # Определяем id курса на основе grade
            grade = course_form.cleaned_data['grade']
            if grade == '6class':
                course_id = 1
            elif grade == '7class':
                course_id = 2
            elif grade == '8class':
                course_id = 3
            elif grade == '9class':
                course_id = 4
            else:
                course_id = None  # Обработка случаев, когда grade не соответствует ожидаемым значениям

            if course_id is not None:
                course_instance = course

                for i, tf in enumerate(task_forms):
                    if tf.is_valid() and tf.cleaned_data.get('description'):
                        task = tf.save(commit=False)
                        task.course = course_instance
                        task.save()

                return redirect('course_list')

    else:
        existing_courses = Course.objects.all()
        course_form = CourseForm()
        task_forms = [TaskForm(prefix=str(i), instance=existing_courses[i-1].tasks.first()) if i <= existing_courses.count() else TaskForm(prefix=str(i)) for i in range(1, 26)]

    return render(request, 'tasks/add_task.html', {'course_form': course_form, 'task_forms': task_forms})

@login_required
def task_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    theoretical_tasks = course.tasks.filter(is_theory=True)
    practical_tasks = course.tasks.filter(is_theory=False)
    
    user_statuses = request.user.profile.statuses.all()

    # Создаем словарь с информацией о доступности каждого курса для пользователя
    course_access = {course: course.required_status in user_statuses}

    # Проверка наличия конкретных статусов
    has_advanced_access = user_statuses.filter(name='advanced').exists()
    has_premium_access = user_statuses.filter(name='premium').exists()
    has_gold_access = user_statuses.filter(name='gold').exists()
    has_platinum_access = user_statuses.filter(name='platinum').exists()

    if request.method == 'POST' and 'proceed_to_practice' not in request.POST:
        results = []
        for task in practical_tasks:
            user_answer = request.POST.get(f'answer_{task.id}')
            user_status, created = UserTaskStatus.objects.get_or_create(user=request.user, task=task)
            user_status.answer = user_answer
            user_status.is_correct = (user_answer == task.correct_answer)
            if not user_status.is_correct:
                user_status.total_answer = user_answer
            user_status.save()
            results.append((task, user_answer, user_status.is_correct))

        return render(request, 'tasks/task_detail.html', {
            'course': course,
            'theoretical_tasks': theoretical_tasks,
            'practical_tasks': practical_tasks,
            'results': results,
            'show_practical_tasks': True,
        })

    return render(request, 'tasks/task_detail.html', {
        'course': course,
        'theoretical_tasks': theoretical_tasks,
        'practical_tasks': practical_tasks,
        'course_access': course_access,
        'has_advanced_access': has_advanced_access,
        'has_premium_access': has_premium_access,
        'has_gold_access': has_gold_access,
        'has_platinum_access': has_platinum_access,
        'show_practical_tasks': 'proceed_to_practice' in request.POST,
    })

@login_required
def explanation_detail(request, explain_id):
    explanation = get_object_or_404(Explain, id=explain_id)
    explains = explanation.explains.all()  

    return render(request, 'tasks/explanation_detail.html', {'explains': explains, 'explanation': explanation})
    
def computer_science_tasks(request):
    tasks = ComputerScienceTask.objects.all()
    return render(request, 'tasks/computer_science_tasks.html', {'tasks': tasks})

@user_passes_test(lambda u: u.is_superuser)
def add_computer_science_task(request):
    if request.method == 'POST':
        task_form = ComputerScienceTaskForm(request.POST)
        detail_forms = [ComputerScienceTaskDetailForm(request.POST, request.FILES, prefix=str(i)) for i in range(15)] # Adjust the range as needed

        if task_form.is_valid() and all(df.is_valid() for df in detail_forms):
            task = task_form.save()
            for detail_form in detail_forms:
                detail = detail_form.save(commit=False)
                detail.task = task
                detail.save()
            return redirect('computer_science_tasks')
    else:
        task_form = ComputerScienceTaskForm()
        detail_forms = [ComputerScienceTaskDetailForm(prefix=str(i)) for i in range(3)] # Adjust the range as needed

    return render(request, 'tasks/add_computer_science_task.html', {
        'task_form': task_form,
        'detail_forms': detail_forms
    })
    
@login_required
def computer_science_task_detail(request, pk):
    task = get_object_or_404(ComputerScienceTask, pk=pk)
    details = ComputerScienceTaskDetail.objects.filter(task=task)
    return render(request, 'tasks/computer_science_task_detail.html', {'task': task, 'details': details})
    
