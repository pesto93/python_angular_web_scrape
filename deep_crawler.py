from web_crawler import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import requests
import json
from datetime import datetime


def get_product_description(driver: webdriver, link: str) -> str:
	# open new blank tab
	driver.execute_script("window.open();")
	# switch to the new window which is second in window_handles array
	driver.switch_to.window(driver.window_handles[1])
	# open successfully, get page source and close
	driver.get(link)
	time.sleep(5)
	content = Bs(driver.page_source, 'lxml')
	driver.close()
	# Switch back to the first tab with URL A
	driver.switch_to.window(driver.window_handles[0])
	# find and extract product description
	des = content.find('div', class_="description").text
	return des


def get_product_addition_desc(link: str) -> (str, str):
	# use with -> to close every connection after request.get
	with requests.get(link, stream=True) as read:
		content = json.loads(read.content)
		created_at = content["product"]["created_at"]
		published_at = content["product"]["published_at"]
		print(created_at, published_at)
		return created_at, published_at


def show_all_product() -> tuple:
	# --------------------- Start Output file creation process ------------------------------------
	# File name var
	file = 'All_product_name_and_brand.csv'
	# call write create csv function
	create_csv(file, ("Name", "Brand", "sku", "price", "offer", "Old_price", "product_URL", "Img_URL", "Description", "created_at", "published_at"))
	# ------------------------------ END ----------------------------------------------------------

	# ------------------ Start web page curl with selenium to get content and quite chrome driver ---------------
	url = "https://www.osom.com/collections/femenino-perfumeria-belleza"
	# call func -> selenium_start which returns a str and webdriver
	driver = selenium_start()
	# Add a web driver wait -> to check some web element presence
	wait = WebDriverWait(driver, 10)
	# send request to load/get website
	driver.get(url)

	while True:
		try:
			load_more = wait.until(ec.visibility_of_element_located((
				By.XPATH,
				"//a[@class='ss-infinite-loadmore-button'][contains(text(), 'Ver Más')]"))
			)
			load_more.click()
			wait.until(ec.staleness_of(load_more))

		except TimeoutException:
			break

	# get page content and parse to bs4
	soup = Bs(driver.page_source, 'lxml')

	return soup, driver, file
	# ------------------------------ END ----------------------------------------------------------


def start_content_parsing():
	# ------------------------------ Start HTML parsing with BS4 to extract data ------------------
	soup, driver, output_file = show_all_product()

	product_container = len(soup.find_all(
		"div",
		{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
	))

	for i in range(product_container):
		find_product_brand = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].find(class_="info").find_all('p')[0].text

		find_product_name = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].find(class_="info").find_all('p')[1].text

		find_product_deal = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].find(class_="info").find(class_="deal").text

		sku = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].get('data-sku')

		find_product_retail = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].find(class_="info").find(class_="retail").text
		# check if there is a discount for the product
		offer, find_product_deal, find_product_retail = is_offer(find_product_deal, find_product_retail)

		find_product_link = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].find(class_="image-wrapper").find('a').get('href')

		find_product_img = soup.find_all(
			"div",
			{"class": "ss-product-item product-item animation grid__item large--one-quarter medium--one-half small--one-half ng-scope"}
		)[i].find(class_="img animation").get('style').replace('")', '')

		product_description = get_product_description(driver, "https:" + find_product_link)

		created_at, published_at = get_product_addition_desc("https:" + find_product_link + ".json")

		print("https:" + find_product_link)

		write_to_csv(
			output_file,
			(
				find_product_name.strip(),
				find_product_brand,
				sku,
				find_product_deal,
				offer,
				find_product_retail,
				"https:" + find_product_link,
				find_product_img.replace('background-image: url("', 'https:'),
				product_description,
				created_at,
				published_at
			)
		)

	# kill driver
	quit_driver(driver)


# autopilot
extract_content()
start_content_parsing()

# use a simple python flask or just send a request with json
# https://www.osom.com/products/michael-kors-sheer-100ml-edp-spray-michael-kors-343603.json
# get_product_addition_desc("https://www.osom.com/products/michael-kors-sheer-100ml-edp-spray-michael-kors-343603.json")
