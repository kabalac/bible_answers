from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:8000"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Opening Bible Answers...")
    page.goto(BASE_URL, wait_until="networkidle")

    # Verify the page loaded
    assert "Bible Answers" in page.locator("body").inner_text()
    print("✓ Home page loaded")

    # Find the input
    textarea = page.locator("textarea")

    assert textarea.is_visible()
    print("✓ Feeling input is visible")

    # Enter a real user question
    textarea.fill("I feel anxious about my future.")
    print("✓ Question entered")

    # Click Find an Answer
    page.get_by_role("button", name="Find an Answer").click()
    print("✓ Find an Answer clicked")

    # Wait for the AI response
    response = page.locator(".response-text")
    response.wait_for(state="visible", timeout=60_000)

    assert response.inner_text().strip()
    print("✓ AI response appeared")

    # Verify Scripture appeared
    scripture = page.locator(".scripture")
    scripture.wait_for(state="visible", timeout=10_000)

    assert scripture.inner_text().strip()
    print("✓ Scripture appeared")
    # Test Begin Again
    page.get_by_role("button", name="Begin again").click()

    # Wait for the reset animation/state change
    page.wait_for_timeout(800)

    assert textarea.is_visible()
    assert textarea.is_enabled()
    assert textarea.input_value() == ""

    print("✓ Begin Again works")

        # Test feedback flow
    # The app shows feedback after the 3rd Begin Again.
    for question in [
        "I feel worried about my future.",
        "I need strength to face today.",
    ]:
        textarea.fill(question)

        page.get_by_role("button", name="Find an Answer").click()

        page.locator(".response-text").wait_for(
            state="visible",
            timeout=60_000,
        )

        page.get_by_role("button", name="Begin again").click()
        page.wait_for_timeout(800)

    # The third Begin Again happens after the original answer
    # plus the two additional answers above.
    feedback_card = page.locator(".feedback-card")
    feedback_card.wait_for(state="visible", timeout=5_000)

    assert feedback_card.is_visible()
    print("✓ Feedback card appeared")

    # Submit helpful feedback
    page.get_by_role("button", name="😊 Helpful").click()

    # Allow the feedback fade-out animation to complete
    page.wait_for_timeout(500)

    assert not feedback_card.is_visible()
    print("✓ Feedback submission works")

           # Test Privacy PDF opens in a new tab
    with page.expect_popup(timeout=10_000) as popup_info:
        page.get_by_role("link", name="Privacy").click()

    privacy_page = popup_info.value

    # The important browser-level check:
    # clicking Privacy must open a separate tab/window.
    assert privacy_page is not None

    print("✓ Privacy PDF opens in a new tab")

    privacy_page.close() 

    print()
    print("🎉 Main user journey passed!")

    browser.close()