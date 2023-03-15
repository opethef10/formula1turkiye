from datetime import datetime

from django.test import TestCase
from django.urls import resolve

from ..models import *
from .. import views


class ViewTestMixin:
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

    def test_view_contains_navigation_links(self):
        homepage_url = reverse('home')
        response = self.client.get(self.url_reverse())
        self.assertContains(response, f'href={homepage_url}')


class DetailViewTestMixin(ViewTestMixin):
    def test_view_not_found_status_code(self):
        response = self.client.get(self.url_reverse(kwargs=self.url_kwargs_404))
        self.assertEquals(response.status_code, 404)


class HomeTests(ViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url_name = 'home'
        cls.urlstring_without_slash = "/fantasy"
        cls.template_name = "fantasy/championship_list.html"
        cls.context_variable = 'championship_list'
        cls.view = views.ChampionshipListView


class DriverListTests(ViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2022, series="Formula 1")
        cls.url_name = 'driver_list'
        cls.url_kwargs = {'champ': cls.championship.slug}
        cls.urlstring_without_slash = f"/fantasy/{cls.championship.slug}/drivers"
        cls.template_name = "fantasy/driver_list.html"
        cls.context_variable = 'driver_list'
        cls.view = views.DriverListView


class RaceListTests(ViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2022, series="Formula 1")
        cls.url_name = 'race_list'
        cls.url_kwargs = {'champ': cls.championship.slug}
        cls.url_kwargs_404 = {'champ': "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/{cls.championship.slug}"
        cls.template_name = "fantasy/race_list.html"
        cls.context_variable = 'race_list'
        cls.view = views.RaceListView

    def test_view_uses_championship_context(self):
        response = self.client.get(self.url_reverse())
        self.assertEquals(self.championship, response.context["championship"])


class TeamListTests(ViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2022, series="Formula 1")
        cls.url_name = 'team_list'
        cls.url_kwargs = {'champ': cls.championship.slug}
        cls.url_kwargs_404 = {'champ': "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/{cls.championship.slug}/teams"
        cls.template_name = "fantasy/team_list.html"
        cls.context_variable = 'team_list'
        cls.view = views.TeamListView


class DriverDetailViewTests(DetailViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.driver = Driver.objects.create(
            forename='Sebastian', surname="Vettel", number=5, code="VET", nationality="German"
        )
        cls.url_name = 'driver_detail'
        cls.url_kwargs = {'driver_slug': cls.driver.slug}
        cls.url_kwargs_404 = {'driver_slug': "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/drivers/{cls.driver.slug}"
        cls.template_name = "fantasy/driver_detail.html"
        cls.context_variable = 'driver'
        cls.view = views.DriverDetailView


class RaceDetailViewTests(DetailViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2024, series="Formula 1")
        circuit = Circuit.objects.create(name="İstanbul Park", country="Turkey")
        cls.race = Race.objects.create(
            name="Turkish GP",
            championship=cls.championship,
            round=1,
            circuit=circuit,
            datetime=datetime.now()
        )
        cls.url_name = 'race_detail'
        cls.url_kwargs = {'champ': cls.championship.slug, "round": cls.race.round}
        cls.url_kwargs_404 = {'champ': cls.championship.slug, "round": 99}
        cls.urlstring_without_slash = f"/fantasy/{cls.championship.slug}/{cls.race.round}"
        cls.template_name = "fantasy/race_detail.html"
        cls.context_variable = 'race'
        cls.view = views.RaceDetailView


class TeamDetailViewTests(DetailViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(year=2024, series="Formula 1")
        cls.user = User.objects.create_user(username='test_user', password='12345')
        cls.team = Team.objects.create(
            user=cls.user,
            championship=cls.championship
        )
        cls.url_name = 'team_detail'
        cls.url_kwargs = {'champ': cls.championship.slug, "username": cls.user.username}
        cls.url_kwargs_404 = {'champ': cls.championship.slug, "username": "arbitrary"}
        cls.urlstring_without_slash = f"/fantasy/{cls.championship.slug}/teams/{cls.user.username}"
        cls.template_name = "fantasy/team_detail.html"
        cls.context_variable = 'team'
        cls.view = views.TeamDetailView
