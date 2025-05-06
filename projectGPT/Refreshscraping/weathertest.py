import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# Headers for web scraping
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Weather code to description mapping
weather_code_map = {
    '0': 'Cerah / Clear Skies',
    '1': 'Cerah Berawan / Partly Cloudy',
    '2': 'Cerah Berawan / Partly Cloudy',
    '3': 'Berawan / Mostly Cloudy',
    '4': 'Berawan Tebal / Overcast',
    '5': 'Udara Kabur / Haze',
    '10': 'Asap / Smoke',
    '45': 'Kabut / Fog',
    '60': 'Hujan Ringan / Light Rain',
    '61': 'Hujan Sedang / Rain',
    '63': 'Hujan Lebat / Heavy Rain',
    '80': 'Hujan Lokal / Isolated Shower',
    '95': 'Hujan Petir / Severe Thunderstorm',
    '97': 'Hujan Petir / Severe Thunderstorm'
}

def parse_datetime(dt_str):
    """Convert datetime string to a datetime object."""
    return datetime.strptime(dt_str, "%Y%m%d%H%M")

def get_value(parameter, unit):
    """Get value from the parameter with specified unit."""
    values = parameter.find_all("value")
    for value in values:
        if value.get("unit") == unit:
            return value.text
    return ""

def save_forecast_to_file(filename, content):
    """Save the forecast content to a text file."""
    filename = filename.replace('.xml', '') + '.txt'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def convert_utc_to_wib(utc_dt):
    """Convert UTC datetime to WIB datetime."""
    wib_dt = utc_dt + timedelta(hours=7)
    return wib_dt

def generate_area_forecast(area, hourly_data, daily_max_temp, daily_min_temp, daily_max_humidity, daily_min_humidity):
    """Generate forecast for a specific area."""
    area_name_en = area.find("name", {"xml:lang": "en_US"}).text if area.find("name", {"xml:lang": "en_US"}) else "Unknown"
    area_name_id = area.find("name", {"xml:lang": "id_ID"}).text if area.find("name", {"xml:lang": "id_ID"}) else "Unknown"
    area_domain = area.get("domain", "Unknown")  # Safely get the 'domain' attribute

    output_content = ""

    for day in sorted(daily_max_temp.keys()):
        for hour in sorted(hourly_data[day].keys()):
            dt_obj = datetime.strptime(day + f'{hour:02d}00', "%Y%m%d%H%M")
            utc_time = convert_utc_to_wib(dt_obj)
            formatted_time = utc_time.strftime("%d %B %Y jam %H:%M WIB")
            
            weather_code = hourly_data[day][hour].get('weather', 'N/A')
            weather_description = weather_code_map.get(weather_code, 'Unknown Weather')

            output_content += f"\n [Prakiraan Cuaca Harian Wilayah {area_name_en} {area_name_id} {area_domain} pada tanggal {formatted_time}\n Suhu: {hourly_data[day][hour].get('temperature', 'N/A')}°C dan Kelembaban: {hourly_data[day][hour].get('humidity', 'N/A')}%\nKemungkinan Cuaca: {weather_description}\n Kecepatan dan Arah Angin: {hourly_data[day][hour].get('wind_speed', 'N/A')} km/h,{hourly_data[day][hour].get('wind_direction', 'N/A')}°\nTemperatur Maksimal: {daily_max_temp.get(day, 'N/A')}°C Temperatur Minimal: {daily_min_temp.get(day, 'N/A')}°C\nKelembaban Maksimal: {daily_max_humidity.get(day, 'N/A')}% Kelembaban Minimal: {daily_min_humidity.get(day, 'N/A')}%]\n"
    
    return output_content

def get_weather_data(url):
    """Fetch weather data from the provided URL."""
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return BeautifulSoup(response.content, "xml")
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return None

def main():
    urls = [
        "https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SumateraSelatan.xml",
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SumateraUtara.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SumateraBarat.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SulawesiUtara.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SulawesiTenggara.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SulawesiTengah.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SulawesiBarat.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-SulawesiSelatan.xml',  
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Aceh.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Bali.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-BangkaBelitung.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Banten.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Bengkulu.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-DIYogyakarta.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-DKIJakarta.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Gorontalo.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Jambi.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-JawaBarat.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-JawaTengah.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-JawaTimur.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KalimantanBarat.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KalimantanSelatan.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KalimantanTengah.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KalimantanTimur.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KalimantanUtara.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KepulauanRiau.xml',
        'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Lampung.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Maluku.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-MalukuUtara.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-NusaTenggaraBarat.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-NusaTenggaraTimur.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Papua.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-PapuaBarat.xml',
        # 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Riau.xml'
    ]
    
    base_url = 'https://www.bmkg.go.id/cuaca/prakiraan-cuaca-bandara.bmkg?s='
    all_data = []

    # Scrape data from BMKG Bandara/Stasiun
    for s in range(1, 7):
        url = f'{base_url}{s}'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad responses

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            table = soup.find('table', class_='table-striped')

            if table:
                data = []

                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    data.append(cols)

                df = pd.DataFrame(data, columns=['#', 'Bandara/Stasiun', 'Waktu Prakiraan (Local Time)',
                                                 'Arah Angin (dibaca: dari)', 'Kecepatan Angin dengan satuan km/jam',
                                                 'Jarak Pandang (km)', 'Cuaca', 'Probabilitas'])

                df['Waktu Prakiraan (Local Time)'] = df['Waktu Prakiraan (Local Time)'].str.replace(r'\d{2}:\d{2} WIB', '', regex=True)

                df['URL'] = url

                all_data.append(df)

            else:
                print(f'Tabel cuaca tidak ditemukan untuk URL: {url}')

        except requests.exceptions.RequestException as e:
            print(f'Error saat mengakses URL {url}: {e}')

    if all_data:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp2 = datetime.now().strftime("%Y-%m-%d")
        filename = f'D:/BMKG-GPT/data/Prakiraancuacabandara.txt'

        # Hapus file yang sudah ada (jika ada)
        if os.path.exists(filename):
            os.remove(filename)

        # Tulis data baru ke file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"\nData ini diambil pada: {timestamp} Jika terdapat data diawal dari jam 01:00 - 20:00 pada tanggal {timestamp} dan dibawah urutan kolom terdapat data 00:00 - dst maka tanggal sudah berganti menjadi tanggal selanjutnya  \n\n")

            # Loop semua data dan tambahkan ke file
            for df in all_data:
                for index, row in df.iterrows():
                    file.write(
                        f"[PRAKIRAAN CUACA BANDARA: {row['Bandara/Stasiun']}\n"
                        f"Tanggal: {timestamp2}\n"
                        f"Waktu Prakiraan Cuaca {row['Waktu Prakiraan (Local Time)']}\n"
                        f"Arah Angin: {row['Arah Angin (dibaca: dari)']}\n"
                        f"Kecepatan Angin: {row['Kecepatan Angin dengan satuan km/jam']} km/jam\n"
                        f"Visibility atau Jarak Pandang: {row['Jarak Pandang (km)']}\n"
                        f"Cuaca: {row['Cuaca']}]\n\n")

            print(f'Forecast data has been successfully saved to {filename}')
    else:
        print('Tidak ada data untuk ditampilkan.')

    # Fetching weather data from XML files
    for url in urls:
        soup = get_weather_data(url)
        if soup:
            areas = soup.find_all("area")
            daily_max_temp = {}
            daily_min_temp = {}
            daily_max_humidity = {}
            daily_min_humidity = {}
            hourly_data = {}
            parameters = soup.find_all("parameter")
            
            for parameter in parameters:
                param_id = parameter.get("id")
                timeranges = parameter.find_all("timerange")
                
                for timerange in timeranges:
                    dt = timerange.get("datetime")
                    if not dt:
                        continue  # Skip if datetime is not specified
                    
                    dt_obj = parse_datetime(dt)
                    day = dt_obj.strftime("%Y%m%d")
                    hour = int(dt_obj.strftime("%H"))
                    
                    if day not in hourly_data:
                        hourly_data[day] = {}
                    
                    if param_id == 'tmax':
                        daily_max_temp[day] = get_value(timerange, "C")
                    elif param_id == 'tmin':
                        daily_min_temp[day] = get_value(timerange, "C")
                    elif param_id == 'humax':
                        daily_max_humidity[day] = get_value(timerange, "%")
                    elif param_id == 'humin':
                        daily_min_humidity[day] = get_value(timerange, "%")
                    elif param_id == 't':
                        hourly_data[day][hour] = hourly_data[day].get(hour, {})
                        hourly_data[day][hour]['temperature'] = get_value(timerange, "C")
                    elif param_id == 'hu':
                        hourly_data[day][hour] = hourly_data[day].get(hour, {})
                        hourly_data[day][hour]['humidity'] = get_value(timerange, "%")
                    elif param_id == 'ws':
                        hourly_data[day][hour] = hourly_data[day].get(hour, {})
                        hourly_data[day][hour]['wind_speed'] = get_value(timerange, "KPH")
                    elif param_id == 'wd':
                        hourly_data[day][hour] = hourly_data[day].get(hour, {})
                        hourly_data[day][hour]['wind_direction'] = get_value(timerange, "deg")
                    elif param_id == 'weather':
                        hourly_data[day][hour] = hourly_data[day].get(hour, {})
                        hourly_data[day][hour]['weather'] = get_value(timerange, "icon")
            
            output_content = ""
            for area in areas:
                area_forecast = generate_area_forecast(area, hourly_data, daily_max_temp, daily_min_temp, daily_max_humidity, daily_min_humidity)
                output_content += area_forecast
            
            save_forecast_to_file(f"D:/BMKG-GPT/data/Prakiraancuaca{url.split('/DigitalForecast-')[-1]}", output_content)
            print(f"Forecast data for {url} has been successfully saved.")
        else:
            print(f"Skipping {url} due to fetch failure.")


if __name__ == "__main__":
    main()
