# Automation Test Techniques

This document outlines the key techniques and patterns used in our Playwright automation framework to ensure reliability, scalability, and maintainability.

## 1. Page Object Model (POM)
**Goal**: Separate test logic from UI details.
- Each page is represented by a Python class (e.g., `HomePage`, `ClientUpdatePage`).
- Locators and interactions are encapsulated within these classes.
- Tests read like high-level user stories (e.g., `home.add_client(...)`).

## 2. API-Based Authentication Bypass
**Goal**: Speed up tests and avoid testing the login form repeatedly.
- **Technique**: Use a valid JWT token generated via API request (`api_context`).
- **Implementation**: Inject the token into `localStorage` or `BrowserContext` storage state.
- **Benefit**: Skips the UI login flow for non-login tests, saving time and reducing flakiness.

## 3. Dynamic Wait Strategies
**Goal**: Handle asynchronous UI updates (SPA) reliably.
- **Auto-waiting**: Playwright's built-in auto-waiting for actionability (visible, enabled, stable).
- **Explicit Waits**: 
  - `expect(locator).to_be_visible(timeout=10000)`: verifying elements appear.
  - `page.wait_for_load_state("networkidle")`: waiting for background network requests to settle.
  - `page.get_by_role("dialog").wait_for(state="detached")`: ensuring overlays are fully closed.

## 4. Atomic & Independent Tests
**Goal**: Tests can run in any order and in parallel.
- **Fixture Management**: Use `pytest` fixtures (`new_client`, `auth_page`) to set up and tear down state.
- **Data Isolation**: Generate unique data (e.g., `uuid` based names) to avoid collision between parallel workers.

## 5. Visual & Functional Assertions
**Goal**: Verify state accurately.
- **Functional**: `expect(locator).to_have_text(...)`, `to_be_visible()`.
- **Lists/Grids**: Verify rows in tables using filtered locators (`get_by_role("row", name=...)`).

## 6. Parallel Execution
**Goal**: Reduce test suite execution time.
- **Tool**: `pytest-xdist`.
- **Strategy**: Run multiple workers (`-n 2`). Each worker gets its own isolated browser context and auth state.

## 7. Reporting & Debugging
**Goal**: Fast failure analysis.
- **Pytest HTML Report**: Detailed step-by-step execution logs using `utils.step`.
- **Artifacts**: Screenshots and traces (optional) on failure.
- **CI/CD**: GitHub Actions workflow generates and uploads reports automatically.

## 8. Continuous Integration (CI)
**Goal**: Run tests automatically on code changes.
- **GitHub Actions**: Configured in `.github/workflows/test.yml`.
- **Services**: Spins up local API and UI servers before running tests.
