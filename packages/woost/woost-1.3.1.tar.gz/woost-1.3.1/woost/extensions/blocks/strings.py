#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import (
    translations,
    DATE_STYLE_TEXT,
    DATE_STYLE_ABBR,
    DATE_STYLE_NUMBERS
)
from cocktail.translations.helpers import ca_possessive, plural2

translations.define("Action edit_blocks",
    ca = u"Editar blocs",
    es = u"Editar bloques",
    en = u"Edit blocks"
)

translations.define("woost.extensions.blocks.slots.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define(
    "woost.extensions.blocks.editblocksnode.EditBlocksNode-instance",
    ca = lambda instance:
        u"Editant els blocs " + ca_possessive(translations(instance.item)),
    es = lambda instance:
        u"Editando los bloques de " + translations(instance.item),
    en = lambda instance:
        u"Editing the blocks for " + translations(instance.item)
)

translations.define("woost.extensions.blocks.BlockSection.edit_slot_link",
    ca = u"Editar aquest espai",
    es = u"Editar este espacio",
    en = u"Edit this slot"
)

# Configuration
#------------------------------------------------------------------------------
translations.define("Configuration.common_blocks",
    ca = u"Blocs comuns",
    es = u"Bloques comunes",
    en = u"Common blocks"
)

# Style
#------------------------------------------------------------------------------
translations.define("Style.applicable_to_blocks",
    ca = u"Aplicable a blocs",
    es = u"Aplicable a bloques",
    en = u"Applicable to blocks"
)

# News
#------------------------------------------------------------------------------
translations.define("News.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# Event
#------------------------------------------------------------------------------
translations.define("Event.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# ImageFactory
#------------------------------------------------------------------------------
translations.define("ImageFactory.applicable_to_blocks",
    ca = u"Aplicable a blocs",
    es = u"Aplicable a bloques",
    en = u"Applicable to blocks"
)

# BlocksPage
#------------------------------------------------------------------------------
translations.define("BlocksPage",
    ca = u"Pàgina de blocs",
    es = u"Página de bloques",
    en = u"Blocks page"
)

translations.define("BlocksPage-plural",
    ca = u"Pàgines de blocs",
    es = u"Páginas de bloques",
    en = u"Blocks pages"
)

translations.define("BlocksPage.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# Blocks page template
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.blocks_page_template.title",
    ca = u"Plantilla pàgina de blocs",
    es = u"Plantilla página de bloques",
    en = u"Blocks page template"
)

# Element types
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.ElementType=div",
    ca = u"Element genèric (div)",
    es = u"Elemento genérico (div)",
    en = u"Generic element (div)"
)

translations.define("woost.extensions.blocks.ElementType=section",
    ca = u"Secció",
    es = u"Sección",
    en = u"Section"
)

translations.define("woost.extensions.blocks.ElementType=article",
    ca = u"Article",
    es = u"Artículo",
    en = u"Article"
)

translations.define("woost.extensions.blocks.ElementType=details",
    ca = u"Detalls",
    es = u"Detalles",
    en = u"Details"
)

translations.define("woost.extensions.blocks.ElementType=figure",
    ca = u"Recurs complementari (figure)",
    es = u"Recurso complementario (figure)",
    en = u"Figure"
)

translations.define("woost.extensions.blocks.ElementType=aside",
    ca = u"Contingut relacionat (aside)",
    es = u"Contenido relacionado (aside)",
    en = u"Tangentially related content (aside)"
)

translations.define("woost.extensions.blocks.ElementType=header",
    ca = u"Capçalera",
    es = u"Cabecera",
    en = u"Header"
)

translations.define("woost.extensions.blocks.ElementType=footer",
    ca = u"Peu",
    es = u"Pie",
    en = u"Footer"
)

translations.define("woost.extensions.blocks.ElementType=nav",
    ca = u"Navegació",
    es = u"Navegación",
    en = u"Navigation"
)

translations.define("woost.extensions.blocks.ElementType=dd",
    ca = u"Definició (dd)",
    es = u"Definición (dd)",
    en = u"Definition (dd)"
)

# Block
#------------------------------------------------------------------------------
translations.define("Block",
    ca = u"Bloc",
    es = u"Bloque",
    en = u"Block"
)

translations.define("Block-plural",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define("Block.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("Block.behavior",
    ca = u"Comportament",
    es = u"Comportamiento",
    en = u"Behavior"
)

translations.define("Block.html",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

translations.define("Block.heading",
    ca = u"Encapçalament",
    es = u"Encabezado",
    en = u"Heading"
)

translations.define("Block.heading_type",
    ca = u"Tipus d'encapçalament",
    es = u"Tipo de encabezado",
    en = u"Heading type"
)

translations.define("Block.heading_type=hidden",
    ca = u"Ocult",
    es = u"Oculto",
    en = u"Hidden"
)

translations.define("Block.heading_type=generic",
    ca = u"Etiqueta genèrica (div)",
    es = u"Etiqueta genérica (div)",
    en = u"Generic label (div)"
)

translations.define("Block.heading_type=hidden_h1",
    ca = u"Encapçalament de secció ocult",
    es = u"Encabezado de sección oculto",
    en = u"Hidden section heading"
)

for level in range(1, 7):
    translations.define("Block.heading_type=h" + str(level),
        ca = u"Encapçalament %d" % level,
        es = u"Encabezado %d" % level,
        en = u"Heading %d" % level
    )

translations.define("Block.heading_type=dt",
    ca = u"Terme (dt)",
    es = u"Término (dt)",
    en = u"Term (dt)"
)

translations.define("Block.heading_type=figcaption",
    ca = u"Títol per un recurs complementari (figcaption)",
    es = u"Título para un recurso complementario (figcaption)",
    en = u"Figure caption"
)

translations.define("Block.html_attributes",
    ca = u"Atributs HTML",
    es = u"Atributos HTML",
    en = u"HTML attributes"
)

translations.define("Block.styles",
    ca = u"Estils",
    es = u"Estilos",
    en = u"Styles"
)

translations.define("Block.inline_css_styles",
    ca = u"Estils en línia",
    es = u"Estilos en linea",
    en = u"Inline CSS styles"
)

translations.define("Block.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Active"
)

translations.define("Block.start_date",
    ca = u"Inici de publicació",
    es = u"Inicio de publicación",
    en = u"Publication start"
)

translations.define("Block.end_date",
    ca = u"Fi de publicació",
    es = u"Fin de publicación",
    en = u"Publication end"
)

translations.define("Block.controller",
    ca = u"Controlador",
    es = u"Controlador",
    en = u"Controller"
)

# CustomBlock
#------------------------------------------------------------------------------
translations.define("CustomBlock",
    ca = u"Bloc a mida",
    es = u"Bloque a medida",
    en = u"Custom block"
)

translations.define("CustomBlock-plural",
    ca = u"Blocs a mida",
    es = u"Bloques a medida",
    en = u"Custom blocks"
)

translations.define("CustomBlock.view_class",
    ca = u"Vista",
    es = u"Vista",
    en = u"View"
)

translations.define("CustomBlock.view_class-explanation",
    ca = u"Nom qualificat de la vista CML a mostrar",
    es = u"Nombre cualificado de la vista CML a mostrar",
    en = u"The qualified name of the CML view to display"
)

# ContainerBlock
#------------------------------------------------------------------------------
translations.define("ContainerBlock",
    ca = u"Contenidor",
    es = u"Contenedor",
    en = u"Container"
)

translations.define("ContainerBlock-plural",
    ca = u"Contenidors",
    es = u"Contenedores",
    en = u"Containers"
)

translations.define("ContainerBlock.blocks",
    ca = u"Blocs fills",
    es = u"Bloques hijos",
    en = u"Child blocks"
)

translations.define("ContainerBlock.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

translations.define("ContainerBlock.list_type",
    ca = u"Tipus de llista",
    es = u"Tipo de lista",
    en = u"List type"
)

translations.define("ContainerBlock.list_type=div",
    ca = u"Element genèric (div)",
    es = u"Elemento genérico (div)",
    en = u"Generic element (div)"
)

translations.define("ContainerBlock.list_type=ul",
    ca = u"Llista",
    es = u"Lista",
    en = u"List"
)

translations.define("ContainerBlock.list_type=ol",
    ca = u"Llista ordenada",
    es = u"Lista ordenada",
    en = u"Ordered list"
)

translations.define("ContainerBlock.list_type=dl",
    ca = u"Llista de definició",
    es = u"Lista de definición",
    en = u"Definition list"
)

# SlideShowBlock
#------------------------------------------------------------------------------
translations.define("SlideShowBlock",
    ca = u"Passador",
    es = u"Pasador",
    en = u"Slide show"
)

translations.define("SlideShowBlock-plural",
    ca = u"Passadors",
    es = u"Pasadores",
    en = u"Slide shows"
)

translations.define("SlideShowBlock.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

translations.define("SlideShowBlock.slides",
    ca = u"Diapositives",
    es = u"Diapositivas",
    en = u"Slides"
)

translations.define("SlideShowBlock.transition_settings",
    ca = u"Transicions",
    es = u"Transiciones",
    en = u"Transitions"
)

translations.define("SlideShowBlock.autoplay",
    ca = u"Transicions automàtiques",
    es = u"Transiciones automáticas",
    en = u"Autoplay"
)

translations.define("SlideShowBlock.controls",
    ca = u"Controls",
    es = u"Controles",
    en = u"Controls"
)

translations.define("SlideShowBlock.navigation_controls",
    ca = u"Mostrar controls de navegació",
    es = u"Mostrar controles de navegación",
    en = u"Show navigation controls"
)

translations.define("SlideShowBlock.bullet_controls",
    ca = u"Mostrar botons de diapositiva",
    es = u"Mostrar botones de diapositiva",
    en = u"Show slide bullets"
)

translations.define("SlideShowBlock.bullet_view_class",
    ca = u"Aparença dels botons de diapositiva",
    es = u"Apariencia de los botones de diapositiva",
    en = u"Slide bullets appearence"
)

translations.define(
    "SlideShowBlock.bullet_view_class"
    "=woost.extensions.blocks.SlideShowButtonBullet",
    ca = u"Botó",
    es = u"Botón",
    en = u"Button"
)

translations.define(
    "SlideShowBlock.bullet_view_class"
    "=woost.extensions.blocks.SlideShowTextBullet",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define(
    "SlideShowBlock.bullet_view_class"
    "=woost.extensions.blocks.SlideShowImageBullet",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define(
    "SlideShowBlock.bullet_view_class"
    "=woost.extensions.blocks.SlideShowTextAndImageBullet",
    ca = u"Imatge i text",
    es = u"Imagen y texto",
    en = u"Image and text"
)

translations.define("SlideShowBlock.bullet_image_factory",
    ca = u"Processat d'imatge pels botons de diapositiva",
    es = u"Procesado de imagen para los botones de diapositiva",
    en = u"Image processing for slide bullets"
)

translations.define("SlideShowBlock.interval",
    ca = u"Freqüència de les transicions",
    es = u"Frecuencia de las transiciones",
    en = u"Time between transitions"
)

translations.define("SlideShowBlock.interval-explanation",
    ca = u"Si s'activen les transicions automàtiques, indica el nombre de "
         u"milisegons abans que el bloc passi a la següent diapositiva.",
    es = u"Si se activan las transiciones automáticas, indica el número de "
         u"milisegundos antes que el bloque pase a la diapositiva siguiente.",
    en = u"If autoplay is enabled, indicates the number of milliseconds that "
         u"pass between automatic transitions."
)

translations.define("SlideShowBlock.transition_duration",
    ca = u"Duració de les transicions",
    es = u"Duración de las transiciones",
    en = u"Transition duration"
)

translations.define("SlideShowBlock.transition_duration-explanation",
    ca = u"Especifica la duració de l'efecte de transició, en milisegons",
    es = u"Especifica la duración del efecto de transición, en milisegundos",
    en = u"Sets the duration of the slide transition effect, in milliseconds"
)

translations.define("SlideShowBlock.transition_effect",
    ca = u"Efecte de transició",
    es = u"Efecto de transición",
    en = u"Transition effect"
)

translations.define("SlideShowBlock.transition_effect=fade",
    ca = u"Fondre",
    es = u"Fundir",
    en = u"Fade"
)

translations.define("SlideShowBlock.transition_effect=topBottomSlide",
    ca = u"Lliscar de dalt a baix",
    es = u"Deslizar de arriba abajo",
    en = u"Top-bottom slide"
)

# MenuBlock
#------------------------------------------------------------------------------
translations.define("MenuBlock",
    ca = u"Menú",
    es = u"Menú",
    en = u"Menu"
)

translations.define("MenuBlock-plural",
    ca = u"Menús",
    es = u"Menús",
    en = u"Menus"
)

translations.define("MenuBlock.root",
    ca = u"Arrel",
    es = u"Raiz",
    en = u"Root"
)

translations.define("MenuBlock.root_visible",
    ca = u"Arrel visible",
    es = u"Raiz visible",
    en = u"Root visible"
)

translations.define("MenuBlock.max_depth",
    ca = u"Profunditat màxima",
    es = u"Profundidad máxima",
    en = u"Maximum depth"
)

translations.define("MenuBlock.expanded",
    ca = u"Expandit",
    es = u"Expandido",
    en = u"Expanded"
)

# HTMLBlock
#------------------------------------------------------------------------------
translations.define("HTMLBlock",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

translations.define("HTMLBlock-plural",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

translations.define("HTMLBlock.html",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

# TextBlock
#------------------------------------------------------------------------------
translations.define("TextBlock",
    ca = u"Text + imatges",
    es = u"Texto + imágenes",
    en = u"Text + images"
)

translations.define("TextBlock-plural",
    ca = u"Text + imatges",
    es = u"Texto + imágenes",
    en = u"Text + images"
)

translations.define("TextBlock.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

translations.define("TextBlock.link",
    ca = u"Enllaç",
    es = u"Enlace",
    en = u"Link"
)

translations.define("TextBlock.link_destination",
    ca = u"Destí de l'enllaç",
    es = u"Destino del enlace",
    en = u"Linked resource"
)

translations.define("TextBlock.link_parameters",
    ca = u"Paràmetres addicionals per l'enllaç",
    es = u"Parámetros adicionales para el enlace",
    en = u"Additional URL parameters"
)

translations.define("TextBlock.link_parameters-explanation",
    ca = u"Un paràmetre per línia, separant el nom i el valor amb un caràcter "
         u"'='",
    es = u"Un parámetro por linea, separando el nombre y el valor con un "
         u"caracter '='",
    en = u"One parameter per line, with key and value separated by a "
         u"'=' character"
)

translations.define("TextBlock.link_opens_in_new_window",
    ca = u"Obrir l'enllaç a una nova finestra",
    es = u"Abrir el enlace en una ventana nueva",
    en = u"Open the link in a new window"
)

translations.define("TextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("TextBlock.images",
    ca = u"Imatges",
    es = u"Imágenes",
    en = u"Images"
)

translations.define("TextBlock.image_alignment",
    ca = u"Disposició de les imatges",
    es = u"Disposición de las imágenes",
    en = u"Image alignment"
)

translations.define("TextBlock.image_alignment=float_top_left",
    ca = u"Flotar a l'esquerra",
    es = u"Flotar a la izquierda",
    en = u"Top left, floating"
)

translations.define("TextBlock.image_alignment=float_top_right",
    ca = u"Flotar a la dreta",
    es = u"Flotar a la derecha",
    en = u"Top right, floating"
)

translations.define("TextBlock.image_alignment=column_left",
    ca = u"Columna a l'esquerra",
    es = u"Columna a la izquierda",
    en = u"Top left, in their own column"
)

translations.define("TextBlock.image_alignment=column_right",
    ca = u"Columna a la dreta",
    es = u"Columna a la derecha",
    en = u"Top right, in their own column"
)

translations.define("TextBlock.image_alignment=top_left",
    ca = u"A dalt a l'esquerra",
    es = u"Arriba a la izquierda",
    en = u"Top left"
)

translations.define("TextBlock.image_alignment=bottom_left",
    ca = u"A sota a l'esquerra",
    es = u"Abajo a la izquierda",
    en = u"Bottom left"
)

translations.define("TextBlock.image_alignment=center_top",
    ca = u"Centrar a dalt",
    es = u"Centrar arriba",
    en = u"Top center"
)

translations.define("TextBlock.image_alignment=center_bottom",
    ca = u"Centrar a sota",
    es = u"Centrar abajo",
    en = u"Bottom center"
)

translations.define("TextBlock.image_alignment=top_right",
    ca = u"A dalt a la dreta",
    es = u"Arriba a la derecha",
    en = u"Top right"
)

translations.define("TextBlock.image_alignment=inline",
    ca = u"En línia",
    es = u"En linea",
    en = u"Inline"
)

translations.define("TextBlock.image_alignment=background",
    ca = u"Imatge de fons",
    es = u"Imagen de fondo",
    en = u"Background image"
)

translations.define("TextBlock.image_alignment=fallback",
    ca = u"Imatge amb descripció textual substitutiva",
    es = u"Imagen con descripción textual sustitutiva",
    en = u"Image with fallback content"
)

translations.define("TextBlock.image_thumbnail_factory",
    ca = u"Processat de les imatges",
    es = u"Procesado de las imágenes",
    en = u"Image processing"
)

translations.define("TextBlock.image_close_up_enabled",
    ca = u"Ampliar les imatges en fer-hi clic",
    es = u"Ampliar las imágenes al pulsarlas",
    en = u"Click to enlarge"
)

translations.define("TextBlock.image_close_up_factory",
    ca = u"Processat de les imatges ampliades",
    es = u"Procesado de las imágenes ampliadas",
    en = u"Image processing for enlarged images"
)

translations.define("TextBlock.image_close_up_preload",
    ca = u"Precàrrega de les imatges ampliades",
    es = u"Precarga de las imágenes ampliadas",
    en = u"Preload enlarged images"
)

translations.define("TextBlock.image_labels_visible",
    ca = u"Mostrar els títols de les imatges",
    es = u"Mostrar los títulos de las imágenes",
    en = u"Show image titles"
)

translations.define("TextBlock.image_original_link_visible",
    ca = u"Mostrar un enllaç a la imatge sense modificar",
    es = u"Mostrar un enlace a la imagen sin modificar",
    en = u"Show a link to the original image"
)

# VideoBlock
#------------------------------------------------------------------------------
translations.define("VideoBlock",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("VideoBlock-plural",
    ca = u"Vídeos",
    es = u"Vídeos",
    en = u"Videos"
)

translations.define("VideoBlock.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

translations.define("VideoBlock.video",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("VideoBlock.player_settings",
    ca = u"Opcions de reproductor de vídeo",
    es = u"Opciones de reproductor de video",
    en = u"Video player settings"
)

# VimeoBlock
#------------------------------------------------------------------------------
translations.define("VimeoBlock",
    ca = u"Vídeo de Vimeo",
    es = u"Video de Vimeo",
    en = u"Vimeo video"
)

translations.define("VimeoBlock-plural",
    ca = u"Vídeos de Vimeo",
    es = u"Vídeos de Vimeo",
    en = u"Vimeo videos"
)

translations.define("VimeoBlock.appearence",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define("VimeoBlock.video_id",
    ca = u"Codi del vídeo",
    es = u"Código del video",
    en = u"Video ID"
)

translations.define("VimeoBlock.vimeo_autoplay",
    ca = u"Reproducció automàtica",
    es = u"Reproducción automática",
    en = u"Autoplay"
)

translations.define("VimeoBlock.vimeo_loop",
    ca = u"Reproduïr continuament",
    es = u"Reproducir continuamente",
    en = u"Loop"
)

translations.define("VimeoBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("VimeoBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("VimeoBlock.allow_fullscreen",
    ca = u"Permetre pantalla completa",
    es = u"Permitir pantalla completa",
    en = u"Allow fullscreen"
)

translations.define("VimeoBlock.vimeo_title",
    ca = u"Mostrar el títol del vídeo",
    es = u"Mostrar el título del video",
    en = u"Show the video's title"
)

translations.define("VimeoBlock.vimeo_byline",
    ca = u"Mostrar informació de l'autor",
    es = u"Mostrar información del autor",
    en = u"Show the video's byline"
)

translations.define("VimeoBlock.vimeo_portrait",
    ca = u"Mostrar imatge de l'autor",
    es = u"Mostrar imagen del autor",
    en = u"Show the author's portrait"
)

translations.define("VimeoBlock.vimeo_color",
    ca = u"Color del reproductor",
    es = u"Color del reproductor",
    en = u"Player color"
)

# TwitterTimelineBlock
#------------------------------------------------------------------------------
translations.define("TwitterTimelineBlock",
    ca = u"Missatges de Twitter",
    es = u"Mensajes de Twitter",
    en = u"Twitter timeline"
)

translations.define("TwitterTimelineBlock-plural",
    ca = u"Missatges de Twitter",
    es = u"Mensajes de Twitter",
    en = u"Twitter timeline"
)

translations.define("TwitterTimelineBlock.tweet",
    ca = u"Tuit",
    es = u"Tuit",
    en = u"Tweet"
)

translations.define("TwitterTimelineBlock.appearence",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define("TwitterTimelineBlock.widget_id",
    ca = u"ID del widget",
    es = u"ID del widget",
    en = u"Widget ID"
)

translations.define("TwitterTimelineBlock.theme",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Theme"
)

translations.define("TwitterTimelineBlock.theme=light",
    ca = u"Clar",
    es = u"Claro",
    en = u"Light"
)

translations.define("TwitterTimelineBlock.theme=dark",
    ca = u"Fosc",
    es = u"Oscuro",
    en = u"Dark"
)

translations.define("TwitterTimelineBlock.link_color",
    ca = u"Color de l'enllaç",
    es = u"Color del enlace",
    en = u"Link color"
)

translations.define("TwitterTimelineBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("TwitterTimelineBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("TwitterTimelineBlock.related_accounts",
    ca = u"Comptes relacionats",
    es = u"Cuentas relacionadas",
    en = u"Related accounts"
)

# LinksBox
#------------------------------------------------------------------------------
translations.define("LinksBlock",
    ca = u"Llista d'enllaços",
    es = u"Lista de enlaces",
    en = u"Link list"
)

translations.define("LinksBlock-plural",
    ca = u"Llistes d'enllaços",
    es = u"Listas de enlaces",
    en = u"Link lists"
)

translations.define("LinksBlock.links",
    ca = u"Enllaços",
    es = u"Enlaces",
    en = u"Links"
)

# FolderBlock
#------------------------------------------------------------------------------
translations.define("FolderBlock",
    ca = u"Llistat de documents fills",
    es = u"Listado de documentos hijos",
    en = u"Child documents listing"
)

translations.define("FolderBlock-plural",
    ca = u"Llistats de documents fills",
    es = u"Listados de documentos hijos",
    en = u"Child documents listings"
)

translations.define("FolderBlock.show_hidden_children",
    ca = u"Mostrar documents ocults",
    es = u"Mostrar documentos ocultos",
    en = u"Show hidden documents"
)

translations.define("FolderBlock.show_thumbnails",
    ca = u"Mostrar miniatures",
    es = u"Mostrar miniaturas",
    en = u"Show thumbnails"
)

translations.define("FolderBlock.thumbnails_factory",
    ca = u"Processador de miniatures",
    es = u"Procesador de miniaturas",
    en = u"Thumbnail factory"
)

# LoginBlock
#------------------------------------------------------------------------------
translations.define("LoginBlock",
    ca = u"Formulari d'autenticació d'usuari",
    es = u"Formulario de autenticación de usuario",
    en = u"Login form"
)

translations.define("LoginBlock-plural",
    ca = u"Formularis d'autenticació d'usuari",
    es = u"Formularios de autenticación de usuario",
    en = u"Login forms"
)

translations.define("LoginBlock.login_target",
    ca = u"Pàgina de destí",
    es = u"Página de destino",
    en = u"Destination page"
)

translations.define("LoginBlock.login_target-explanation",
    ca = u"La pàgina que rebrà la petició d'autenticació de l'usuari",
    es = u"La pàgina que recibirá la petición de autenticación del "
         u"usuario",
    en = u"The page that will handle the user's authentication request"
)

translations.define("LoginBlockForm.user",
    ca = u"Usuari",
    es = u"Usuario",
    en = u"User"
)

translations.define("LoginBlockForm.password",
    ca = u"Contrasenya",
    es = u"Contraseña",
    en = u"Password"
)

translations.define("woost.extensions.blocks.LoginBlockView.submit_button",
    ca = u"Entrar",
    es = u"Entrar",
    en = u"Login"
)

# IFrameBlock
#------------------------------------------------------------------------------
translations.define("IFrameBlock",
    ca = u"IFrame",
    es = u"IFrame",
    en = u"IFrame"
)

translations.define("IFrameBlock-plural",
    ca = u"IFrames",
    es = u"IFrames",
    en = u"IFrames"
)

translations.define("IFrameBlock.src",
    ca = u"Adreça a mostrar",
    es = u"Dirección a mostrar",
    en = u"Content URL"
)

translations.define("IFrameBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("IFrameBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

# EditBlocksView
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.EditBlocksView.body_header",
    ca = lambda item:
        u"Editant els blocs " + ca_possessive(translations(item)),
    es = lambda item:
        u"Editando los bloques de " + translations(item),
    en = lambda item:
        u"Editing the blocks for " + translations(item)
)

# BackOfficeItemViewOverlay
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.blocks."
    "BackOfficeItemViewOverlay.block_map.explanation",
    ca = lambda count:
        u"Aplicat a " + plural2(
            count,
            "<strong>1</strong> bloc:",
            "<strong>%d</strong> blocs:" % count
        ),
    es = lambda count:
        u"Aplicado a " + plural2(
            count,
            "<strong>1</strong> bloque:",
            "<strong>%d</strong> bloques:" % count
        ),
    en = lambda count:
        u"Applied to " + plural2(
            count,
            "<strong>1</strong> block:",
            "<strong>%d</strong> blocks:" % count
        )
)

# EditBlocksSlotList
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.blocks.EditBlocksSlotList.new_blocks_panel.panel_header",
    ca = u"Crear un nou bloc",
    es = u"Crear un bloque nuevo",
    en = u"Create a new block"
)

translations.define(
    "woost.extensions.blocks.EditBlocksSlotList.common_blocks_panel.panel_header",
    ca = u"Afegir un bloc existent",
    es = u"Añadir un bloque existente",
    en = u"Add an existing block"
)

translations.define(
    "woost.extensions.blocks.EditBlocksSlotList.dialog_buttons.cancel_button",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

# BlockDisplay
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.BlockDisplay.common_status.label",
    ca = u"Comú",
    es = u"Común",
    en = u"Common"
)

translations.define("woost.extensions.blocks.BlockDisplay.common_status.title",
    ca = u"Aquest bloc resideix a la llibreria de blocs comuns, i pot "
         u"aparèixer a més d'una pàgina",
    es = u"Este bloque reside en la libreria de bloques comunes, pudiendo "
         u"aparecer en más de una página",
    en = u"This block resides within the site's common blocks gallery, and "
         u"it may appear in more than one page"
)

translations.define("woost.extensions.blocks.BlockDisplay.disabled_status.label",
    ca = u"Inactiu",
    es = u"Inactivo",
    en = u"Disabled"
)

translations.define("woost.extensions.blocks.BlockDisplay.disabled_status.title",
    ca = u"Aquest bloc està deshabilitat, no s'inclourà a la pàgina",
    es = u"Este bloque está deshabilitado, no se incluirá en la página",
    en = u"This block is disabled and won't be displayed in the page"
)

translations.define("woost.extensions.blocks.BlockDisplay.expired_status.label",
    ca = u"Expirat",
    es = u"Expirado",
    en = u"Expired"
)

translations.define("woost.extensions.blocks.BlockDisplay.expired_status.title",
    ca = u"Aquest bloc ha assolit la seva data d'expiració i ha deixat d'estar "
         u"visible",
    es = u"Este bloque ha alcanzado su fecha de expiración y ha dejado de "
         u"estar visible",
    en = u"This block has reached its expiration date and is no longer visible"
)

translations.define(
    "woost.extensions.blocks.BlockDisplay.awaiting_publication_status.label",
    ca = u"Esperant inici de publicació",
    es = u"Esperando inicio de publicación",
    en = u"Awaiting start of publication"
)

translations.define(
    "woost.extensions.blocks.BlockDisplay.awaiting_publication_status.title",
    ca = u"Aquest bloc no ha assolit la seva data d'inici de publicació i "
         u"encara no és visible",
    es = u"Este bloque no ha alcanzado su fecha de inicio de publicación y "
         u"todavía no es visible",
    en = u"This block has not reached its publication date and is not "
         u"visible yet"
)

translations.define("woost.extensions.blocks.BlockDisplay.temporary_status.label",
    ca = u"Temporal",
    es = u"Temporal",
    en = u"Temporary"
)

translations.define("woost.extensions.blocks.BlockDisplay.temporary_status.title",
    ca = u"Aquest bloc es publica només durant una finestra de temps",
    es = u"Este bloque solo se publicada durante una ventana de tiempo",
    en = u"This block is only published during a certain time window"
)

translations.define("Action add_block",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("Action add_block_before",
    ca = u"Afegir davant",
    es = u"Añadir en frente",
    en = u"Add before"
)

translations.define("Action add_block_after",
    ca = u"Afegir darrere",
    es = u"Añadir detrás",
    en = u"Add after"
)

translations.define("Action edit_block",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("Action remove_block",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define("Action copy_block",
    ca = u"Copiar",
    es = u"Copiar",
    en = u"Copy"
)

translations.define("Action cut_block",
    ca = u"Retallar",
    es = u"Cortar",
    en = u"Cut"
)

translations.define("Action paste_block",
    ca = u"Enganxar",
    es = u"Pegar",
    en = u"Paste"
)

translations.define("Action paste_block_after",
    ca = u"Enganxar darrere",
    es = u"Pegar detrás",
    en = u"Paste after"
)

translations.define("Action paste_block_before",
    ca = u"Enganxar davant",
    es = u"Pegar delante",
    en = u"Paste before"
)

translations.define("Action share_block",
    ca = u"Afegir a la llibreria",
    es = u"Añadir a la libreria",
    en = u"Add to the library"
)

translations.define("woost.extensions.blocks.empty_clipboard",
    ca = u"El portaretalls no conté cap bloc",
    es = u"El portapapeles no cotiene ningún bloque",
    en = u"The clipboard is empty"
)

translations.define("woost.extensions.blocks.clipboard_error",
    ca = u"El contingut del portaretalls no és vàlid",
    es = u"El contenido del portapapeles no es válido",
    en = u"The clipboard content is not valid"
)

# YouTubeBlock
#------------------------------------------------------------------------------
translations.define("YouTubeBlock",
    ca = u"Vídeo de YouTube",
    es = u"Video de YouTube",
    en = u"YouTube video"
)

translations.define("YouTubeBlock-plural",
    ca = u"Vídeos de YouTube",
    es = u"Videos de YouTube",
    en = u"YouTube videos"
)

translations.define("YouTubeBlock.video",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("YouTubeBlock.video_id",
    ca = u"Identificador del vídeo",
    es = u"Identificador del video",
    en = u"Video ID"
)

translations.define("YouTubeBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("YouTubeBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Ancho"
)

translations.define("YouTubeBlock.allow_fullscreen",
    ca = u"Permetre pantalla completa",
    es = u"Permitir pantalla completa",
    en = u"Allow fullscreen"
)

translations.define("YouTubeBlock.autoplay",
    ca = u"Iniciar la reproducció automàticament",
    es = u"Iniciar la reproducción automáticamente",
    en = u"Autoplay"
)

translations.define("YouTubeBlock.show_info",
    ca = u"Sobreimpressionar el títol del vídeo",
    es = u"Sobreimpresionar el título del video",
    en = u"Overlay the video title"
)

translations.define("YouTubeBlock.show_related_videos",
    ca = u"Mostrar vídeos relacionats",
    es = u"Mostrar videos relacionados",
    en = u"Show related videos"
)

translations.define("YouTubeBlock.show_player_controls",
    ca = u"Mostrar controls de reproducció",
    es = u"Mostrar controles de reproducción",
    en = u"Show player controls"
)

# NewsListing
#------------------------------------------------------------------------------
translations.define("NewsListing",
    ca = u"Llistat de notícies",
    es = u"Listado de noticias",
    en = u"News listing"
)

translations.define("NewsListing-plural",
    ca = u"Llistats de notícies",
    es = u"Listados de noticias",
    en = u"News listings"
)

translations.define("NewsListing.listing",
    ca = u"Llistat",
    es = u"Listado",
    en = u"Listing"
)

translations.define("NewsListing.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

translations.define("NewsListing.paginated",
    ca = u"Paginar els resultats",
    es = u"Paginar los resultados",
    en = u"Paginate results"
)

translations.define("NewsListing.page_size",
    ca = u"Mida del llistat",
    es = u"Tamaño del listado",
    en = u"Listing size"
)

translations.define("NewsListing.view_class",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define(
    "NewsListing.view_class=woost.views.CompactNewsListing",
    ca = u"Compacta",
    es = u"Compacta",
    en = u"Compact"
)

translations.define(
    "NewsListing.view_class=woost.views.TextOnlyNewsListing",
    ca = u"Només text",
    es = u"Solo texto",
    en = u"Text only"
)

translations.define(
    "NewsListing.view_class=woost.views.TextAndImageNewsListing",
    ca = u"Text i imatge",
    es = u"Texto e imagen",
    en = u"Text and image"
)

# EventListing
#------------------------------------------------------------------------------
translations.define("EventListing",
    ca = u"Llistat d'esdeveniments",
    es = u"Listado de eventos",
    en = u"Event listing"
)

translations.define("EventListing-plural",
    ca = u"Llistats d'events",
    es = u"Listados de eventos",
    en = u"Event listings"
)

translations.define("EventListing.listing",
    ca = u"Llistat",
    es = u"Listado",
    en = u"Listing"
)

translations.define("EventListing.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

translations.define("EventListing.include_expired",
    ca = u"Incloure esdeveniments passats",
    es = u"Incluir eventos pasados",
    en = u"Include expired events"
)

translations.define("EventListing.listing_order",
    ca = u"Ordenació",
    es = u"Ordenación",
    en = u"Order"
)

translations.define("EventListing.listing_order=event_start",
    ca = u"Data d'inici, ascendent",
    es = u"Fecha de inicio, ascendente",
    en = u"Event start, ascending"
)

translations.define("EventListing.listing_order=-event_start",
    ca = u"Data d'inici, descendent",
    es = u"Fecha de inicio, descendente",
    en = u"Event start, descending"
)

translations.define("EventListing.paginated",
    ca = u"Paginar els resultats",
    es = u"Paginar los resultados",
    en = u"Paginate results"
)

translations.define("EventListing.page_size",
    ca = u"Mida del llistat",
    es = u"Tamaño del listado",
    en = u"Listing size"
)

translations.define("EventListing.view_class",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define(
    "EventListing.view_class=woost.views.CompactEventListing",
    ca = u"Només el títol",
    es = u"Solo el título",
    en = u"Title only"
)

translations.define(
    "EventListing.view_class=woost.views.DateLocationTitleEventListing",
    ca = u"Data, ubicació i títol",
    es = u"Fecha, ubicación y título",
    en = u"Date, location and title"
)

# FileListing
#------------------------------------------------------------------------------
translations.define("FileListing",
    ca = u"Llistat de fitxers",
    es = u"Listado de ficheros",
    en = u"File listing"
)

translations.define("FileListing-plural",
    ca = u"Llistats de fitxers",
    es = u"Listados de ficheros",
    en = u"File listings"
)

translations.define("FileListing.listing",
    ca = u"Llistat",
    es = u"Listado",
    en = u"Listing"
)

translations.define("FileListing.files",
    ca = u"Fitxers",
    es = u"Ficheros",
    en = u"Files"
)

translations.define("FileListing.listing_order",
    ca = u"Ordenació",
    es = u"Ordenación",
    en = u"Order"
)

translations.define("FileListing.listing_order=arbitrary",
    ca = u"Arbitrària",
    es = u"Arbitraria",
    en = u"Arbitrary"
)

translations.define("FileListing.listing_order=title",
    ca = u"Alfabètica",
    es = u"Alfabética",
    en = u"Alphabetical"
)

translations.define("FileListing.listing_order=-last_update_time",
    ca = u"Última modificació",
    es = u"Última modificación",
    en = u"Last update"
)

translations.define("FileListing.links_open_in_new_window",
    ca = u"Obrir els enllaços a una nova finestra",
    es = u"Abrir los enlaces en una ventana nueva",
    en = u"Open links in a new window"
)

translations.define("FileListing.image_factory",
    ca = u"Processat d'imatge",
    es = u"Procesado de imagen",
    en = u"Image processing"
)

# FacebookLikeButton
#------------------------------------------------------------------------------
translations.define("FacebookLikeButton",
    ca = u'Botó de "M\'agrada" de Facebook',
    es = u'Botón de "Me gusta" de Facebook',
    en = u"Facebook Like button"
)

translations.define("FacebookLikeButton-plural",
    ca = u'Botons de "M\'agrada" de Facebook',
    es = u'Botones de "Me gusta" de Facebook',
    en = u"Facebook Like buttons"
)

translations.define("FacebookLikeButton.appearence",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define("FacebookLikeButton.fb_href",
    ca = u"Recurs",
    es = u"Recurso",
    en = u"Resource"
)

translations.define("FacebookLikeButton.fb_href-explanation",
    ca = u"La pàgina a recomanar. Deixar en blanc per seleccionar la pàgina on "
         u"es trobi el botó.",
    es = u"La página a recomendar. Dejar en blanco para seleccionar la página "
         u"donde se ubique el botón.",
    en = u"The resource to like. Leave blank to assume the page that contains "
         u"the button."
)

translations.define("FacebookLikeButton.fb_send",
    ca = u"Mostrar el botó d'enviar",
    es = u"Mostrar el botón de enviar",
    en = u"Show the Send button"
)

translations.define("FacebookLikeButton.fb_layout",
    ca = u"Disposició",
    es = u"Disposición",
    en = u"Layout"
)

translations.define("FacebookLikeButton.fb_layout=standard",
    ca = u"Estàndard",
    es = u"Estándar",
    en = u"Standard"
)

translations.define("FacebookLikeButton.fb_layout=button_count",
    ca = u"Recompte",
    es = u"Recuento",
    en = u"Button count"
)

translations.define("FacebookLikeButton.fb_layout=box_count",
    ca = u"Recompte en caixa vertical",
    es = u"Recuento con caja vertical",
    en = u"Box count"
)

translations.define("FacebookLikeButton.fb_show_faces",
    ca = u"Mostrar cares",
    es = u"Mostrar caras",
    en = u"Show faces"
)

translations.define("FacebookLikeButton.fb_width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("FacebookLikeButton.fb_action",
    ca = u"Verb",
    es = u"Verbo",
    en = u"Verb"
)

translations.define("FacebookLikeButton.fb_action=like",
    ca = u"M'agrada",
    es = u"Me gusta",
    en = u"Like"
)

translations.define("FacebookLikeButton.fb_action=recommend",
    ca = u"Recomanar",
    es = u"Recomendar",
    en = u"Recommend"
)

translations.define("FacebookLikeButton.fb_font",
    ca = u"Font",
    es = u"Fuente",
    en = u"Font"
)

translations.define("FacebookLikeButton.fb_colorscheme",
    ca = u"Esquema de colors",
    es = u"Esquema de colores",
    en = u"Colorscheme"
)

translations.define("FacebookLikeButton.fb_colorscheme=light",
    ca = u"Clar",
    es = u"Claro",
    en = u"Light"
)

translations.define("FacebookLikeButton.fb_colorscheme=dark",
    ca = u"Fosc",
    es = u"Oscuro",
    en = u"Dark"
)

translations.define("FacebookLikeButton.fb_ref",
    ca = u"Codi de seguiment",
    es = u"Código de seguimiento",
    en = u"Referral tracking label"
)

# FacebookLikeBox
#------------------------------------------------------------------------------
translations.define("FacebookLikeBox",
    ca = u'Caixa de "M\'agrada" per pàgines de Facebook',
    es = u'Caja de "Me gusta" para páginas de Facebook',
    en = u"Facebook Like Box"
)

translations.define("FacebookLikeBox-plural",
    ca = u'Caixes de "M\'agrada" per pàgines de Facebook',
    es = u'Cajas de "Me gusta" para páginas de Facebook',
    en = u"Facebook Like Boxes"
)

translations.define("FacebookLikeBox.appearence",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define("FacebookLikeBox.fb_href",
    ca = u"Pàgina de Facebook",
    es = u"Página de Facebook",
    en = u"Facebook page"
)

translations.define("FacebookLikeBox.fb_show_faces",
    ca = u"Mostrar cares",
    es = u"Mostrar caras",
    en = u"Show faces"
)

translations.define("FacebookLikeBox.fb_stream",
    ca = u"Mostrar entrades del mur",
    es = u"Mostrar entradas del muro",
    en = u"Show stream"
)

translations.define("FacebookLikeBox.fb_header",
    ca = u"Mostrar el logo de Facebook",
    es = u"Mostrar el logo de Facebook",
    en = u"Show Facebook's logo"
)

translations.define("FacebookLikeBox.fb_width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("FacebookLikeBox.fb_height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("FacebookLikeBox.fb_border_color",
    ca = u"Color de la vora",
    es = u"Color del borde",
    en = u"Border color"
)

translations.define("FacebookLikeBox.fb_colorscheme",
    ca = u"Esquema de colors",
    es = u"Esquema de colores",
    en = u"Colorscheme"
)

translations.define("FacebookLikeBox.fb_colorscheme=light",
    ca = u"Clar",
    es = u"Claro",
    en = u"Light"
)

translations.define("FacebookLikeBox.fb_colorscheme=dark",
    ca = u"Fosc",
    es = u"Oscuro",
    en = u"Dark"
)

# TweetButton
#------------------------------------------------------------------------------
translations.define("TweetButton",
    ca = u"Botó de Twitter",
    es = u"Botón de Twitter",
    en = u"Twitter button"
)

translations.define("TweetButton-plural",
    ca = u"Botons de Twitter",
    es = u"Botones de Twitter",
    en = u"Twitter buttons"
)

translations.define("TweetButton.tweet",
    ca = u"Tuit",
    es = u"Tuit",
    en = u"Tweet"
)

translations.define("TweetButton.appearence",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define("TweetButton.tw_target",
    ca = u"Element a compartir",
    es = u"Elemento a compartir",
    en = u"Element to tweet"
)

translations.define("TweetButton.tw_target-explanation",
    ca = u"Deixar en blanc per compartir la pàgina on s'ubiqui el botó",
    es = u"Dejar en blanco para compartir la página donde se ubique el "
         u"botón",
    en = u"Leave blank to tweet the same page where the button resides"
)

translations.define("TweetButton.tw_via",
    ca = u"Via",
    es = u"Via",
    en = u"Via"
)

translations.define("TweetButton.tw_via-explanation",
    ca = u"Nom d'usuari al que s'atribuirà el tuit",
    es = u"Nombre de usuario al que se atribuirá el tuit",
    en = u"Screen name of the user to attribute the Tweet to"
)

translations.define("TweetButton.tw_related",
    ca = u"Comptes relacionats",
    es = u"Cuentas relacionadas",
    en = u"Related accounts"
)

translations.define("TweetButton.tw_hashtags",
    ca = u"Hashtags",
    es = u"Hashtags",
    en = u"Hashtag"
)

translations.define("TweetButton.tw_dnt",
    ca = u"Deshabilitar el seguiment de Twitter",
    es = u"Deshabilitar el seguimiento de Twitter",
    en = u"Opt out of Twitter tailoring"
)

translations.define("TweetButton.tw_text",
    ca = u"Text per defecte",
    es = u"Texto por defecto",
    en = u"Default text for the Tweet"
)

translations.define("TweetButton.tw_size",
    ca = u"Mida del botó",
    es = u"Tamaño del botón",
    en = u"Button size"
)

translations.define("TweetButton.tw_size=medium",
    ca = u"Mitjana",
    es = u"Mediana",
    en = u"Medium"
)

translations.define("TweetButton.tw_size=big",
    ca = u"Gran",
    es = u"Grande",
    en = u"Big"
)

translations.define("TweetButton.tw_count",
    ca = u"Recompte",
    es = u"Recuento",
    en = u"Count"
)

translations.define("TweetButton.tw_count=none",
    ca = u"Invisible",
    es = u"Invisible",
    en = u"None"
)

translations.define("TweetButton.tw_count=horizontal",
    ca = u"Horitzontal",
    es = u"Horizontal",
    en = u"Horizontal"
)

translations.define("TweetButton.tw_count=vertical",
    ca = u"Vertical",
    es = u"Vertical",
    en = u"Vertical"
)

# FlashBlock
#------------------------------------------------------------------------------
translations.define("FlashBlock",
    ca = u"Animació Flash",
    es = u"Animación Flash",
    en = u"Flash animation"
)

translations.define("FlashBlock-plural",
    ca = u"Animacions Flash",
    es = u"Animaciones Flash",
    en = u"Flash animations"
)

translations.define("FlashBlock.swf_file",
    ca = u"Fitxer Flash",
    es = u"Fichero Flash",
    en = u"Flash file"
)

translations.define("FlashBlock.swf_file",
    ca = u"Fitxer Flash",
    es = u"Fichero Flash",
    en = u"Flash file"
)

translations.define("FlashBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("FlashBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("FlashBlock.flash_version",
    ca = u"Versió del reproductor Flash",
    es = u"Versión del reproductor Flash",
    en = u"Flash player version"
)

translations.define("FlashBlock.flash_vars",
    ca = u"Variables Flash",
    es = u"Variables Flash",
    en = u"Flash variables"
)

translations.define("FlashBlock.flash_params",
    ca = u"Paràmetres Flash",
    es = u"Parámetros Flash",
    en = u"Flash parameters"
)

translations.define("FlashBlock.flash_attributes",
    ca = u"Atributs Flash",
    es = u"Atributos Flash",
    en = u"Flash attributes"
)

# Palette groups
#------------------------------------------------------------------------------
translations.define("woost.type_groups.blocks.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("woost.type_groups.blocks.layout",
    ca = u"Disposició",
    es = u"Disposición",
    en = u"Layout"
)

translations.define("woost.type_groups.blocks.listings",
    ca = u"Llistats",
    es = u"Listados",
    en = u"Listings"
)

translations.define("woost.type_groups.blocks.social",
    ca = u"Xarxes socials",
    es = u"Redes sociales",
    en = u"Social networks"
)

translations.define("woost.type_groups.blocks.forms",
    ca = u"Formularis",
    es = u"Formularios",
    en = u"Forms"
)

translations.define("woost.type_groups.blocks.custom",
    ca = u"Avançats",
    es = u"Avanzados",
    en = u"Custom"
)

# VimeoBlockRenderer
#------------------------------------------------------------------------------
translations.define("VimeoBlockRenderer",
    ca = u"Pintador de fotogrames pels blocs de Vimeo",
    es = u"Pintador de fotogramas para los bloques de Vimeo",
    en = u"Vimeo blocks still renderer"
)

translations.define("VimeoBlockRenderer-plural",
    ca = u"Pintadors de fotogrames pels blocs de Vimeo",
    es = u"Pintadores de fotogramas para los bloques de Vimeo",
    en = u"Vimeo blocks still renderers"
)

# YouTubeBlockRenderer
#------------------------------------------------------------------------------
translations.define("YouTubeBlockRenderer",
    ca = u"Pintador de fotogrames pels blocs de YouTube",
    es = u"Pintador de fotogramas para los bloques de YouTube",
    en = u"YouTube blocks still renderer"
)

translations.define("YouTubeBlockRenderer-plural",
    ca = u"Pintadors de fotogrames pels blocs de YouTube",
    es = u"Pintadores de fotogramas para los bloques de YouTube",
    en = u"YouTube blocks still renderers"
)

# PublishableListing
#------------------------------------------------------------------------------
translations.define("PublishableListing",
    ca = u"Llistat d'elements publicables",
    es = u"Listado de elementos publicables",
    en = u"Publishable elements listing"
)

translations.define("PublishableListing-plural",
    ca = u"Llistats d'elements publicables",
    es = u"Listados de elementos publicables",
    en = u"Publishable elements listings"
)

translations.define("PublishableListing.listing",
    ca = u"Llistat",
    es = u"Listado",
    en = u"Listing"
)

translations.define("PublishableListing.publishables",
    ca = u"Elements publicables",
    es = u"Elementos publicables",
    en = u"Publishable elements"
)

translations.define("PublishableListing.item_accessibility",
    ca = u"Control d'estat dels elements",
    es = u"Control de estado de los elementos",
    en = u"Item accessibility check"
)

translations.define("PublishableListing.item_accessibility=accessible",
    ca = u"Elements publicats i amb drets de lectura",
    es = u"Elementos publicados y con derechos de lectura",
    en = u"Published items with read privileges"
)

translations.define("PublishableListing.item_accessibility=published",
    ca = u"Elements publicats, tinguin o no drets de lectura",
    es = u"Elementos publicados, tengan o no derechos de lectura",
    en = u"Published items, regardless of read privileges"
)

translations.define("PublishableListing.item_accessibility=any",
    ca = u"Qualsevol element",
    es = u"Cualquier elemento",
    en = u"Any item"
)

translations.define("PublishableListing.listing_order",
    ca = u"Ordenació",
    es = u"Ordenación",
    en = u"Order"
)

translations.define("PublishableListing.listing_order=arbitrary",
    ca = u"Arbitrària",
    es = u"Arbitraria",
    en = u"Arbitrary"
)

translations.define("PublishableListing.listing_order=-last_update_time",
    ca = u"Última modificació",
    es = u"Última modificación",
    en = u"Last update"
)

translations.define("PublishableListing.links_open_in_new_window",
    ca = u"Obrir els enllaços a una nova finestra",
    es = u"Abrir los enlaces en una ventana nueva",
    en = u"Open links in a new window"
)

translations.define("PublishableListing.paginated",
    ca = u"Paginar els resultats",
    es = u"Paginar los resultados",
    en = u"Paginate results"
)

translations.define("PublishableListing.page_size",
    ca = u"Mida del llistat",
    es = u"Tamaño del listado",
    en = u"Listing size"
)

translations.define("PublishableListing.view_class",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

translations.define(
    "PublishableListing.view_class=woost.views.PublishableTextualListing",
    ca = u"Només text",
    es = u"Solo texto",
    en = u"Text only"
)

translations.define(
    "PublishableListing.view_class=woost.views.PublishableIconListing",
    ca = u"Icona i text",
    es = u"Icono y texto",
    en = u"Icon and text"
)

translations.define(
    "PublishableListing.view_class=woost.views.PublishableGrid",
    ca = u"Graella",
    es = u"Parrilla",
    en = u"Grid"
)

translations.define("PublishableListing.element_type",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Element type"
)

