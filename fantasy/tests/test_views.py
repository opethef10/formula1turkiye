from datetime import date

from django.test import TestCase
from django.urls import resolve, reverse
from django.views.generic.base import TemplateView

from ..models import *
from .. import views


class ViewTestBase:
    app_name_prefix = "fantasy:"
    url_name = ''
    url_kwargs = {}
    url_kwargs_404 = {}
    urlstring_without_slash = ''
    template_name = ''
    context_variable = 'None'
    view = views.DriverListView

    def url_reverse(self, kwargs=None):
        if kwargs is None:
            kwargs = self.url_kwargs
        return reverse(self.app_name_prefix + self.url_name, kwargs=kwargs)

    def urlstring(self):
        return self.urlstring_without_slash + "/"

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(self.urlstring())
        self.assertEqual(response.status_code, 200)

    def test_view_url_redirects_url_without_trailing_slash(self):
        response = self.client.get(self.urlstring_without_slash)
        self.assertRedirects(response, self.urlstring(), status_code=301)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(self.url_reverse())
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url_reverse())
        self.assertTemplateUsed(response, self.template_name)

    def test_view_uses_correct_context(self):
        response = self.client.get(self.url_reverse())
        self.assertIn(self.context_variable, response.context)

    def test_view_url_resolves_correct_view(self):
        view = resolve(self.url_reverse())
        self.assertEquals(view.func.view_class, self.view)


class DetailViewTestBase(ViewTestBase):
    def test_view_not_found_status_code(self):
        response = self.client.get(self.url_reverse(kwargs=self.url_kwargs_404))
        self.assertEquals(response.status_code, 404)


class HomeTests(ViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url_name = 'home'
        cls.urlstring_without_slash = "/fantasy"
        cls.template_name = "fantasy/home.html"
        cls.view = TemplateView

    def test_home_view_contains_link_to_driver_list_page(self):
        response = self.client.get(self.url_reverse())
        driver_list_url = reverse('fantasy:driver_list')
        self.assertContains(response, f'href="{driver_list_url}"')

    def test_home_view_contains_link_to_championship_list_page(self):
        response = self.client.get(self.url_reverse())
        championship_list_url = reverse('fantasy:championship_list')
        self.assertContains(response, f'href="{championship_list_url}"')


class DriverListTests(ViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url_name = 'driver_list'
        cls.urlstring_without_slash = "/fantasy/drivers"
        cls.template_name = "fantasy/driver_list.html"
        cls.context_variable = 'driver_list'
        cls.view = views.DriverListView

    def test_driver_list_view_contains_navigation_links(self):
        homepage_url = reverse('fantasy:home')
        response = self.client.get(self.url_reverse())
        self.assertContains(response, f'href="{homepage_url}"')


class ChampionshipListTests(ViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url_name = 'championship_list'
        cls.urlstring_without_slash = "/fantasy/championships"
        cls.template_name = "fantasy/championship_list.html"
        cls.context_variable = 'championship_list'
        cls.view = views.ChampionshipListView

        cls.championship = Championship.objects.create(year=2022, series="Formula 1")
        cls.championship2 = Championship.objects.create(year=2022, series="Formula 2")


class RaceListTests(ViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2022, series="Formula 1")
        cls.url_name = 'race_list'
        cls.url_kwargs = {'slug': cls.championship.slug}
        cls.url_kwargs_404 = {'slug': "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/championships/{cls.championship.slug}/races"
        cls.template_name = "fantasy/race_list.html"
        cls.context_variable = 'race_list'
        cls.view = views.RaceListView

    def test_view_uses_championship_context(self):
        response = self.client.get(self.url_reverse())
        self.assertEquals(self.championship, response.context["championship"])


class DriverDetailViewTests(DetailViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        championship = Championship.objects.create(year=2022, series="Formula 1")
        constructor = Constructor.objects.create(name="Mclaren", nationality="British")
        constructor.championship.add(championship, through_defaults={"garage_order": 1})
        cls.driver = Driver.objects.create(
            forename='Sebastian', surname="Vettel", number=5, code="VET", nationality="German", constructor=constructor
        )
        cls.url_name = 'driver_detail'
        cls.url_kwargs = {'slug': cls.driver.slug}
        cls.url_kwargs_404 = {'slug': "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/drivers/{cls.driver.slug}"
        cls.template_name = "fantasy/driver_detail.html"
        cls.context_variable = 'driver'
        cls.view = views.DriverDetailView


class ChampionshipDetailViewTests(DetailViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2024, series="Formula 1")
        cls.url_name = 'championship_detail'
        cls.url_kwargs = {'slug': cls.championship.slug}
        cls.url_kwargs_404 = {'slug': "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/championships/{cls.championship.slug}"
        cls.template_name = "fantasy/championship_detail.html"
        cls.context_variable = 'championship'
        cls.view = views.ChampionshipDetailView


class RaceDetailViewTests(DetailViewTestBase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2024, series="Formula 1")
        circuit = Circuit.objects.create(name="İstanbul Park", country="Turkey")
        cls.race = Race.objects.create(
            name="Turkish GP",
            championship=cls.championship,
            round=1,
            circuit=circuit,
            date=date.today()
        )
        cls.url_name = 'race_detail'
        cls.url_kwargs = {'slug': cls.championship.slug, "round": cls.race.round}
        cls.url_kwargs_404 = {'slug': cls.championship.slug, "round": 99}
        cls.urlstring_without_slash = f"/fantasy/championships/{cls.championship.slug}/races/{cls.race.round}"
        cls.template_name = "fantasy/race_detail.html"
        cls.context_variable = 'race'
        cls.view = views.RaceDetailView
