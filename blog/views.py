from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

def post_share(request, post_id):
    #retrive post by id
    post = get_object_or_404(Post, id=post_id, status = "published")
    sent = False

    if request.method == "POST":
        #form sumitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #form passed via validation
            cd = form.cleaned_data
            #send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject =  '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, "blog/post/share.html", {"post":post,
                                                   "form":form,
                                                   "sent":sent})


class postListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts':posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day
                             )
    #list of active comments for this post
    comments = post.comments.filter(active = True)

    if request.method = "POST":
        #commetn was posted
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            #create comment obj but not save to database
            new_comment = comment_form.save(commit=False)
            #assign current post to commetn
            new_comment.post = post
            #save comment to database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post,
                                                     "comments": comments,
                                                     "comment_form": comment_form})

