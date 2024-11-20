# Formula 1 Türkiye

## About the Project

**Formula 1 Türkiye** is a comprehensive website developed to serve the vibrant community of Formula 1 enthusiasts in Turkey. Originating from the **Formula 1 Türkiye Facebook group**, which boasts over 5000 members and stands as the largest Formula 1 fan group in Turkey, the website is dedicated to enhancing the group’s activities and fostering engagement among its members.

The website provides a platform for leagues, data, and statistics while preserving a rich history of Formula 1 racing from its inception in 1950. Below is an overview of the core features of the website:

---

## Fantasy League

The **Fantasy League** is one of the flagship features of the Formula 1 Türkiye website. Originally launched in **2017**, the league transitioned to an online format through the website in **2023**, allowing members to participate more conveniently.

### Formula 1 Fantasy League
- Participants are given a **budget** to manage their team of drivers.
- Before each race, participants can **buy** and **sell drivers**, building a team within their allocated budget.
- Points are earned based on the performance of the drivers in each race.

### Formula 2 Fantasy League
In **2023**, the Fantasy League was extended to include the **Formula 2 Championship**, giving fans the opportunity to:
- Manage teams of Formula 2 drivers.
- Earn points based on their performance in each race.
- Compete in a dedicated standings table for Formula 2.

### Standings and Classifications
- Both Formula 1 and Formula 2 leagues provide a **Race Standings** section to display results after each Grand Prix or Formula 2 event.
- Separate **General Classifications** are maintained for the entire season, showcasing the overall rankings of participants in each league.

---

## Prediction League

The **Prediction League** challenges participants to forecast race outcomes and has been a cornerstone of the website since **2018**. It transitioned to an online format in **2023**, enhancing accessibility for users.

### Formula 1 Prediction League
- Participants predict the **top 10 finishing positions** for each Grand Prix.
- They also answer **two multiple-choice questions** related to the race.
- Points are awarded based on the accuracy of predictions and answers.

### Standings and Classifications
- The website maintains separate **Race Standings** and **General Classifications** for Formula 1, providing a clear overview of individual performances.

---

## Comprehensive Formula 1 Race Data and Statistics

The website houses an extensive database of Formula 1 race results and statistics dating back to the very first race in **1950**. This includes:

- Race-by-race results for all drivers and teams.
- Historical championship standings.
- Detailed analysis of race performances.

The platform provides fans and statisticians with easy access to decades of Formula 1 history, all in one place.

---

## Formula 2 Results Since 2023

In addition to leagues, the website features complete results from the **Formula 2 Championship**, starting from **2023**. This ensures comprehensive coverage of both major tiers of racing talent, allowing fans to follow the progression of future Formula 1 stars.

---

## Race Ratings Since 2016

After every Formula 1 Grand Prix, members of the Facebook group are invited to rate the race. These ratings are then collected and published on the website, providing:

- A detailed archive of race ratings since **2016**.
- Insights into fan opinions and trends over the years.
- Comparisons of the most memorable and least exciting races.

This section serves as a community-driven perspective on the history of Formula 1 races.

---

## Qualifying Comparisons and Elo Ratings

Using historical data from **1950**, the website features a unique system to compare drivers’ qualifying performances against their teammates. The **Elo rating system** is applied to rank drivers based on their qualifying head-to-head results, creating:

- A dynamic ranking system for qualifying performance.
- An innovative way to measure and compare driver skill over time.
- Visualizations and statistics for fans to explore.

---

## Responsive Design and Progressive Web App (PWA)

The **Formula 1 Türkiye** website is fully responsive, ensuring compatibility with **mobile devices** and providing a seamless user experience across various screen sizes. While the platform does not currently offer a native mobile app, it supports **Progressive Web App (PWA)** functionality, allowing users to:

- Install the website as an app on their devices.
- Access core features offline with cached data.
- Enjoy a faster and app-like browsing experience.

This ensures that the website is accessible and user-friendly, meeting the needs of a tech-savvy audience.

---
### User Registration and Login

To access the **Fantasy League** and **Prediction League**, users need to **sign up** and **log in** to the website. The account enables users to:

- Manage teams for Fantasy Leagues (Formula 1 and Formula 2).
- Submit predictions for Prediction Leagues (Formula 1 and Formula 2).

For other features, such as viewing race data, statistics, or race ratings, **no login is required**, ensuring that the broader community can explore and enjoy the wealth of information available on the site without barriers.

---
**Formula 1 Türkiye** is more than just a website; it is a digital hub that connects fans, preserves the sport's legacy, and enhances the community's passion for Formula 1 and Formula 2.

---

## How to Install locally

## Requirements

- Python 3.10 or higher

## Setup Instructions

Follow these steps to set up the project on your local machine.

### 1. Create a Virtual Environment

Create a virtual environment in the root of your project folder:

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
**On Windows**:

```bash
venv\Scripts\activate
```

**On Linux**:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages using pip. Run the following command:

```bash
pip install -r requirements/development.txt
```

### 4. Set Up the Database

Run the following commands to set up the database:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Follow the prompts to create a superuser account.

### 5. Run the Development Server

Now you can run the development server:

```bash
python manage.py runserver
```

The server will start, and you can access it by navigating to `http://127.0.0.1:8888/` in your web browser.
