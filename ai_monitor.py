#!/usr/bin/env python3
"""
AI_Radar - Agente de Monitoreo de Inteligencia Artificial
Para desarrollo profesional y OPC (One Person Company)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

# Configuración
SOURCES_FILE = "sources.txt"
REPORT_FILE = "report.md"
TOPICS = ["artificial intelligence", "machine learning", "automation", "LLM"]

def fetch_page(url):
    """Extrae contenido HTML de una URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error en {url}: {e}")
    return None

def extract_articles(html, url):
    """Extrae títulos de artículos del HTML"""
    articles = []
    if not html:
        return articles
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Buscar títulos en diferentes formatos
    for tag in soup.find_all(['h1', 'h2', 'h3', 'article', 'a']):
        title = tag.get_text().strip()
        if title and len(title) > 20 and len(title) < 200:
            articles.append({
                'title': title,
                'url': url,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
    
    return articles[:5]  # Máximo 5 artículos por fuente

def filter_by_topics(articles):
    """Filtra artículos por temas relevantes"""
    filtered = []
    for article in articles:
        title_lower = article['title'].lower()
        if any(topic in title_lower for topic in TOPICS):
            filtered.append(article)
    return filtered

def send_whatsapp(message):
    """Envía mensaje por WhatsApp usando CallMeBot"""
    phone = os.getenv('WHATSAPP_PHONE', '')
    api_key = os.getenv('WHATSAPP_API_KEY', '')
    
    if not phone or not api_key:
        print("⚠️ WhatsApp no configurado (sin variables de entorno)")
        return False
    
    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            'phone': phone,
            'text': message,
            'apikey': api_key
        }
        response = requests.post(url, data=params)
        if response.status_code == 200:
            print("✅ Mensaje enviado a WhatsApp")
            return True
    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")
    return False

def generate_report(articles):
    """Genera reporte en Markdown"""
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"# AI Radar Report\n\n"
    report += f"**Fecha:** {date}\n\n"
    report += f"**Total de artículos encontrados:** {len(articles)}\n\n"
    
    if articles:
        report += "## Top Avances en IA\n\n"
        for i, article in enumerate(articles[:10], 1):
            report += f"{i}. **{article['title']}**\n"
            report += f"   - Fuente: {article['url']}\n"
            report += f"   - Fecha: {article['date']}\n\n"
        
        report += "## Habilidades Recomendadas\n\n"
        report += "- Python para automatización\n"
        report += "- Machine Learning básico\n"
        report += "- Análisis de datos\n"
        report += "- Ética en IA\n\n"
        
        report += "## Oportunidades de Negocio (OPC)\n\n"
        report += "- Consultoría en automatización con IA\n"
        report += "- Desarrollo de chatbots personalizados\n"
        report += "- Análisis de datos para pequeñas empresas\n"
    else:
        report += "No se encontraron artículos relevantes.\n"
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte guardado en {REPORT_FILE}")
    return report

def main():
    print("=" * 60)
    print("AI RADAR - Iniciando monitoreo")
    print("=" * 60)
    
    # Leer fuentes
    try:
        with open(SOURCES_FILE, 'r') as f:
            sources = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"📚 {len(sources)} fuentes cargadas")
    except FileNotFoundError:
        print(f"❌ No se encontró {SOURCES_FILE}")
        sources = [
            "https://www.worldbank.org/en/topic/artificial-intelligence",
            "https://openai.com/research",
            "https://blog.google/technology/ai/"
        ]
    
    all_articles = []
    
    # Procesar cada fuente
    for url in sources:
        print(f"\n🔍 Procesando: {url}")
        html = fetch_page(url)
        if html:
            articles = extract_articles(html, url)
            filtered = filter_by_topics(articles)
            all_articles.extend(filtered)
            print(f"   → {len(filtered)} artículos relevantes")
        time.sleep(1)  # Pausa entre requests
    
    print(f"\n{'=' * 60}")
    print(f"✅ Total de artículos recopilados: {len(all_articles)}")
    print(f"{'=' * 60}\n")
    
    # Generar reporte
    report = generate_report(all_articles)
    
    # Enviar resumen por WhatsApp (máximo 500 caracteres)
    if all_articles:
        whatsapp_msg = f"🤖 AI RADAR - {datetime.now().strftime('%d/%m/%Y')}\n\n"
        whatsapp_msg += "TOP 3 AVANCES IA:\n"
        for i, article in enumerate(all_articles[:3], 1):
            whatsapp_msg += f"{i}. {article['title'][:80]}\n"
        whatsapp_msg += "\nOPORTUNIDAD OPC:\n"
        whatsapp_msg += "Consultoría en automatización con IA"
        
        send_whatsapp(whatsapp_msg)
    
    print("\n✅ AI Radar completado")

if __name__ == "__main__":
    main()
