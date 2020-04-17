from bs4 import BeautifulSoup as Bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import time


def create_csv(filename: str, data: tuple):
	with open(filename, "w", encoding='utf-8') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=";", lineterminator="\n")
		wr.writerow(data)


def write_to_csv(filename: str, data: tuple):
	with open(filename, "a", encoding='utf-8') as myfile:
		try:
			wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=";", lineterminator="\n")
			wr.writerow(data)
		except Exception as error:
			print("Error while adding new line ", error)


def selenium_start() -> webdriver:
	# instantiate chrome options (that is how you want the chrome drive to work/function)
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--disable-gpu')
	# spin off automated chrome
	driver = webdriver.Chrome(options=options)

	return driver


def quit_driver(driver):
	driver.quit()
	print(" ----------- > Chrome driver instance closed successfully < ------------------")


def is_offer(find_product_deal, find_product_retail):
	if find_product_deal:
		offer = 1
	else:
		offer = 0
		find_product_deal = find_product_retail
		find_product_retail = ''
	return offer, find_product_deal, find_product_retail


def extract_content():
	# ------------------ Start web page curl with selenium to get content and quite chrome driver ---------------
	# first URL for task 1 - 4
	url = "https://www.osom.com/search?q=GUESS+1981+EDT+100ML&view=spring"
	# call func -> selenium_start which returns a str and webdriver
	driver = selenium_start()
	# send request to load/get website
	driver.get(url)
	time.sleep(5)
	# get page content
	html_content = driver.page_source
	# close automated browser
	quit_driver(driver)
	# ------------------------------ END ----------------------------------------------------------
	# --------------------- Start Output file creation process ------------------------------------
	# File name var
	file = 'product_name_and_brand.csv'
	# call write create csv function
	create_csv(file, ("Name", "Brand", "sku", "price", "offer", "Old_price", "product_URL", "Img_URL"))
	# ------------------------------ END ----------------------------------------------------------
	# ------------------------------ Start HTML parsing with BS4 to extract data ------------------
	# parse to bs4
	soup = Bs(html_content, 'lxml')
	# this variable holds the product containers/wrapper used for further iterations
	product_container = soup.find('div', class_='grid ss-item-container ss-item-container-grid ss-targeted')
	product_count = len(product_container.find_all(class_="info"))

	for i in range(product_count):
		# first
		find_product_brand = product_container.find_all(class_="info")[i].find_all('p')[0].text
		find_product_name = product_container.find_all(class_="info")[i].find_all('p')[1].text

		# second
		find_product_deal = product_container.find_all(class_="info")[i].find(class_="deal").text
		sku = product_container.find_all('div', recursive=False)[i].get('data-sku')

		# third
		find_product_retail = product_container.find_all(class_="info")[i].find(class_="retail").text
		# check if there is a discount for the product
		offer, find_product_deal, find_product_retail = is_offer(find_product_deal, find_product_retail)

		# fourth
		find_product_link = product_container.find_all(class_="image-wrapper")[i].find('a').get('href')
		find_product_img = product_container.find_all(class_="img animation")[i].get('style').replace('")', '')

		print(
			find_product_name.strip(),
			find_product_brand,
			sku,
			find_product_deal,
			offer,
			find_product_retail,
			"https:" + find_product_link,
			find_product_img.replace('background-image: url("', 'https:')
		)
		# ------------------------------ END ----------------------------------------------------------
		# --------------------- Write incoming extracted data to initial created csv file -------------
		write_to_csv(
			file,
			(
				find_product_name.strip(),
				find_product_brand,
				sku,
				find_product_deal,
				offer,
				find_product_retail,
				"https:" + find_product_link,
				find_product_img.replace('background-image: url("', 'https:')
			)
		)
		# ------------------------------ END ----------------------------------------------------------
