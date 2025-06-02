import requests
from bs4 import BeautifulSoup
import csv
from openpyxl import Workbook
from urllib.parse import urljoin

def get_page_content(url):
    """Получает содержимое страницы"""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch page: {url}")

def parse_book_page(book_url):
    """Парсит страницу книги и возвращает информацию"""
    content = get_page_content(book_url)
    soup = BeautifulSoup(content, 'html.parser')
    
    title = soup.find('h1').text
    price = soup.find('p', class_='price_color').text.strip('Â£')
    
    # Парсинг рейтинга
    rating_element = soup.find('p', class_='star-rating')
    rating_classes = rating_element['class']
    rating = 0
    for cls in rating_classes:
        if cls.startswith('One'):
            rating = 1
        elif cls.startswith('Two'):
            rating = 2
        elif cls.startswith('Three'):
            rating = 3
        elif cls.startswith('Four'):
            rating = 4
        elif cls.startswith('Five'):
            rating = 5
    
    # Проверка наличия
    availability = soup.find('p', class_='instock availability').text.strip()
    
    return {
        'Title': title,
        'Price': float(price),
        'Rating': rating,
        'Availability': availability,
        'URL': book_url
    }

def parse_category(category_url):
    """Парсит все книги в категории с учетом пагинации"""
    all_books = []
    
    while True:
        content = get_page_content(category_url)
        soup = BeautifulSoup(content, 'html.parser')
        
        # Парсим книги на текущей странице
        books = soup.find_all('article', class_='product_pod')
        for book in books:
            book_link = book.find('h3').find('a')['href']
            full_book_url = urljoin(category_url, book_link)
            book_info = parse_book_page(full_book_url)
            all_books.append(book_info)
        
        # Проверяем наличие следующей страницы
        next_button = soup.find('li', class_='next')
        if next_button:
            next_link = next_button.find('a')['href']
            # Обрабатываем относительные URL для пагинации
            if 'catalogue/' not in next_link:
                next_link = 'catalogue/' + next_link
            category_url = urljoin(category_url, next_link)
        else:
            break
    
    return all_books

def save_to_csv(books, filename):
    """Сохраняет данные в CSV файл"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Price', 'Rating', 'Availability', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)

def save_to_excel(books, filename):
    """Сохраняет данные в Excel файл"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Books"
    
    # Заголовки
    ws.append(['Title', 'Price', 'Rating', 'Availability', 'URL'])
    
    # Данные
    for book in books:
        ws.append([
            book['Title'],
            book['Price'],
            book['Rating'],
            book['Availability'],
            book['URL']
        ])
    
    wb.save(filename)

if __name__ == "__main__":
    # Пример использования для категории Travel
    base_url = "http://books.toscrape.com/"
    category_url = urljoin(base_url, "catalogue/category/books/travel_2/index.html")
    
    print("Парсинг книг...")
    books_data = parse_category(category_url)
    
    print("Сохранение в CSV...")
    save_to_csv(books_data, "books.csv")
    
    print("Сохранение в Excel...")
    save_to_excel(books_data, "books.xlsx")
    
    print(f"Готово! Спарсено {len(books_data)} книг.")