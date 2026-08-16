#!/usr/bin/env python3
"""
Try to post a comment or post on Stacker News to earn sats.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load cookies
        with open('/home/user/income-quest/data/stacker_news_cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # Go to home page and look for posts to comment on
        await page.goto("https://stacker.news/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Find a post to comment on
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_home_rendered.html', 'w') as f:
            f.write(content)
        
        # Look for comment buttons or reply links
        comment_elements = await page.query_selector_all('button:has-text("comment"), button:has-text("reply"), a:has-text("comment"), a:has-text("reply"), [data-testid*="comment"]')
        print(f"Comment/reply elements found: {len(comment_elements)}")
        
        # Look for post items
        post_elements = await page.query_selector_all('[class*="item"], [class*="post"], article, [data-id]')
        print(f"Post elements found: {len(post_elements)}")
        
        # Try to find the first post and click it
        for i, post in enumerate(post_elements[:5]):
            text = await post.text_content()
            if text and len(text) > 50:
                print(f"\nPost {i}: {text[:200]}")
                # Look for link to post
                links = await post.query_selector_all('a[href*="/items/"]')
                for link in links:
                    href = await link.get_attribute('href')
                    if href:
                        print(f"  Post link: {href}")
                        # Navigate to post
                        post_page = await context.new_page()
                        await post_page.goto(f"https://stacker.news{href}" if href.startswith('/') else href, wait_until="networkidle")
                        await post_page.wait_for_timeout(2000)
                        
                        post_content = await post_page.content()
                        with open(f'/home/user/income-quest/data/stacker_post_{i}.html', 'w') as f:
                            f.write(post_content)
                        
                        # Look for comment form
                        comment_textarea = await post_page.query_selector('textarea[name="comment"], textarea[placeholder*="comment" i], textarea[placeholder*="reply" i]')
                        if comment_textarea:
                            print(f"  Found comment textarea!")
                            # Try to comment
                            comment_text = "Great post! Thanks for sharing. ⚡"
                            await comment_textarea.fill(comment_text)
                            
                            # Find submit button
                            submit_btn = await post_page.query_selector('button[type="submit"]:has-text("Comment"), button[type="submit"]:has-text("Reply"), button[type="submit"]')
                            if submit_btn:
                                await submit_btn.click()
                                await post_page.wait_for_timeout(3000)
                                print(f"  Submitted comment!")
                                
                                # Check result
                                result_content = await post_page.content()
                                if comment_text in result_content:
                                    print(f"  Comment appears on page!")
                                else:
                                    print(f"  Comment may need approval or failed")
                        else:
                            print(f"  No comment form found (may need login)")
                        
                        await post_page.close()
                        break
                break
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())