# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [major.minor.patch] - yyyy-mm-dd
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->

## [2.7.5] - 2024-10-29
### Fixed
- form-control bug

## [2.7.4] - 2024-10-29
### Added
- Driver age function
### Fixed
- Alım satım form form-control bug

## [2.7.3] - 2024-10-28
### Changed
- Driver detail page into responsive grid layout

## [2.7.2] - 2024-10-28
### Changed
- Made season stat card-flex mobile compatible

## [2.7.1] - 2024-10-28
### Changed
- Card flex texts are smaller

## [2.7.0] - 2024-10-28
### Added
- Win, pole, fastest lap, podium, sprint win statistics in season stats page

## [2.6.4] - 2024-10-27
### Added
- Homepage banner

## [2.6.3] - 2024-10-27
### Added
- Winning driver and constructor to rating pages

## [2.6.2] - 2024-10-27
### Fixed
- Tahmin question choices bug

## [2.6.1] - 2024-10-26
### Changed
- Upgraded Bootstrap and JQuery
- Row-col to card deck in home page
- Fontawesome icons to our products
- Header tag sizes
### Removed
- Homepage breadcrumb

## [2.6.0] - 2024-10-26
### Added
- Qualifying times in race edit page
- Sprint qualifying results in race detail
- Qualifying margin and ratios in race detail page
- Race datetimes in race detail
### Changed
- DriverStatsView to FantasyStatsView
- Disable race detail datatable searching
- Home page order
- Home page visuals

## [2.5.5] - 2024-10-23
### Added
- Question links to tahmin results page
- test to scripts directory

## [2.5.4] - 2024-10-23
### Added
- Admin change urls in race and fantasy detail
### Changed
- Admin only buttons to grey

## [2.5.3] - 2024-10-23
### Added
- Fantasy paths in all fantasy related pages
### Deprecated
- teams in fantasy paths

## [2.5.2] - 2024-10-22
### Added
- Supergrid

## [2.5.1] - 2024-10-22
### Fixed
- Python3.12 deprecated unittest aliases
### Added
- Race detail page independent from fantasy
- LastRaceFantasyRedirectView
- RaceFantasyView
- get_fantasy_url

## [2.5.0] - 2024-10-21
### Added
- 1985-2024 quali results

## [2.4.9] - 2024-10-21
### Fixed
- Season stats page title

## [2.4.8] - 2024-10-18
### Added
- F1Calendar.com crosscheck management command

## [2.4.7] - 2024-10-03
### Added
- Fastest lap eligibility check for sprint and feature races
- Fastest lap eligibility thresholds
### Fixed
- Fastest lap points given outside top 10

## [2.4.6] - 2024-08-09
### Fixed
- Driver stats from_year, to_year error

## [2.4.5] - 2024-07-28
### Added
- Initial tahmin tests
### Fixed
- Tahmin question unpacking error

## [2.4.4] - 2024-07-28
### Added
- Tahmin count matrix
- Correct tahmin question answers
### Fixed
- Yarışı düzenle iframe height
- Driver predictions_X related_name

## [2.4.3] - 2024-07-27
### Changed
- Disable clearcache

## [2.4.2] - 2024-07-27
### Added
- Race winner, polesitter etc
### Fixed
- Tahmin ligi Wiki height

## [2.4.1] - 2024-07-26
### Added
- Title column to the Green Flag magazine
- Green Flag magazine to the navbar

## [2.4.0] - 2024-07-26
### Added
- Greenflag magazine
### Fixed
- Margins and paddings in base and footer

## [2.3.5] - 2024-06-22
### Fixed
- Wiki frame width

## [2.3.4] - 2024-06-13
### Fixed
- Slow queries in the admin pages

## [2.3.3] - 2024-05-21
### Added
- Questions in tahmin results page

## [2.3.2] - 2024-05-21
### Added
- Token, budget and tactic columns to the fantasy standings
- Driver links to fantasy league profile
- Fantasy profile redirect view

## [2.3.1] - 2024-05-17
### Added
- Navigator menus
- Footer to fantasy stats page
- Amount of votes indicator in ratings column in season page
- Most races without win page
### Changed
- Fantasy stats URL
- Is staff access to superuser access in forms
- Admin page navbar link is accessible by the staff
- Fantasy user profile when there is no championship or team

## [2.3.0] - 2024-04-20
### Added
- Print season calendar
- DEV to title in development mode
- Short str method in championship model
- Next and previous championships scroll through
- is_puanla method to championship model
- League menus
- One explanatory line to the ratings main page
- Season stats page
- Many driver statistics pages
- Formula section in the main page, separated from the leagues
- Add F1 stats link to navbar
### Changed
- Navbar leagues dropdown links redirect to league main pages for current season
- Homepage league links redirect to league main pages for current season
- Championship menu to redirect to leagues
- Sprint Shootout to Sprint Sıralama
- Center the driver detail grid/finish counts
### Fixed
- League access for non existing league pages
- Ratings average calculation
- Unnecessary footer line for season calendars
- Tahmin league race page breadcrumb
- Tests failing due to closed championships

## [2.2.4] - 2024-04-08
### Added
- Pythonanywhere script files

## [2.2.3] - 2024-04-07
### Fixed
- In Fantasy driver stats, the average values

## [2.2.1] - 2024-03-27
### Changed
- Mobile css max width value

## [2.2.0] - 2024-03-26
## Added
- Yarışı Puanla Form

## [2.1.6] - 2024-03-24
### Changed
- Footer pusher length

## [2.1.5] - 2024-03-24
### Fixed
- Mobile detect test error

## [2.1.4] - 2024-03-24
### Added
- Django mobile detector
### Changed
- Improvements in visual aspects of website

## [2.1.3] - 2024-03-18
### Changed
- Added series detail to driver detail page
- Make more mobile friendly design.

## [2.1.2] - 2024-03-09
### Added
- Location icon in front of circuits in the race list
- Local FontAwesome files in development
- Driver URLs in drivers tab in race_detail page
### Changed
- Development runserver port is 8888 by default

## [2.1.1] - 2024-03-07
### Changed
- FontAwesome Django app to webkit
- Driver URLs in race_detail page
### Fixed
- Server error when constructors and drivers don't have results yet
- Rating in Race List n+1 query problem

## [2.1.0] - 2024-02-29
### Added
- Leagues and products to the navbar
- Tabs to the driver detail page
### Fixed
- Driver birthdays shown as None
### Removed
- Constructors' race detail table

## [2.0.5] - 2024-02-27
### Added
- Price img to new team form
### Changed
- Logout on POST request
- Make non-tahmin seasons return 404

## [2.0.4] - 2024-02-27
### Added
- FAQ page

## [2.0.3] - 2024-02-27
### Added
- Race Ratings Page served from the database
- Drivers page
- Win, Pole, Podium, Pole, Fastest Lap stats pages
- Constructors page

### Changed
- Changed page structures
- Add pages to navigation bar

## [1.13.4] - 2023-11-14
### Added
- Driver career table

## [1.13.3] - 2023-11-12
### Added
- Driver list and detail pages

## [1.13.2] - 2023-11-11
### Fixed
- Driver list calculation error

## [1.13.1] - 2023-11-11
### Changed
- Driver model

## [1.13.0] - 2023-11-11
### Changed
- Constructor model

## [1.12.0] - 2023-11-10
### Removed
- Team model

## [1.11.6] - 2023-11-02
### Fixed
- Protocol error in password reset mail

## [1.11.5] - 2023-11-02
### Fixed
- New fantasy team error

## [1.11.4] - 2023-10-29
### Fixed
- Fantasycopy year error

## [1.11.3] - 2023-10-16
### Fixed
- New tahmin footer error

## [1.11.2] - 2023-10-16
### Fixed
- Service worker fetch error

## [1.11.1] - 2023-10-16
### Fixed
- Radio check file not caching in offline page

## [1.11.0] - 2023-10-13
### Added
- Progressive web app structure
- Add offline page template

## [1.10.1] - 2023-10-13
### Fixed
- Tahmin race list table performance issue


## [1.10.0] - 2023-10-09
### Added
- Circuit model
- Circuit link in season pages

## [1.9.9] - 2023-10-05
### Added
- Changelog page

## [1.9.8] - 2023-10-04
### Fixed
- Race list tables

## [1.9.7] - 2023-10-04
### Added
- Fantasy ready check
### Changed
- Order of sprint_shootout and sprint fields in Race model

## [1.9.6] - 2023-10-04
### Added
- Session datetime fields
### Changed
- deadline to fp1_datetime
- Tahmin ligi menu

## [1.9.5] - 2023-09-29
### Added
- Link to race in fantasy forms

## [1.9.4] - 2023-09-29
### Fixed
- Unsticky footer

## [1.9.3] - 2023-09-29
### Fixed
- production.txt in requirements
- Contact form text alignment

## [1.9.2] - 2023-09-28
### Added
- Contact form
- Footer
- Bootstrap-social
- Fontawesome
### Fixed
- Flatpages breadcrumb

## [1.9.1] - 2023-09-28
### Added
- django-summernote

## [1.9.0] - 2023-09-27 (Multilanguage)
### Added
- Redirects app
- language.js
- Languages settings
### Changed
- URLs to i18n patterns
- Flatpages URL to /pages/

## [1.8.9] - 2023-09-12
### Fixed
- Fix fantasycopy bug

## [1.8.8] - 2023-08-24
### Added
- user field to RaceTeam
### Changed
- Nonnullify Tahmin

## [1.8.7] - 2023-08-24
### Fixed
- Forms viewed before the deadline but sent after it
- n+1 queries problem in TeamDetailView

## [1.8.6] - 2023-08-07
### Changed
- Apps to f1t/apps folder

## [1.8.5] - 2023-08-05
### Added
- tests.py to settings
- .editorconfig
### Changed
- __core__ directory to f1t
- static and templates directories to project folder
### Fixed
- 403.html

## [1.8.4] - 2023-08-03
### Added
- Flexible container width transition
### Changed
- Requirements location
- Simplify .env.example
- Static file locations into app folders
### Removed
- Empty files

## [1.8.3] - 2023-07-19
### Fixed
- site.webmanifest

## [1.8.2] - 2023-07-19
### Added
- Favicons

## [1.8.1] - 2023-07-19
### Changed
- Logging console in development
- All F1T loggings are unified

## [1.8.0] - 2023-07-13 (Separate setting files)
### Changed
- Separate settings files for different environments

## [1.7.10] - 2023-07-01
### Added
- robots.txt
### Fixed
- RaceTeam points not in floating point

## [1.7.9] - 2023-06-16
### Fixed
- Optimize static images

## [1.7.8] - 2023-06-16
### Changed
- Simplify Tahmin logic
- RaceDrivers having no results yet get None points

## [1.7.7] - 2023-06-03
### Changed
- Place of choices to their respective models
### Removed
- All remaining view caches except flatpages

## [1.7.6] - 2023-06-01
### Added
- Model orderings
- Championship.fastest_lap_point
- Title blocks for each template
- LastRaceRedirectView
### Changed
- RaceDriver.fastest_lap & RaceDriver.sprint_fastest_lap to BooleanField
- question_* fields in Tahmin to answer_* fields to reduce ambiguity
- Simplify alım satım form __init__
- Flatpage title element
### Removed
- Redundant order_by in most model querysets
### Fixed
- order_by error in compound statements

## [1.7.5] - 2023-05-28
### Added
- SuccessMessageMixin to TeamNewEditBaseView
### Changed
- RaceDetailView to RaceTahminView
- Refactor NewTahminView
### Fixed
- next() to next

## [1.7.4] - 2023-05-27
### Fixed
- Star imports

## [1.7.3] - 2023-05-27
### Added
- select_related for championship in driver list

## [1.7.2] - 2023-05-27
### Fixed
- "tahmin_form.html" can't be found
- 216 duplicate queries in tahmin form

## [1.7.1] - 2023-05-26
### Removed
- TahminTeam

## [1.7.0] - 2023-05-26 (Performance Improvements, Remove Teams)
### Added
- RaceTahmin user field
### Changed
- Place of tahmin_score function
- RaceTahmin to Tahmin
### Deprecated
- TahminTeam
- RaceTeam
### Fixed
- Tahmin TeamList performance issues

## [1.6.1] - 2023-05-21
### Changed
- Place of coefficient function in fantasy models
### Removed
- Unnecessary is_authenticated in team_list views
- driver_count_dict in driver_list
- circuit model in tests

## [1.6.0] - 2023-05-19
### Added
- Really3D Casio watch to Tahmin race detail page
- Driver stats link to homepage
### Changed
- List of links to horizontal list group in Fantasy Race List
- Race edit page more compact
### Removed
- Driver detail page and view
- Circuit column from race list
- Circuit model and Circuit field for Race

## [1.5.4] - 2023-05-18
### Changed
- Race detail team and price tabs have link colored drivers
### Removed
- Driver get_absolute_url
- Some get_tahmin_url

## [1.5.3] - 2023-05-18
### Added
- Style to driver names

## [1.5.2] - 2023-05-18
### Added
- Color fields to Championship Constructor table
- Fastest lap information as superscript
### Changed
- Body font to Cabin
### Removed
- Fastest lap column in race detail page

## [1.5.1] - 2023-05-14
### Added
- error_base.html
- Conditional formatting in datatables
- Wikipedia-like race position background coloring
### Changed
- DRY'ed error templates

## [1.5.0] - 2023-05-11 (Compact Datatables)
### Added
- Tanzim driver statistic
- Sprint race result and grid statistics
### Changed
- Made datatables compact, striped, hovered
- Container is now 86% of the page width
- Search box aligned to left side

## [1.4.7] - 2023-04-30
### Fixed
- Attribute error point_None

## [1.4.6] - 2023-04-28
### Added
- latest_race and next_race functions to Championship
### Changed
- Front page league links

## [1.4.5] - 2023-04-04
### Changed
- price_img field from race to championship

## [1.4.4] - 2023-04-04
### Deprecated
- Driver detail page
### Removed
- Nationality field in drivers and constructors

## [1.4.3] - 2023-04-04
### Changed
- Tahmin point is tied to the correct answer
### Fixed
- Form not showing 4 buttons when there is 4 choices

## [1.4.2] - 2023-04-02
### Added
### Changed
- Country names to flags in result tables
### Deprecated
- Circuit in race list
### Removed
### Fixed
- Total points column sometimes without decimal point
### Security

## [1.4.1] - 2023-03-30
### Added
- Previous/next races buttons in race results

## [1.4.0] - 2023-03-27 (Fantasy F2)
### Added
- Fantasy F2 Season
### Fixed
- Different coefficients for different series

## [1.3.2] - 2023-03-19
### Added
- Rank for result pages

## [1.3.1] - 2023-03-15
### Fixed
- Tactic choice bug

## [1.3.0] - 2023-03-15 (Flatpages)
### Added
- Flatpages such as elo, puanla, quiz
### Changed
- Expired page image

## [1.2.2] - 2023-03-11
### Added
- Team radio error messages
- Price images now can be uploaded from admin page
- Admin e-mail interface for server errors
### Fixed
- Alım satım Javascript error for discounted drivers

## [1.2.1] - 2023-03-06
### Added
- HTML minifying
- Question model to database
- Meta OG tags
### Changed
- Prediction league results are ready for users
- Tahmin forms are now automated
### Fixed
- HTML minifying

## [1.2.0] - 2023-03-05 (Tahmin Ligi)
### Added
- Sent page after sending prediction forms
- Prediction scoring system picture
### Changed
- Prediction league interface is made ready
- Predictions aren't visible to public until race begins
- Page bottom margin increased
### Removed
- Prediction team absolute urls as they don't exist

## [1.1.1] - 2023-03-01
### Changed
- Password validators removed

## [1.1.0] - 2023-03-01 (New Page Structure)
### Changed
- Changed page structure

## [1.0.0] - 2023-02-28 (F1T)
### Added
- Formula 1 Türkiye website is open for visitors
