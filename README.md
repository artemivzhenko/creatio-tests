Creatio UI Test Automation Framework
Overview
This project is an automation testing framework designed specifically for Creatio front-end UI.
It allows you to easily create and run automated tests for Creatio pages without spending hours on manual regression checks.

Manual testing is useful for verifying new features, but it is slow and costly for full regression. With automation, you write your tests once and run them repeatedly to instantly detect regressions and check the health of your system.
Creatio’s front-end is not the easiest for automation, so many teams don’t use UI automation at all. This tool solves that problem by providing a ready-to-use solution for automating UI tests in Creatio.

Current Features (v1.0)

✅ Check if a field exists on a page

✅ Verify if a field is require

✅ Set a field value (text/number/datetime/lookup)

✅ Verify a field value

✅ Check if a field is readonly

Planned Features

🔜 Button click automation

🔜 Case tracking and validation

🔜 Navigation between Creatio pages

```from pages.auth_page import CreatioAuthPage
from pages.field_page import FieldPage

# Load auth settings
auth = CreatioAuthPage.from_json("auth.json")

# Create a test page object
page = FieldPage(driver=auth.driver)

# Check if field exists
page.fields["Dear"].check_exists()

# Set field value
page.fields["Dear"].set_value("Test Recipient")

# Verify value
page.fields["Dear"].check_value("Test Recipient")
