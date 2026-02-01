# Portfolio Calculator Web App

This is a web-based version of the Portfolio Calculator logic, designed to be hosted on GitHub Pages or run locally in any browser.

## Features
- **Real-time Simulation**: Adjust inputs and see the graph update instantly.
- **UK Tax Logic**: Integrated Income Tax, National Insurance, and Student Loan calculations.
- **Retirement Planning**: Strategies for drawdown from LISA, Pension, ISA, and Cash based on age.
- **Property Ladder**: Simulates buying a house and mortgage pay-down.
- **Privacy First**: All calculations run 100% in your browser. No data is sent to any server.

## How to Run Locally
1. Simply double-click `index.html` to open it in your web browser.

## How to Host on GitHub Pages
1. Push this folder (`web_portfolio`) to your GitHub repository.
2. Go to your Repository validation **Settings** > **Pages**.
3. Under **Build and deployment**, select **Source** as `Deploy from a branch`.
4. Select `main` (or `master`) branch and the `/web_portfolio` folder (if you pushed the whole folder) or `/root` (if you pushed just the contents).
    - *Note: If GitHub Pages only allows selecting `/root` or `/docs`, you may need to move these files to the root of a new repository or a `docs` folder.*
5. Click **Save**.
6. GitHub will generate a link (e.g., `https://yourusername.github.io/your-repo/`).

## Tech Stack
- **HTML5 & CSS3**: Custom responsive design with dark mode aesthetics.
- **JavaScript (ES6)**: Core simulation logic directly ported from Python.
- **Chart.js**: Interactive data visualization.
