# todo_list/todo_app/views.py
from django.utils import timezone
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from .models import ToDoList, ToDoItem
from django.urls import reverse, reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import  Http404,HttpResponseForbidden

import datetime



class CustomLoginView(LoginView):
    template_name = "todo_app/login.html"
    fields = "__all__"
    reedirect_authenticated_user = True

    def get_success_url(self):
        return reverse("index")
    

class Register_Page(FormView):
    template_name = 'todo_app/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(Register_Page, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("index")
        return super(Register_Page, self).get(*args, **kwargs)

    def get_success_url(self):
        return reverse("index")

class ListListView(LoginRequiredMixin,ListView):
    model = ToDoList
    template_name = "todo_app/index.html"

    def get_queryset(self):
        return ToDoList.objects.filter(user=self.request.user)

class ItemListView(LoginRequiredMixin,ListView):
    model = ToDoItem
    template_name = "todo_app/todo_list.html"
    # print(f"called on:{datetime.datetime.now()} duedate = {ToDoItem.due_date}")
    
    def get_queryset(self):
        return ToDoItem.objects.filter(todo_list_id=self.kwargs["list_id"])


    def get_context_data(self):
        context = super().get_context_data()
        # context["todo_list"] = ToDoList.objects.get(id=self.kwargs["list_id"])
        context["todo_list"] = ToDoList.objects.get(id=self.kwargs["list_id"])
        
        overdue_todo_items = ToDoItem.objects.filter(
            todo_list_id=self.kwargs["list_id"],
            due_date__lt=timezone.now().date()
        )

        for item in overdue_todo_items:
            item.delete()
        return context
    
class ListCreate(LoginRequiredMixin, CreateView):
    model = ToDoList
    fields = ["title"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


    def get_context_data(self):
        context = super(ListCreate, self).get_context_data()
        context["title"] = "Add a new list"
        return context


class ItemCreate(LoginRequiredMixin,CreateView):

    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


    def get_initial(self):
        initial_data = super(ItemCreate, self).get_initial()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        initial_data["todo_list"] = todo_list
        return initial_data


    def get_context_data(self):
        context = super(ItemCreate, self).get_context_data()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        context["todo_list"] = todo_list
        context["title"] = "Create a new item"

        return context


    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
        "Done",
    ]

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)



    def get_context_data(self):
        context = super(ItemUpdate, self).get_context_data()
        context["todo_list"] = self.object.todo_list
        context["title"] = "Edit item"
        return context


    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ListDelete(LoginRequiredMixin, DeleteView):
    model = ToDoList
    success_url = reverse_lazy("index")

class ItemDelete(LoginRequiredMixin,DeleteView):
    model = ToDoItem

    def get_success_url(self):
        return reverse_lazy("list", args=[self.kwargs["list_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todo_list"] = self.object.todo_list
        return context