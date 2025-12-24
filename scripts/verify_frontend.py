
import asyncio
from playwright.async_api import async_playwright, expect
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        base_url = f"file://{os.getcwd()}"

        # Create verification directory
        os.makedirs('/home/jules/verification', exist_ok=True)

        # 1. Navigate to main index and click Class 5
        await page.goto(f"{base_url}/index.html")
        await page.screenshot(path="/home/jules/verification/01_main_index.png")
        await page.get_by_role("link", name="Class 5").click()

        # 2. On class page, take screenshot and click first story
        await expect(page).to_have_title("Class 5 Chapters - Telugu Buddy")
        await page.screenshot(path="/home/jules/verification/02_class5_chapters.png")
        await page.get_by_role("link", name="Read Story").first.click()

        # 3. On story page, take screenshot and go back
        await expect(page).to_have_title("Pandem - Telugu Buddy")
        await page.screenshot(path="/home/jules/verification/03_chapter1_story.png")
        await page.get_by_role("link", name="Back to Chapter Selection").first.click()

        # 4. On class page, click first exercise
        await expect(page).to_have_title("Class 5 Chapters - Telugu Buddy")
        await page.get_by_role("link", name="Exercises").first.click()

        # 5. On exercise page, take screenshot
        await expect(page).to_have_title("Pandem - Exercises - Telugu Buddy")
        await page.screenshot(path="/home/jules/verification/04_chapter1_exercises.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
