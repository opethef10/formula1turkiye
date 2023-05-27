# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.2] - 2023-05-27
### Added
### Changed
### Deprecated
### Removed
### Fixed
- "tahmin_form.html" can't be found
- 216 duplicate queries in tahmin form 
### Security

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
