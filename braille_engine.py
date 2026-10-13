MONUMENT_DB = {
    'Taj Mahal': {
        'short': 'Taj Mahal, white marble mausoleum, Agra, India, built 1632.',
        'built': '1632', 'height_m': 73
    },
    'Qutub Minar': {
        'short': 'Qutub Minar, brick minaret, Delhi, India, built 1193.',
        'built': '1193', 'height_m': 72
    },
    'Red Fort': {
        'short': 'Red Fort, sandstone fortress, Delhi, India, built 1648.',
        'built': '1648', 'height_m': 33
    },
    'Starry Night': {
        'short': 'Starry Night, painting by Van Gogh, 1889, oil on canvas.',
        'built': '1889', 'height_m': 0
    },
}

BRAILLE_ALPHABET = {
    'a': 0x01, 'b': 0x03, 'c': 0x09, 'd': 0x19, 'e': 0x11,
    'f': 0x0B, 'g': 0x1B, 'h': 0x13, 'i': 0x0A, 'j': 0x1A,
    'k': 0x05, 'l': 0x07, 'm': 0x0D, 'n': 0x1D, 'o': 0x15,
    'p': 0x0F, 'q': 0x1F, 'r': 0x17, 's': 0x0E, 't': 0x1E,
    'u': 0x25, 'v': 0x27, 'w': 0x3A, 'x': 0x2D, 'y': 0x3D,
    'z': 0x35, ' ': 0x00, ',': 0x02, '.': 0x32,
}

def text_to_braille_unicode(text):
    result = ''
    for char in text.lower():
        bits = BRAILLE_ALPHABET.get(char, 0x00)
        result += chr(0x2800 + bits)
    return result

def get_monument_info(name):
    return MONUMENT_DB.get(name, {
        'short': name,
        'built': 'Unknown',
        'height_m': 0
    })