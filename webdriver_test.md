# WebDriver Test Instructions

Test the WebDriver functionality using these commands:

## 1. Start g3 with WebDriver enabled:
```bash
cargo run -- --webdriver --chrome-headless --chat
```

## 2. In the g3 interactive session, try these commands:

### Start WebDriver session:
```
Start a webdriver session
```

### Navigate to a website:
```
Navigate to https://example.com
```

### Get page information:
```
Get the current URL and page title
```

### Find elements:
```
Find the h1 element on the page and get its text
```

### Take a screenshot:
```
Take a screenshot of the current page and save it to /tmp/test-screenshot.png
```

### Test navigation:
```
Navigate to https://httpbin.org/html, then go back, forward, and refresh
```

### Execute JavaScript:
```
Execute JavaScript: return document.title
```

### Get page source:
```
Get the page source (limited to first 1000 characters)
```

### End session:
```
Close the webdriver session
```

## Available WebDriver Tools:

- `webdriver_start` - Start a WebDriver session
- `webdriver_navigate` - Navigate to a URL
- `webdriver_get_url` - Get current URL
- `webdriver_get_title` - Get page title
- `webdriver_find_element` - Find element by CSS selector
- `webdriver_find_elements` - Find multiple elements
- `webdriver_click` - Click an element
- `webdriver_send_keys` - Send text to an element
- `webdriver_execute_script` - Execute JavaScript
- `webdriver_get_page_source` - Get page HTML source
- `webdriver_screenshot` - Take screenshot
- `webdriver_back` - Navigate back
- `webdriver_forward` - Navigate forward
- `webdriver_refresh` - Refresh page
- `webdriver_quit` - Close browser and end session

## Configuration:

The system is configured to use:
- ChromeDriver on port 9515
- Chromium browser in headless mode
- All WebDriver tools enabled when `--webdriver` flag is used