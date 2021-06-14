import requests
import bs4
import datetime
import pandas as pd


class Scraper(object):
	"""
	Scraper.

	Parameters:
		url: String. BDE url.
	"""

	def __init__(self, url):
		"""
		Init method.
		"""
		self.url = url
		self.fetch_time = None

	def __repr__(self):
		"""
		Visualization
		"""
		return self.url + "\n" + self.fetch_time

	def fetching_data(self, filename: str):
		"""
		Retrieve data and save it as a csv file.

		Parameters:
			filename: String. Filename path. E.g.: "Unidades.csv"

		Returns:
			Fetched data saved in a CSV file.
		"""

		with requests.Session() as s:
			# First request, retrieving hidden values.
			r = s.get(url=self.url)
			soup = bs4.BeautifulSoup(r.content, "html.parser")

			token = soup.find("input", attrs={"name": "token", "type": "hidden"})["value"]
			form_submit = soup.find("input", attrs={"name": "form_SUBMIT", "type": "hidden"})["value"]
			javax = soup.find("input", attrs={"name": "javax.faces.ViewState", "type": "hidden"})["value"]

			# Second request, sending payload as a post.
			payload = {"ComboBox": "", "form:BotoneraUsuarioLimitado_3": "CSV Downloads",
					   "token": token, "form_SUBMIT": form_submit, "javax.faces.ViewState": javax}

			form_url = "http://app.bde.es/sew_www/faces/sew_wwwias/jsp/op/DescargaUnidadesSEC2010UltimaFechaOP/DescargaUnidadesSEC2010UltimaFecha.jsp"
			r = s.post(form_url, data=payload)
			soup = bs4.BeautifulSoup(r.content, "html.parser")

			# Third request, downloading lastest available data.
			raw_url = 'http://app.bde.es'
			csv_link = soup.find("a", attrs={"id": "form:Enlace_Link"})["href"]
			csv_file = s.get(raw_url + csv_link)

		with open(filename, "wb") as f:
			f.write(csv_file.content)

		self.fetch_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

	def reading_csv(self, filename: str):
		"""
		Read CSV file into a data frame.

		Parameters:
			filename: String. CSV file to read.

		Returns:
			Read file into a dataframe.
		"""

		return pd.read_csv(filename, skiprows=3, encoding='iso-8859-1')


if __name__ == "__main__":
	url = 'http://app.bde.es/sew_www/GestorDePeticiones?IdOperacion=besew_www_DescargaUnidadesSEC2010UltimaFechaOP'
	filename_csv = "data/test.csv"
	bde = Scraper(url)
	bde.fetching_data(filename_csv)
	df = bde.reading_csv(filename_csv)

	print("Process Completed.")
