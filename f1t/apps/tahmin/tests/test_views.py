from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from ...fantasy.models import Championship, Race
from .. import views

CHAMPIONSHIP_TEST_DATA = dict(
    year=2022,
    series="f1",
    is_fantasy=True,
    is_tahmin=True,
    overtake_coefficient=2.1,
    qualifying_coefficient=3.2,
    finish_coefficient=1.8,
    beginning_token=18,
    starting_budget=Decimal("50.0")
)


class ViewTestMixin:
    app_name_prefix = "formula:tahmin:"
    url_name = ''
    url_kwargs = {}
    url_kwargs_404 = {}
    urlstring_without_slash = ''
    template_name = ''
    context_variable = 'None'

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
        self.assertEqual(view.func.view_class, self.view)

    def test_view_contains_navigation_links(self):
        homepage_url = reverse('home')
        response = self.client.get(self.url_reverse())
        self.assertContains(response, f'href={homepage_url}')


class DetailViewTestMixin(ViewTestMixin):
    def test_view_not_found_status_code(self):
        response = self.client.get(self.url_reverse(kwargs=self.url_kwargs_404))
        self.assertEqual(response.status_code, 404)


class TeamListTests(ViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(**CHAMPIONSHIP_TEST_DATA)
        cls.start_race = Race.objects.create(
            name="Start Race",
            championship=cls.championship,
            round=1,
            country="TR",
            datetime=timezone.now()
        )
        cls.end_race = Race.objects.create(
            name="End Race",
            championship=cls.championship,
            round=2,
            country="TR",
            datetime=timezone.now()
        )
        cls.url_name = 'team_list'
        cls.url_kwargs = {'series': cls.championship.series, 'year': cls.championship.year}
        cls.url_kwargs_404 = {'series': "arbitrary", 'year': 9999}
        cls.urlstring_without_slash = f"/{cls.championship.series}/{cls.championship.year}/tahmin"
        cls.template_name = "tahmin/team_list.html"
        cls.context_variable = 'tahmin_list'
        cls.view = views.TeamListView


class RaceDetailViewTests(ViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.championship = Championship.objects.create(**CHAMPIONSHIP_TEST_DATA)
        cls.race = Race.objects.create(
            name="Turkish GP",
            championship=cls.championship,
            round=1,
            country="TR",
            datetime=timezone.now()
        )
        cls.url_name = 'race_tahmins'
        cls.url_kwargs = {'series': cls.championship.series, 'year': cls.championship.year, "round": cls.race.round}
        cls.url_kwargs_404 = {'series': cls.championship.series, 'year': cls.championship.year, "round": 99}
        cls.urlstring_without_slash = f"/{cls.championship.series}/{cls.championship.year}/{cls.race.round}/tahmin"
        cls.template_name = "tahmin/race_tahmins.html"
        cls.context_variable = 'tahmin_list'
        cls.view = views.RaceTahminView
