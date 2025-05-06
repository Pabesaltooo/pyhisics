from typing import Union
from ..linalg import ScalarLike

def to_superscript(value: Union[ScalarLike, str]) -> str:
    """
    Convert a value (int, float, complex, or str) into a Unicode superscript string.

    - Digits 0–9, sign symbols, decimal point, plus “j” for complex, and
      basic Latin letters (a–z) are mapped to their superscript codepoints.
    - Any character not in the mapping is left as-is.
    - Complex numbers (e.g. 3+4j) will be rendered like “³⁺⁴ʲ”.
    
    Examples:
        to_superscript(123)         -> '¹²³'
        to_superscript(-5.07)       -> '⁻⁵·⁰⁷'
        to_superscript(2+3j)        -> '²⁺³ʲ'
        to_superscript("nabla")     -> 'ᶰᵃᵇˡᵃ'
    """
    sup_map = {
        '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹',
        '+':'⁺','-':'⁻','.':'·',
        'a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ','g':'ᶢ','h':'ʰ','i':'ⁱ','j':'ʲ',
        'k':'ᵏ','l':'ˡ','m':'ᵐ','n':'ⁿ','o':'ᵒ','p':'ᵖ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ',
        'v':'ᵛ','w':'ʷ','x':'ˣ','y':'ʸ','z':'ᶻ',
        'A':'ᴬ','B':'ᴮ','D':'ᴰ','E':'ᴱ','G':'ᴳ','H':'ᴴ','I':'ᴵ','J':'ᴶ','K':'ᴷ','L':'ᴸ',
        'M':'ᴹ','N':'ᴺ','O':'ᴼ','P':'ᴾ','R':'ᴿ','T':'ᵀ','U':'ᵁ','V':'ⱽ','W':'ᵂ'
    }

    text = str(value)
    return ''.join(sup_map.get(ch, ch) for ch in text)
