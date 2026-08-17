import asyncio
from playwright.async_api import async_playwright
import random
import string

async def register_clickworker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto('https://workplace.clickworker.com/en/users/new/', wait_until='networkidle')
        await page.wait_for_timeout(3000)
        
        username = f'gravityquest{random.randint(1000,9999)}'
        password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#', k=16))
        
        print(f'Attempting registration: {username} / gravitywell@riseup.net')
        
        # Fill everything via evaluate
        await page.evaluate(f'''() => {{
            // Text inputs
            document.querySelector('#user_first_name').value = 'Gravity';
            document.querySelector('#user_last_name').value = 'Quest';
            document.querySelector('#user_username').value = '{username}';
            document.querySelector('#user_email').value = 'gravitywell@riseup.net';
            document.querySelector('#user_password').value = '{password}';
            document.querySelector('#user_password_confirmation').value = '{password}';
            document.querySelector('#user_date_of_birth').value = '1990-01-01';
            document.querySelector('#user_address_street').value = '123 Main St';
            document.querySelector('#user_address_postal_code').value = '10001';
            document.querySelector('#user_address_city').value = 'New York';
            document.querySelector('#user_address_phone_number').value = '5551234567';
            
            // Select dropdowns
            document.querySelector('#user_address_country').value = 'US';
            document.querySelector('#user_address_state').value = 'NY';
            document.querySelector('#user_address_phone_code').value = '1';
            
            // Trigger change events
            ['#user_address_country', '#user_address_state', '#user_address_phone_code', '#user_date_of_birth'].forEach(sel => {{
                const el = document.querySelector(sel);
                if (el) {{
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                }}
            }});
            
            // Checkboxes
            document.querySelector('#user_agreements_is_full_age').checked = true;
            document.querySelector('#user_agreements_terms').checked = true;
            document.querySelector('#user_agreements_privacy').checked = true;
            ['#user_agreements_is_full_age', '#user_agreements_terms', '#user_agreements_privacy'].forEach(sel => {{
                const el = document.querySelector(sel);
                if (el) {{
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            }});
        }}''')
        
        # Native language search
        await page.evaluate('''() => {
            const inputs = document.querySelectorAll('input[type=search]');
            inputs.forEach(input => {
                if (input.offsetParent !== null) {
                    input.value = 'English';
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                    input.dispatchEvent(new Event('change', {bubbles: true}));
                }
            });
        }''')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(1000)
        
        print('Submitting...')
        await page.click('input[name=commit]')
        await page.wait_for_timeout(15000)
        
        print('=== RESULT ===')
        print('URL:', page.url)
        print('Title:', await page.title())
        
        body = await page.query_selector('body')
        text = await body.inner_text()
        print(text[:5000])
        
        await browser.close()

asyncio.run(register_clickworker())