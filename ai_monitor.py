#!/usr/bin/env python3
"""
AI_Radar - Agente de Monitoreo de Inteligencia Artificial
Para desarrollo profesional y OPC (One Person Company)

Extrae automáticamente los últimos avances en IA de organismos internacionales 
y entidades chinas para mantener informado y direccionar el aprendizaje.
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import pandas as pd
from datetime import datetime
import re
import time
from urllib.parse import urljoin

# Temas de interés para filtrar
TOPICS = ['artificial intelligence', 'machine learning', 'automation', 
          'deep learning', 'neural network', 'AI', 'generative AI',
          'large language model', 'LLM', 'computer vision', 'NLP']

def read_sources(filename='sources.txt'):
    """Lee las URLs desde el archivo sources.txt"""
    with open(filename, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def extract_date_from_text(text):
    """Intenta extraer una fecha de un texto"""
    date_patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
        r'\b(\d{4}-\d{2}-\d{2})\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|December)\s+\d{4}\b'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def fetch_page_content(url, timeout=10):
    """Obtiene el contenido HTML de una URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def extract_articles_from_html(html, url):
    """Extrae artículos desde HTML usando BeautifulSoup"""
    articles = []
    
    if not html:
        return articles
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Intentar encontrar títulos de artículos
    title_tags = soup.find_all(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|headline|article', re.I))
    
    # También buscar enlaces que parezcan artículos
    links = soup.find_all('a', href=True)
    
    found_items = set()
    
    for tag in title_tags[:20]:  # Limitar a 20 títulos
        title = tag.get_text(strip=True)
        if title and len(title) > 10 and len(title) < 200:
            if title not in found_items:
                # Buscar fecha cercana
                date_elem = tag.find_next_sibling(string=re.compile(r'\d'))
                date_str = extract_date_from_text(str(tag.parent)) if date_elem else None
                
                articles.append({
                    'title': title,
                    'date': date_str or 'Recent',
                    'source': url,
                    'url': url
                })
                found_items.add(title)
    
    # Buscar en enlaces también
    for link in links[:50]:  # Limitar a 50 enlaces
        title = link.get_text(strip=True)
        if title and len(title) > 15 and len(title) < 150:
            # Verificar si parece un artículo
            if any(topic.lower() in title.lower() for topic in TOPICS):
                if title not in found_items:
                    articles.append({
                        'title': title,
                        'date': 'Recent',
                        'source': url,
                        'url': urljoin(url, link['href']) if link['href'].startswith('/') else link['href']
                    })
                    found_items.add(title)
    
    return articles

def filter_by_topics(articles, topics):
    """Filtra artículos por temas de interés"""
    filtered = []
    for article in articles:
        title_lower = article['title'].lower()
        if any(topic.lower() in title_lower for topic in topics):
            filtered.append(article)
    return filtered

def generate_recommendations(articles):
    """Genera recomendaciones basadas en los artículos encontrados"""
    recommendations = {
        'skills': set(),
        'opportunities': set()
    }
    
    skill_keywords = {
        'Python': ['python', 'programming'],
        'Machine Learning': ['machine learning', 'ml', 'scikit-learn'],
        'Deep Learning': ['deep learning', 'neural networks', 'tensorflow', 'pytorch'],
        'Data Analysis': ['data analysis', 'pandas', 'statistics'],
        'NLP': ['nlp', 'natural language processing', 'llm', 'language model'],
        'Computer Vision': ['computer vision', 'image processing', 'opencv'],
        'Cloud Computing': ['cloud', 'aws', 'azure', 'gcp'],
        'AI Ethics': ['ethics', 'responsible ai', 'ai governance'],
        'Automation': ['automation', 'rpa', 'workflow'],
        'Generative AI': ['generative ai', 'gpt', 'diffusion', 'stable diffusion']
    }
    
    opportunity_keywords = {
        'Consultoría en IA': ['consulting', 'implementation', 'strategy'],
        'Desarrollo de Modelos Custom': ['custom', 'fine-tuning', 'specialized'],
        'Automatización de Procesos': ['automation', 'efficiency', 'process'],
        'Análisis de Datos': ['analytics', 'insights', 'data-driven'],
        'Educación en IA': ['training', 'education', 'workshop'],
        'Integración de APIs de IA': ['api', 'integration', 'deployment']
    }
    
    for article in articles:
        title_lower = article['title'].lower()
        
        for skill, keywords in skill_keywords.items():
            if any(kw in title_lower for kw in keywords):
                recommendations['skills'].add(skill)
        
        for opp, keywords in opportunity_keywords.items():
            if any(kw in title_lower for kw in keywords):
                recommendations['opportunities'].add(opp)
    
    # Añadir recomendaciones base si no hay suficientes
    default_skills = ['Python', 'Machine Learning', 'Data Analysis', 'AI Ethics']
    default_opps = ['Consultoría en IA', 'Automatización de Procesos', 'Desarrollo de Modelos Custom']
    
    while len(recommendations['skills']) < 4:
        for skill in default_skills:
            recommendations['skills'].add(skill)
    
    while len(recommendations['opportunities']) < 3:
        for opp in default_opps:
            recommendations['opportunities'].add(opp)
    
    return recommendations

def generate_report(articles, output_file='report.md'):
    """Genera el reporte en formato Markdown"""
    recommendations = generate_recommendations(articles)
    
    # Ordenar artículos por relevancia (simplificado)
    sorted_articles = sorted(articles, key=lambda x: len(x['title']), reverse=True)[:5]
    
    report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    md_content = f"""# AI_Radar - Reporte de Monitoreo de Inteligencia Artificial

**Fecha del Reporte:** {report_date}

---

## 📊 Resumen Ejecutivo

Este reporte presenta los últimos avances en Inteligencia Artificial extraídos de organismos internacionales y entidades chinas, diseñado para apoyar el desarrollo profesional y oportunidades de negocio en una One Person Company (OPC).

**Total de artículos analizados:** {len(articles)}

---

## 🏆 Top 5 Avances Más Importantes

"""
    
    for i, article in enumerate(sorted_articles, 1):
        md_content += f"""### {i}. {article['title']}

- **Fuente:** {article['source']}
- **Fecha:** {article['date']}
- **Enlace:** [{article['url']}]({article['url']})

"""
    
    md_content += """---

## 💡 Habilidades Recomendadas a Aprender

Basado en las tendencias identificadas, estas son las habilidades más relevantes para desarrollar:

"""
    
    skills_list = list(recommendations['skills'])[:8]
    for i, skill in enumerate(skills_list, 1):
        md_content += f"{i}. **{skill}**\n"
    
    md_content += """
### Plan de Aprendizaje Sugerido:

1. **Corto plazo (1-3 meses):** Python, Fundamentos de Machine Learning
2. **Mediano plazo (3-6 meses):** Deep Learning, NLP o Computer Vision (según interés)
3. **Largo plazo (6-12 meses):** Especialización en área elegida + Ética en IA

---

## 💼 Oportunidades de Negocio Identificadas

"""
    
    opps_list = list(recommendations['opportunities'])[:6]
    for i, opp in enumerate(opps_list, 1):
        md_content += f"{i}. **{opp}**\n"
    
    md_content += """
### Estrategias para OPC:

- **Servicios de Consultoría:** Ayudar a empresas a implementar soluciones de IA
- **Productos Digitalizados:** Crear herramientas basadas en IA para nichos específicos
- **Automatización como Servicio:** Ofrecer servicios de automatización de procesos
- **Contenido Educativo:** Desarrollar cursos y materiales sobre IA

---

## 📈 Tendencias Observadas

"""
    
    # Análisis simple de tendencias
    topic_counts = {}
    for article in articles:
        title_lower = article['title'].lower()
        for topic in TOPICS[:5]:
            if topic.lower() in title_lower:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    if topic_counts:
        md_content += "Temas más frecuentes en las publicaciones:\n\n"
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            md_content += f"- **{topic.title()}**: {count} menciones\n"
    else:
        md_content += "Se recomienda revisar las fuentes directamente para identificar tendencias específicas.\n"
    
    md_content += f"""
---

## 🔗 Fuentes Monitoreadas

"""
    
    sources = set(article['source'] for article in articles)
    for source in sources:
        md_content += f"- {source}\n"
    
    md_content += f"""
---

*Reporte generado automáticamente por AI_Radar - Tu asistente de monitoreo de IA*

**Próxima actualización sugerida:** {datetime.now().strftime('%Y-%m-%d')} + 7 días
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return output_file

def main():
    print("=" * 60)
    print("AI_Radar - Agente de Monitoreo de Inteligencia Artificial")
    print("=" * 60)
    print()
    
    # Leer fuentes
    print("📖 Leyendo fuentes desde sources.txt...")
    urls = read_sources()
    print(f"   Encontradas {len(urls)} fuentes")
    print()
    
    all_articles = []
    
    # Procesar cada URL
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Procesando: {url[:50]}...")
        
        html = fetch_page_content(url)
        if html:
            articles = extract_articles_from_html(html, url)
            filtered = filter_by_topics(articles, TOPICS)
            all_articles.extend(filtered)
            print(f"   → {len(filtered)} artículos relevantes encontrados")
        
        time.sleep(0.5)  # Pequeña pausa entre requests
    
    print()
    print(f"✅ Total de artículos recopilados: {len(all_articles)}")
    print()
    
    if all_articles:
        # Generar reporte
        print("📝 Generando reporte...")
        output_file = generate_report(all_articles)
        print(f"   Reporte guardado en: {output_file}")
        print()
        
        # Mostrar resumen
        print("=" * 60)
        print("RESUMEN DEL REPORTE")
        print("=" * 60)
        
        recommendations = generate_recommendations(all_articles)
        print("\n🎯 Habilidades clave recomendadas:")
        for skill in list(recommendations['skills'])[:5]:
            print(f"   • {skill}")
        
        print("\n💼 Oportunidades de negocio:")
        for opp in list(recommendations['opportunities'])[:3]:
            print(f"   • {opp}")
        
        print()
        print(f"📄 Ver reporte completo en: {output_file}")
    else:
        print("⚠️ No se encontraron artículos. Esto puede deberse a:")
        print("   - Restricciones de acceso a las páginas web")
        print("   - Cambios en la estructura HTML de los sitios")
        print("   - Necesidad de usar APIs oficiales en lugar de scraping")
        print()
        print("Generando reporte básico de todas formas...")
        generate_report([], 'report.md')
    
    print()
    print("¡AI_Radar ha completado su ejecución!")

if __name__ == "__main__":
    main()
