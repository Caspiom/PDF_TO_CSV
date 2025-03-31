import zipfile
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import pdfplumber

# Constants
REQUEST_TIMEOUT = 10  # Timeout in seconds for HTTP requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
MAX_RETRIES = 3  # Maximum number of download retries
DOWNLOAD_CHUNK_SIZE = 8192  # Chunk size for streaming downloads
DOWNLOAD_FOLDER = "temp_pdfs"
OUTPUT_FOLDER = "output"
CSV_FILENAME = "lista_de_procedimentos.csv"
ZIP_FILENAME = f"Teste_Lucas_Gaspari.zip"

# Legend for column abbreviations
LEGENDA = {
    "OD": "Seg. Odontológica",
    "AMB": "Seg. Ambulatorial",
}

def setup_directories() -> None:
    """Crie os diretórios necessários para o processo."""
    Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)


def fetch_page_content(url: str) -> BeautifulSoup:
    """Buscar conteúdo HTML de uma URL com tratamento de erros."""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as error:
        raise ConnectionError(f"Failed to fetch page content: {error}")


def download_pdf_file(pdf_url: str, save_path: Path) -> bool:
    """Baixar um arquivo PDF com tentativas repetidas e download em partes."""
    headers = {'User-Agent': USER_AGENT}
    session = requests.Session()

    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(
                pdf_url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                stream=True
            )
            response.raise_for_status()

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
            return True

        except (requests.RequestException, IOError) as error:
            if attempt == MAX_RETRIES - 1:
                raise ConnectionError(f"Failed to download PDF after {MAX_RETRIES} attempts: {error}")
            continue

    return False


def extract_tables_from_pdf(pdf_path: Path) -> pd.DataFrame:
    """Extrair tabelas de um PDF usando pdfplumber."""
    all_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    if len(table) > 1:  # Ignore empty tables
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df = df.dropna(how='all')
                        all_tables.append(df)

        if not all_tables:
            raise ValueError("No tables found in PDF")

        return pd.concat(all_tables, ignore_index=True)

    except pdfplumber.PDFSyntaxError:
        raise ValueError("Invalid or corrupted PDF file")


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Processar dados e substituir abreviações."""
    processed_df = df.copy()

    # Replace abbreviations
    for col in LEGENDA.keys():
        if col in processed_df.columns:
            processed_df[col] = processed_df[col].replace(LEGENDA)

    # Data cleaning
    processed_df = processed_df.dropna(how='all')
    processed_df = processed_df.map(lambda x: x.strip() if isinstance(x, str) else x)

    return processed_df


def save_and_compress(df: pd.DataFrame) -> Path:
    """Salvar DataFrame em CSV e compactá-lo."""
    csv_path = Path(OUTPUT_FOLDER) / CSV_FILENAME
    zip_path = Path(OUTPUT_FOLDER) / ZIP_FILENAME

    # Save CSV
    df.to_csv(csv_path, index=True, encoding='utf-8-sig')

    # Create ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_path, arcname=csv_path.name)

    return zip_path


def cleanup() -> None:
    """Limpar arquivos temporários."""
    # Remove downloaded PDFs
    temp_dir = Path(DOWNLOAD_FOLDER)
    if temp_dir.exists():
        for file in temp_dir.glob('*'):
            file.unlink()
        temp_dir.rmdir()

    # Remove CSV (optional, comment out if you want to keep it)
    csv_path = Path(OUTPUT_FOLDER) / CSV_FILENAME
    if csv_path.exists():
        csv_path.unlink()