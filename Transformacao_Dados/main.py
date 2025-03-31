import services
import re
from urllib.parse import urljoin, urlparse


#constantes
URL = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'
DOWNLOAD_FOLDER = "temp_pdfs"
PDF_PATTERN = re.compile(r'(?i)Anexo[ _-]*I.*\.pdf$')

def main():

    try:
        print("Starting processing...")
        services.setup_directories()

        # 1. Consegue o conteudo da pagina web do PDF
        print("Fetching page content...")
        soup = services.fetch_page_content(URL)
        pdf_links = soup.find_all('a', href=PDF_PATTERN)

        if not pdf_links:
            raise ValueError("No PDF link found matching the pattern")

        # 2. Baixa PDF
        pdf_url = urljoin(URL, pdf_links[0]['href'])
        pdf_filename = services.Path(urlparse(pdf_url).path).name
        pdf_path = services.Path(DOWNLOAD_FOLDER) / pdf_filename

        print(f"Downloading PDF: {pdf_filename}")
        if not services.download_pdf_file(pdf_url, pdf_path):
            raise ConnectionError("Failed to download PDF")

        # 3. Extraindo tabelas do PDF
        print("Extracting tables from PDF...")
        raw_data = services.extract_tables_from_pdf(pdf_path)

        # 4. Processa data
        print("Processing data...")
        processed_data = services.process_data(raw_data)

        # 5. Salva e compacta
        print("Saving and compressing results...")
        output_file = services.save_and_compress(processed_data)

        print(f"\nProcess completed successfully!")
        print(f"Output file: {output_file.absolute()}")

    except Exception as e:
        print(f"\nError during execution: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        services.cleanup()


if __name__ == "__main__":
    import sys

    main() 