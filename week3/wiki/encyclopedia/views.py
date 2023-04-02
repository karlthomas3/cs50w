import random
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from markdown2 import Markdown

from . import util


markdowner = Markdown()


class NewPageForm(forms.Form):
    page_title = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Name of wiki"})
    )
    page_body = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": "5", "placeholder": "Body of wiki (in markdown)"}
        )
    )


# if POST run search else show list of entries
def index(request):
    if request.method == "POST":
        return search(request)
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


# return a page with content or None
def title(request, title):
    content = util.get_entry(title)
    if content:
        content = markdowner.convert(content)

    return render(
        request, "encyclopedia/title.html", {"title": title, "content": content}
    )


# search entries and send to matching page
def search(request):
    search_term = request.POST["q"]
    content = util.get_entry(request.POST["q"])
    if content:
        content = markdowner.convert(content)

        return render(
            request, "encyclopedia/title.html", {"title": title, "content": content}
        )

    entries = [i for i in util.list_entries() if search_term in i.lower()]
    return render(request, "encyclopedia/results.html", {"entries": entries})


# create a new iki page as long as it doesnt already exist
def create(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["page_title"]
            body = form.cleaned_data["page_body"]
            if not util.get_entry(name):
                util.save_entry(name, body)
                return HttpResponseRedirect(f"wiki/{name}")

            return render(request, "encyclopedia/exist.html", {"name": name})

        return render(request, "encyclopedia/create.html", {"form": form})

    return render(request, "encyclopedia/create.html", {"form": NewPageForm()})


# edit an existing page
def edit_page(request):
    # GET fills the form with the old content
    if request.method == "GET":
        name = request.GET["p_title"]
        body = util.get_entry(name)
        form = NewPageForm({"page_title": name, "page_body": body})
        return render(request, "encyclopedia/edit.html", {"form": form})
    # post rewrites to new content
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["page_title"]
            body = form.cleaned_data["page_body"]
            util.save_entry(name, body)
            return HttpResponseRedirect(f"wiki/{name}")

        return render(request, "encyclopedia/create.html", {"form": form})


# redirect to random page
def random_page():
    r_page = random.choice(util.list_entries())
    return HttpResponseRedirect(f"wiki/{r_page}")
