# -*- coding: utf-8 -*-
"""Django page CMS template test suite module."""
from pages.models import Page, Content
from pages.placeholders import PlaceholderNode, get_filename
from pages.tests.testcase import TestCase, MockRequest
from pages.templatetags.pages_tags import get_page_from_string_or_id
from django.contrib.auth.models import User
from pages.phttp import get_request_mock, remove_slug

import django
import unittest
import six

from django.template import Template, RequestContext, Context
from django.template import Template, TemplateSyntaxError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

import datetime


class TemplateTestCase(TestCase):
    """Django page CMS unit test suite class."""

    def test_placeholder_inherit_content(self):
        """Test placeholder content inheritance between pages."""
        self.set_setting("PAGE_USE_SITE_ID", False)
        author = User.objects.all()[0]
        p1 = self.new_page(content={'inher':'parent-content'})
        p2 = self.new_page()
        template = django.template.loader.get_template('pages/tests/test7.html')
        context = Context({'current_page': p2, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')

        p2.move_to(p1, position='first-child')
        self.assertEqual(template.render(context), 'parent-content')

    def test_get_page_template_tag(self):
        """Test get_page template tag."""
        context = Context({})
        pl1 = """{% load pages_tags %}{% get_page "get-page-slug" as toto %}{{ toto }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(template.render(context), 'None')
        page = self.new_page({'slug': 'get-page-slug'})
        self.assertEqual(template.render(context), 'get-page-slug')

    def test_placeholder_all_syntaxes(self):
        """Test placeholder syntaxes."""
        page = self.new_page()
        context = Context({'current_page': page, 'lang': 'en-us'})

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(template.render(context), '')

        pl1 = """{% load pages_tags %}{% placeholder title as hello %}{{ hello }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(template.render(context), page.title())


        # to be sure to raise an errors in parse template content
        setattr(settings, "DEBUG", True)

        page = self.new_page({'wrong': '{% wrong %}'})
        context = Context({'current_page': page, 'lang':'en-us'})

        pl2 = """{% load pages_tags %}{% placeholder wrong parsed %}"""
        template = self.get_template_from_string(pl2)
        from pages.placeholders import PLACEHOLDER_ERROR
        error = PLACEHOLDER_ERROR % {
            'name': 'wrong',
            'error': "Invalid block tag: 'wrong'",
        }
        self.assertEqual(template.render(context), error)

        # generate errors
        pl3 = """{% load pages_tags %}{% placeholder %}"""
        try:
            template = self.get_template_from_string(pl3)
        except TemplateSyntaxError:
            pass

        pl4 = """{% load pages_tags %}{% placeholder wrong wrong %}"""
        try:
            template = self.get_template_from_string(pl4)
        except TemplateSyntaxError:
            pass

        pl5 = """{% load pages_tags %}{% placeholder wrong as %}"""
        try:
            template = self.get_template_from_string(pl5)
        except TemplateSyntaxError:
            pass


    def test_placeholder_quoted_name(self):
        """Test placeholder name with quotes."""
        page = self.new_page()
        context = Context({'current_page': page, 'lang': 'en-us'})
        placeholder = PlaceholderNode("test name")
        placeholder.save(page, 'en-us', 'some random value', False)

        pl1 = """{% load pages_tags %}{% placeholder "test name" as hello %}{{ hello }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(template.render(context), 'some random value')

        placeholder = PlaceholderNode("with accent éàè")
        placeholder.save(page, 'en-us', 'some random value', False)

        pl1 = """{% load pages_tags %}{% placeholder "with accent éàè" as hello %}{{ hello }}"""
        template = self.get_template_from_string(pl1)
        self.assertEqual(template.render(context), 'some random value')

    def test_parsed_template(self):
        """Test the parsed template syntax."""
        setattr(settings, "DEBUG", True)
        page = self.new_page({'title':'<b>{{ "hello"|capfirst }}</b>'})
        page.save()
        context = Context({'current_page': page, 'lang':'en-us'})
        pl_parsed = """{% load pages_tags %}{% placeholder title parsed %}"""
        template = self.get_template_from_string(pl_parsed)
        self.assertEqual(template.render(context), '<b>Hello</b>')
        setattr(settings, "DEBUG", False)
        page = self.new_page({'title':'<b>{{ "hello"|wrong_filter }}</b>'})
        context = Context({'current_page': page, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')

    def test_placeholder_untranslated_content(self):
        """Test placeholder untranslated content."""
        self.set_setting("PAGE_USE_SITE_ID", False)
        page = self.new_page(content={})
        placeholder = PlaceholderNode('untrans', page='p', untranslated=True)
        placeholder.save(page, 'fr-ch', 'test-content', True)
        placeholder.save(page, 'en-us', 'test-content', True)
        self.assertEqual(len(Content.objects.all()), 1)
        self.assertEqual(Content.objects.all()[0].language, 'en-us')

        placeholder = PlaceholderNode('untrans', page='p', untranslated=False)
        placeholder.save(page, 'fr-ch', 'test-content', True)
        self.assertEqual(len(Content.objects.all()), 2)

        # test the syntax
        page = self.new_page()
        template = django.template.loader.get_template(
                'pages/tests/untranslated.html')
        context = Context({'current_page': page, 'lang':'en-us'})
        self.assertEqual(template.render(context), '')

    def test_get_content_tag(self):
        """
        Test the {% get_content %} template tag
        """
        page_data = {'title': 'test', 'slug': 'test'}
        page = self.new_page(page_data)

        context = RequestContext(MockRequest(), {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" "en-us" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% get_content page "title" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), page_data['title'])

    def test_get_content_tag_bug(self):
        """
        Make sure that {% get_content %} use the "lang" context variable if
        no language string is provided.
        """
        page_data = {'title': 'test', 'slug': 'english'}
        page = self.new_page(page_data)
        Content(page=page, language='fr-ch', type='title', body='french').save()
        Content(page=page, language='fr-ch', type='slug', body='french').save()
        self.assertEqual(page.slug(language='fr-ch'), 'french')
        self.assertEqual(page.slug(language='en-us'), 'english')

        # default
        context = RequestContext(MockRequest(), {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), 'english')

        # french specified
        context = RequestContext(MockRequest(), {'page': page, 'lang': 'fr'})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), 'french')

        # english specified
        context = RequestContext(MockRequest(), {'page': page, 'lang': 'en-us'})
        template = Template('{% load pages_tags %}'
                            '{% get_content page "slug" as content %}'
                            '{{ content }}')
        self.assertEqual(template.render(context), 'english')

    def test_show_content_tag(self):
        """
        Test the {% show_content %} template tag.
        """
        page_data = {'title':'test', 'slug':'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        context = RequestContext(MockRequest(), {'page': page, 'lang':'en-us',
            'path':'/page-1/'})
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" "en-us" %}')
        self.assertEqual(template.render(context), page_data['title'])
        template = Template('{% load pages_tags %}'
                            '{% show_content page "title" %}')
        self.assertEqual(template.render(context), page_data['title'])

    def test_pages_siblings_menu_tag(self):
        """
        Test the {% pages_siblings_menu %} template tag.
        """
        page_data = {'title':'test', 'slug':'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        context = RequestContext(MockRequest(), {'page': page, 'lang':'en-us',
            'path':'/page-1/'})
        template = Template('{% load pages_tags %}'
                            '{% pages_siblings_menu page %}')
        renderer = template.render(context)

    def test_admin_menu_tag(self):
        """
        Test the {% pages_admin_menu %} template tag with cookies.
        """
        page_data = {'title':'test', 'slug':'test'}
        page = self.new_page(page_data)
        # cleanup the cache from previous tests
        page.invalidate()

        request = MockRequest()
        request.COOKIES['tree_expanded'] = "%d,10,20" % page.id
        context = RequestContext(request, {'page': page, 'lang':'en-us',
            'path':'/page-1/'})
        template = Template('{% load pages_tags %}'
                            '{% pages_admin_menu page %}')
        renderer = template.render(context) 

    def test_show_absolute_url_with_language(self):
        """
        Test a {% show_absolute_url %} template tag  bug.
        """
        page_data = {'title': 'english', 'slug': 'english'}
        page = self.new_page(page_data)
        Content(page=page, language='fr-ch', type='title', body='french').save()
        Content(page=page, language='fr-ch', type='slug', body='french').save()

        self.assertEqual(page.get_url_path(language='fr-ch'),
            self.get_page_url('french'))
        self.assertEqual(page.get_url_path(language='en-us'),
            self.get_page_url('english'))

        context = RequestContext(MockRequest(), {'page': page})
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "en-us" %}')
        self.assertEqual(template.render(context),
            self.get_page_url('english'))
        template = Template('{% load pages_tags %}'
                            '{% show_absolute_url page "fr-ch" %}')
        self.assertEqual(template.render(context),
            self.get_page_url('french'))

    def test_get_page_from_id_context_variable(self):
        """Test get_page_from_string_or_id with an id context variable."""
        page = self.new_page({'slug': 'test'})
        self.assertEqual(get_page_from_string_or_id(str(page.id)), page)

        content = Content(page=page, language='en-us', type='test_id',
            body=page.id)
        content.save()
        context = Context({'current_page': page})
        context = RequestContext(MockRequest(), context)
        template = Template('{% load pages_tags %}'
                            '{% placeholder test_id as str %}'
                            '{% get_page str as p %}'
                            '{{ p.slug }}')
        self.assertEqual(template.render(context), 'test')

    def test_get_page_from_slug_context_variable(self):
        """Test get_page_from_string_or_id with an slug context variable."""
        page = self.new_page({'slug': 'test'})

        context = Context({'current_page': page})
        context = RequestContext(MockRequest(), context)
        template = Template('{% load pages_tags %}'
                            '{% placeholder slug as str %}'
                            '{% get_page str as p %}'
                            '{{ p.slug }}')
        self.assertEqual(template.render(context), 'test')

        template = Template('{% load pages_tags %}'
                            '{% get_page "test" as p %}'
                            '{{ p.slug }}')
        self.assertEqual(template.render(context), 'test')

    def test_get_page_template_tag_with_page_arg_as_id(self):
        """Test get_page template tag with page argument given as a page id"""
        context = Context({})
        pl1 = """{% load pages_tags %}{% get_page 1 as toto %}{{ toto }}"""
        template = self.get_template_from_string(pl1)
        page = self.new_page({'id': 1, 'slug': 'get-page-slug'})
        self.assertEqual(template.render(context), 'get-page-slug')

    def test_get_page_template_tag_with_variable_containing_page_id(self):
        """Test get_page template tag with page argument given as a page id"""
        context = Context({})
        pl1 = ('{% load pages_tags %}{% placeholder somepage as page_id %}'
            '{% get_page page_id as toto %}{{ toto }}')
        template = self.get_template_from_string(pl1)
        page = self.new_page({'id': 1, 'slug': 'get-page-slug',
            'somepage': '1'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), 'get-page-slug')

    def test_get_page_template_tag_with_variable_containing_page_slug(self):
        """Test get_page template tag with page argument given as a page id"""
        context = Context({})
        pl1 = ('{% load pages_tags %}{% placeholder somepage as slug %}'
            '{% get_page slug as toto %}{{ toto }}')
        template = self.get_template_from_string(pl1)
        page = self.new_page({'slug': 'get-page-slug', 'somepage':
            'get-page-slug' })
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), 'get-page-slug')

    def test_variable_disapear_in_block(self):
        """Try to test the disapearance of a context variable in a block."""
        tpl = ("{% load pages_tags %}"
          "{% placeholder slug as test_value untranslated %}"
          "{% block someblock %}"
          "{% get_page test_value as toto %}"
          "{{ toto.slug }}"
          "{% endblock %}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'slug': 'get-page-slug'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), 'get-page-slug')

    def test_get_filename(self):
        placeholder = PlaceholderNode("placeholdername")
        page = self.new_page({'slug': 'page1'})
        fakefile = SimpleUploadedFile(name=six.u("myfile.pdf"), content=six.b('bytes'))
        self.assertTrue(fakefile.name in get_filename(page, placeholder, fakefile))
        self.assertTrue("page_%d" % page.id in get_filename(page, placeholder, fakefile))
        self.assertTrue(placeholder.name in get_filename(page, placeholder, fakefile))

    def test_json_placeholder(self):
        tpl = ("{% load pages_tags %}{% jsonplaceholder p1 as v %}{{ v.a }}")

        template = self.get_template_from_string(tpl)
        page = self.new_page({'p1': '{"a":1}'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), '1')

        tpl = ("{% load pages_tags %}{% jsonplaceholder p1 %}")
        template = self.get_template_from_string(tpl)
        page = self.new_page({'p1': 'wrong'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), 'wrong')

    def test_file_placeholder(self):
        tpl = ("{% load pages_tags %}{% fileplaceholder f1 %}")
        
        template = self.get_template_from_string(tpl)
        page = self.new_page({'f1': 'filename'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), 'filename')
        
    def test_image_placeholder(self):
        tpl = ("{% load pages_tags %}{% imageplaceholder f1 %}")
        
        template = self.get_template_from_string(tpl)
        page = self.new_page({'f1': 'filename'})
        context = Context({'current_page': page})
        self.assertEqual(template.render(context), 'filename')
        
    def test_contact_placeholder(self):
        tpl = ("{% load pages_tags %}{% contactplaceholder contact %}")
        
        template = self.get_template_from_string(tpl)
        page = self.new_page({'contact': 'hello'})
        context = Context({'current_page': page})
        
        import logging
        logger = logging.getLogger("pages")
        lvl = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        
        with self.assertRaises(ValueError): 
            self.assertEqual(template.render(context), 'hello')
            
        logger.setLevel(lvl)
            
        context = Context({'current_page': page, 'request':get_request_mock()})
        self.assertTrue("<form" in template.render(context))