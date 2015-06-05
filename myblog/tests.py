import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import utc
from myblog.models import Post, Category


class PostTestCase(TestCase):
    fixtures = ['myblog_test_fixture.json', ]

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_unicode(self):
        expected = u"This is a title"
        p1 = Post(title=expected)
        actual = unicode(p1)
        self.assertEqual(expected, actual)

    def test_author_name(self):
        expected = u"Mr. Administrator"
        p1 = Post(author=self.user)
        actual = p1.author_name()
        self.assertEqual(expected, actual)

    def test_author_names(self):
        names = [("Bob", "Marley", "Bob Marley"), ("Cher", "", "Cher "), ("Sting", "", "Sting "), ("Elliott", "Smith", "Elliott Smith")]
        author = User();
        p1 = Post(author=author)
        for first_name, last_name, expected in names:
            author.first_name = first_name
            author.last_name = last_name
            actual = p1.author_name()
            self.assertEqual(expected, actual)


class CategoryTestCase(TestCase):

    def test_unicode(self):
        expected = "A Category"
        c1 = Category(name=expected)
        actual = unicode(c1)
        self.assertEqual(expected, actual)


class FrontEndTestCase(TestCase):
    """test views provided in the front-end"""
    fixtures = ['myblog_test_fixture.json', ]

    def setUp(self):
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.timedelta = datetime.timedelta(15)
        author = User.objects.get(pk=1)
        category = Category()
        category.name = "Test Category"
        for count in range(1, 11):
            post = Post(title="Post %d Title" % count,
                        text="foo",
                        author=author)
            if count < 6:
                # publish the first five posts
                pubdate = self.now - self.timedelta * count
                post.published_date = pubdate
            if count % 2:
                post.category = category
            post.save()

    def test_list_only_published(self):
        resp = self.client.get('/')
        self.assertTrue("Recent Posts" in resp.content)
        for count in range(1, 11):
            title = "Post %d Title" % count
            if count < 6:
                self.assertContains(resp, title, count=1)
            else:
                self.assertNotContains(resp, title)

    def test_details_only_published(self):
        for count in range(1, 11):
            title = "Post %d Title" % count
            post = Post.objects.get(title=title)
            resp = self.client.get('/posts/%d/' % post.pk)
            if count < 6:
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, title)
            else:
                self.assertEqual(resp.status_code, 404)

    def test_category(self):
        resp = self.client.get('/categories/1/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Category: Test Category")
        self.assertContains(resp, "Post 1 Title")
        self.assertContains(resp, "Post 3 Title")
        self.assertContains(resp, "Post 5 Title")
