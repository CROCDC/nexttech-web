"""One-time data seeding.

Projects used to be hardcoded in the templates; this seeds the same 15 into the
DB so the public pages keep rendering after the move. It runs only when the
`projects` table is empty, so it is safe to call on every startup and never
clobbers admin edits. `featured`/`featured_order` reproduce the home scroller
selection; `short_description` is the shorter blurb the home used.
"""

from app.factory import db
from app.models.project import Project

# (name, url, icon, round_icon, description, short_description)
# short_description is only set for the 6 projects shown on the home scroller.
_PROJECTS = [
    ("Juana María", "https://juana-maria.nexttech.com.ar/", "juanamaria.svg", False,
     "Sitio del velero histórico Juana María: una ballenera de doble proa de madera, dibujada por Manuel M. Campos y botada en el Tigre en 1941, con 85 años navegando el Río de la Plata.", ""),
    ("MG Náutica", "https://www.mgnauticabroker.com/", "mgnautica.png", False,
     "Broker y gestor naval en Argentina y Uruguay: compra y venta de embarcaciones, trámites, traslados y mantenimiento, con asesoramiento integral en cada operación.", ""),
    ("9 del 12", "https://9del12.com/", "9del12.svg", False,
     "Sitio conmemorativo de la cuarta Copa Libertadores de River Plate, ganada a Boca el 9 de diciembre de 2018 en Madrid: crónicas, galería, jugadores y el camino a la gloria.",
     "Sitio conmemorativo de la cuarta Copa Libertadores de River: crónicas, galería y el camino a la gloria."),
    ("Hacelo y me muero", "https://haceloymemuero.com/", "haceloymemuero.png", True,
     "Espacio digital dedicado a River Plate: noticias, videos, entrevistas y la emoción millonaria contada por hinchas, para hinchas.", ""),
    ("Track Produce", "https://trackproduce.nexttech.com.ar/", "trackproduce.png", False,
     "Productora audiovisual y musical en Buenos Aires: videoclips, estudios de grabación, dirección de arte, shows en vivo y eventos.",
     "Productora audiovisual y musical en Buenos Aires: videoclips, shows en vivo y eventos."),
    ("GLÜCK", "https://gluck.nexttech.com.ar/", "gluck.webp", True,
     "Bolsos y carteras minimalistas de cuero vegano, hechos a mano. Diseño atemporal con foco en materiales y procesos artesanales.",
     "E-commerce de bolsos y carteras de cuero vegano, hechos a mano. Diseño atemporal y artesanal."),
    ("FF Retro", "https://ffretro.nexttech.com.ar/", "ffretro.jpg", False,
     "Servicio de retroexcavadora en Colonia del Sacramento: excavaciones, zanjas para cañerías, cimientos, plateas y limpieza de terrenos.", ""),
    ("El Pampero", "https://elpampero.com.ar/", "elpampero.png", False,
     "Náutica, cultura y río: notas marineras, historias de naufragios y efemérides para preservar el patrimonio fluvial del Río de la Plata.",
     "Náutica, cultura y río: notas marineras e historias para preservar el patrimonio fluvial."),
    ("Comunicación Pública", "https://comunicacionpublica.org/", "comunicacionpublica.png", False,
     "Herramienta para profesionales de la información y plataforma de comunicación entre países y medios: artículos, consultoría, entrevistas y espacio de debate.", ""),
    ("Kailua Sailing", "https://kailuasailing.com.ar/", "kailua.svg", False,
     "Charters, traslados de embarcaciones y paseos en velero en el Río de la Plata. Amaneceres, atardeceres, luna llena y experiencias a medida desde San Isidro.",
     "Charters y paseos en velero en el Río de la Plata. Experiencias a medida desde San Isidro."),
    ("Focus Consultores PR", "http://focusconsultorespr.com/", "focus.png", False,
     "Consultoría estratégica en comunicación: planes de comunicación, media training, organización de eventos, marketing digital, relaciones con prensa y gestión de crisis.", ""),
    ("El Sonido Del Torno", "https://elsonidodeltorno.com.ar/", "logo-elsonidodeltorno.png", False,
     "Comunidad y medio sobre tornería en madera: historias de artesanos, noticias del oficio, tips prácticos, agenda de seminarios y eventos como Mega Artesanal.", ""),
    ("Chaac", "https://chaac.nexttech.com.ar/", "chaac.svg", False,
     "Tu plataforma para prepararte para el examen náutico deportivo. Practicá preguntas sobre normativa, señales, meteorología y más para el Brevet Deportivo clases A, B, C y D en Uruguay.",
     "Plataforma para preparar el examen náutico deportivo: normativa, señales, meteorología y más."),
    ("Calculadora de Madera", "https://calculadorademadera.nexttech.com.ar/", "calculadorademadera.png", False,
     "Herramienta para calcular cortes de madera: seleccioná tipo de corte (cuadrado, rectangular), ingresá medidas y consultá el historial de cálculos.", ""),
    ("Leviatán", "https://leviatan.nexttech.com.ar/", "leviatan.png", False,
     "Horarios de ferries desde Colonia del Sacramento: salidas, llegadas y mapa con la operación de Buquebus y Colonia Express en un solo lugar.", ""),
]

# Names shown on the home scroller, in display order.
_FEATURED_ORDER = ["9 del 12", "GLÜCK", "Track Produce", "Kailua Sailing", "Chaac", "El Pampero"]


def seed_projects():
    if Project.query.count() > 0:
        return

    featured_rank = {name: i for i, name in enumerate(_FEATURED_ORDER)}
    for sort_order, (name, url, icon, round_icon, desc, short) in enumerate(_PROJECTS):
        is_featured = name in featured_rank
        db.session.add(Project(
            name=name,
            url=url,
            icon=icon,
            description=desc,
            short_description=short,
            round_icon=round_icon,
            featured=is_featured,
            sort_order=sort_order,
            featured_order=featured_rank.get(name, 0),
        ))
    db.session.commit()
