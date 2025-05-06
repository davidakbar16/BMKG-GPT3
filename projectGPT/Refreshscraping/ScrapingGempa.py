import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import schedule
import os


def fetch_data_and_save(url, filename_prefix, title):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        if url.endswith(".xml"):
            soup = BeautifulSoup(response.content, "xml")
            earthquakes = []
            
            if url == "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.xml":
                alerts = soup.find_all("gempa")
                
                for info in alerts:
                    tanggal = info.find("Tanggal").text
                    jam = info.find("Jam").text
                    latitude = info.find("Lintang").text
                    longitude = info.find("Bujur").text
                    magnitude = info.find("Magnitude").text
                    depth = info.find("Kedalaman").text
                    area = info.find("Wilayah").text
                    potensi = info.find("Potensi").text
                    dirasakan = info.find("Dirasakan").text
                                
                    earthquake = {
                        "Tanggal": tanggal,
                        "Jam": jam,
                        "Latitude": latitude,
                        "Longitude": longitude,
                        "Magnitude": magnitude,
                        "Depth": depth,
                        "Area": area,
                        "Potensi": potensi,
                        "Dirasakan": dirasakan,
                    }
                    
                    earthquakes.append(earthquake)
            
            else:
                alerts = soup.find_all("alert")
                
                for alert in alerts:
                    infos = alert.find_all("info")
                    for info in infos:
                        event = info.find("event").text
                        date = info.find("date").text
                        time = info.find("time").text
                        latitude = info.find("latitude").text
                        longitude = info.find("longitude").text
                        magnitude = info.find("magnitude").text
                        depth = info.find("depth").text
                        area = info.find("area").text
                        potential = info.find("potential").text
                        subject = info.find("subject").text
                        headline = info.find("headline").text
                        description = info.find("description").text
                        instruction = info.find("instruction").text
            
                        earthquake = {
                            "Event": event,
                            "Date": date,
                            "Time": time,
                            "Latitude": latitude,
                            "Longitude": longitude,
                            "Magnitude": magnitude,
                            "Depth": depth,
                            "Area": area,
                            "Potential": potential,
                            "Subject": subject,
                            "Headline": headline,
                            "Description": description,
                            "Instruction": instruction
                        }
                        
                        earthquakes.append(earthquake)
            
            filename = f"D:/BMKG-GPT/data/{filename_prefix}.txt"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"\t {title}\n")
                for idx, eq in enumerate(earthquakes, start=1):
                    if url == "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.xml":
                        file.write(f"[{title}\nGempa Bumi terbaru pada tanggal dan jam: {eq['Tanggal']} {eq['Jam']}\nLintang dan Bujur: {eq['Latitude']} {eq['Longitude']}\nKekuatan/Magnitude: {eq['Magnitude']} M\nKedalaman: {eq['Depth']} km\nArea: {eq['Area']}\nPotensi: {eq['Potensi']}\nDirasakan: {eq['Dirasakan']}]\n\n\n")
                    else:
                        file.write(f"[{title}\nGempa Bumi terjadi pada tanggal dan jam: {eq['Date']} {eq['Time']}\nLintang dan Bujur: {eq['Latitude']} {eq['Longitude']}\nKekuatan/Magnitude: {eq['Magnitude']} M\nKedalaman: {eq['Depth']} km\nArea: {eq['Area']}\nPotensi: {eq['Potential']}\nSubjek: {eq['Subject']}\nInformasi: {eq['Headline']}\nDeskripsi: {eq['Description']}\nInstruksi: {eq['Instruction']}]\n\n\n")
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"\nData ini diambil pada: {timestamp} WIB\n")
            
            print(f"Data berhasil disimpan di {filename}")
        
        elif url.endswith(".html"):
            soup = BeautifulSoup(response.content, "html.parser")
            earthquakes = []
            
            alerts = soup.find_all("gempa")
            
            for info in alerts:
                tanggal = info.find("Tanggal").text
                jam = info.find("Jam").text
                latitude = info.find("Lintang").text
                longitude = info.find("Bujur").text
                magnitude = info.find("Magnitude").text
                depth = info.find("Kedalaman").text
                area = info.find("Wilayah").text
                potensi = info.find("Potensi").text
                dirasakan = info.find("Dirasakan").text
                            
                earthquake = {
                    "Tanggal": tanggal,
                    "Jam": jam,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Magnitude": magnitude,
                    "Depth": depth,
                    "Area": area,
                    "Potensi": potensi,
                    "Dirasakan": dirasakan,
                }
                
                earthquakes.append(earthquake)
            
            filename = f"D:/BMKG-GPT/data/{filename_prefix}.txt"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"\t {title}\n")
                for idx, eq in enumerate(earthquakes, start=1):
                    file.write(f"[{title}\nGempa Bumi terjadi pada tanggal dan jam: {eq['Tanggal']} {eq['Jam']}\nLintang dan Bujur: {eq['Latitude']} {eq['Longitude']}\nKekuatan/Magnitude: {eq['Magnitude']} M\nKedalaman: {eq['Depth']} km\nArea: {eq['Area']}\nPotensi: {eq['Potensi']}\nDirasakan: {eq['Dirasakan']}]\n\n\n")
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"\nData ini diambil pada: {timestamp} WIB\n")
            
            print(f"Data berhasil disimpan di {filename}")
            
        else:
            print(f"Unsupported file format for URL: {url}")
    
    else:
        print(f"Gagal mengambil data dari {url}. Kode status: {response.status_code}")

def main():
    urls = [
        ("https://bmkg-content-inatews.storage.googleapis.com/last30feltevent.xml", "GEMPABUMIDIRASAKAN", "GEMPA DIRASAKAN GEMPA BUMI DIRASAKAN\nBerikut Kumpulan Informasi Gempa YANG TERASAKAN MASYARAKAT di Indonesia dan sekitar"),
        ("https://bmkg-content-inatews.storage.googleapis.com/last30event.xml", "GEMPABUMIKEKUATAN5Lebih", "Berikut Kumpulan Informasi Gempa Bumi Dengan Kekuatan Lebih dari 5 (M>5) yang terjadi di Indonesia dan sekitar\nINFORMASI Gempa Bumi Dengan Kekuatan Lebih dari 5 (M>5)"),
        ("https://bmkg-content-inatews.storage.googleapis.com/last30tsunamievent.xml", "GEMPABUMIMEMUNGKINANTSUNAMI", "Berikut Kumpulan Informasi GEMPA BUMI MEMUNGKINKAN MENYEBABKAN TSUNAMI yang terjadi di Indonesia dan sekitar\nINFORMASI GEMPA BUMI MEMUNGKINKAN MENYEBABKAN TSUNAMI"),
        ("https://data.bmkg.go.id/DataMKG/TEWS/autogempa.xml", "GempaBumiTerbaru", "Gempa Bumi Terbaru")
    ]
    
    for url, filename_prefix, title in urls:
        fetch_data_and_save(url, filename_prefix, title)

if __name__ == "__main__":
    main()

